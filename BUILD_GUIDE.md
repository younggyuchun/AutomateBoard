# Hansomang 자동화 도구 - EXE 빌드 가이드

## EXE 파일 생성 방법

### 1. PyInstaller 설치
```bash
pip install pyinstaller
```

### 2. EXE 파일 빌드

#### 방법 A: spec 파일 사용 (권장)
```bash
pyinstaller HansomangAutomation.spec
```

#### 방법 B: 빌드 스크립트 사용
```bash
python build_exe.py
```

#### 방법 C: 직접 명령어 실행
```bash
pyinstaller --name=HansomangAutomation --onefile --windowed --collect-all=customtkinter --collect-all=playwright --hidden-import=customtkinter --hidden-import=playwright --hidden-import=playwright.sync_api gui_app.py
```

### 3. 생성된 파일 확인
- `dist/HansomangAutomation.exe` 파일이 생성됩니다.

## 윈도우에서 배포하기

### 배포 패키지 구성
1. **HansomangAutomation.exe** - 메인 실행 파일
2. **setup_playwright.bat** - Playwright 브라우저 설치 스크립트
3. **사용설명서.txt** (선택사항)

### 사용자 설치 방법

#### 처음 사용 시 (최초 1회만)
1. `setup_playwright.bat` 파일을 실행합니다.
2. 크로미움 브라우저가 자동으로 다운로드되고 설치됩니다.
3. 설치가 완료되면 창을 닫습니다.

#### 프로그램 실행
- `HansomangAutomation.exe` 파일을 더블클릭하여 실행합니다.

## 주의사항

### Playwright 브라우저 설치
- EXE 파일 자체에는 Playwright 브라우저가 포함되지 않습니다.
- 처음 사용하는 컴퓨터에서는 반드시 `setup_playwright.bat`를 실행해야 합니다.
- 인터넷 연결이 필요합니다 (약 100-200MB 다운로드).

### 시스템 요구사항
- Windows 10 이상
- 인터넷 연결 (Playwright 설치 및 웹사이트 접속)
- 약 500MB 이상의 디스크 공간

### 알려진 제한사항
1. **백신 프로그램 경고**: 일부 백신 프로그램에서 PyInstaller로 만든 EXE 파일을 의심할 수 있습니다.
   - 해결방법: 백신 프로그램의 예외 목록에 추가
   
2. **첫 실행 시간**: EXE 파일 압축 해제로 인해 첫 실행이 느릴 수 있습니다.
   - 정상적인 현상이며, 두 번째 실행부터는 빠릅니다.

3. **파일 크기**: 단일 EXE 파일은 약 100-200MB 정도 됩니다.
   - 모든 라이브러리가 포함되어 있기 때문입니다.

## 대안: Playwright 브라우저 포함 배포

더 복잡하지만 브라우저까지 포함한 배포를 원한다면:

```bash
# Playwright 브라우저를 프로젝트 폴더에 다운로드
set PLAYWRIGHT_BROWSERS_PATH=%CD%\browsers
playwright install chromium

# 브라우저 포함하여 빌드
pyinstaller --add-data "browsers;browsers" HansomangAutomation.spec
```

단점: 파일 크기가 500MB 이상으로 증가합니다.

## 트러블슈팅

### EXE 실행 시 오류 발생
1. Windows Defender 또는 백신 프로그램 확인
2. 관리자 권한으로 실행
3. `setup_playwright.bat` 재실행

### Playwright 오류
```
Error: Executable doesn't exist at ...
```
- 해결: `setup_playwright.bat` 실행

### customtkinter 테마 오류
- spec 파일의 datas 설정이 올바른지 확인
- 빌드 재시도

## 문의
문제가 발생하면 로그를 확인하고 필요시 개발자에게 문의하세요.

