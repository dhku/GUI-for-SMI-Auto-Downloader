"""
티스토리 글의 WinPNG 이미지에서 자막 파일을 추출하는 스크립트

디코딩/변환 로직을 직접 구현하지 않고, 블로그에 실제로 배포된 WinPNG 뷰어
(https://github.com/harnenim/Jamaker 의 WinPNG/tistory/Viewer.js)를
PC에 설치된 Edge 또는 Chrome에서 그대로 실행합니다.
  글 열기 → 뷰어 초기화 대기 → 본문 이미지 클릭 → 뷰어가 만든 파일(blob)을 그대로 저장
따라서 블로그에서 직접 받는 파일과 바이트 단위로 동일한 결과가 나오며,
뷰어가 업데이트되면 별도 작업 없이 반영됩니다.
브라우저 본체는 설치 파일에 넣지 않습니다.
"""
import argparse
import base64
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

# 뷰어 동작과 무관한 분석/광고 스크립트는 막아서 로딩을 빠르게
BLOCKED_HOSTS = ("googletagmanager.com", "google-analytics.com", "googlesyndication.com",
                 "doubleclick.net", "tiara", "developers.kakao.com", "search1.daumcdn.net")

# 뷰어의 window.load 핸들러가 UI(#viewFileList)와 이미지 클릭 핸들러를 만든 뒤라야 클릭이 먹힘
JS_VIEWER_READY = """() => (typeof window.downloadZip === 'function'
    && !!document.getElementById('viewFileList'))"""

# 뷰어는 해석 실패 시 prompt(비밀번호) → alert("해석 실패")를 띄움. 이를 실패 신호로 사용
JS_SETUP = """() => {
    window.__wp = { failed: false };
    window.alert = () => { window.__wp.failed = true; };
    window.prompt = () => null;
    window.confirm = () => false;
}"""

# 뷰어의 클릭 핸들러와 같은 조건: #content 안에서 주소가 .png 로 끝나는 이미지
JS_CANDIDATES = """() => {
    const seen = new Set(), out = [];
    document.querySelectorAll('#content img').forEach((img, i) => {
        const src = img.src || '';
        if (!src.split('?')[0].toLowerCase().endsWith('.png') || seen.has(src)) return;
        seen.add(src);
        img.setAttribute('data-wp-index', i);
        out.push({ index: i, src });
    });
    return out;
}"""

JS_CLICK = """(index) => {
    window.__wp.failed = false;
    document.getElementById('viewFileList').innerHTML = '';   // 이전 결과로 오판 방지
    document.querySelector(`#content img[data-wp-index="${index}"]`).click();
}"""

# 'failed' / 'done' / null(대기). 원본 항목은 a[data-href] (안쪽 [SMI]/[ASS] 링크는 중첩된 a)
JS_STATE = """() => {
    if (window.__wp.failed) return 'failed';
    const root = document.getElementById('winPNG');
    if (root && root.classList.contains('progress')) return null;
    const entries = document.querySelectorAll('#viewFileList a[data-href]');
    if (!entries.length) return null;
    if (document.querySelector('#viewFileList a.processing')) return null;
    return 'done';
}"""

# 뷰어가 만든 blob 을 바이트 그대로 base64 로 꺼냄 (BOM 포함, 받는 파일과 동일)
JS_COLLECT = """async () => {
    const b64 = async (url) => {
        if (!url) return null;
        try {
            const buf = new Uint8Array(await (await fetch(url)).arrayBuffer());
            let s = '';
            for (let i = 0; i < buf.length; i += 0x8000)
                s += String.fromCharCode(...buf.subarray(i, i + 0x8000));
            return btoa(s);
        } catch (e) { return null; }
    };
    const out = [];
    for (const a of document.querySelectorAll('#viewFileList a[data-href]')) {
        const dirSpan = a.querySelector(':scope > span:not(.file)');
        const sub = (attr) => [...a.querySelectorAll('a')]
            .find((x) => x.download && a.getAttribute(attr) && x.download.toLowerCase().endsWith(attr === 'data-ass' ? '.ass' : '.smi'));
        const assA = sub('data-ass'), smiA = sub('data-smi');
        out.push({
            dir: dirSpan ? dirSpan.textContent : '',
            name: a.download,
            raw: await b64(a.getAttribute('data-href')),
            assName: assA ? assA.download : null,
            ass: await b64(a.getAttribute('data-ass')),
            smiName: smiA ? smiA.download : null,
            smi: await b64(a.getAttribute('data-smi')),
        });
    }
    return out;
}"""


def safe_join(base: str, rel: str) -> str:
    rel = rel.replace("\\", "/")
    parts = [p for p in rel.split("/") if p not in ("", ".", "..")]
    parts = [re.sub(r'[*?"<>|:]', "_", p) for p in parts]
    return os.path.join(base, *parts)


_NO_PROXY = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _http_json(url: str, timeout: float = 5):
    with _NO_PROXY.open(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _windows_browser_from_registry():
    import winreg
    for exe in ("msedge.exe", "chrome.exe"):
        subkey = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\\" + exe
        for root in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            for access in (winreg.KEY_READ, winreg.KEY_READ | winreg.KEY_WOW64_32KEY):
                try:
                    with winreg.OpenKey(root, subkey, 0, access) as key:
                        value, _ = winreg.QueryValueEx(key, "")
                except OSError:
                    continue
                if value and os.path.isfile(value):
                    return value
    return None


def _find_browser():
    """설치된 Edge를 우선 사용하고, 없으면 Chrome을 찾는다."""
    system = platform.system()
    if system == "Windows":
        found = _windows_browser_from_registry()
        if found:
            return found
        candidates = [
            os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe"),
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
    elif system == "Darwin":
        candidates = [
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
    else:
        for name in ("microsoft-edge", "microsoft-edge-stable", "google-chrome",
                     "google-chrome-stable", "chromium"):
            path = shutil.which(name)
            if path:
                return path
        return None
    for path in candidates:
        if path and os.path.isfile(path):
            return path
    return None


def _hidden_popen_kwargs(headed: bool):
    if platform.system() != "Windows":
        return {"start_new_session": True}
    if headed:
        return {}
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = 0
    return {"startupinfo": startup, "creationflags": subprocess.CREATE_NO_WINDOW}


def _stop_browser(proc):
    if proc is None or proc.poll() is not None:
        return
    if platform.system() == "Windows":
        flags = subprocess.CREATE_NO_WINDOW
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags,
        )
    else:
        try:
            os.killpg(proc.pid, 15)
        except OSError:
            proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def _remove_dir(path):
    if not path:
        return
    for _ in range(5):
        try:
            shutil.rmtree(path)
            return
        except OSError:
            time.sleep(0.2)


def _free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class _Cdp:
    """로컬 브라우저의 DevTools 소켓. 표준 라이브러리만 사용한다."""

    def __init__(self, ws_url: str):
        host, port, path = self._split_ws(ws_url)
        self._sock = socket.create_connection((host, port), timeout=10)
        self._sock.settimeout(None)
        self._handshake(host, port, path)
        self._lock = threading.Lock()
        self._pending = {}
        self._next_id = 0
        self._error = None
        self._closed = False
        threading.Thread(target=self._read_loop, daemon=True).start()

    @staticmethod
    def _split_ws(url: str):
        rest = url.split("://", 1)[1]
        hostport, path = rest.split("/", 1)
        host, port = hostport.rsplit(":", 1)
        return host, int(port), "/" + path

    def _handshake(self, host, port, path):
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "\r\n"
        )
        self._sock.sendall(request.encode())
        data = b""
        while b"\r\n\r\n" not in data:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise ConnectionError("브라우저 디버깅 소켓 연결에 실패했습니다.")
            data += chunk
        header, extra = data.split(b"\r\n\r\n", 1)
        status = header.split(b"\r\n", 1)[0]
        if b" 101 " not in status:
            raise ConnectionError("브라우저가 웹소켓 연결을 거절했습니다.")
        self._buf = extra

    def call(self, method: str, params=None, timeout: float = 30):
        event = threading.Event()
        box = {}
        with self._lock:
            if self._error:
                raise ConnectionError(str(self._error))
            self._next_id += 1
            mid = self._next_id
            self._pending[mid] = (event, box)
            self._send({"id": mid, "method": method, "params": params or {}})
        if not event.wait(timeout):
            with self._lock:
                self._pending.pop(mid, None)
            raise TimeoutError(method)
        if box.get("error"):
            err = box["error"]
            raise RuntimeError(err.get("message") or str(err))
        return box.get("result") or {}

    def close(self):
        self._closed = True
        try:
            self._sock.close()
        except OSError:
            pass

    def _send(self, msg):
        payload = json.dumps(msg).encode()
        header = bytearray([0x81])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header += length.to_bytes(2, "big")
        else:
            header.append(0x80 | 127)
            header += length.to_bytes(8, "big")
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self._sock.sendall(bytes(header) + mask + masked)

    def _read_loop(self):
        try:
            while not self._closed:
                opcode, payload = self._read_message()
                if opcode == 9:
                    with self._lock:
                        self._send_control(payload, 0x8A)
                    continue
                if opcode == 8:
                    raise ConnectionError("브라우저 연결이 종료되었습니다.")
                if opcode != 1 or not payload:
                    continue
                msg = json.loads(payload)
                if "id" in msg:
                    with self._lock:
                        pending = self._pending.pop(msg["id"], None)
                    if pending:
                        event, box = pending
                        box["result"] = msg.get("result")
                        box["error"] = msg.get("error")
                        event.set()
                elif msg.get("method") == "Page.javascriptDialogOpening":
                    with self._lock:
                        self._next_id += 1
                        self._send({
                            "id": self._next_id,
                            "method": "Page.handleJavaScriptDialog",
                            "params": {"accept": False},
                        })
        except Exception as exc:
            self._error = exc
            with self._lock:
                pending = list(self._pending.values())
                self._pending.clear()
            for event, box in pending:
                box["error"] = {"message": str(exc)}
                event.set()

    def _send_control(self, payload: bytes, opcode: int):
        mask = os.urandom(4)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        frame = bytes([opcode, 0x80 | len(payload)]) + mask + masked
        self._sock.sendall(frame)

    def _read_exact(self, size: int) -> bytes:
        buf = bytearray()
        if self._buf:
            take = self._buf[:size]
            self._buf = self._buf[size:]
            buf += take
        while len(buf) < size:
            chunk = self._sock.recv(size - len(buf))
            if not chunk:
                raise ConnectionError("브라우저 연결이 끊겼습니다.")
            buf += chunk
        return bytes(buf)

    def _read_message(self):
        parts = []
        opcode = None
        while True:
            header = self._read_exact(2)
            fin = header[0] & 0x80
            op = header[0] & 0x0F
            length = header[1] & 0x7F
            if length == 126:
                length = int.from_bytes(self._read_exact(2), "big")
            elif length == 127:
                length = int.from_bytes(self._read_exact(8), "big")
            if header[1] & 0x80:
                mask = self._read_exact(4)
                payload = self._read_exact(length)
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            else:
                payload = self._read_exact(length) if length else b""
            if op == 0:
                parts.append(payload)
            else:
                opcode = op
                parts = [payload]
            if fin or op in (8, 9, 10):
                return opcode, b"".join(parts)


def _launch_browser(browser: str, port: int, headed: bool):
    modes = [None] if headed else ["--headless=new", "--headless"]
    last_error = None
    for mode in modes:
        user_data = tempfile.mkdtemp(prefix="winpng-")
        args = [
            browser,
            f"--remote-debugging-port={port}",
            "--remote-allow-origins=*",
            f"--user-data-dir={user_data}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--disable-sync",
            "--disable-popup-blocking",
            "--mute-audio",
            "about:blank",
        ]
        if mode:
            args[1:1] = [mode, "--disable-gpu"]
        proc = subprocess.Popen(
            args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            **_hidden_popen_kwargs(headed),
        )
        try:
            return proc, user_data, _wait_page_ws(proc, port, 20)
        except Exception as exc:
            last_error = exc
            _stop_browser(proc)
            _remove_dir(user_data)
            if headed:
                break
    raise last_error


def _wait_page_ws(proc, port: int, timeout: float) -> str:
    deadline = time.monotonic() + timeout
    url = f"http://127.0.0.1:{port}/json/list"
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("브라우저가 바로 종료되었습니다.")
        try:
            pages = _http_json(url, timeout=1)
        except Exception:
            time.sleep(0.2)
            continue
        for page in pages:
            if page.get("type") == "page" and page.get("webSocketDebuggerUrl"):
                return page["webSocketDebuggerUrl"]
        time.sleep(0.2)
    raise TimeoutError("브라우저 디버깅 포트에 연결하지 못했습니다.")


def _evaluate(cdp: _Cdp, expression: str, await_promise: bool = False, timeout: float = 60):
    result = cdp.call("Runtime.evaluate", {
        "expression": expression,
        "returnByValue": True,
        "awaitPromise": await_promise,
    }, timeout=timeout)
    details = result.get("exceptionDetails")
    if details:
        exc = details.get("exception") or {}
        raise RuntimeError(exc.get("description") or details.get("text") or "스크립트 오류")
    return (result.get("result") or {}).get("value")


def _call_js(source: str, arg=None) -> str:
    if arg is None:
        return f"({source})()"
    return f"({source})({json.dumps(arg)})"


def _wait_document(cdp: _Cdp, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            state = _evaluate(cdp, "document.readyState")
            href = _evaluate(cdp, "location.href") or ""
        except Exception:
            time.sleep(0.2)
            continue
        if state in ("interactive", "complete") and href and not href.startswith("about:"):
            return True
        time.sleep(0.2)
    return False


def _wait_js(cdp: _Cdp, source: str, timeout: float, poll: float = 0.25):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = _evaluate(cdp, _call_js(source), timeout=max(5, poll + 1))
        if value:
            return value
        time.sleep(poll)
    raise TimeoutError(source)


def extract(post_url: str, image_timeout: float = 60, headed: bool = False):
    """글 URL → [{dir, name, raw, assName, ass, smiName, smi}, ...] (바이트 값은 bytes 또는 None)"""
    browser = _find_browser()
    if not browser:
        print("Edge 또는 Chrome을 찾을 수 없습니다.")
        return []

    results = []
    proc = cdp = user_data = None
    try:
        port = _free_port()
        proc, user_data, ws_url = _launch_browser(browser, port, headed)
        cdp = _Cdp(ws_url)
        cdp.call("Page.enable")
        cdp.call("Network.enable")
        try:
            cdp.call("Network.setBlockedURLs", {"urls": [f"*{host}*" for host in BLOCKED_HOSTS]})
        except Exception:
            pass
        cdp.call("Emulation.setUserAgentOverride", {"userAgent": UA})
        try:
            cdp.call("Emulation.setDeviceMetricsOverride", {
                "width": 1280, "height": 900, "deviceScaleFactor": 1, "mobile": False,
            })
        except Exception:
            pass

        cdp.call("Page.navigate", {"url": post_url}, timeout=30)
        if not _wait_document(cdp, 60):
            print("페이지를 열지 못했습니다.")
            return []

        try:
            _wait_js(cdp, JS_VIEWER_READY, 20)
        except TimeoutError:
            print("WinPNG 뷰어가 없는 페이지입니다.")
            return []
        _evaluate(cdp, _call_js(JS_SETUP))

        cands = _evaluate(cdp, _call_js(JS_CANDIDATES)) or []
        print(f"후보 이미지 {len(cands)}개")
        for n, cand in enumerate(cands, 1):
            _evaluate(cdp, _call_js(JS_CLICK, cand["index"]))
            try:
                state = _wait_js(cdp, JS_STATE, image_timeout)
            except TimeoutError:
                print(f"[{n}] 시간 초과 → 건너뜀")
                continue
            if state == "failed":
                print(f"[{n}] WinPNG 데이터 없음")
                continue
            entries = _evaluate(cdp, _call_js(JS_COLLECT), await_promise=True,
                                timeout=max(image_timeout, 60))
            print(f"[{n}] 파일 {len(entries)}개")
            for entry in entries:
                for key in ("raw", "ass", "smi"):
                    entry[key] = base64.b64decode(entry[key]) if entry[key] else None
                results.append(entry)
    except Exception as exc:
        print(f"WinPNG 추출 실패: {exc}")
    finally:
        if cdp is not None:
            cdp.close()
        _stop_browser(proc)
        _remove_dir(user_data)
    return results


def winpng(post_url: str, out_dir: str = "winpng_out", to_ass: bool = False,
          to_smi: bool = False, headed: bool = False):
    os.makedirs(out_dir, exist_ok=True)
    entries = extract(post_url, headed=headed)
    saved = []

    def write(rel_dir, name, data):
        dst = safe_join(out_dir, rel_dir + name)
        os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
        with open(dst, "wb") as f:
            f.write(data)
        print(f"     → {dst} ({len(data):,} bytes)")
        saved.append(dst)

    for e in entries:
        # JMK 파일은 저장하지 않음
        # if e["raw"] is not None:
        #     write(e["dir"], e["name"], e["raw"])
        if to_ass and e["ass"] is not None:
            write(e["dir"], e["assName"] or os.path.splitext(e["name"])[0] + ".ass", e["ass"])
        if to_smi and e["smi"] is not None:
            write(e["dir"], e["smiName"] or os.path.splitext(e["name"])[0] + ".smi", e["smi"])

    jmks = [e for e in entries if e["name"].lower().endswith(".jmk")]
    if to_ass and jmks and not any(e["ass"] for e in jmks):
        print("참고: 뷰어가 ASS 변환을 제공하지 않은 JMK입니다 (<SAMI> 태그에 ASS 속성 없음).")
    print(f"완료: 파일 {len(saved)}개 저장")
    return saved

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="티스토리 WinPNG 자막 추출기 (블로그 뷰어 사용)")
    ap.add_argument("url", help="티스토리 글 URL")
    ap.add_argument("out_dir", nargs="?", default="winpng_out", help="출력 폴더")
    ap.add_argument("--ass", action="store_true", help="뷰어가 변환한 .ass 도 저장")
    ap.add_argument("--smi", action="store_true", help="뷰어가 변환한 .smi 도 저장")
    ap.add_argument("--headed", action="store_true", help="브라우저 창을 띄워서 실행 (디버깅용)")
    args = ap.parse_args()
    ok = winpng(args.url, args.out_dir, args.ass, args.smi, headed=args.headed)
    sys.exit(0 if ok else 1)
