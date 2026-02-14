@echo off
echo ================================================
echo Hansomang 자동화 도구 - Playwright 설정
echo ================================================
echo.
echo Playwright 브라우저를 설치합니다...
echo 이 작업은 처음 한 번만 실행하면 됩니다.
echo.

REM 현재 디렉토리에 playwright 설치
playwright install chromium

if %errorlevel% equ 0 (
    echo.
    echo ================================================
    echo 설치가 완료되었습니다!
    echo 이제 HansomangAutomation.exe를 실행할 수 있습니다.
    echo ================================================
) else (
    echo.
    echo ================================================
    echo 오류가 발생했습니다.
    echo 인터넷 연결을 확인하고 다시 시도해주세요.
    echo ================================================
)

echo.
pause

