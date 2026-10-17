import html
import json
import os
import re
import threading
import time
import zipfile
from datetime import datetime

import yaml

from . import subs_download as subs

# 일본어 자막을 한국어로 번역합니다. OpenAI SDK 로 OpenAI 와 Gemini 를 모두 호출합니다.
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
TEXT_EXTENSIONS = (".srt", ".vtt", ".ass", ".ssa", ".smi", ".sami", ".txt")
# 한 파일의 대사를 요청 한 번에 넣습니다. 이 한도를 넘을 때만 나눠 보냅니다.
BATCH_LINES = 4000
BATCH_CHARS = 500000
_translate_lock = threading.Lock()
_log_lock = threading.Lock()
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


class AiClientError(Exception):
    pass


class _LineCountError(AiClientError):
    pass


def korean_output_path(src_path):
    root, ext = os.path.splitext(src_path)
    if ext.lower() == ".zip":
        return root + ".ko"
    return root + ".ko" + ext


def load_ai_translate_settings(path=None):
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

    active_raw = section.get("active", "none")
    if isinstance(active_raw, bool) or active_raw is None:
        active = "none"
    else:
        active = str(active_raw).strip().lower()

    providers = section.get("providers") or {}
    if not isinstance(providers, dict):
        providers = {}
    return active, providers


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
    return active, _read_api_key(active, info), model


def ensure_translate_ready(path=None):
    resolve_provider(path)


def translate_subtitle_file(src_path, on_progress=None):
    if not os.path.isfile(src_path):
        raise AiClientError("번역할 원본 자막 파일이 없습니다.")

    with _translate_lock:
        _begin_translate_log(src_path)
        try:
            client, provider, model = _make_client()
        except Exception as error:
            _translate_log("[-] Error : %s" % error)
            _translate_log("================================================================")
            raise

        _translate_log("> 제공자: " + provider)
        _translate_log("> 모델: " + model)
        _translate_log("================================================================")
        _notify_progress(on_progress, "번역 중")
        ticker = _TranslateTicker(on_progress)
        ticker.start()

        def translate(lines):
            return _translate_lines(client, provider, model, lines, on_progress)

        try:
            saved = _translate_path(src_path, translate)
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
    provider, api_key, model = resolve_provider()
    try:
        from openai import OpenAI
    except ImportError as error:
        raise AiClientError("openai 패키지가 없습니다. pip install openai 로 설치하세요.") from error

    kwargs = {"api_key": api_key, "timeout": 180.0}
    if provider == "gemini":
        kwargs["base_url"] = GEMINI_BASE_URL
    elif provider != "openai":
        raise AiClientError("지원하지 않는 AI 제공자입니다: " + provider)
    return OpenAI(**kwargs), provider, model


def _gemini_reasoning(model):
    name = model.lower()
    if "2.5" in name and "pro" not in name:
        return "none"
    return "low"


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


def _chat(client, provider, model, lines):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({"lines": lines}, ensure_ascii=False)},
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
    }
    if provider == "gemini":
        payload["reasoning_effort"] = _gemini_reasoning(model)

    last_error = None
    for _attempt in range(4):
        try:
            response = client.chat.completions.create(**payload)
            if not response.choices:
                text = ""
            else:
                text = _message_text(response.choices[0].message)
            if text.strip() == "":
                if "response_format" in payload:
                    payload.pop("response_format", None)
                    last_error = AiClientError("AI 응답이 비어 있습니다.")
                    continue
                raise AiClientError("AI 응답이 비어 있습니다.")
            return text
        except AiClientError:
            raise
        except Exception as error:
            last_error = error
            message = str(error).lower()
            changed = False
            format_rejected = (
                "response_format" in message
                or "json_object" in message
                or "response format" in message
            )
            if "response_format" in payload and format_rejected:
                payload.pop("response_format", None)
                changed = True
            if "temperature" in payload and "temperature" in message:
                payload.pop("temperature", None)
                changed = True
            if "reasoning_effort" in payload and "reasoning" in message:
                payload.pop("reasoning_effort", None)
                changed = True
            if not changed:
                break
    raise AiClientError("AI 번역 요청에 실패했습니다.\n" + str(last_error))


def _translate_group(client, provider, model, lines):
    if not lines:
        return []
    try:
        return _parse_lines(_chat(client, provider, model, lines), len(lines))
    except _LineCountError:
        if len(lines) == 1:
            raise AiClientError("번역 결과 형식이 맞지 않습니다.")
        _translate_log("[=] 번역 결과 줄 수가 맞지 않아 나누어 다시 요청합니다.")
        mid = len(lines) // 2
        left = _translate_group(client, provider, model, lines[:mid])
        right = _translate_group(client, provider, model, lines[mid:])
        return left + right


def _translate_lines(client, provider, model, lines, on_progress):
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
        detail = str(len(chunk)) + "줄 번역을 요청합니다."
        if total > 1:
            detail += " (" + str(index) + "번째 요청)"
        _translate_log("[+] " + detail)
        _notify_progress(on_progress, "번역 중")
        output.extend(_translate_group(client, provider, model, chunk))
    return output


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


def _write_text(path, text):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    partial = path + ".part"
    try:
        with open(partial, "w", encoding="utf-8-sig", newline="") as file:
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


def _translate_path(src_path, translate):
    ext = os.path.splitext(src_path)[1].lower()
    if ext == ".zip":
        return _translate_zip(src_path, translate)

    text = _read_text(src_path)
    kind = ext if ext in TEXT_EXTENSIONS else _sniff_extension(text)
    if kind == "" and _needs_translation(text[:20000]):
        kind = ".txt"
    if kind == "":
        shown = ext or "알 수 없음"
        raise AiClientError("이 형식은 텍스트 자막이 아니라 번역할 수 없습니다: " + shown)

    _translate_log("> 형식: " + kind)
    _write_text(korean_output_path(src_path), _translate_document(text, kind, translate))
    return korean_output_path(src_path)


def _translate_document(text, ext, translate):
    if ext in (".srt", ".vtt"):
        return _translate_cues(text, translate)
    if ext in (".ass", ".ssa"):
        return _translate_ass(text, translate)
    if ext in (".smi", ".sami"):
        return _translate_smi(text, translate)
    if ext == ".txt":
        return _translate_plain(text, translate)
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


def _translate_ass(text, translate):
    newline = _newline_style(text)
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    in_events = False
    text_index = 9
    bodies = []
    targets = []

    for index, line in enumerate(lines):
        section = re.match(r"^\s*\[(.+?)\]\s*$", line)
        if section:
            in_events = section.group(1).strip().lower() == "events"
            continue
        if not in_events:
            continue
        format_match = re.match(r"^\s*Format\s*:(.*)$", line, re.IGNORECASE)
        if format_match:
            fields = [part.strip().lower() for part in format_match.group(1).split(",")]
            if "text" in fields:
                text_index = fields.index("text")
            continue
        dialogue = re.match(r"^(\s*Dialogue\s*:)(.*)$", line, re.IGNORECASE)
        if not dialogue:
            continue
        parts = dialogue.group(2).split(",", text_index)
        if len(parts) <= text_index:
            continue
        targets.append((index, dialogue.group(1) + ",".join(parts[:text_index]) + ",", len(bodies)))
        bodies.append(parts[text_index])

    translated = _map_texts(bodies, translate)
    for index, prefix, body_index in targets:
        lines[index] = prefix + translated[body_index]
    return newline.join(lines)


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


def _translate_zip(src_path, translate):
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
            translated = _translate_document(text, ext, translate)
            root, member_ext = os.path.splitext(name)
            outputs.append((root + ".ko" + member_ext, translated))

    if not outputs:
        raise AiClientError("압축 파일 안에 번역할 자막이 없습니다.")

    out_dir = korean_output_path(src_path)
    for name, text in outputs:
        _write_text(os.path.join(out_dir, name.replace("/", os.sep)), text)
    return out_dir
