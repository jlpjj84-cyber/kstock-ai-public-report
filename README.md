# KStock AI — 공개 성능 리포트 미러

이 저장소는 **읽기 전용 공개 성능 보고서** 전용입니다. 개인 계좌, 종목별 보유/주문, 키움 API 인증정보, 비공개 아카이브를 저장하지 않습니다.

## 제공하는 URL (GitHub Pages가 활성화된 후)

- HTML: https://jlpjj84-cyber.github.io/kstock-ai-public-report/
- TEXT: https://jlpjj84-cyber.github.io/kstock-ai-public-report/report.txt
- JSON: https://jlpjj84-cyber.github.io/kstock-ai-public-report/report.json

> 실제 게시 완료 여부는 위 URL에 대한 HTTP 200과 GitHub Actions 성공 기록으로 확인해야 합니다. 이 링크는 배포 대상 주소이며 배포 성공을 보증하는 것은 아닙니다.

## 갱신 방식

GitHub Actions `KStock public report mirror (GitHub Pages)`가 원본에 **익명 HTTPS GET**으로 접근합니다.

원본:
- https://kstock-ai-public-report.keenskunk257.chatgpt.site/report.txt
- https://kstock-ai-public-report.keenskunk257.chatgpt.site/report.json

장중(평일 09:00–15:30 KST) 약 30분마다, 그리고 매일 22:30 KST 동기화를 요청합니다. Actions는 실행 지연이 있을 수 있습니다. `Actions` 메뉴에서 수동 실행도 가능합니다. Sites 측 보고서 갱신 주기에 따라 동일 데이터가 유지될 수 있습니다.

두 파일이 모두 응답·검증에 성공해야만 정적 결과물을 만들고 Pages에 **아티팩트 단위로 배포**합니다. 원본 접속 실패·기밀 필드 발견 시 실패 처리하고 마지막 정상 배포는 변경하지 않습니다.

## 최초 설정 (소유자가 1회 수행)

1. GitHub 저장소 **Settings → Pages**로 이동합니다.
2. **Build and deployment → Source → GitHub Actions**를 선택합니다.
3. 저장소 **Actions**에서 `KStock public report mirror (GitHub Pages)`를 수동 실행합니다.
4. 결과가 성공했는지, HTML·TEXT·JSON URL이 로그인 없이 각각 200을 반환하는지 확인합니다.

**저장소 공개(Public) 상태를 유지하되 원본 비공개 저장소 `kstock-ai-paper`는 절대로 공개하지 마세요.**

## 한계

- 공개 보고서 원본 내용은 Sites 제공 값과 동일한 의미로 저장하지만 JSON 텍스트의 공백 및 객체 키 순서는 정규화될 수 있습니다.
- 공개 보고서의 검증 결과는 원본 데이터가 주장한 값입니다. GitHub Pages를 만든다고 AI 모델의 성능이 독립적으로 입증되는 것은 아닙니다.
- ChatGPT의 웹 조회 제한이 GitHub Pages에도 적용되는지는 실제 게시 후 직접 확인해야 합니다.
