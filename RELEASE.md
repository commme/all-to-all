# All-to-All 변환기 🔄

**이미지·PDF·HWP·영상·음성을 한 화면에서 바로 변환. 전부 내 PC에서만 돈다.**

🔗 로컬 실행: `py web.py` → http://localhost:5000

---

## 이런 분께

- 카톡 보낼 PNG가 너무 커서 JPG로 줄여야 한다
- HWP 받았는데 다른 PC에 한컴이 없다 → PDF로 바꾸고 싶다
- PDF를 카톡/슬랙에 이미지로 던지고 싶다
- 회의 영상에서 음성만 뽑아 자막용 MP3로 쓰고 싶다
- 짧은 영상 하나를 GIF 움짤로 만들고 싶다
- 온라인 변환기는 파일이 외부로 나가서 찜찜하다

---

## 30초 요약

1. `pip install -r requirements.txt` (최초 1회)
2. `py web.py` 실행
3. http://localhost:5000 에서 파일 드래그 → 포맷 선택 → 다운로드 끝

파일은 **내 PC 안에서만** 변환됨. 외부 서버 ❌

---

## 시작하기 (3단계)

### 1. 파이썬 + 의존성

```bash
pip install -r requirements.txt
```

설치되는 것: Pillow (이미지) · pypdfium2 (PDF) · Flask (웹UI)

### 2. 시스템 도구 (필요할 때만)

| 도구 | 어떤 변환에 필요 |
|------|----------------|
| [FFmpeg](https://ffmpeg.org/download.html) | MP4 → MP3 / GIF / WAV |
| [LibreOffice](https://www.libreoffice.org/download/) | HWP → PDF / PNG |

이미지·PDF만 쓸 거면 둘 다 안 깔아도 됨.

### 3. 웹 UI 띄우기

```bash
py web.py
```

브라우저 → http://localhost:5000 → 파일 끌어다 놓기 → 변환 포맷 클릭 → 자동 다운로드.

여러 파일 한 번에 → 자동으로 ZIP으로 묶임.

---

## 핵심 변환 8가지

| # | 변환 | 어디 쓰나 |
|---|------|----------|
| 1 | PNG → JPG | 용량 줄이기 |
| 2 | JPG → PNG | 투명 배경 |
| 3 | 이미지 → WEBP | 웹 최적화 |
| 4 | PDF → PNG | 이미지 캡처/공유 |
| 5 | 이미지 → PDF | 문서 제출 |
| 6 | MP4 → MP3 | 음성 추출 |
| 7 | MP4 → GIF | 움짤 |
| 8 | HWP → PDF | 한글 파일 변환 |

CLI에서는 40+ 포맷 조합 모두 가능.

---

## CLI도 됨

```bash
# 단일 변환
py convert.py 사진.png jpg
py convert.py 영상.mp4 mp3

# 여러 파일 일괄
py convert.py 1.png 2.png 3.png webp

# 파일만 넣으면 변환 가능 포맷 목록 표시
py convert.py 파일.pdf

# input/ 폴더 통째로 대화형 변환
py convert.py
```

---

## 자주 묻는 질문

**Q. 인터넷 필요해요?** 아뇨. 의존성 설치 후엔 완전 오프라인.

**Q. 파일이 외부로 나가요?** **아니요.** Flask는 `127.0.0.1`(localhost) 바인딩, 외부 접근 차단.

**Q. 업로드한 원본은요?** 변환 끝나면 `_uploads/` 폴더에서 즉시 삭제.

**Q. 모바일에서도 돼요?** 같은 와이파이 PC에 띄워두고 휴대폰 브라우저로 접속하는 건 가능. 단 보안상 권장 안 함.

**Q. 동영상 길이 제한?** 없음. 단 GIF 변환은 길수록 용량 폭증.

**Q. 한컴 한글 없이 HWP 변환 되나요?** 네, LibreOffice가 대신 처리.

**Q. 카페·도서관 PC에서 띄워도 돼요?** 비추. 같은 네트워크 다른 사람도 접근 가능. 무조건 `host='127.0.0.1'` 유지.

---

## 보안·개인정보

| 항목 | 상태 |
|------|------|
| 외부 서버 전송 | ❌ 전혀 없음 |
| 웹서버 바인딩 | `127.0.0.1` (localhost) 전용 |
| 업로드 파일 보존 | 변환 완료 즉시 삭제 |
| 외부 스크립트 | CSP로 외부 차단, self만 허용 |
| XSS 방지 | 사용자 입력 textContent 처리 |
| 인증 | ❌ 없음 (로컬 전용 가정) |

### ⚠️ 공용 네트워크에서 절대 띄우지 마세요

`web.py`는 인증이 없습니다. `host='0.0.0.0'`로 바꾸면 같은 네트워크의 다른 사람이 **인증 없이 파일 업로드/변환 가능**합니다.

→ 항상 `host='127.0.0.1'`, `debug=False` 유지하세요.

---

## 단축 기능

- 드래그앤드롭 다중 파일 → ZIP 일괄 다운로드
- 소스 확장자 인식 → 변환 가능 포맷만 표시
- 다크 테마 + 모바일 반응형
- 변환 후 자동 다운로드 (1개면 바로, 여러개면 ZIP)

---

## 만든 사람

© 2026 COMMME · MIT License

오픈소스 · Claude Code Opus 4.6으로 제작.
피드백/버그: https://github.com/commme/all-to-all/issues
