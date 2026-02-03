@echo off
chcp 65001 > nul
title 네이버 맵 다운로더 설치

echo ============================================================
echo    네이버 맵 다운로더 설치 프로그램
echo ============================================================
echo.

REM Python 확인
echo [1/3] Python 설치 확인 중...
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았습니다.
    echo.
    echo Python을 설치해야 합니다:
    echo 1. https://www.python.org/downloads/ 방문
    echo 2. "Download Python" 버튼 클릭
    echo 3. 설치 시 "Add Python to PATH" 체크 필수!
    echo.
    echo 설치 후 이 창을 닫고 다시 실행하세요.
    echo.
    
    set /p open_browser="Python 다운로드 페이지를 열까요? (Y/N): "
    if /i "%open_browser%"=="Y" (
        start https://www.python.org/downloads/
    )
    
    pause
    exit /b 1
) else (
    echo ✅ Python 설치 확인 완료
    python --version
    echo.
)

REM pip 업그레이드
echo [2/3] pip 업그레이드 중...
python -m pip install --upgrade pip --quiet
if %errorlevel% equ 0 (
    echo ✅ pip 업그레이드 완료
) else (
    echo ⚠️  pip 업그레이드 실패 (계속 진행)
)
echo.

REM 패키지 설치
echo [3/3] 필수 패키지 설치 중...
echo    - selenium (웹 자동화)
echo    - requests (HTTP 요청)
echo    - pandas (엑셀 처리)
echo    - openpyxl (엑셀 파일 읽기)
echo.

if not exist "requirements.txt" (
    echo requirements.txt 파일이 없습니다. 직접 생성합니다...
    (
        echo selenium^>=4.15.0
        echo requests^>=2.31.0
        echo pandas^>=2.0.0
        echo openpyxl^>=3.1.0
    ) > requirements.txt
)

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ❌ 패키지 설치 실패!
    echo.
    echo 해결 방법:
    echo 1. 인터넷 연결 확인
    echo 2. 관리자 권한으로 실행
    echo 3. 방화벽 설정 확인
    echo.
    pause
    exit /b 1
)

echo.
echo ✅ 모든 패키지 설치 완료!
echo.

REM Chrome 확인
echo ============================================================
echo 📌 Chrome 브라우저 확인
echo ============================================================
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome 브라우저가 설치되어 있습니다.
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome 브라우저가 설치되어 있습니다.
) else (
    echo ⚠️  Chrome 브라우저가 설치되지 않았을 수 있습니다.
    echo.
    echo Chrome을 설치해야 합니다:
    echo https://www.google.com/chrome/
    echo.
    
    set /p open_chrome="Chrome 다운로드 페이지를 열까요? (Y/N): "
    if /i "%open_chrome%"=="Y" (
        start https://www.google.com/chrome/
    )
)
echo.

REM 설치 완료
echo ============================================================
echo 🎉 설치 완료!
echo ============================================================
echo.
echo 이제 다음 방법으로 실행할 수 있습니다:
echo.
echo 방법 1: 실행.bat 파일을 더블클릭
echo 방법 2: 명령 프롬프트에서
echo         python naver_map_bulk_downloader.py 엑셀파일.xlsx
echo.

REM 설치된 패키지 확인
echo 설치된 패키지 목록:
pip list | findstr "selenium requests pandas openpyxl"
echo.

REM 실행 여부 확인
set /p run_now="지금 바로 실행하시겠습니까? (Y/N): "
if /i "%run_now%"=="Y" (
    echo.
    call 실행.bat
) else (
    echo.
    echo 나중에 "실행.bat" 파일을 더블클릭하여 실행하세요.
    echo.
    pause
)
