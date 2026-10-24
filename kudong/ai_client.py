import html
import json
import os
import re
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import yaml

from . import ai_subtitle as sub
from . import subs_download as subs

# 일본어 자막을 한국어로 번역합니다. OpenAI SDK 로 OpenAI 와 Gemini 를 모두 호출합니다.
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# base_url 을 비워 두면 쓰는 주소입니다. openai 는 SDK 기본 주소를 씁니다.
DEFAULT_BASE_URLS = {"openai": "", "gemini": GEMINI_BASE_URL}
TEXT_EXTENSIONS = (".srt", ".vtt", ".ass", ".ssa", ".smi", ".sami", ".txt")
# ASS/SRT 는 규칙에 맞게 다시 만들고 UTF-8(BOM 없음), LF 로 저장합니다.
REWRITE_EXTENSIONS = (".srt", ".ass", ".ssa")
GLOSSARY_FOLDER = "용어집"
# VTT, SMI, TXT 문자열 줄은 요청 한 번에 넣습니다. 이 한도를 넘을 때만 나눠 보냅니다.
BATCH_LINES = 4000
BATCH_CHARS = 500000
# SRT, ASS, SSA 한 요청의 기본 대사 수입니다. settings.yml 의 ai-translate.item_batch 로 바꿉니다.
ITEM_BATCH = 200
MAX_ITEM_BATCH = 4000
CONTEXT_ITEMS = 6
DEFAULT_CONCURRENCY = 3
MAX_CONCURRENCY = 8
REQUEST_TIMEOUT = 180.0
TRANSIENT_RETRIES = 2
GLOSSARY_SCRIPT_CHARS = 30000
_translate_lock = threading.Lock()
_log_lock = threading.Lock()
_reasoning_lock = threading.Lock()
_cancel_event = None
_reasoning_choice = {}
_translate_log_name = ""
_translate_log_lines = []
_JP_CHARS = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uff66-\uff9d]")
_TOKEN = re.compile(r"@@(\d+)@@")
_ASS_DRAWING = re.compile(r"\{\\p[1-9]")
_KARAOKE = re.compile(r"\{\\[kK][of]?\d+\}")
_ASS_TAG = re.compile(r"\{[^{}]*\}")
_HTML_TAG = re.compile(r"</?[A-Za-z][^<>]*>")
_SMI_TEXT = re.compile(
    r"(<P\b[^>]*>)(.*?)(?=<SYNC\b|</BODY>|</SAMI>|<P\b|$)",
    re.IGNORECASE | re.DOTALL,
)

# prompt.yml 이 없거나 항목이 비었을 때 쓰는 기본 프롬프트입니다.
PROMPT_FILE = "prompt.yml"
SYSTEM_PROMPT = (
    "당신은 애니메이션 자막 번역가입니다. 일본어 자막을 자연스러운 한국어 자막으로 번역합니다.\n"
    '입력은 {"lines": ["...", "..."]} JSON 입니다.\n'
    "출력도 같은 형식의 JSON 하나만 반환합니다. 설명이나 코드 블록은 붙이지 않습니다.\n"
    "규칙:\n"
    "- lines 길이와 순서를 입력과 같게 유지합니다.\n"
    "- @@0@@ 같은 토큰은 글자도 위치도 바꾸지 않습니다.\n"
    "- 줄을 합치거나 나누지 않습니다.\n"
    "- 대사의 말투와 호칭을 유지하고, 자막답게 간결하게 번역합니다.\n"
    "- 번역할 일본어가 없으면 그 줄은 그대로 둡니다."
)

TRANSLATE_PROMPT = """당신은 일본 애니메이션 전문 한국어 자막 번역가입니다. 일본어 대사를 자연스러운 한국어 자막으로 옮깁니다.

[입력 형식]
{"context":[...], "lines":[{"id":1,"who":"화자","type":"대사","ja":"원문","cont":true}, ...]}
- lines: 번역할 대사입니다. 시간순입니다.
- context: 바로 앞의 대사입니다. 흐름 파악에만 쓰고 번역하지 않습니다.
- who: 화자 이름입니다. 없으면 앞뒤 문맥으로 판단합니다. 번역문에 쓰지 않습니다.
- type: 대사 / 속마음 / 음성(전화·방송·화면 밖 목소리) / 이탤릭 / 화면(간판·자막 글자) / 가사
- cont: true 이면 문장이 다음 id로 이어집니다. 끝에 마침표를 찍지 않고, 다음 id와 이어 읽었을 때 자연스럽도록 그 id의 시간에 해당하는 내용만 옮깁니다.

[출력 형식]
JSON 객체 하나만 출력합니다: {"1":"번역","2":"번역"}
- lines의 모든 id를 빠짐없이 한 번씩 씁니다. id를 합치거나 나누지 않습니다.
- 설명, 코드 블록, 화자 이름, 일본어 원문, 줄바꿈을 넣지 않습니다.

[번역 원칙]
1. 직역보다 자연스러운 한국어 구어체로 옮깁니다. 의미를 빼거나 덧붙이지 않습니다.
2. 자막은 빨리 읽혀야 하므로 짧고 간결하게 옮깁니다.
3. 일본어에서 생략된 주어·목적어는 한국어에서도 생략이 자연스러우면 채우지 않습니다.
4. 존댓말/반말은 원문의 경어(です·ます체, 존경어·겸양어)와 용어집의 화자 관계로 정하고, 같은 두 사람 사이에서는 끝까지 일관되게 씁니다.
5. 1인칭(俺·僕·私·わたくし)과 고유 말투(～ですわ 등)는 한국어 어미로 캐릭터성을 살리되 과장하지 않습니다.
6. 고유명사는 용어집 표기를 반드시 따릅니다. 용어집에 없으면 나무위키 등 한국 정식 표기, 그다음 국립국어원 일본어 표기법을 따릅니다. 서양식 이름은 원어 철자에 맞춥니다.
7. 경칭은 용어집이 우선이고, 기본값은 ～さん→~씨, ～様→~님, ～先輩→선배, ～くん·～ちゃん→관계에 맞게(생략 가능), お嬢様→아가씨, 殿下→전하, 陛下→폐하 입니다.
8. えっ·はぁ·うわっ 같은 감탄사와 의성어·의태어는 한국어에서 자연스러운 표현으로 바꿉니다. (예: えっ→어?, はぁ→하아, うわっ→으악, あっ→앗)
9. 문장부호: 평서문 끝에는 마침표(.)를 찍지 않습니다. ?와 !는 그대로 씁니다. 말끝을 흐리면 ...을 씁니다. 「」→" ", 『』→' ' 로 바꾸고, ～는 쓰지 않습니다.
10. 히라가나·가타카나를 번역문에 남기지 않습니다.

[예시]
입력: {"lines":[{"id":1,"who":"ユウト","type":"대사","ja":"しまった 遅刻する!"},{"id":2,"type":"속마음","ja":"どうやら 俺は","cont":true},{"id":3,"type":"속마음","ja":"ベリーハードな人生のようだ。"},{"id":4,"who":"ユウト","type":"대사","ja":"ま… 待って下さい 田中さん!"},{"id":5,"type":"대사","ja":"えっ? 『マジエク』?"}]}
출력: {"1":"이런, 지각하겠어!","2":"아무래도 나는","3":"베리 하드한 인생인 모양이다","4":"자, 잠깐만요, 다나카 씨!","5":"어? '마지에크'?"}"""

GLOSSARY_PROMPT = """당신은 일본 애니메이션 한국어 자막 번역을 준비하는 감수자입니다. 일본어 자막 대본을 읽고 번역 용어집을 만듭니다.

[입력]
작품 제목, 기존 용어집, 대본(한 줄에 "화자: 대사", 화자를 모르면 "-: 대사").

[출력]
JSON 객체 하나만 출력합니다. 설명이나 코드 블록은 붙이지 않습니다.
{"terms":{"일본어 표기":"한국어 표기"},"characters":{"일본어 이름":"1인칭과 말투"},"speech":["A → B: 존댓말"]}

[규칙]
- terms: 인물명, 별명, 지명, 학교·조직명, 기술·마법명 등 작품 고유명사만 넣습니다. 일반 명사는 넣지 않습니다.
- 한국어 표기는 나무위키(한국 정식 방영·발매 표기)를 최우선으로 합니다. 모르면 국립국어원 일본어 표기법을 따르고, 서양식 이름(가타카나)은 원어 철자가 알려져 있으면 그에 맞춥니다.
- 성과 이름이 따로 불리면 각각도 넣습니다. (예: 山田太郎, 山田, 太郎)
- characters: 대본에서 확인되는 1인칭(俺·僕·私 등)과 말투(존댓말 위주, 반말, ～ですわ 같은 아가씨 말투 등)를 짧게 씁니다.
- speech: 누가 누구에게 존댓말/반말을 쓰는지 씁니다. 대본에 근거가 있는 것만 씁니다.
- 기존 용어집에 있는 항목은 다시 쓰지 않고 새 항목만 출력합니다. 확실하지 않으면 넣지 않습니다."""

DEFAULT_PROMPTS = {
    "translate": TRANSLATE_PROMPT,
    "glossary": GLOSSARY_PROMPT,
    "legacy": SYSTEM_PROMPT,
}

PROMPT_NOTES = {
    "translate": "ASS/SRT 대사 번역 프롬프트입니다. 입력은 id 가 붙은 lines JSON, 출력은 {\"id\":\"번역\"} JSON 이어야 합니다.",
    "glossary": "번역 전에 용어집을 만드는 프롬프트입니다. 출력은 terms/characters/speech 를 가진 JSON 이어야 합니다.",
    "legacy": "SMI/VTT/TXT 번역 프롬프트입니다. 입력과 출력은 {\"lines\": [...]} JSON 이고 @@0@@ 토큰을 지켜야 합니다.",
}


class AiClientError(Exception):
    pass


class _LineCountError(AiClientError):
    pass


class TranslateCancelled(Exception):
    pass


def korean_output_path(src_path):
    root, ext = os.path.splitext(src_path)
    if ext.lower() == ".zip":
        return root + ".ko"
    return root + ".ko" + ext


def _load_translate_section(path=None):
    path = path or "settings.yml"
    try:
        with open(path, encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}
    except FileNotFoundError as error:
        raise AiClientError("settings.yml 파일을 찾지 못했습니다.") from error
    except yaml.YAMLError as error:
        raise AiClientError("settings.yml 형식이 올바르지 않습니다.\n" + str(error)) from error

    if not isinstance(data, dict):
        raise AiClientError("settings.yml 형식이 올바르지 않습니다.")

    section = data.get("ai-translate") or {}
    if not isinstance(section, dict):
        raise AiClientError("settings.yml의 ai-translate 형식이 올바르지 않습니다.")
    return section


def load_ai_translate_settings(path=None):
    section = _load_translate_section(path)
    active_raw = section.get("active", "none")
    if isinstance(active_raw, bool) or active_raw is None:
        active = "none"
    else:
        active = str(active_raw).strip().lower()

    providers = section.get("providers") or {}
    if not isinstance(providers, dict):
        providers = {}
    return active, providers


def load_translate_options(path=None):
    section = _load_translate_section(path)
    try:
        concurrency = int(section.get("concurrency", DEFAULT_CONCURRENCY))
    except (TypeError, ValueError):
        concurrency = DEFAULT_CONCURRENCY
    try:
        item_batch = int(section.get("item_batch", ITEM_BATCH))
    except (TypeError, ValueError):
        item_batch = ITEM_BATCH
    glossary = section.get("glossary", True)
    if isinstance(glossary, str):
        glossary = glossary.strip().lower() not in ("false", "off", "no", "none", "0", "")
    return {
        "concurrency": min(MAX_CONCURRENCY, max(1, concurrency)),
        "glossary": bool(glossary),
        "item_batch": min(MAX_ITEM_BATCH, max(1, item_batch)),
    }


def _prompt_file_text():
    lines = [
        "# AI 번역 프롬프트입니다. 고친 내용은 다음 번역부터 바로 적용됩니다.",
        "# 항목을 지우거나 비우면 프로그램 기본 프롬프트를 씁니다. 이 파일을 지우면 기본값으로 다시 만듭니다.",
        "# 출력 형식(JSON) 설명을 바꾸면 결과를 읽지 못할 수 있으니 번역 원칙과 예시 위주로 고치세요.",
    ]
    for key, text in DEFAULT_PROMPTS.items():
        lines.append("")
        lines.append("# " + PROMPT_NOTES[key])
        lines.append(key + ": |")
        lines.extend(("  " + line) if line else "" for line in text.split("\n"))
    return "\n".join(lines) + "\n"


def load_prompts(path=None):
    path = path or PROMPT_FILE
    prompts = dict(DEFAULT_PROMPTS)
    if not os.path.isfile(path):
        try:
            _write_text(path, _prompt_file_text())
            _translate_log("> 프롬프트: %s 이 없어 기본값으로 만들었습니다." % path)
        except OSError as error:
            _translate_log("[=] 프롬프트: %s 을 만들지 못해 기본값을 씁니다. (%s)" % (path, error))
        return prompts

    try:
        with open(path, encoding="utf-8-sig") as file:
            data = yaml.safe_load(file) or {}
        if not isinstance(data, dict):
            raise ValueError("최상위가 항목: 값 형식이 아닙니다.")
    except Exception as error:
        _translate_log("[=] 프롬프트: %s 을 읽지 못해 기본값을 씁니다. (%s)" % (path, " ".join(str(error).split())))
        return prompts

    defaults = []
    for key in DEFAULT_PROMPTS:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            prompts[key] = value.strip()
        else:
            defaults.append(key)
    if defaults:
        _translate_log("> 프롬프트: %s (기본값 사용: %s)" % (path, ", ".join(defaults)))
    else:
        _translate_log("> 프롬프트: " + path)
    return prompts


def resolve_provider(path=None):
    active, providers = load_ai_translate_settings(path)
    if active in ("", "none", "off", "false", "disabled", "null"):
        raise AiClientError(
            "AI 번역이 꺼져 있습니다.\n"
            "settings.yml의 ai-translate.active를 openai 또는 gemini로 바꾼 뒤 API 키를 입력하세요."
        )

    info = None
    for key, value in providers.items():
        if str(key).strip().lower() == active and isinstance(value, dict):
            info = value
            break
    if info is None:
        raise AiClientError("settings.yml에 '" + active + "' 제공자 설정이 없습니다.")

    model = str(info.get("model") or "").strip()
    if model == "" or "모델명" in model:
        raise AiClientError(active + "의 model에 사용할 모델 이름을 입력하세요.")
    base_url = _read_base_url(active, info)
    return active, _read_api_key(active, info), model, base_url


def _read_base_url(provider, info):
    value = info.get("base_url")
    value = "" if value is None else str(value).strip()
    if value == "":
        value = DEFAULT_BASE_URLS.get(provider, "")
    if value == "" and provider not in DEFAULT_BASE_URLS:
        raise AiClientError(
            "'" + provider + "'는 기본 주소가 없는 제공자입니다.\n"
            "settings.yml의 ai-translate.providers." + provider + ".base_url 에 OpenAI 호환 API 주소를 적으세요."
        )
    if value and not re.match(r"^https?://", value, re.IGNORECASE):
        raise AiClientError(provider + "의 base_url은 http:// 또는 https:// 로 시작해야 합니다: " + value)
    return value


def ensure_translate_ready(path=None):
    resolve_provider(path)


def translate_subtitle_file(src_path, on_progress=None, cancel_event=None):
    if not os.path.isfile(src_path):
        raise AiClientError("번역할 원본 자막 파일이 없습니다.")

    global _cancel_event
    cancel_event = cancel_event or threading.Event()
    # 다른 파일 번역이 끝나길 기다리는 동안에도 취소할 수 있게 짧게 나눠 기다립니다.
    while not _translate_lock.acquire(timeout=0.2):
        if cancel_event.is_set():
            raise TranslateCancelled()
    try:
        _cancel_event = cancel_event
        _check_cancel()
        return _translate_locked(src_path, on_progress)
    finally:
        _cancel_event = None
        _translate_lock.release()


def cancel_requested():
    event = _cancel_event
    return event is not None and event.is_set()


def _check_cancel():
    if cancel_requested():
        raise TranslateCancelled()


def _wait_or_cancel(seconds):
    event = _cancel_event
    if event is None:
        time.sleep(seconds)
    elif event.wait(seconds):
        raise TranslateCancelled()


def _translate_locked(src_path, on_progress):
    _begin_translate_log(src_path)
    try:
        client, provider, model, base_url = _make_client()
    except Exception as error:
        _translate_log("[-] Error : %s" % error)
        _translate_log("================================================================")
        raise

    try:
        options = load_translate_options()
    except AiClientError:
        options = {"concurrency": DEFAULT_CONCURRENCY, "glossary": True, "item_batch": ITEM_BATCH}
    levels = _reasoning_levels(provider, model)
    _translate_log("> 제공자: " + provider)
    _translate_log("> 모델: " + model)
    _translate_log("> 주소: " + (base_url or "기본값"))
    if levels:
        _translate_log("> 생각 단계: " + levels[0])
    _translate_log("> 동시 요청: %d개" % options["concurrency"])
    _translate_log("> 대사 묶음: %d줄" % options["item_batch"])
    _translate_log("> 용어집: " + ("사용" if options["glossary"] else "사용 안 함"))
    _translate_log("================================================================")
    _notify_progress(on_progress, "번역 중")
    ticker = _TranslateTicker(on_progress)
    ticker.start()
    translator = _Translator(client, provider, model, on_progress, options, load_prompts())

    try:
        saved = _translate_path(src_path, translator)
    except TranslateCancelled:
        elapsed = _elapsed_label(ticker.stop())
        _translate_log("[-] 번역을 취소했습니다. 결과 파일은 저장하지 않았습니다.")
        _translate_log("> 소요 시간: " + elapsed)
        _translate_log("================================================================")
        raise
    except Exception as error:
        elapsed = _elapsed_label(ticker.stop())
        _translate_log("[-] Error : %s" % error)
        _translate_log("> 소요 시간: " + elapsed)
        _translate_log("================================================================")
        raise

    elapsed = _elapsed_label(ticker.stop())
    _translate_log("[+] 번역이 완료 되었습니다.")
    _translate_log("> 저장: " + saved)
    _translate_log("> 소요 시간: " + elapsed)
    _translate_log("================================================================")
    return saved


def _log_folder():
    folder = subs.log_path or (os.path.abspath(".") + "/log/")
    if not folder.endswith(("/", "\\")):
        folder += "/"
    return folder


def _new_log_name():
    try:
        return subs.get_new_log_file()
    except Exception:
        day = datetime.now().strftime("%Y-%m-%d")
        counter = 1
        while True:
            name = f"{day}-{counter}.log"
            if not os.path.exists(_log_folder() + name):
                return name
            counter += 1


def _begin_translate_log(src_path):
    global _translate_log_name, _translate_log_lines
    _translate_log_lines = []
    _translate_log_name = ""
    try:
        if not subs.isRunning:
            subs.console_output = ""
        if subs.log_path == "":
            subs.log_path = _log_folder()
        os.makedirs(_log_folder(), exist_ok=True)
        _translate_log_name = _new_log_name()
        subs.text_to_file("", _log_folder() + _translate_log_name)
    except Exception:
        _translate_log_name = ""
    _translate_log("AI 자막 번역")
    _translate_log("================================================================")
    _translate_log("> 파일: " + src_path)


def _elapsed_label(elapsed):
    seconds = int(elapsed)
    if seconds < 1:
        return "1초 미만"
    return str(seconds) + "초"


class _TranslateTicker:
    def __init__(self, on_progress):
        self._on_progress = on_progress
        self._stop = threading.Event()
        self._started = time.monotonic()
        self._thread = threading.Thread(target=self._run, name="ai-translate-log", daemon=True)

    def start(self):
        self._started = time.monotonic()
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread.is_alive():
            self._thread.join()
        return time.monotonic() - self._started

    def _run(self):
        while not self._stop.wait(1.0):
            seconds = max(1, int(time.monotonic() - self._started))
            _translate_log("[=] 번역이 진행중입니다... (" + str(seconds) + "초 지남)")
            _notify_progress(self._on_progress, "번역 중")


def _translate_log(message):
    text = str(message)
    with _log_lock:
        try:
            subs.print_log(text)
        except Exception:
            pass
        _translate_log_lines.append(text)
        _flush_translate_log()


def _flush_translate_log():
    if _translate_log_name == "":
        return
    try:
        subs.text_to_file("\n".join(_translate_log_lines) + "\n", _log_folder() + _translate_log_name)
    except Exception:
        pass


def _notify_progress(on_progress, text):
    if on_progress is not None:
        on_progress(text)


def _read_api_key(provider, info):
    key = info.get("api_key")
    key = "" if key is None else str(key).strip()
    if key:
        return key
    raise AiClientError(
        "API 키가 없습니다.\n"
        "settings.yml의 ai-translate.providers." + provider + ".api_key 에 키를 적으세요."
    )


def _make_client():
    provider, api_key, model, base_url = resolve_provider()
    try:
        from openai import OpenAI
    except ImportError as error:
        raise AiClientError("openai 패키지가 없습니다. pip install openai 로 설치하세요.") from error

    # SDK 의 자동 재시도는 로그 없이 몇 분씩 기다리므로 끄고, _chat 에서 이유를 남기며 재시도합니다.
    kwargs = {"api_key": api_key, "timeout": REQUEST_TIMEOUT, "max_retries": 0}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs), provider, model, base_url


def _gemini_reasoning_levels(model):
    # 번역은 깊은 추론이 필요 없어 생각 단계를 끄거나 최소로 둡니다. 모델이 거부하면 다음 값으로 내려갑니다.
    name = model.lower()
    if "2.5" in name:
        return ["low"] if "pro" in name else ["none", "low"]
    return ["minimal", "low"]


def _reasoning_levels(provider, model):
    if provider != "gemini":
        return []
    key = (provider, model)
    with _reasoning_lock:
        if key in _reasoning_choice:
            chosen = _reasoning_choice[key]
            return [chosen] if chosen else []
    return _gemini_reasoning_levels(model)


def _remember_reasoning(provider, model, level):
    with _reasoning_lock:
        _reasoning_choice[(provider, model)] = level


def _message_text(message):
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                parts.append(str(part.get("text") or ""))
            else:
                text = getattr(part, "text", None)
                if text:
                    parts.append(str(text))
        return "".join(parts)
    return "" if content is None else str(content)


def _parse_lines(content, expected):
    text = content.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    elif text.startswith("["):
        end = text.rfind("]")
        if end > 0:
            text = text[:end + 1]

    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise _LineCountError("번역 결과를 읽지 못했습니다.") from error

    if isinstance(data, dict):
        lines = data.get("lines")
    else:
        lines = data
    if not isinstance(lines, list) or len(lines) != expected:
        raise _LineCountError("번역 결과 줄 수가 맞지 않습니다.")
    return ["" if line is None else str(line) for line in lines]


def _describe_error(error):
    names = {
        "APITimeoutError": "시간 초과(%d초)" % REQUEST_TIMEOUT,
        "APIConnectionError": "서버 연결 실패",
        "RateLimitError": "요청 한도 초과",
        "AuthenticationError": "API 키 인증 실패",
        "PermissionDeniedError": "권한 없음",
        "NotFoundError": "모델 또는 주소를 찾을 수 없음",
        "BadRequestError": "잘못된 요청",
        "InternalServerError": "서버 오류",
    }
    kind = names.get(type(error).__name__, type(error).__name__)
    status = getattr(error, "status_code", None)
    if status:
        kind += " (HTTP %s)" % status
    detail = " ".join(str(error).split())
    if len(detail) > 300:
        detail = detail[:300] + "..."
    return kind + (": " + detail if detail else "")


def _is_transient(error):
    if type(error).__name__ in ("APITimeoutError", "APIConnectionError", "RateLimitError"):
        return True
    status = getattr(error, "status_code", None)
    return isinstance(status, int) and (status == 429 or status >= 500)


def _retry_delay(error, attempt):
    if type(error).__name__ == "RateLimitError" or getattr(error, "status_code", None) == 429:
        return 10.0 * attempt
    return 3.0 * attempt


def _create_cancellable(client, payload):
    event = _cancel_event
    if event is None:
        return client.chat.completions.create(**payload)

    # 진행 중인 HTTP 요청은 끊을 수 없으므로 별도 스레드에서 받고, 취소되면 결과를 버리고 바로 빠져나옵니다.
    box = {}

    def run():
        try:
            box["response"] = client.chat.completions.create(**payload)
        except BaseException as error:
            box["error"] = error

    thread = threading.Thread(target=run, name="ai-request", daemon=True)
    thread.start()
    while thread.is_alive():
        if event.wait(0.2):
            raise TranslateCancelled()
        thread.join(0.05)
    if "error" in box:
        raise box["error"]
    return box["response"]


def _chat(client, provider, model, system, user, label="AI 요청"):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    levels = _reasoning_levels(provider, model)
    if levels:
        payload["reasoning_effort"] = levels.pop(0)

    last_error = None
    transient = 0
    for _attempt in range(8):
        _check_cancel()
        started = time.monotonic()
        try:
            response = _create_cancellable(client, payload)
            if provider == "gemini":
                _remember_reasoning(provider, model, payload.get("reasoning_effort"))
            choice = response.choices[0] if response.choices else None
            text = _message_text(choice.message) if choice is not None else ""
            finish = getattr(choice, "finish_reason", None) if choice is not None else None
            if finish == "length":
                _translate_log("[=] %s: 응답이 출력 길이 한도에서 잘렸습니다. 받은 부분만 사용합니다." % label)
            elif finish not in (None, "stop"):
                _translate_log("[=] %s: 응답 종료 이유가 '%s'입니다." % (label, finish))
            if text.strip() == "":
                reason = "AI 응답이 비어 있습니다." + (" (종료 이유: %s)" % finish if finish else "")
                if "response_format" in payload:
                    _translate_log("[=] %s: %s JSON 형식 지정을 빼고 다시 요청합니다." % (label, reason))
                    payload.pop("response_format", None)
                    last_error = AiClientError(reason)
                    continue
                raise AiClientError(reason)
            return text
        except (AiClientError, TranslateCancelled):
            raise
        except Exception as error:
            last_error = error
            elapsed = time.monotonic() - started
            reason = _describe_error(error)
            if _is_transient(error) and transient < TRANSIENT_RETRIES:
                transient += 1
                delay = _retry_delay(error, transient)
                _translate_log(
                    "[=] %s 실패 (%.0f초 경과): %s → %.0f초 뒤 다시 요청합니다. (%d/%d)"
                    % (label, elapsed, reason, delay, transient, TRANSIENT_RETRIES)
                )
                _wait_or_cancel(delay)
                continue

            message = str(error).lower()
            changed = False
            format_rejected = (
                "response_format" in message
                or "json_object" in message
                or "response format" in message
            )
            if "response_format" in payload and format_rejected:
                payload.pop("response_format", None)
                _translate_log("[=] %s: 이 모델은 JSON 형식 지정 없이 번역합니다." % label)
                changed = True
            if "temperature" in payload and "temperature" in message:
                payload.pop("temperature", None)
                _translate_log("[=] %s: 이 모델은 기본 temperature로 번역합니다." % label)
                changed = True
            if "reasoning_effort" in payload and ("reasoning" in message or "thinking" in message):
                rejected = payload.pop("reasoning_effort")
                if levels:
                    payload["reasoning_effort"] = levels.pop(0)
                    _translate_log("[=] 생각 단계 '%s'를 지원하지 않아 '%s'로 바꿉니다." % (rejected, payload["reasoning_effort"]))
                else:
                    _translate_log("[=] 생각 단계 '%s'를 지원하지 않아 모델 기본값을 사용합니다." % rejected)
                changed = True
            if not changed:
                _translate_log("[-] %s 실패 (%.0f초 경과): %s" % (label, elapsed, reason))
                break
    if isinstance(last_error, AiClientError):
        raise last_error
    raise AiClientError("AI 번역 요청에 실패했습니다.\n" + _describe_error(last_error))


def _translate_group(client, provider, model, lines, system):
    if not lines:
        return []
    try:
        user = json.dumps({"lines": lines}, ensure_ascii=False)
        return _parse_lines(_chat(client, provider, model, system, user), len(lines))
    except _LineCountError:
        if len(lines) == 1:
            raise AiClientError("번역 결과 형식이 맞지 않습니다.")
        _translate_log("[=] 번역 결과 줄 수가 맞지 않아 나누어 다시 요청합니다.")
        mid = len(lines) // 2
        left = _translate_group(client, provider, model, lines[:mid], system)
        right = _translate_group(client, provider, model, lines[mid:], system)
        return left + right


def _translate_lines(client, provider, model, lines, on_progress, system=SYSTEM_PROMPT):
    if not lines:
        return []

    chunks = []
    current = []
    size = 0
    for line in lines:
        if current and (len(current) >= BATCH_LINES or size + len(line) > BATCH_CHARS):
            chunks.append(current)
            current = []
            size = 0
        current.append(line)
        size += len(line)
    if current:
        chunks.append(current)

    output = []
    total = len(chunks)
    for index, chunk in enumerate(chunks, start=1):
        _check_cancel()
        detail = str(len(chunk)) + "줄 번역을 요청합니다."
        if total > 1:
            detail += " (" + str(index) + "번째 요청)"
        _translate_log("[+] " + detail)
        _notify_progress(on_progress, "번역 중")
        output.extend(_translate_group(client, provider, model, chunk, system))
    return output


def _json_object(content):
    text = content.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _parse_items(content):
    data = _json_object(content)
    if isinstance(data, dict):
        for key in ("lines", "ko", "result", "results", "translations", "items", "output"):
            if isinstance(data.get(key), (dict, list)):
                data = data[key]
                break

    result = {}
    if isinstance(data, dict):
        for key, value in data.items():
            if str(key).strip().isdigit() and isinstance(value, str):
                result[int(str(key).strip())] = value
    elif isinstance(data, list):
        for entry in data:
            if not isinstance(entry, dict) or "id" not in entry:
                continue
            value = entry.get("ko", entry.get("text", entry.get("t")))
            if str(entry["id"]).strip().isdigit() and isinstance(value, str):
                result[int(str(entry["id"]).strip())] = value
    if result:
        return result

    # 응답이 중간에 잘려 JSON 으로 읽히지 않으면 완성된 항목만 건집니다.
    for key, value in re.findall(r'"(\d+)"\s*:\s*"((?:[^"\\]|\\.)*)"', content):
        try:
            result[int(key)] = json.loads('"' + value + '"')
        except json.JSONDecodeError:
            continue
    return result


def _glossary_block(glossary):
    sections = []
    terms = glossary.get("terms") or {}
    if terms:
        sections.append("고유명사:\n" + "\n".join("- %s → %s" % (ja, ko) for ja, ko in terms.items()))
    characters = glossary.get("characters") or {}
    if characters:
        sections.append("캐릭터 말투:\n" + "\n".join("- %s: %s" % item for item in characters.items()))
    speech = glossary.get("speech") or []
    if speech:
        sections.append("존댓말/반말:\n" + "\n".join("- " + str(line) for line in speech))
    notes = glossary.get("notes") or []
    if notes:
        sections.append("메모:\n" + "\n".join("- " + str(line) for line in notes))
    return "\n".join(sections)


class _Translator:
    def __init__(self, client, provider, model, on_progress, options, prompts):
        self.client = client
        self.provider = provider
        self.model = model
        self.on_progress = on_progress
        self.concurrency = options["concurrency"]
        self.item_batch = options["item_batch"]
        self.use_glossary = options["glossary"]
        self.prompts = prompts

    def lines(self, lines):
        return _translate_lines(
            self.client, self.provider, self.model, lines, self.on_progress, self.prompts["legacy"]
        )

    def extend_glossary(self, glossary, parts):
        script = []
        size = 0
        for part in parts:
            line = (part.who or "-") + ": " + part.text
            size += len(line) + 1
            if size > GLOSSARY_SCRIPT_CHARS:
                break
            script.append(line)
        user = "작품 제목: %s\n\n기존 용어집:\n%s\n\n대본:\n%s" % (
            glossary.get("title") or "알 수 없음",
            _glossary_block(glossary) or "(없음)",
            "\n".join(script),
        )
        _translate_log("[+] 용어집을 정리합니다.")
        _notify_progress(self.on_progress, "번역 중")
        try:
            content = _chat(self.client, self.provider, self.model, self.prompts["glossary"], user, "용어집 요청")
        except AiClientError as error:
            _translate_log("[=] 용어집을 만들지 못해 기존 용어집으로 번역합니다. (%s)" % str(error).splitlines()[-1])
            return 0
        data = _json_object(content)
        if not isinstance(data, dict):
            snippet = " ".join(content.split())[:200]
            _translate_log("[=] 용어집 응답을 JSON으로 읽지 못해 기존 용어집으로 번역합니다. 응답 앞부분: " + snippet)
            return 0
        return _merge_glossary(glossary, data)

    def items(self, parts, glossary):
        system = self.prompts["translate"]
        block = _glossary_block(glossary)
        if block:
            system += "\n\n[용어집: 표기와 말투 관계를 반드시 따릅니다]\n" + block

        items = []
        for index, part in enumerate(parts, start=1):
            item = {"id": index}
            if part.who:
                item["who"] = part.who
            item["type"] = part.kind
            item["ja"] = part.text
            if part.cont:
                item["cont"] = True
            items.append(item)

        chunks = [items[start:start + self.item_batch] for start in range(0, len(items), self.item_batch)]

        def run(number, chunk):
            _check_cancel()
            detail = str(len(chunk)) + "줄 번역을 요청합니다."
            if len(chunks) > 1:
                detail += " (%d/%d)" % (number, len(chunks))
            _translate_log("[+] " + detail)
            _notify_progress(self.on_progress, "번역 중")
            first = chunk[0]["id"] - 1
            context = [
                ((item.get("who") or "-") + ": " + item["ja"])
                for item in items[max(0, first - CONTEXT_ITEMS):first]
            ]
            got = self._request(system, chunk, context, 0, "%d/%d" % (number, len(chunks)))
            if len(chunks) > 1:
                _translate_log("[+] %d/%d 묶음 번역을 받았습니다." % (number, len(chunks)))
            return got

        results = {}
        workers = min(self.concurrency, len(chunks))
        if workers <= 1:
            for number, chunk in enumerate(chunks, start=1):
                results.update(run(number, chunk))
        else:
            with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="ai-translate") as pool:
                futures = [pool.submit(run, number, chunk) for number, chunk in enumerate(chunks, start=1)]
                try:
                    for future in as_completed(futures):
                        results.update(future.result())
                except BaseException:
                    for future in futures:
                        future.cancel()
                    raise
        return [results[item["id"]] for item in items]

    def _request(self, system, items, context, depth, label):
        user = json.dumps({"context": context, "lines": items}, ensure_ascii=False)
        span = "id %d~%d" % (items[0]["id"], items[-1]["id"])
        tag = "번역 %s, %s" % (label, span)
        try:
            content = _chat(self.client, self.provider, self.model, system, user, tag)
            parsed = _parse_items(content)
            if not parsed:
                snippet = " ".join(content.split())[:200]
                _translate_log("[=] %s: 응답을 JSON으로 읽지 못했습니다. 응답 앞부분: %s" % (tag, snippet))
        except AiClientError as error:
            if depth >= 2:
                raise
            _translate_log("[=] %s: 요청이 실패해 나눠서 다시 요청합니다. (%s)" % (tag, str(error).splitlines()[-1]))
            parsed = {}

        got = {}
        absent = empty = kana = 0
        for item in items:
            value = parsed.get(item["id"])
            if not isinstance(value, str):
                absent += 1
                continue
            # 처음 요청에서는 비었거나 가나가 남은 번역도 다시 받아 봅니다.
            if depth == 0 and value.strip() == "":
                empty += 1
                continue
            if sub.has_kana(value):
                if depth == 0:
                    kana += 1
                    continue
                _translate_log("[=] %s: id %d에 가나가 남았지만 그대로 씁니다. (%s)" % (tag, item["id"], value))
            got[item["id"]] = value

        missing = [item for item in items if item["id"] not in got]
        if not missing:
            return got
        reasons = []
        if absent:
            reasons.append("응답에 없음 %d줄" % absent)
        if empty:
            reasons.append("빈 번역 %d줄" % empty)
        if kana:
            reasons.append("가나 남음 %d줄" % kana)
        if depth >= 2:
            _translate_log("[-] %s: 다시 요청해도 %d줄을 받지 못했습니다. (%s)" % (tag, len(missing), ", ".join(reasons)))
            raise AiClientError("번역 결과가 %d줄 비어 있습니다. 잠시 후 다시 시도하세요." % len(missing))
        _translate_log("[=] %s: %d줄을 다시 요청합니다. (%s)" % (tag, len(missing), ", ".join(reasons)))
        size = max(1, (len(missing) + 1) // 2) if len(missing) > 20 else len(missing)
        for start in range(0, len(missing), size):
            got.update(self._request(system, missing[start:start + size], context, depth + 1, label + " 재요청"))
        return got


def _work_title(name):
    stem = os.path.basename(name.replace("\\", "/"))
    stem = re.sub(r"(\.ko)?\.[A-Za-z0-9]{2,4}$", "", stem)
    title = re.sub(r"^\s*(\[[^\]]*\]\s*)+", "", stem)
    title = re.split(
        r"\.S\d{1,2}E\d{1,3}|\s+S\d{1,2}E\d{1,3}|\s-\s*\d{1,3}(?:v\d)?(?!\d)|\s*第\s*\d+\s*[話话]"
        r"|\s*#\s*\d+|\s+E[Pp]?\d{1,3}(?!\d)|\s*\(\s*\d{3,4}p|\s*\[",
        title,
    )[0]
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title.replace("_", " ")).strip(" .")
    return title or stem or "subtitle"


def _glossary_path(folder, name):
    return os.path.join(folder, GLOSSARY_FOLDER, _work_title(name) + ".yml")


def _empty_glossary(title):
    return {"title": title, "keep_lyrics": False, "terms": {}, "characters": {}, "speech": [], "notes": []}


def _load_glossary(path, title):
    glossary = _empty_glossary(title)
    writable = True
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8") as file:
                data = yaml.safe_load(file) or {}
            if not isinstance(data, dict):
                raise ValueError("형식이 올바르지 않습니다.")
            glossary["title"] = str(data.get("title") or title)
            glossary["keep_lyrics"] = bool(data.get("keep_lyrics"))
            for key in ("terms", "characters"):
                if isinstance(data.get(key), dict):
                    glossary[key] = {str(k): str(v) for k, v in data[key].items() if v is not None}
            for key in ("speech", "notes"):
                if isinstance(data.get(key), list):
                    glossary[key] = [str(line) for line in data[key] if line is not None]
        except Exception as error:
            # 사용자가 고친 파일이 깨졌을 수 있으므로 덮어쓰지 않습니다.
            writable = False
            _translate_log("[=] 용어집을 읽지 못해 이번 번역에는 쓰지 않습니다: %s" % error)
    return glossary, writable


def _merge_glossary(glossary, data):
    added = 0
    for key in ("terms", "characters"):
        found = data.get(key)
        if not isinstance(found, dict):
            continue
        for ja, value in found.items():
            ja = str(ja).strip()
            value = "" if value is None else str(value).strip()
            if ja and value and ja not in glossary[key]:
                glossary[key][ja] = value
                added += 1
    speech = data.get("speech")
    if isinstance(speech, list):
        known = {re.split(r"\s*:\s*", line, 1)[0].replace(" ", "") for line in glossary["speech"]}
        for line in speech:
            line = str(line).strip()
            pair = re.split(r"\s*:\s*", line, 1)[0].replace(" ", "")
            if line and ":" in line and pair not in known:
                glossary["speech"].append(line)
                known.add(pair)
                added += 1
    return added


def _save_glossary(path, glossary):
    body = yaml.safe_dump(
        {
            "title": glossary["title"],
            "keep_lyrics": glossary["keep_lyrics"],
            "terms": glossary["terms"],
            "characters": glossary["characters"],
            "speech": glossary["speech"],
            "notes": glossary["notes"],
        },
        allow_unicode=True,
        sort_keys=False,
        width=1000,
    )
    header = (
        "# AI 번역 용어집입니다. 고친 내용은 같은 작품의 다음 번역부터 그대로 적용됩니다.\n"
        "# terms: 고유명사 표기, characters: 1인칭과 말투, speech: 존댓말/반말 관계\n"
        "# keep_lyrics: 노래 가사(♪)도 번역해 넣을 작품이면 true\n"
    )
    _write_text(path, header + body)


def _rewrite_subtitle(text, ext, translator, name, glossary_folder):
    if ext == ".srt":
        raws, stats = sub.parse_srt(text)
    else:
        raws, stats = sub.parse_ass(text)
    if not raws:
        raise AiClientError("자막에서 대사를 찾지 못했습니다.")

    path = _glossary_path(glossary_folder, name)
    exists = translator.use_glossary and os.path.isfile(path)
    if translator.use_glossary:
        glossary, writable = _load_glossary(path, _work_title(name))
    else:
        glossary, writable = _empty_glossary(_work_title(name)), False
    events, removed = sub.build_events(raws, glossary["keep_lyrics"])
    _translate_log(
        "> 정리: 원본 %d개 → %d개 (같은 시간 병합 %d개, 효과음·가사·라벨 줄 제거 %d개)"
        % (stats["source"], len(events), stats["merged"], removed)
    )

    parts = [part for event in events for part in event.parts() if part.ko == ""]
    _translate_log("번역 대상 => " + str(len(parts)) + "줄")
    _check_cancel()
    if parts:
        if not translator.use_glossary:
            _translate_log("> 용어집: 사용 안 함")
        elif exists and not writable:
            pass
        else:
            added = translator.extend_glossary(glossary, parts)
            if added:
                try:
                    _save_glossary(path, glossary)
                    if exists:
                        _translate_log("> 용어집: %s (기존 용어집 사용, 새 항목 %d개)" % (path, added))
                    else:
                        _translate_log("> 용어집: %s (새로 만듦, 항목 %d개)" % (path, added))
                except OSError as error:
                    _translate_log("[=] 용어집을 저장하지 못했습니다: %s" % error)
            elif exists:
                _translate_log("> 용어집: %s (기존 용어집 사용, 새 항목 없음)" % path)
            else:
                _translate_log("> 용어집: 만들 항목이 없어 저장하지 않았습니다. 다음 번역 때 다시 만듭니다.")
        for part, value in zip(parts, translator.items(parts, glossary)):
            part.ko = sub.polish(value, part.cont)

    if ext == ".srt":
        rendered, warnings = sub.render_srt(events)
    else:
        rendered, warnings = sub.render_ass(events)
    for warning in warnings:
        _translate_log("[=] " + warning)
    return rendered


def _needs_translation(text):
    plain = _TOKEN.sub("", text)
    return _JP_CHARS.search(plain) is not None


def _keep_original(text):
    if _ASS_DRAWING.search(text):
        return True
    shielded, _tokens = _shield(text)
    return not _needs_translation(shielded)


def _shield(text):
    tokens = []

    def put(value):
        tokens.append(value)
        return "@@" + str(len(tokens) - 1) + "@@"

    text = _KARAOKE.sub("", text)
    text = _ASS_TAG.sub(lambda match: put(match.group(0)), text)
    text = _HTML_TAG.sub(lambda match: put(match.group(0)), text)
    text = text.replace("\\N", put("\\N")).replace("\\n", put("\\n")).replace("\\h", put("\\h"))
    text = text.replace("\n", put("\n"))
    return text, tokens


def _restore(text, tokens):
    def repl(match):
        index = int(match.group(1))
        if 0 <= index < len(tokens):
            return tokens[index]
        return match.group(0)

    return _TOKEN.sub(repl, text)


def _map_texts(texts, translate):
    output = list(texts)
    jobs = []
    for index, text in enumerate(texts):
        if text is None or _keep_original(text):
            continue
        shielded, tokens = _shield(text)
        jobs.append((index, tokens, shielded))
    _translate_log("번역 대상 => " + str(len(jobs)) + "/" + str(len(texts)) + "줄")
    if not jobs:
        return output

    translated = translate([job[2] for job in jobs])
    if not isinstance(translated, list) or len(translated) != len(jobs):
        raise AiClientError("번역 결과 수가 맞지 않습니다.")
    for (index, tokens, _shielded), line in zip(jobs, translated):
        output[index] = _restore(str(line), tokens)
    return output


def _newline_style(text):
    if "\r\n" in text:
        return "\r\n"
    return "\n"


def _decode_bytes(data):
    if data.startswith(b"\xef\xbb\xbf"):
        return data.decode("utf-8-sig")
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    head = data[:4000]
    if len(head) >= 2 and head.count(b"\x00") * 3 > len(head):
        encoding = "utf-16-le" if head[1:2] == b"\x00" else "utf-16-be"
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    for encoding in ("utf-8", "cp932", "euc-jp"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def _read_text(path):
    size = os.path.getsize(path)
    if size > 8 * 1024 * 1024:
        raise AiClientError("자막 파일이 너무 커서 번역하지 않습니다.")
    with open(path, "rb") as file:
        return _decode_bytes(file.read())


def _write_text(path, text, bom=False):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    partial = path + ".part"
    try:
        with open(partial, "w", encoding="utf-8-sig" if bom else "utf-8", newline="") as file:
            file.write(text)
        os.replace(partial, path)
    except Exception:
        if os.path.isfile(partial):
            try:
                os.remove(partial)
            except OSError:
                pass
        raise


def _sniff_extension(text):
    sample = text.lstrip("\ufeff")[:8000]
    upper = sample.upper()
    if upper.startswith("WEBVTT"):
        return ".vtt"
    if "<SAMI" in upper:
        return ".smi"
    if "[SCRIPT INFO]" in upper or re.search(r"(?im)^[ \t]*dialogue\s*:", sample):
        return ".ass"
    if "-->" in sample:
        return ".srt"
    return ""


def _translate_path(src_path, translator):
    ext = os.path.splitext(src_path)[1].lower()
    if ext == ".zip":
        return _translate_zip(src_path, translator)

    text = _read_text(src_path)
    kind = ext if ext in TEXT_EXTENSIONS else _sniff_extension(text)
    if kind == "" and _needs_translation(text[:20000]):
        kind = ".txt"
    if kind == "":
        shown = ext or "알 수 없음"
        raise AiClientError("이 형식은 텍스트 자막이 아니라 번역할 수 없습니다: " + shown)

    _translate_log("> 형식: " + kind)
    folder = os.path.dirname(os.path.abspath(src_path))
    translated = _translate_document(text, kind, translator, src_path, folder)
    _write_text(korean_output_path(src_path), translated, bom=kind not in REWRITE_EXTENSIONS)
    return korean_output_path(src_path)


def _translate_document(text, ext, translator, name, glossary_folder):
    if ext in REWRITE_EXTENSIONS:
        return _rewrite_subtitle(text, ext, translator, name, glossary_folder)
    if ext == ".vtt":
        return _translate_cues(text, translator.lines)
    if ext in (".smi", ".sami"):
        return _translate_smi(text, translator.lines)
    if ext == ".txt":
        return _translate_plain(text, translator.lines)
    raise AiClientError("이 형식은 번역할 수 없습니다: " + ext)


def _translate_cues(text, translate):
    newline = _newline_style(text)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if normalized.startswith("\ufeff"):
        normalized = normalized[1:]
    chunks = re.split(r"\n[ \t]*\n", normalized.strip())
    blocks = []
    bodies = []
    for chunk in chunks:
        if chunk.strip() == "":
            continue
        lines = chunk.split("\n")
        time_index = None
        for index, line in enumerate(lines[:3]):
            if "-->" in line:
                time_index = index
                break
        if time_index is None:
            blocks.append({"kind": "raw", "text": chunk})
            continue
        body = "\n".join(lines[time_index + 1:])
        blocks.append({
            "kind": "cue",
            "head": "\n".join(lines[:time_index + 1]),
            "body_index": len(bodies),
        })
        bodies.append(body)

    translated = _map_texts(bodies, translate)
    parts = []
    for block in blocks:
        if block["kind"] == "raw":
            parts.append(block["text"])
            continue
        body = translated[block["body_index"]]
        if body:
            parts.append(block["head"] + "\n" + body)
        else:
            parts.append(block["head"])
    rendered = "\n\n".join(parts) + "\n"
    if newline != "\n":
        rendered = rendered.replace("\n", newline)
    return rendered


def _translate_plain(text, translate):
    newline = _newline_style(text)
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    return newline.join(_map_texts(lines, translate))


def _edge_text(value):
    match = re.match(r"^(\s*)(.*?)(\s*)$", value, re.DOTALL)
    return match.group(1), match.group(2), match.group(3)


def _translate_smi(text, translate):
    body_match = re.search(r"<BODY\b[^>]*>", text, re.IGNORECASE)
    if not body_match:
        raise AiClientError("SMI 본문을 찾지 못했습니다.")

    head = text[:body_match.end()]
    body = text[body_match.end():]
    pieces = []
    shielded_lines = []
    cursor = 0
    for found in _SMI_TEXT.finditer(body):
        pieces.append(body[cursor:found.start()])
        pieces.append(found.group(1))
        leading, inner, trailing = _edge_text(found.group(2))
        unescaped = html.unescape(inner)
        if _keep_original(unescaped):
            pieces.append(leading + inner + trailing)
        else:
            shielded, tokens = _shield(unescaped)
            pieces.append((len(shielded_lines), tokens, leading, trailing))
            shielded_lines.append(shielded)
        cursor = found.end()
    pieces.append(body[cursor:])

    _translate_log("번역 대상 => " + str(len(shielded_lines)) + "줄")
    translated = translate(shielded_lines) if shielded_lines else []
    if len(translated) != len(shielded_lines):
        raise AiClientError("번역 결과 수가 맞지 않습니다.")

    output = [head]
    for piece in pieces:
        if not isinstance(piece, tuple):
            output.append(piece)
            continue
        index, tokens, leading, trailing = piece
        escaped = html.escape(str(translated[index]), quote=False)
        output.append(leading + _restore(escaped, tokens) + trailing)
    return "".join(output)


def _zip_member_name(info):
    name = info.filename.replace("\\", "/")
    if info.flag_bits & 0x800:
        return name
    try:
        return name.encode("cp437").decode("cp932")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def _safe_zip_name(name):
    if os.path.isabs(name):
        return ""
    cleaned = os.path.normpath(name).replace("\\", "/")
    parts = [part for part in cleaned.split("/") if part not in ("", ".")]
    if not parts or ".." in parts or parts[0] == "__MACOSX":
        return ""
    if parts[-1].startswith("."):
        return ""
    return "/".join(parts)


def _translate_zip(src_path, translator):
    folder = os.path.dirname(os.path.abspath(src_path))
    outputs = []
    with zipfile.ZipFile(src_path) as archive:
        for info in archive.infolist():
            if info.is_dir() or info.file_size > 8 * 1024 * 1024:
                continue
            name = _safe_zip_name(_zip_member_name(info))
            if name == "":
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext not in TEXT_EXTENSIONS or ext == ".txt":
                continue
            text = _decode_bytes(archive.read(info))
            _translate_log("[+] 압축 항목 => " + name)
            _translate_log("> 형식: " + ext)
            translated = _translate_document(text, ext, translator, name, folder)
            root, member_ext = os.path.splitext(name)
            outputs.append((root + ".ko" + member_ext, translated, ext not in REWRITE_EXTENSIONS))

    if not outputs:
        raise AiClientError("압축 파일 안에 번역할 자막이 없습니다.")

    out_dir = korean_output_path(src_path)
    for name, text, bom in outputs:
        _write_text(os.path.join(out_dir, name.replace("/", os.sep)), text, bom=bom)
    return out_dir
