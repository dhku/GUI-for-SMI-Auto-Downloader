import html
import re
import unicodedata

# ASS/SRT 원문을 번역 단위로 정리하고, 번역문을 출력 규칙에 맞춰 다시 만듭니다.
ASS_HEADER = """[Script Info]
ScriptType: v4.00+
Collisions: Normal
PlayDepth: 0
PlayResX: 640
PlayResY: 360
ScaledBorderAndShadow: yes
Title: Korean
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,맑은 고딕,28,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.3,0,2,20,20,23,1
Style: TopLeft,맑은 고딕,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.3,0,7,20,20,23,1
Style: TopCenter,맑은 고딕,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.3,0,8,20,20,23,1
Style: TopRight,맑은 고딕,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.3,0,9,20,20,23,1
Style: CenterLeft,맑은 고딕,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.3,0,4,20,20,23,1
Style: CenterCenter,맑은 고딕,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.3,0,5,20,20,23,1
Style: CenterRight,맑은 고딕,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.3,0,6,20,20,23,1
Style: BottomLeft,맑은 고딕,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.3,0,1,20,20,23,1
Style: BottomCenter,맑은 고딕,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.3,0,2,20,20,23,1
Style: BottomRight,맑은 고딕,26,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,1.3,0,3,20,20,23,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

MAX_LINE = 20

KIND_DIALOGUE = "대사"
KIND_INNER = "속마음"
KIND_VOICE = "음성"
KIND_ITALIC = "이탤릭"
KIND_SCREEN = "화면"
KIND_LYRICS = "가사"

# 원문의 《》, ＜＞, 이탤릭 태그를 NFKC 정규화에 영향받지 않는 사용자 영역 문자로 바꿔 추적합니다.
_INNER_OPEN, _INNER_CLOSE = "\ue001", "\ue002"
_VOICE_OPEN, _VOICE_CLOSE = "\ue003", "\ue004"
_ITALIC_OPEN, _ITALIC_CLOSE = "\ue005", "\ue006"
_MARKS = _INNER_OPEN + _INNER_CLOSE + _VOICE_OPEN + _VOICE_CLOSE + _ITALIC_OPEN + _ITALIC_CLOSE
_MARK_ACTIONS = {
    _INNER_OPEN: ("inner", True),
    _INNER_CLOSE: ("inner", False),
    _VOICE_OPEN: ("voice", True),
    _VOICE_CLOSE: ("voice", False),
    _ITALIC_OPEN: ("italic", True),
    _ITALIC_CLOSE: ("italic", False),
}
_SOURCE_MARKS = {
    "《": _INNER_OPEN,
    "》": _INNER_CLOSE,
    "≪": _INNER_OPEN,
    "≫": _INNER_CLOSE,
    "＜": _VOICE_OPEN,
    "＞": _VOICE_CLOSE,
}

_DEFAULT_ASS_FIELDS = ["layer", "start", "end", "style", "name", "marginl", "marginr", "marginv", "effect", "text"]
_JP = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\u3400-\u9fff\uff66-\uff9d]")
_KANA = re.compile(r"[\u3040-\u30ff\u31f0-\u31ff\uff66-\uff9d]")
_LYRICS = re.compile(r"[♪♬♫♩\U0001F3B5\U0001F3B6]")
_ARROWS = re.compile(r"[➡➨➔➜➝➞➙➛→⇒⇨]")
_CONTINUES = re.compile(r"(?:[➡➨➔➜➝➞➙➛→⇒⇨—―–、,]\s*)[\s" + _MARKS + r"]*$")
_TRAIL_DASH = re.compile(r"\s*[—―–]+(?=[\s" + _MARKS + r"]*$)")
_LEAD_DASH = re.compile(r"^\s*[-‐‑]\s*(?=\S)")
_PAREN = re.compile(r"\([^()]*\)")
_PAREN_LABEL = re.compile(r"\(([^()]{1,20})\)\s*")
_COLON_LABEL = re.compile(r"([^\s()「」『』:、。!?…・" + _MARKS + r"]{1,12}):\s*")
_SFX_LABEL = re.compile(r"音|拍手|笑い|泣き|息|悲鳴|歓声|ため息|咳|どよめき|ざわめき|BGM|曲|音楽|鳴き|響き")
_SCREEN_STYLE = re.compile(r"sign|title|screen|caption|card|place|location|telop|テロップ|看板|タイトル", re.I)
_SONG_STYLE = re.compile(r"^(?:op|ed)(?:$|[\s_\-\d])|song|kara|lyric|歌", re.I)
_ASS_DRAWING = re.compile(r"\\p[1-9]")
_ASS_TOKEN = re.compile(r"(\{[^{}]*\}|\\N|\\n|\\h)")
_SRT_TOKEN = re.compile(r"(<[^<>]*>|\{[^{}]*\})")
_STATEMENT_END = "다요죠네군"


class Part:
    __slots__ = ("text", "who", "kind", "italic", "cont", "ko")

    def __init__(self, text, who, kind, italic):
        self.text = text
        self.who = who
        self.kind = kind
        self.italic = italic
        self.cont = False
        self.ko = ""


class Event:
    __slots__ = ("start", "end", "style", "segments")

    def __init__(self, start, end, style, segments):
        self.start = start
        self.end = end
        self.style = style
        self.segments = segments

    def parts(self):
        return [part for segment in self.segments for part in segment]


def has_japanese(text):
    return _JP.search(text or "") is not None


def has_kana(text):
    return _KANA.search(text or "") is not None


def _mark(text):
    for source, marker in _SOURCE_MARKS.items():
        text = text.replace(source, marker)
    return text


def _ass_seconds(value):
    match = re.match(r"^\s*(\d+):(\d+):(\d+)(?:[.,](\d+))?", value)
    if not match:
        return 0.0
    hours, minutes, seconds, fraction = match.groups()
    total = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    if fraction:
        total += int(fraction) / (10 ** len(fraction))
    return float(total)


def _normalize_newlines(text):
    if text.startswith("\ufeff"):
        text = text[1:]
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _new_group(groups, order, start, end):
    key = (start, end)
    group = groups.get(key)
    if group is None:
        group = {
            "start": start,
            "end": end,
            "seconds": _ass_seconds(start),
            "index": len(order),
            "entries": [],
        }
        groups[key] = group
        order.append(group)
    return group


def _finish_groups(order, count):
    raws = []
    for group in order:
        entries = sorted(group["entries"], key=lambda entry: entry["sort"])
        lines = []
        for entry in entries:
            lines.extend((text, color, entry["name"]) for text, color in entry["lines"])
        raws.append({
            "start": group["start"],
            "end": group["end"],
            "seconds": group["seconds"],
            "index": group["index"],
            "lines": lines,
            "screen": all(entry["screen"] for entry in entries),
            "song": any(entry["song"] for entry in entries),
        })
    raws.sort(key=lambda raw: (raw["seconds"], raw["index"]))
    return raws, {"source": count, "merged": count - len(raws)}


def _ass_text_lines(raw):
    pos = None
    color = None
    karaoke = False
    lines = []
    buffer = []
    line_color = None
    for token in _ASS_TOKEN.split(raw):
        if token == "":
            continue
        if token == "\\N":
            lines.append(("".join(buffer), line_color))
            buffer = []
            line_color = None
            continue
        if token in ("\\n", "\\h"):
            buffer.append(" ")
            continue
        if token.startswith("{") and token.endswith("}"):
            if pos is None:
                found = re.search(r"\\(?:pos|move)\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)", token)
                if found:
                    pos = (float(found.group(1)), float(found.group(2)))
            for value in re.findall(r"\\1?c&H([0-9A-Fa-f]+)&?", token):
                color = value.upper().lstrip("0") or "0"
            for value in re.findall(r"\\i([01])(?!\d)", token):
                buffer.append(_ITALIC_OPEN if value == "1" else _ITALIC_CLOSE)
            if re.search(r"\\[kK][fo]?\d", token):
                karaoke = True
            continue
        if line_color is None and token.strip():
            line_color = color
        buffer.append(_mark(token))
    lines.append(("".join(buffer), line_color))
    return lines, pos, karaoke


def parse_ass(text):
    section = ""
    fields = None
    groups = {}
    order = []
    count = 0
    for line in _normalize_newlines(text).split("\n"):
        stripped = line.strip()
        header = re.match(r"^\[(.+)\]$", stripped)
        if header:
            section = header.group(1).strip().lower()
            continue
        if section != "events":
            continue
        if stripped.lower().startswith("format:"):
            fields = [field.strip().lower() for field in stripped[7:].split(",")]
            continue
        dialogue = re.match(r"^dialogue\s*:\s?(.*)$", stripped, re.IGNORECASE)
        if not dialogue:
            continue
        names = fields if fields and "text" in fields else _DEFAULT_ASS_FIELDS
        values = dialogue.group(1).split(",", len(names) - 1)
        if len(values) < len(names):
            continue
        row = dict(zip(names, values))
        count += 1
        body = row.get("text", "")
        if _ASS_DRAWING.search(body):
            continue
        lines, pos, karaoke = _ass_text_lines(body)
        style = row.get("style", "").strip()
        name = row.get("name", "").strip()
        group = _new_group(groups, order, row.get("start", "").strip(), row.get("end", "").strip())
        x, y = pos if pos else (0.0, 1e9)
        group["entries"].append({
            "sort": (y, x, len(group["entries"])),
            "lines": lines,
            "name": name,
            "screen": bool(_SCREEN_STYLE.search(style) or _SCREEN_STYLE.search(name)),
            "song": bool(karaoke or _SONG_STYLE.search(style)),
        })
    return _finish_groups(order, count)


def _srt_line(raw, color):
    buffer = []
    for token in _SRT_TOKEN.split(html.unescape(raw)):
        if token == "":
            continue
        if token.startswith("<") and token.endswith(">"):
            tag = token.lower().replace(" ", "")
            if tag == "<i>":
                buffer.append(_ITALIC_OPEN)
            elif tag == "</i>":
                buffer.append(_ITALIC_CLOSE)
            found = re.search(r"color=[\"']?#?([0-9a-z]+)", tag)
            if found:
                color = found.group(1).upper()
            continue
        if token.startswith("{") and token.endswith("}"):
            for value in re.findall(r"\\i([01])(?!\d)", token):
                buffer.append(_ITALIC_OPEN if value == "1" else _ITALIC_CLOSE)
            continue
        buffer.append(_mark(token))
    return "".join(buffer), color


def parse_srt(text):
    groups = {}
    order = []
    count = 0
    for block in re.split(r"\n[ \t]*\n", _normalize_newlines(text).strip()):
        lines = block.split("\n")
        time_index = None
        for index, line in enumerate(lines[:3]):
            if "-->" in line:
                time_index = index
                break
        if time_index is None:
            continue
        timing = re.match(r"^\s*(\S+)\s*-->\s*(\S+)", lines[time_index])
        if not timing:
            continue
        count += 1
        color = None
        body = []
        for line in lines[time_index + 1:]:
            if line.strip() == "":
                continue
            marked, color = _srt_line(line, color)
            body.append((marked, color))
        group = _new_group(groups, order, timing.group(1), timing.group(2))
        group["entries"].append({
            "sort": (0, 0, len(group["entries"])),
            "lines": body,
            "name": "",
            "screen": False,
            "song": False,
        })
    return _finish_groups(order, count)


def _clean_spaces(text):
    return re.sub(r"\s+", " ", text).strip()


class _Builder:
    def __init__(self, keep_lyrics):
        self.keep_lyrics = keep_lyrics
        self.state = {"inner": False, "voice": False, "italic": False}
        self.removed = 0

    def _mode(self):
        if self.state["inner"]:
            return KIND_INNER
        if self.state["voice"]:
            return KIND_VOICE
        if self.state["italic"]:
            return KIND_ITALIC
        return None

    def _walk(self, text):
        runs = []
        buffer = []
        mode = self._mode()
        for char in text:
            action = _MARK_ACTIONS.get(char)
            if action is None:
                buffer.append(char)
                continue
            piece = _clean_spaces("".join(buffer))
            if piece:
                runs.append((piece, mode))
            buffer = []
            self.state[action[0]] = action[1]
            mode = self._mode()
        piece = _clean_spaces("".join(buffer))
        if piece:
            runs.append((piece, mode))
        return runs

    def _line(self, text):
        text = unicodedata.normalize("NFKC", text)
        text = text.replace("((", "").replace("))", "")
        dash = False
        lead = _LEAD_DASH.match(text)
        if lead:
            dash = True
            text = text[lead.end():]

        prefix = re.match(r"^[\s" + _MARKS + r"]*", text).group(0)
        rest = text[len(prefix):]
        label = ""
        found = _PAREN_LABEL.match(rest)
        if found and not _SFX_LABEL.search(found.group(1)):
            label = found.group(1).strip()
            rest = rest[found.end():]
        else:
            found = _COLON_LABEL.match(rest)
            if found and re.search(r"[^\d\s]", found.group(1)):
                label = found.group(1).strip()
                rest = rest[found.end():]
        text = prefix + rest

        song = _LYRICS.search(text) is not None
        while _PAREN.search(text):
            text = _PAREN.sub("", text)
        cont = _CONTINUES.search(text) is not None
        text = _TRAIL_DASH.sub("", text)
        text = _ARROWS.sub(" ", text)
        if song:
            text = _LYRICS.sub(" ", text)
        return label, dash, text, cont, song

    def event(self, raw):
        self.state["italic"] = False
        segments = []
        pending_label = ""
        last_cont = False
        has_song = False
        for text, color, name in raw["lines"]:
            label, dash, cleaned, cont, song = self._line(text)
            runs = self._walk(cleaned)
            if song or raw["song"]:
                if not self.keep_lyrics:
                    if runs:
                        self.removed += 1
                    continue
                has_song = True
            label = label or pending_label
            if not runs:
                if label:
                    pending_label = label
                elif text.strip():
                    self.removed += 1
                continue
            pending_label = ""
            who = label or name
            current = segments[-1] if segments else None
            if (
                current is None
                or dash
                or (who and who != current["who"])
                or (not who and color != current["color"])
            ):
                current = {"who": who, "color": color, "runs": []}
                segments.append(current)
            for piece, mode in runs:
                if current["runs"] and current["runs"][-1][1] == mode:
                    current["runs"][-1][0] += " " + piece
                else:
                    current["runs"].append([piece, mode])
            last_cont = cont

        built = []
        for segment in segments:
            parts = []
            for piece, mode in segment["runs"]:
                piece = _clean_spaces(piece)
                if not piece:
                    continue
                if raw["screen"]:
                    kind = KIND_SCREEN
                elif has_song:
                    kind = KIND_LYRICS
                else:
                    kind = mode or KIND_DIALOGUE
                part = Part(piece, segment["who"], kind, mode is not None)
                if not has_japanese(piece):
                    part.ko = polish(piece)
                parts.append(part)
            if parts:
                built.append(parts)
        if not built:
            return None
        built[-1][-1].cont = last_cont
        style = "TopCenter" if raw["screen"] else "BottomCenter"
        return Event(raw["start"], raw["end"], style, built)


def build_events(raws, keep_lyrics=False):
    builder = _Builder(keep_lyrics)
    events = []
    for raw in raws:
        event = builder.event(raw)
        if event is not None:
            events.append(event)
    return events, builder.removed


def polish(text, cont=False):
    value = "" if text is None else str(text)
    value = re.sub(r"\{[^{}]*\}", "", value)
    value = re.sub(r"</?[A-Za-z][^<>]*>", "", value)
    for token in ("\\N", "\\n", "\\h", "\r", "\n"):
        value = value.replace(token, " ")
    for char in _MARKS + "《》≪≫＜＞":
        value = value.replace(char, "")
    pairs = (
        ("「", '"'), ("」", '"'), ("『", "'"), ("』", "'"), ("“", '"'), ("”", '"'),
        ("！", "!"), ("？", "?"), ("　", " "), ("，", ","), ("、", ","), ("。", "."),
        ("…", "..."), ("‥", ".."), ("・・・", "..."), ("{", "("), ("}", ")"), ("\\", ""),
    )
    for source, target in pairs:
        value = value.replace(source, target)
    value = re.sub(r"[～〜~]+", "", value)
    value = _ARROWS.sub(" ", value)
    value = _LYRICS.sub("", value)
    value = re.sub(r"\.{4,}", "...", value)
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\s+([,!?]|\.(?!\.))", r"\1", value)
    if not value:
        return ""
    if cont:
        if value.endswith(".") and not value.endswith(".."):
            value = value[:-1].rstrip()
    elif value[-1] in _STATEMENT_END:
        value += "."
    return value


def _wrap(runs):
    chars = []
    for index, (text, italic) in enumerate(runs):
        if index > 0:
            chars.append((" ", italic and runs[index - 1][1]))
        chars.extend((char, italic) for char in text)
    plain = "".join(char for char, _italic in chars)
    if len(plain) <= MAX_LINE:
        return [chars]

    best = None
    for index, char in enumerate(plain):
        if char != " ":
            continue
        left = plain[:index].rstrip()
        right = plain[index + 1:].lstrip()
        if not left or not right:
            continue
        score = max(len(left), len(right))
        if left[-1] in ".,?!":
            score -= 4
        if min(len(left), len(right)) < 4:
            score += 10
        if best is None or score < best[0]:
            best = (score, index)
    if best is None:
        return [chars]
    return [chars[:best[1]], chars[best[1] + 1:]]


def _render_line(chars, italic_open, italic_close):
    groups = []
    for char, italic in chars:
        if groups and groups[-1][1] == italic:
            groups[-1][0].append(char)
        else:
            groups.append([[char], italic])
    output = []
    for letters, italic in groups:
        text = "".join(letters)
        if not italic or text.strip() == "":
            output.append(text)
            continue
        lead = text[:len(text) - len(text.lstrip())]
        tail = text[len(text.rstrip()):]
        output.append(lead + italic_open + text.strip() + italic_close + tail)
    return re.sub(r"\s+", " ", "".join(output)).strip()


def _layout(event, italic_open, italic_close):
    segments = []
    for parts in event.segments:
        runs = [(part.ko, part.italic) for part in parts if part.ko]
        if runs:
            segments.append(runs)
    if not segments:
        return []
    if len(segments) == 1:
        rows = _wrap(segments[0])
        return [_render_line(row, italic_open, italic_close) for row in rows]

    lines = []
    for index, runs in enumerate(segments):
        chars = []
        for position, (text, italic) in enumerate(runs):
            if position > 0:
                chars.append((" ", italic and runs[position - 1][1]))
            chars.extend((char, italic) for char in text)
        line = _render_line(chars, italic_open, italic_close)
        lines.append(("- " + line) if index > 0 else line)
    return lines


def render_ass(events):
    output = [ASS_HEADER.rstrip("\n")]
    warnings = []
    for event in events:
        lines = _layout(event, "{\\i1}", "{\\i0}")
        if not lines:
            continue
        if len(lines) > 2:
            warnings.append("%d줄 자막: %s ~ %s" % (len(lines), event.start, event.end))
        output.append(
            "Dialogue: 0,%s,%s,%s,,0,0,0,,%s" % (event.start, event.end, event.style, "\\N".join(lines))
        )
    return "\n".join(output) + "\n", warnings


def render_srt(events):
    blocks = []
    warnings = []
    for event in events:
        lines = _layout(event, "<i>", "</i>")
        if not lines:
            continue
        if len(lines) > 2:
            warnings.append("%d줄 자막: %s ~ %s" % (len(lines), event.start, event.end))
        blocks.append("%d\n%s --> %s\n%s" % (len(blocks) + 1, event.start, event.end, "\n".join(lines)))
    return "\n\n".join(blocks) + "\n", warnings
