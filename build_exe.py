"""
EXE 파일 생성 스크립트
PyInstaller를 사용하여 Windows에서 실행 가능한 독립 실행 파일을 생성합니다.
"""

import subprocess
import sys

def build_exe():
    """PyInstaller를 사용하여 EXE 파일 생성"""

    print("=" * 60)
    print("윈도우 EXE 파일 생성 시작")
    print("=" * 60)

    # PyInstaller 명령어 설정
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=HansomangAutomation",  # EXE 파일 이름
        "--onefile",  # 단일 실행 파일로 생성
        "--windowed",  # 콘솔 창 숨김 (GUI 앱)
        "--add-data=.venv/Lib/site-packages/customtkinter;customtkinter",  # customtkinter 데이터 포함
        "--hidden-import=customtkinter",
        "--hidden-import=playwright",
        "--hidden-import=playwright.sync_api",
        "--collect-all=customtkinter",
        "--collect-all=playwright",
        "--icon=NONE",  # 아이콘이 있으면 경로 지정
        "gui_app.py"
    ]

    print("\n실행 명령어:")
    print(" ".join(command))
    print("\n")

    try:
        # PyInstaller 실행
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)

        print("\n" + "=" * 60)
        print("✓ EXE 파일 생성 완료!")
        print("=" * 60)
        print("\n생성된 파일 위치: dist/HansomangAutomation.exe")
        print("\n주의사항:")
        print("1. Playwright를 처음 사용하는 경우, 브라우저 설치가 필요합니다.")
        print("2. EXE 파일을 배포할 때 함께 제공할 setup_playwright.bat 파일을 실행해야 합니다.")

    except subprocess.CalledProcessError as e:
        print("\n✗ 오류 발생:")
        print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 예상치 못한 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()


