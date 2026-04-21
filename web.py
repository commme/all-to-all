"""
All-to-All Web UI
  브라우저에서 파일 업로드 → 변환 → 다운로드
  여러 파일 동시 처리 지원

실행:
  py web.py          # http://localhost:5000
  py web.py 8080     # 포트 지정
"""

import sys
import json
import zipfile
import tempfile
from pathlib import Path
from flask import Flask, request, send_file, jsonify, render_template
from werkzeug.utils import secure_filename

from convert import convert, get_category, OUTPUT_DIR

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB

UPLOAD_DIR = Path(__file__).parent / "_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# 8대 핵심 변환 규칙
QUICK_RULES = {
    # 소스 카테고리 → 추천 변환 목록
    "image": [
        {"ext": ".jpg",  "name": "JPG",  "desc": "용량 줄이기 (사진)"},
        {"ext": ".png",  "name": "PNG",  "desc": "투명 배경 지원"},
        {"ext": ".webp", "name": "WEBP", "desc": "웹 최적화 (70% 압축)"},
        {"ext": ".pdf",  "name": "PDF",  "desc": "문서로 제출"},
    ],
    "pdf": [
        {"ext": ".png",  "name": "PNG",  "desc": "이미지로 캡처/공유"},
        {"ext": ".jpg",  "name": "JPG",  "desc": "이미지로 (용량 작게)"},
    ],
    "hwp": [
        {"ext": ".pdf",  "name": "PDF",  "desc": "PDF로 변환 (제출용)"},
        {"ext": ".png",  "name": "PNG",  "desc": "이미지로 캡처"},
    ],
    "video": [
        {"ext": ".mp3",  "name": "MP3",  "desc": "음성만 추출"},
        {"ext": ".gif",  "name": "GIF",  "desc": "움짤 만들기"},
        {"ext": ".mp4",  "name": "MP4",  "desc": "범용 영상 변환"},
        {"ext": ".wav",  "name": "WAV",  "desc": "무손실 음성 추출"},
    ],
    "web": [
        {"ext": ".png",  "name": "PNG",  "desc": "스크린샷 (권장)"},
        {"ext": ".pdf",  "name": "PDF",  "desc": "PDF 저장"},
        {"ext": ".mp4",  "name": "MP4",  "desc": "애니메이션 영상 (8초)"},
        {"ext": ".gif",  "name": "GIF",  "desc": "애니메이션 움짤"},
    ],
}


def get_quick_targets(ext: str) -> list[dict]:
    """소스 확장자에서 핵심 변환 대상 반환"""
    ext = ext.lower()
    cat = get_category(ext)

    if ext in (".pdf",):
        targets = QUICK_RULES["pdf"]
    elif ext in (".hwp", ".hwpx"):
        targets = QUICK_RULES["hwp"]
    elif cat == "image":
        targets = QUICK_RULES["image"]
    elif cat == "video":
        targets = QUICK_RULES["video"]
    elif cat == "web":
        targets = QUICK_RULES["web"]
    else:
        targets = []

    # 자기 자신 제외
    return [t for t in targets if t["ext"] != ext]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/formats", methods=["POST"])
def get_formats():
    data = request.get_json()
    ext = data.get("ext", "").lower()
    if not ext.startswith("."):
        ext = "." + ext

    return jsonify({
        "category": get_category(ext),
        "targets": get_quick_targets(ext)
    })


@app.route("/api/convert", methods=["POST"])
def do_convert():
    """여러 파일 동시 변환 → ZIP 다운로드"""
    files = request.files.getlist("files")
    target = request.form.get("target", "").strip().lower()

    if not files or not files[0].filename:
        return jsonify({"error": "파일이 없습니다"}), 400
    if not target:
        return jsonify({"error": "변환 포맷을 선택하세요"}), 400

    t = target if target.startswith(".") else "." + target
    saved = []
    results = []

    try:
        # 1) 업로드 저장 (파일명 sanitize + UPLOAD_DIR 경계 확인)
        upload_root = UPLOAD_DIR.resolve()
        for f in files:
            if not f.filename:
                continue
            safe_name = secure_filename(f.filename)
            if not safe_name:
                continue
            path = (UPLOAD_DIR / safe_name).resolve()
            # path traversal 방어: 결과 경로가 UPLOAD_DIR 내부인지 확인
            if upload_root != path.parent and upload_root not in path.parents:
                continue
            f.save(str(path))
            saved.append(path)

        # 2) 각 파일 변환
        for src in saved:
            ok = convert(src, target, OUTPUT_DIR)
            if ok:
                found = sorted(OUTPUT_DIR.glob(f"{src.stem}*{t}"))
                results.extend(found)

        if not results:
            return jsonify({"error": "변환 실패"}), 500

        # 3) 단일 파일이면 바로, 여러 파일이면 ZIP
        if len(results) == 1:
            return send_file(
                str(results[0]),
                as_attachment=True,
                download_name=results[0].name
            )

        zip_path = Path(tempfile.mktemp(suffix=".zip"))
        with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
            for r in results:
                zf.write(str(r), r.name)

        return send_file(
            str(zip_path),
            as_attachment=True,
            download_name=f"converted_{len(results)}files.zip",
            mimetype="application/zip"
        )
    finally:
        for p in saved:
            p.unlink(missing_ok=True)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"\n  All-to-All Converter")
    print(f"  http://localhost:{port}\n")
    # 보안: localhost 바인딩 고정, debug 비활성화 (Werkzeug /console RCE 차단)
    app.run(host="127.0.0.1", port=port, debug=False)
