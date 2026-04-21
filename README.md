# All-to-All File Converter

파일 변환기 · 이미지·PDF·영상·오디오·문서·HTML을 서로 변환합니다.  
**파일이 외부 서버로 전송되지 않습니다.**

## 🌐 두 가지 실행 모드

| 모드 | 실행 방식 | 지원 변환 | 설치 |
|------|---------|----------|------|
| **웹 (정적)** | [GitHub Pages](./docs/) · 브라우저만 | 이미지 ↔ 이미지, 이미지 ↔ PDF | ❌ 설치 불필요 |
| **로컬 서버** | `py web.py` · Python + FFmpeg + LibreOffice + Playwright | **전체** (영상/오디오/HTML/HWP 포함) | ✅ 설치 필요 |

👉 **간단한 이미지/PDF 변환** → [웹 버전 바로 가기](https://commme.github.io/all-to-all/) (업로드 없음, 즉시 변환)  
👉 **영상·HTML·HWP 변환** → 로컬 서버 버전 설치 (아래 가이드)

## 지원하는 변환

| 소스 | 변환 가능 | 모드 | 용도 |
|------|----------|------|------|
| PNG / JPG / WEBP / BMP / GIF | → PNG, JPG, WEBP, PDF | 웹·서버 | 용량 줄이기, 웹 최적화, 문서 제출 |
| PDF | → PNG, JPG, WEBP | 웹·서버 | 이미지로 캡처/공유 (카톡, 슬랙) |
| HTML / HTM | → PNG, PDF, MP4, GIF, WEBM | 서버 | 웹 페이지/애니메이션 → 이미지/영상 |
| HWP / DOCX / PPTX | → PDF, PNG | 서버 | 한글·Office 파일 PDF/이미지 변환 |
| MP4 / 영상 | → MP3, GIF, WAV, 다른 영상 | 서버 | 음성 추출, 움짤 만들기, 포맷 변환 |
| MP3 / 오디오 | → WAV, FLAC, AAC, OGG | 서버 | 오디오 포맷 변환 |

> CLI에서는 40+ 포맷 조합을 모두 지원합니다.

---

## 설치

### 1. Python 의존성

```bash
pip install -r requirements.txt
```

- **Pillow** — 이미지 변환
- **pypdfium2** — PDF → 이미지
- **Flask** — 웹 UI 서버

### 2. Playwright 브라우저 (HTML 변환용)

```bash
playwright install chromium
```

### 3. 시스템 도구 (선택)

| 도구 | 용도 | 없으면 |
|------|------|--------|
| [FFmpeg](https://ffmpeg.org/download.html) | 오디오/비디오/HTML→영상 변환 | 영상·음성·HTML→MP4 변환 불가 |
| [LibreOffice](https://www.libreoffice.org/download/) | HWP/DOCX → PDF | 문서 변환 불가 |

---

## 사용법

### 웹 UI (권장)

```bash
py web.py
```

→ http://localhost:5000 에서 파일 드래그앤드롭으로 변환  
→ 여러 파일 동시 선택 가능 (ZIP으로 다운로드)

### CLI

```bash
# 단일 파일
py convert.py 사진.png jpg
py convert.py 문서.pdf png
py convert.py 영상.mp4 mp3

# 여러 파일 한번에
py convert.py 사진1.png 사진2.png 사진3.png webp

# 파일만 지정하면 변환 가능 포맷 목록 표시
py convert.py 파일.pdf

# input/ 폴더 대화형 변환
py convert.py
```

---

## 이 프로젝트를 AI로 만드는 프롬프트

아래 프롬프트를 Claude Code 또는 다른 AI 코딩 도구에 입력하면 유사한 도구를 만들 수 있습니다.

### 프롬프트 1: 핵심 변환 엔진

```
Python으로 파일 포맷 변환기를 만들어줘.
- Pillow로 이미지 간 변환 (PNG, JPG, WEBP, BMP, TIFF, GIF)
- pypdfium2로 PDF → 이미지 변환
- Pillow로 이미지 → PDF 변환
- subprocess로 FFmpeg 호출하여 오디오/비디오 변환
- subprocess로 LibreOffice headless 호출하여 HWP/DOCX → PDF 변환
- CLI: py convert.py <파일> <대상포맷>
- input/ 폴더 자동 스캔 모드
```

### 프롬프트 2: 웹 UI 추가

```
위 변환 엔진에 Flask 웹 UI를 추가해줘.
- 드래그앤드롭 파일 업로드
- 여러 파일 동시 선택 및 변환
- 소스 확장자에 따라 변환 가능 포맷 자동 표시
- 변환 결과 자동 다운로드 (1개면 바로, 여러개면 ZIP)
- 다크 테마, 모바일 반응형
```

### 프롬프트 3: 실용성 집중

```
변환 조합을 실제 많이 쓰는 8가지로 좁혀줘:
1. PNG → JPG (용량 줄이기)
2. JPG → PNG (투명 배경)
3. 이미지 → WEBP (웹 최적화)
4. PDF → PNG (이미지 캡처)
5. 이미지 → PDF (문서 제출)
6. MP4 → MP3 (음성 추출)
7. MP4 → GIF (움짤)
8. HWP → PDF (문서 변환)
웹 UI 하단에 이 8가지를 소스별로 카드형으로 보여줘.
```

---

## 보안 사항

- **모든 변환은 로컬에서 실행됩니다.** 파일이 외부 서버로 전송되지 않습니다.
- 웹 서버는 `localhost`에서만 실행되며, 외부 접근이 차단됩니다.
- 업로드된 파일은 변환 완료 후 즉시 삭제됩니다 (`_uploads/` 폴더).
- Flask debug 모드는 개발용입니다. 외부 공개 시 `debug=False`로 변경하고, `host="127.0.0.1"`로 제한하세요.
- **주의**: `web.py`를 공용 네트워크에서 실행하지 마세요. 인증 없이 파일 업로드/변환이 가능합니다.
- FFmpeg, LibreOffice는 subprocess로 호출됩니다. 신뢰할 수 없는 파일 처리 시 주의하세요.

---

## 프로젝트 구조

```
all-to-all/
├── convert.py          ← 변환 엔진 + CLI (HTML 핸들러 포함)
├── web.py              ← Flask 웹 서버 (전체 기능)
├── templates/
│   └── index.html      ← 서버 모드 웹 UI
├── docs/               ← GitHub Pages 정적 버전 (이미지/PDF만)
│   ├── index.html      ← 정적 UI
│   ├── app.js          ← 클라이언트 사이드 변환 로직
│   └── style.css
├── requirements.txt    ← Python 의존성 (Playwright 포함)
├── input/              ← CLI 배치 변환용 입력 폴더
├── output/             ← 변환 결과 출력 폴더
├── LICENSE             ← MIT License
└── README.md           ← 이 파일
```

## GitHub Pages 배포

`docs/` 폴더를 GitHub Pages로 배포:

1. GitHub 레포 → Settings → Pages
2. Source: **Deploy from a branch**
3. Branch: **main** · Folder: **/docs**
4. Save → 몇 분 뒤 `https://{유저}.github.io/all-to-all/` 접속 가능

정적 버전은 이미지/PDF 변환만 지원합니다. 영상·HTML·HWP 등 서버 전용 변환은 로컬에서 `py web.py`로 실행하세요.

---

## 라이선스

MIT License

Copyright (c) 2026 one-a

이 소프트웨어는 무료로 사용, 복사, 수정, 배포할 수 있습니다.  
자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.

---

## 사용된 오픈소스

| 라이브러리 | 라이선스 | 용도 |
|-----------|---------|------|
| [Pillow](https://python-pillow.org/) | HPND | 이미지 변환 |
| [pypdfium2](https://github.com/nicoptere/pypdfium2) | Apache 2.0 / BSD | PDF 렌더링 |
| [Flask](https://flask.palletsprojects.com/) | BSD-3-Clause | 웹 서버 |
| [FFmpeg](https://ffmpeg.org/) | LGPL / GPL | 오디오/비디오 변환 |
| [LibreOffice](https://www.libreoffice.org/) | MPL 2.0 | 문서 변환 |

> 이 프로젝트는 Claude Code (Anthropic)의 도움으로 제작되었습니다.
