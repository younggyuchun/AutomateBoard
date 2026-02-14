# Hansomang 자동화 도구

이 프로그램은 hansomang.ca 웹사이트의 주일설교 등록과 팝업창 수정을 자동화하는 GUI 애플리케이션입니다.

## 설치 방법

### Python 환경에서 실행
1. 필요한 패키지 설치:
```bash
pip install playwright customtkinter
playwright install chromium
```

### Windows EXE 파일 사용 (권장)
1. `HansomangAutomation.exe` 다운로드
2. 처음 사용 시: `setup_playwright.bat` 실행 (1회만)
3. `HansomangAutomation.exe` 실행

자세한 내용은 `사용설명서.txt`를 참고하세요.

## 실행 방법

### Python으로 실행
```bash
python gui_app.py
```

### Windows EXE 실행
`HansomangAutomation.exe` 더블클릭

## Windows EXE 파일 빌드

### 필요한 패키지 설치
```bash
pip install pyinstaller
```

### 빌드 방법
```bash
# 방법 1: spec 파일 사용 (권장)
pyinstaller HansomangAutomation.spec

# 방법 2: 빌드 스크립트 사용
python build_exe.py
```

생성된 파일: `dist/HansomangAutomation.exe`

자세한 내용은 `BUILD_GUIDE.md`를 참고하세요.

## 사용 방법

### 주일설교 등록 탭
1. "주일설교 등록" 탭을 선택합니다.
2. 다음 정보를 입력합니다:
   - 제목 (기본값: "한소망 교회 주일 설교 [오늘날짜]")
   - 본문 (성경 구절)
   - 설교자 (기본값: "소성범 목사")
   - 날짜 (기본값: 오늘 날짜)
   - 외부영상연결 URL
3. "주일설교 등록 실행" 버튼을 클릭합니다.
4. 브라우저가 자동으로 열리고 작업이 진행됩니다.
5. 로그 창에서 진행 상황을 확인할 수 있습니다.

### 팝업창 수정 탭
1. "팝업창 수정" 탭을 선택합니다.
2. 팝업 URL을 입력합니다.
3. "팝업창 수정 실행" 버튼을 클릭합니다.
4. 브라우저가 자동으로 열리고 작업이 진행됩니다.
5. 로그 창에서 진행 상황을 확인할 수 있습니다.

## 파일 구조

- `gui_app.py`: GUI 메인 애플리케이션
- `HansomangAutomation.spec`: PyInstaller 빌드 설정
- `build_exe.py`: EXE 빌드 스크립트
- `setup_playwright.bat`: Windows용 Playwright 설치 스크립트
- `BUILD_GUIDE.md`: 상세 빌드 가이드
- `사용설명서.txt`: 최종 사용자용 설명서

## 배포 패키지 구성

Windows 사용자에게 배포 시 다음 파일들을 포함하세요:
1. `HansomangAutomation.exe` - 메인 실행 파일
2. `setup_playwright.bat` - Playwright 설치 스크립트
3. `사용설명서.txt` - 한글 사용 설명서
4. `USER_MANUAL_EN.txt` - 영문 사용 설명서 (영문 윈도우용)

## 주의사항

- **EXE 파일 사용 시에도 Python 설치 필수** (Playwright 브라우저 설치를 위해 필요)
- 실행 중에는 버튼이 비활성화되며, 작업이 완료되면 다시 활성화됩니다.
- 모든 필드를 입력해야 실행이 가능합니다.
- 브라우저는 headless=False로 실행되므로 작업 과정을 직접 확인할 수 있습니다.
- EXE 파일은 약 100-200MB 크기입니다.
- 처음 사용 시 Playwright 브라우저 설치가 필요합니다 (약 100-200MB 추가).

## 영문 윈도우 사용자

영문 윈도우를 사용하시는 경우:
- 한글 문서 파일이 깨져 보일 수 있습니다
- 영문 문서 파일을 사용하세요:
  - `README_EN.md` - 영문 README
  - `USER_MANUAL_EN.txt` - 영문 사용 설명서
  - `QUICK_START_EN.txt` - 영문 빠른 시작 가이드
  - `WINDOWS_SETUP_EN.txt` - 영문 윈도우 설치 가이드
- `setup_playwright.bat` 파일은 영문 윈도우에서도 정상 작동합니다
- GUI 프로그램은 윈도우 언어와 관계없이 정상 작동합니다

## 시스템 요구사항

- Windows 10 이상 (EXE 파일 사용 시)
- Python 3.13 이상 (Python으로 실행 시)
- 인터넷 연결
- 약 500MB 이상의 디스크 공간

