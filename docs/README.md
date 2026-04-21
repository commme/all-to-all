# All-to-All Converter — Web Edition

설치 없이 브라우저에서 바로 쓰는 이미지·PDF 변환기.

## 지원 변환

- **이미지 ↔ 이미지** — PNG · JPG · WEBP · BMP · GIF 상호 변환
- **이미지 → PDF** — 사진을 문서로
- **PDF → 이미지** — 페이지마다 PNG/JPG/WEBP로

## 왜 웹 버전?

- ✅ 설치 불필요
- ✅ 파일 업로드 없음 (브라우저에서 전부 처리)
- ✅ 완전 오프라인 (한 번 로드 후 인터넷 차단 가능)

## 한계

웹 버전에서는 **영상·오디오·HTML·HWP/DOCX** 변환을 지원하지 않습니다. 이런 포맷은 브라우저에서 직접 처리하기 어려우므로 [로컬 서버 버전](../)을 사용하세요.

| 변환 | 웹 버전 | 서버 버전 |
|------|:-:|:-:|
| 이미지 ↔ 이미지 | ✅ | ✅ |
| 이미지 ↔ PDF | ✅ | ✅ |
| 영상 (MP4/MOV/MKV 등) | ❌ | ✅ |
| 오디오 (MP3/WAV 등) | ❌ | ✅ |
| HTML → 이미지/PDF/영상 | ❌ | ✅ |
| HWP / DOCX / PPTX → PDF | ❌ | ✅ |

## 사용 라이브러리

- [pdf.js](https://mozilla.github.io/pdf.js/) — PDF 렌더링
- [jsPDF](https://github.com/parallax/jsPDF) — 이미지 → PDF 생성
- Canvas API — 이미지 변환

---

© 2026 COMMME · Built with Claude Code
