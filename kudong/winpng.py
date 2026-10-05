"""
티스토리 글의 WinPNG 이미지에서 자막 파일을 추출하는 스크립트

디코딩/변환 로직을 직접 구현하지 않고, 블로그에 실제로 배포된 WinPNG 뷰어
(https://github.com/harnenim/Jamaker 의 WinPNG/tistory/Viewer.js)를
헤드리스 Chromium에서 그대로 실행합니다.
  글 열기 → 뷰어 초기화 대기 → 본문 이미지 클릭 → 뷰어가 만든 파일(blob)을 그대로 저장
따라서 블로그에서 직접 받는 파일과 바이트 단위로 동일한 결과가 나오며,
뷰어가 업데이트되면 별도 작업 없이 반영됩니다.
"""
import argparse
import base64
import os
import re
import sys

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")

# 뷰어 동작과 무관한 분석/광고 스크립트는 막아서 로딩을 빠르게
BLOCKED_HOSTS = ("googletagmanager.com", "google-analytics.com", "googlesyndication.com",
                 "doubleclick.net", "tiara", "developers.kakao.com", "search1.daumcdn.net")

# 뷰어의 window.load 핸들러가 UI(#viewFileList)와 이미지 클릭 핸들러를 만든 뒤라야 클릭이 먹힘
JS_VIEWER_READY = ("typeof window.downloadZip === 'function'"
                   " && !!document.getElementById('viewFileList')")

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


def extract(post_url: str, image_timeout: float = 60, headed: bool = False):
    """글 URL → [{dir, name, raw, assName, ass, smiName, smi}, ...] (바이트 값은 bytes 또는 None)"""
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        try:
            page = browser.new_page(user_agent=UA, viewport={"width": 1280, "height": 900})
            page.route("**/*", lambda r: r.abort()
                       if any(h in r.request.url for h in BLOCKED_HOSTS) else r.continue_())
            page.on("dialog", lambda d: d.dismiss())   # 혹시 모를 실제 대화상자 방지

            page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
            try:
                page.wait_for_function(JS_VIEWER_READY, timeout=20000)
            except PWTimeout:
                print("WinPNG 뷰어가 없는 페이지입니다.")
                return []
            page.evaluate(JS_SETUP)

            cands = page.evaluate(JS_CANDIDATES)
            print(f"후보 이미지 {len(cands)}개")
            for n, c in enumerate(cands, 1):
                page.evaluate(JS_CLICK, c["index"])
                try:
                    state = page.wait_for_function(JS_STATE, polling=250,
                                                   timeout=image_timeout * 1000).json_value()
                except PWTimeout:
                    print(f"[{n}] 시간 초과 → 건너뜀")
                    continue
                if state == "failed":
                    print(f"[{n}] WinPNG 데이터 없음")
                    continue
                entries = page.evaluate(JS_COLLECT)
                print(f"[{n}] 파일 {len(entries)}개")
                for e in entries:
                    for k in ("raw", "ass", "smi"):
                        e[k] = base64.b64decode(e[k]) if e[k] else None
                    results.append(e)
        finally:
            browser.close()
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
