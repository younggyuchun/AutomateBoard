# GitHub Actions로 Windows EXE 자동 빌드하기

## 개요
Windows PC가 없어도 GitHub의 클라우드에서 자동으로 EXE 파일을 빌드할 수 있습니다!

## 전제 조건
- GitHub 계정 필요
- 프로젝트를 GitHub 저장소에 업로드

## 설정 방법

### 1단계: GitHub 저장소 만들기

```bash
# macOS에서 실행
cd /Users/younggyu.chun/Projects/AutomateBoard

# Git 초기화 (아직 안 했다면)
git init

# 파일 추가
git add .
git commit -m "Initial commit with Windows build setup"

# GitHub에 저장소 만들고 연결
# GitHub 웹사이트에서 새 저장소 생성 후:
git remote add origin https://github.com/[사용자명]/AutomateBoard.git
git branch -M main
git push -u origin main
```

### 2단계: GitHub Actions 파일 확인

이미 생성된 파일:
- `.github/workflows/build-windows-exe.yml`

이 파일이 자동으로 Windows에서 EXE를 빌드합니다!

### 3단계: 빌드 실행

#### 자동 빌드 (코드 푸시 시)
```bash
# 코드 변경 후
git add .
git commit -m "Update code"
git push
```
→ 자동으로 빌드 시작!

#### 수동 빌드
1. GitHub 저장소 웹페이지 접속
2. "Actions" 탭 클릭
3. "Build Windows EXE" 워크플로우 선택
4. "Run workflow" 버튼 클릭
5. "Run workflow" 확인

### 4단계: 빌드 결과 다운로드

1. GitHub Actions 탭에서 완료된 빌드 클릭
2. 하단 "Artifacts" 섹션에서 `HansomangAutomation-Windows.zip` 다운로드
3. ZIP 압축 해제하면 3개 파일이 나옴:
   - HansomangAutomation.exe
   - setup_playwright.bat
   - 사용설명서.txt

## 릴리스 만들기 (선택사항)

버전 태그를 만들면 자동으로 릴리스가 생성됩니다:

```bash
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

→ GitHub의 "Releases" 페이지에 자동으로 ZIP 파일이 업로드됩니다!

## 빌드 시간
- 평균 5-10분 소요
- 무료로 사용 가능 (GitHub Free 계정: 월 2,000분)

## 장점
✅ Windows PC 불필요
✅ 맥에서 모든 작업 가능
✅ 자동화된 빌드
✅ 빌드 기록 보관
✅ 버전 관리 통합

## 단점
⚠️ GitHub 계정 필요
⚠️ 공개 저장소 또는 유료 계정 필요 (Private + Actions)
⚠️ 빌드 시간이 조금 걸림
⚠️ 인터넷 연결 필수

## 사용 시나리오

### 시나리오 1: 개발 중
```bash
# 코드 수정
git add .
git commit -m "Fix bug"
git push
# → 자동 빌드, Artifacts에서 다운로드
```

### 시나리오 2: 정식 버전 릴리스
```bash
# 버전 태그 생성
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
# → 자동 빌드 + GitHub Releases에 업로드
```

### 시나리오 3: 수동 빌드
```
1. GitHub 웹사이트 접속
2. Actions → Build Windows EXE → Run workflow
3. 완료 후 Artifacts 다운로드
```

## 문제 해결

### 빌드 실패
- Actions 탭에서 로그 확인
- Python 버전, 의존성 문제일 가능성
- `.github/workflows/build-windows-exe.yml` 파일 확인

### Artifacts가 보이지 않음
- 빌드가 완료될 때까지 대기 (5-10분)
- 빌드가 성공했는지 확인 (녹색 체크마크)

### Private 저장소에서 사용
- GitHub Pro 계정 필요
- 또는 Public 저장소로 변경

## 비교: Windows PC vs GitHub Actions

| 항목 | Windows PC | GitHub Actions |
|------|-----------|----------------|
| 비용 | PC 필요 | 무료 (제한적) |
| 속도 | 빠름 (1-2분) | 느림 (5-10분) |
| 설정 | 간단 | 중간 |
| 자동화 | 수동 | 자동 |
| 접근성 | PC 필요 | 웹만 있으면 됨 |

## 추천 사용 방법

1. **개발/테스트**: GitHub Actions 사용
   - macOS에서 코드 작성
   - 푸시하면 자동으로 Windows EXE 생성
   - 빠른 테스트 가능

2. **최종 배포**: Windows PC 사용 (있다면)
   - 더 빠른 빌드
   - 직접 테스트 가능
   - 코드 서명 가능

3. **Windows PC 없음**: GitHub Actions만 사용
   - 완전히 가능!
   - 약간 느리지만 충분히 실용적

## 더 알아보기

- [GitHub Actions 문서](https://docs.github.com/actions)
- [PyInstaller 문서](https://pyinstaller.org/)

## 요약

✅ `.github/workflows/build-windows-exe.yml` 파일 생성됨
✅ GitHub에 푸시하면 자동으로 Windows EXE 빌드
✅ macOS에서 Windows 프로그램 개발 가능!

코드를 GitHub에 푸시하고 Actions 탭을 확인해보세요! 🚀

