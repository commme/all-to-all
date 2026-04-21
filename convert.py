"""
All-to-All File Converter
  이미지 / 문서 / 오디오 / 비디오 간 자유 변환

사용법:
  py convert.py 파일.pdf png              # PDF → PNG
  py convert.py 파일.mp4 mp3              # 비디오 → 오디오 추출
  py convert.py 파일.jpg webp             # 이미지 포맷 변환
  py convert.py 파일.docx pdf             # 문서 → PDF
  py convert.py                           # input/ 폴더 → output/ (대화형)
"""

import sys
import os
import subprocess
import shutil
import tempfile
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── 외부 도구 경로 ──────────────────────────────────────────

SOFFICE_PATHS = [
    "C:/Program Files/LibreOffice/program/soffice.exe",
    "C:/Program Files (x86)/LibreOffice/program/soffice.exe",
]
SOFFICE = next((p for p in SOFFICE_PATHS if Path(p).exists()), None)

FFMPEG = shutil.which("ffmpeg")

# ── 포맷 분류 ────────────────────────────────────────────────

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif", ".ico"}
DOC_EXTS = {".pdf", ".docx", ".pptx", ".xlsx", ".hwp", ".hwpx", ".odt", ".odp", ".ods", ".txt"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma"}
VIDEO_EXTS = {".mp4", ".avi", ".mkv", ".mov", ".webm", ".wmv", ".flv"}
WEB_EXTS = {".html", ".htm"}

ALL_EXTS = IMAGE_EXTS | DOC_EXTS | AUDIO_EXTS | VIDEO_EXTS | WEB_EXTS


def get_category(ext: str) -> str:
    ext = ext.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in DOC_EXTS:
        return "document"
    if ext in AUDIO_EXTS:
        return "audio"
    if ext in VIDEO_EXTS:
        return "video"
    if ext in WEB_EXTS:
        return "web"
    return "unknown"


FORMAT_INFO = {
    # 이미지
    ".png":  {"name": "PNG",  "desc": "무손실, 투명 배경 지원", "priority": 1},
    ".jpg":  {"name": "JPG",  "desc": "사진에 최적, 용량 작음", "priority": 2},
    ".jpeg": {"name": "JPEG", "desc": "JPG와 동일", "priority": 99},
    ".webp": {"name": "WEBP", "desc": "웹 최적화, 고압축", "priority": 3},
    ".gif":  {"name": "GIF",  "desc": "애니메이션 지원", "priority": 5},
    ".bmp":  {"name": "BMP",  "desc": "비압축, 용량 큼", "priority": 7},
    ".tiff": {"name": "TIFF", "desc": "인쇄용 고품질", "priority": 6},
    ".tif":  {"name": "TIF",  "desc": "TIFF와 동일", "priority": 99},
    ".ico":  {"name": "ICO",  "desc": "파비콘/아이콘용", "priority": 8},
    # 문서
    ".pdf":  {"name": "PDF",  "desc": "범용 문서 포맷", "priority": 1},
    ".docx": {"name": "DOCX", "desc": "Word 문서", "priority": 2},
    ".pptx": {"name": "PPTX", "desc": "PowerPoint 프레젠테이션", "priority": 3},
    ".xlsx": {"name": "XLSX", "desc": "Excel 스프레드시트", "priority": 4},
    ".hwp":  {"name": "HWP",  "desc": "한글 문서", "priority": 5},
    ".hwpx": {"name": "HWPX", "desc": "한글 문서 (XML)", "priority": 6},
    ".odt":  {"name": "ODT",  "desc": "오픈도큐먼트 텍스트", "priority": 8},
    ".odp":  {"name": "ODP",  "desc": "오픈도큐먼트 프레젠테이션", "priority": 9},
    ".ods":  {"name": "ODS",  "desc": "오픈도큐먼트 스프레드시트", "priority": 10},
    ".txt":  {"name": "TXT",  "desc": "일반 텍스트", "priority": 11},
    # 오디오
    ".mp3":  {"name": "MP3",  "desc": "가장 범용적인 오디오", "priority": 1},
    ".wav":  {"name": "WAV",  "desc": "무손실, 편집용", "priority": 2},
    ".flac": {"name": "FLAC", "desc": "무손실 압축", "priority": 3},
    ".aac":  {"name": "AAC",  "desc": "고효율 (Apple 기본)", "priority": 4},
    ".ogg":  {"name": "OGG",  "desc": "오픈소스 코덱", "priority": 5},
    ".m4a":  {"name": "M4A",  "desc": "Apple 오디오", "priority": 6},
    ".wma":  {"name": "WMA",  "desc": "Windows 오디오", "priority": 7},
    # 비디오
    ".mp4":  {"name": "MP4",  "desc": "가장 범용적인 영상", "priority": 1},
    ".mov":  {"name": "MOV",  "desc": "Apple 영상 포맷", "priority": 2},
    ".mkv":  {"name": "MKV",  "desc": "자막/다중트랙 지원", "priority": 3},
    ".avi":  {"name": "AVI",  "desc": "레거시 영상", "priority": 4},
    ".webm": {"name": "WEBM", "desc": "웹 영상 (VP9)", "priority": 5},
    ".wmv":  {"name": "WMV",  "desc": "Windows 영상", "priority": 6},
    ".flv":  {"name": "FLV",  "desc": "Flash 영상 (레거시)", "priority": 7},
    # 웹
    ".html": {"name": "HTML", "desc": "웹 페이지", "priority": 1},
    ".htm":  {"name": "HTM",  "desc": "웹 페이지", "priority": 99},
}


def get_supported_targets(src_ext: str) -> list[str]:
    """소스 확장자에서 변환 가능한 대상 확장자 목록 (우선순위순)"""
    cat = get_category(src_ext)
    targets = []

    if cat == "image":
        targets = list(IMAGE_EXTS - {src_ext, ".jpeg", ".tif"})
        targets.append(".pdf")
    elif cat == "document":
        if src_ext == ".pdf":
            targets = list(IMAGE_EXTS - {".jpeg", ".tif"})
        else:
            targets = [".pdf"] + list(IMAGE_EXTS - {".jpeg", ".tif"})
    elif cat == "audio":
        targets = list(AUDIO_EXTS - {src_ext})
    elif cat == "video":
        targets = list(VIDEO_EXTS - {src_ext})
        targets.extend(list(AUDIO_EXTS))
        targets.append(".gif")
    elif cat == "web":
        targets = [".png", ".jpg", ".webp", ".pdf", ".mp4", ".gif", ".webm"]

    targets.sort(key=lambda x: FORMAT_INFO.get(x, {}).get("priority", 50))
    return targets


# ── 이미지 변환 ──────────────────────────────────────────────

def convert_image(src: Path, target_ext: str, out_dir: Path) -> bool:
    try:
        from PIL import Image
    except ImportError:
        print("  [오류] Pillow 미설치: pip install Pillow")
        return False

    img = Image.open(str(src))

    # RGBA → RGB (JPEG 등 알파 미지원 포맷)
    if target_ext in (".jpg", ".jpeg", ".bmp", ".ico") and img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif target_ext in (".jpg", ".jpeg", ".bmp") and img.mode != "RGB":
        img = img.convert("RGB")

    out_path = out_dir / f"{src.stem}{target_ext}"

    save_kwargs = {}
    if target_ext in (".jpg", ".jpeg"):
        save_kwargs["quality"] = 95
    elif target_ext == ".webp":
        save_kwargs["quality"] = 90
    elif target_ext == ".png":
        save_kwargs["optimize"] = True

    img.save(str(out_path), **save_kwargs)
    print(f"  ✓ {out_path.name}")
    return True


# ── 이미지 → PDF ─────────────────────────────────────────────

def images_to_pdf(src: Path, out_dir: Path) -> bool:
    try:
        from PIL import Image
    except ImportError:
        print("  [오류] Pillow 미설치: pip install Pillow")
        return False

    img = Image.open(str(src))
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    out_path = out_dir / f"{src.stem}.pdf"
    img.save(str(out_path), "PDF")
    print(f"  ✓ {out_path.name}")
    return True


# ── PDF → 이미지 ─────────────────────────────────────────────

def pdf_to_image(src: Path, target_ext: str, out_dir: Path, dpi: int = 200) -> bool:
    try:
        import pypdfium2 as pdfium
    except ImportError:
        print("  [오류] pypdfium2 미설치: pip install pypdfium2")
        return False

    from PIL import Image as PILImage

    doc = pdfium.PdfDocument(str(src))
    total = len(doc)
    scale = dpi / 72

    for i, page in enumerate(doc):
        bitmap = page.render(scale=scale, rotation=0)
        pil_img = bitmap.to_pil()

        if target_ext in (".jpg", ".jpeg") and pil_img.mode == "RGBA":
            bg = PILImage.new("RGB", pil_img.size, (255, 255, 255))
            bg.paste(pil_img, mask=pil_img.split()[3])
            pil_img = bg

        if total == 1:
            out_path = out_dir / f"{src.stem}{target_ext}"
        else:
            out_path = out_dir / f"{src.stem}_p{i+1:03d}{target_ext}"

        save_kwargs = {}
        if target_ext in (".jpg", ".jpeg"):
            save_kwargs["quality"] = 95
        elif target_ext == ".webp":
            save_kwargs["quality"] = 90

        pil_img.save(str(out_path), **save_kwargs)
        print(f"  ✓ {out_path.name}")

    doc.close()
    return True


# ── 문서 → PDF (LibreOffice) ─────────────────────────────────

def doc_to_pdf(src: Path, out_dir: Path) -> Path | None:
    if not SOFFICE:
        print("  [오류] LibreOffice 미설치")
        print("  설치: https://www.libreoffice.org/download/download/")
        return None

    result = subprocess.run(
        [SOFFICE, "--headless", "--convert-to", "pdf",
         "--outdir", str(out_dir), str(src)],
        capture_output=True, text=True
    )

    pdf_path = out_dir / (src.stem + ".pdf")
    if not pdf_path.exists():
        print(f"  [오류] PDF 변환 실패: {result.stderr.strip()}")
        return None

    return pdf_path


def doc_to_target(src: Path, target_ext: str, out_dir: Path) -> bool:
    """문서 → PDF → 대상 포맷"""
    if target_ext == ".pdf":
        pdf = doc_to_pdf(src, out_dir)
        if pdf:
            print(f"  ✓ {pdf.name}")
            return True
        return False

    # 문서 → PDF → 이미지
    if target_ext in IMAGE_EXTS:
        tmp_dir = Path(tempfile.mkdtemp())
        pdf = doc_to_pdf(src, tmp_dir)
        if not pdf:
            return False
        ok = pdf_to_image(pdf, target_ext, out_dir)
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return ok

    print(f"  [오류] 문서에서 {target_ext}로 직접 변환 불가")
    return False


# ── 오디오 변환 (FFmpeg) ─────────────────────────────────────

def convert_audio(src: Path, target_ext: str, out_dir: Path) -> bool:
    if not FFMPEG:
        print("  [오류] FFmpeg 미설치")
        print("  설치: https://ffmpeg.org/download.html")
        return False

    out_path = out_dir / f"{src.stem}{target_ext}"

    codec_map = {
        ".mp3": ["-codec:a", "libmp3lame", "-q:a", "2"],
        ".wav": ["-codec:a", "pcm_s16le"],
        ".flac": ["-codec:a", "flac"],
        ".aac": ["-codec:a", "aac", "-b:a", "192k"],
        ".ogg": ["-codec:a", "libvorbis", "-q:a", "6"],
        ".m4a": ["-codec:a", "aac", "-b:a", "192k"],
        ".wma": ["-codec:a", "wmav2", "-b:a", "192k"],
    }

    codec = codec_map.get(target_ext, [])
    cmd = [FFMPEG, "-y", "-i", str(src)] + codec + [str(out_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [오류] FFmpeg 실패: {result.stderr[-200:]}")
        return False

    print(f"  ✓ {out_path.name}")
    return True


# ── 비디오 변환 (FFmpeg) ─────────────────────────────────────

def convert_video(src: Path, target_ext: str, out_dir: Path) -> bool:
    if not FFMPEG:
        print("  [오류] FFmpeg 미설치")
        print("  설치: https://ffmpeg.org/download.html")
        return False

    out_path = out_dir / f"{src.stem}{target_ext}"

    # 비디오 → 오디오 (추출)
    if target_ext in AUDIO_EXTS:
        return convert_audio(src, target_ext, out_dir)

    # 비디오 → GIF
    if target_ext == ".gif":
        cmd = [
            FFMPEG, "-y", "-i", str(src),
            "-vf", "fps=15,scale=480:-1:flags=lanczos",
            "-t", "10",
            str(out_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [오류] FFmpeg 실패: {result.stderr[-200:]}")
            return False
        print(f"  ✓ {out_path.name}")
        return True

    # 비디오 → 비디오
    codec_map = {
        ".mp4": ["-codec:v", "libx264", "-codec:a", "aac"],
        ".avi": ["-codec:v", "mpeg4", "-codec:a", "mp3"],
        ".mkv": ["-codec:v", "libx264", "-codec:a", "aac"],
        ".mov": ["-codec:v", "libx264", "-codec:a", "aac"],
        ".webm": ["-codec:v", "libvpx-vp9", "-codec:a", "libopus", "-b:v", "2M"],
        ".wmv": ["-codec:v", "wmv2", "-codec:a", "wmav2"],
        ".flv": ["-codec:v", "flv", "-codec:a", "mp3"],
    }

    codec = codec_map.get(target_ext, [])
    cmd = [FFMPEG, "-y", "-i", str(src)] + codec + [str(out_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [오류] FFmpeg 실패: {result.stderr[-200:]}")
        return False

    print(f"  ✓ {out_path.name}")
    return True


# ── HTML 변환 (Playwright) ───────────────────────────────────

HTML_DEFAULTS = {
    "width": 1200,
    "height": 800,
    "fps": 30,
    "duration": 8.0,
    "screenshot_delay": 2.0,
}


def _html_src_url(src: Path) -> str:
    """Windows 경로 → file:// URL 안전 변환"""
    return src.resolve().as_uri()


def html_to_image(src: Path, target_ext: str, out_dir: Path,
                  width: int = None, height: int = None) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [오류] playwright 미설치: pip install playwright && playwright install chromium")
        return False

    W = width or HTML_DEFAULTS["width"]
    H = height or HTML_DEFAULTS["height"]
    out_path = out_dir / f"{src.stem}{target_ext}"

    # Playwright screenshot은 png/jpeg만 직접 지원 → 그 외는 Pillow로 후처리
    direct = target_ext in (".png", ".jpg", ".jpeg")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(viewport={"width": W, "height": H},
                                       device_scale_factor=1)
            page = ctx.new_page()
            page.goto(_html_src_url(src), wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(int(HTML_DEFAULTS["screenshot_delay"] * 1000))

            if direct:
                page.screenshot(path=str(out_path),
                                type="jpeg" if target_ext in (".jpg", ".jpeg") else "png",
                                full_page=False, omit_background=False)
                browser.close()
                print(f"  ✓ {out_path.name}")
                return True

            # WEBP 등: 먼저 PNG로 저장 후 Pillow 변환
            import tempfile as _tmp
            tmp_png = Path(_tmp.mkdtemp()) / "shot.png"
            page.screenshot(path=str(tmp_png), type="png", full_page=False)
            browser.close()

        from PIL import Image
        img = Image.open(str(tmp_png))
        save_kwargs = {}
        if target_ext == ".webp":
            save_kwargs["quality"] = 90
        img.save(str(out_path), **save_kwargs)
        shutil.rmtree(tmp_png.parent, ignore_errors=True)
        print(f"  ✓ {out_path.name}")
        return True
    except Exception as e:
        print(f"  [오류] HTML 렌더링 실패: {e}")
        return False


def html_to_pdf(src: Path, out_dir: Path,
                width: int = None, height: int = None) -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [오류] playwright 미설치: pip install playwright && playwright install chromium")
        return False

    W = width or HTML_DEFAULTS["width"]
    H = height or HTML_DEFAULTS["height"]
    out_path = out_dir / f"{src.stem}.pdf"

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(viewport={"width": W, "height": H})
            page = ctx.new_page()
            page.goto(_html_src_url(src), wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(int(HTML_DEFAULTS["screenshot_delay"] * 1000))
            page.pdf(path=str(out_path),
                     width=f"{W}px", height=f"{H}px",
                     print_background=True)
            browser.close()
        print(f"  ✓ {out_path.name}")
        return True
    except Exception as e:
        print(f"  [오류] HTML → PDF 실패: {e}")
        return False


def html_to_video(src: Path, target_ext: str, out_dir: Path,
                  width: int = None, height: int = None,
                  fps: int = None, duration: float = None) -> bool:
    """HTML 애니메이션을 프레임 캡처 → FFmpeg 조립."""
    if not FFMPEG:
        print("  [오류] FFmpeg 미설치 (HTML → 영상에 필요)")
        return False
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  [오류] playwright 미설치: pip install playwright && playwright install chromium")
        return False

    W = width or HTML_DEFAULTS["width"]
    H = height or HTML_DEFAULTS["height"]
    FPS = fps or HTML_DEFAULTS["fps"]
    DUR = duration or HTML_DEFAULTS["duration"]
    total_frames = max(1, int(round(FPS * DUR)))

    out_path = out_dir / f"{src.stem}{target_ext}"
    tmp_dir = Path(tempfile.mkdtemp(prefix="html2vid_"))

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(viewport={"width": W, "height": H},
                                       device_scale_factor=1)
            page = ctx.new_page()
            page.goto(_html_src_url(src), wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(2000)

            # 웹 애니메이션 현재시간 리셋
            page.evaluate("() => document.getAnimations?.().forEach(a => { try { a.currentTime = 0; a.play(); } catch(e){} })")

            interval_ms = 1000.0 / FPS
            for i in range(total_frames):
                t = i * interval_ms
                page.evaluate(
                    "(t) => document.getAnimations?.().forEach(a => { try { a.currentTime = t; } catch(e){} })",
                    t,
                )
                frame_file = tmp_dir / f"f_{i:05d}.png"
                page.screenshot(path=str(frame_file), type="png")
            browser.close()

        # FFmpeg 조립
        frames_pattern = str(tmp_dir / "f_%05d.png")
        if target_ext == ".gif":
            vf = f"fps={min(15, FPS)},scale={min(800, W)}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer:bayer_scale=5"
            cmd = [FFMPEG, "-y", "-framerate", str(FPS), "-i", frames_pattern,
                   "-vf", vf, "-loop", "0", str(out_path)]
        elif target_ext == ".webm":
            cmd = [FFMPEG, "-y", "-framerate", str(FPS), "-i", frames_pattern,
                   "-c:v", "libvpx-vp9", "-b:v", "2M", "-pix_fmt", "yuv420p",
                   str(out_path)]
        else:  # .mp4 및 기본
            cmd = [FFMPEG, "-y", "-framerate", str(FPS), "-i", frames_pattern,
                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
                   "-movflags", "+faststart", str(out_path)]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  [오류] FFmpeg 실패: {result.stderr[-200:]}")
            return False

        print(f"  ✓ {out_path.name}")
        return True
    except Exception as e:
        print(f"  [오류] HTML → 영상 실패: {e}")
        return False
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ── 통합 변환 디스패처 ───────────────────────────────────────

def convert(src: Path, target_ext: str, out_dir: Path = None) -> bool:
    if out_dir is None:
        out_dir = OUTPUT_DIR

    src_ext = src.suffix.lower()
    target_ext = target_ext.lower()
    if not target_ext.startswith("."):
        target_ext = "." + target_ext

    src_cat = get_category(src_ext)
    tgt_cat = get_category(target_ext)

    print(f"\n[변환] {src.name} → {target_ext}")

    # 같은 포맷
    if src_ext == target_ext:
        print("  [건너뜀] 같은 포맷입니다")
        return False

    # 이미지 → 이미지
    if src_cat == "image" and tgt_cat == "image":
        return convert_image(src, target_ext, out_dir)

    # 이미지 → PDF
    if src_cat == "image" and target_ext == ".pdf":
        return images_to_pdf(src, out_dir)

    # PDF → 이미지
    if src_ext == ".pdf" and tgt_cat == "image":
        return pdf_to_image(src, target_ext, out_dir)

    # 문서 → PDF / 이미지
    if src_cat == "document" and src_ext != ".pdf":
        return doc_to_target(src, target_ext, out_dir)

    # 오디오 → 오디오
    if src_cat == "audio" and tgt_cat == "audio":
        return convert_audio(src, target_ext, out_dir)

    # 비디오 → 비디오 / 오디오 / GIF
    if src_cat == "video":
        if tgt_cat in ("video", "audio") or target_ext == ".gif":
            return convert_video(src, target_ext, out_dir)

    # HTML → 이미지 / PDF / 영상
    if src_cat == "web":
        if tgt_cat == "image":
            return html_to_image(src, target_ext, out_dir)
        if target_ext == ".pdf":
            return html_to_pdf(src, out_dir)
        if target_ext in (".mp4", ".gif", ".webm"):
            return html_to_video(src, target_ext, out_dir)

    print(f"  [오류] {src_ext} → {target_ext} 변환은 지원되지 않습니다")
    return False


# ── CLI ──────────────────────────────────────────────────────

def print_help():
    print(__doc__)
    print("지원 포맷:")
    print(f"  이미지: {', '.join(sorted(IMAGE_EXTS))}")
    print(f"  문서:   {', '.join(sorted(DOC_EXTS))}")
    print(f"  오디오: {', '.join(sorted(AUDIO_EXTS))}")
    print(f"  비디오: {', '.join(sorted(VIDEO_EXTS))}")
    print(f"  웹:     {', '.join(sorted(WEB_EXTS))}  (Playwright 필요)")


def interactive_mode():
    """input/ 폴더 파일을 대화형으로 변환"""
    if not INPUT_DIR.exists():
        INPUT_DIR.mkdir()

    files = [f for f in INPUT_DIR.iterdir() if f.suffix.lower() in ALL_EXTS]
    if not files:
        print(f"input/ 폴더에 파일을 넣고 다시 실행하세요.")
        print(f"  위치: {INPUT_DIR}")
        return

    print(f"\n[input/ 폴더] {len(files)}개 파일 발견:\n")
    for i, f in enumerate(files, 1):
        targets = get_supported_targets(f.suffix.lower())
        print(f"  {i}. {f.name}  →  변환 가능: {', '.join(targets)}")

    print()
    target = input("변환할 포맷 입력 (예: png, mp3): ").strip().lower()
    if not target:
        return
    if not target.startswith("."):
        target = "." + target

    for f in files:
        convert(f, target)

    print(f"\n완료 → {OUTPUT_DIR}")


def main():
    if len(sys.argv) < 2:
        interactive_mode()
        return

    if sys.argv[1] in ("--help", "-h", "help"):
        print_help()
        return

    if len(sys.argv) == 2:
        # 파일만 지정 → 변환 가능 목록 표시
        src = Path(sys.argv[1])
        if not src.exists():
            print(f"[오류] 파일 없음: {src}")
            return
        targets = get_supported_targets(src.suffix.lower())
        print(f"\n{src.name} 변환 가능 포맷:")
        print(f"  {', '.join(targets)}")
        print(f"\n사용법: py convert.py {src.name} <포맷>")
        return

    # py convert.py <파일> <포맷>
    target_ext = sys.argv[-1].lower()
    src_files = [Path(a) for a in sys.argv[1:-1]]

    for src in src_files:
        if not src.exists():
            print(f"[오류] 파일 없음: {src}")
            continue
        convert(src, target_ext)

    print(f"\n완료 → {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
