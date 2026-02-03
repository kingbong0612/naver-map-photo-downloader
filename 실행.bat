@echo off
chcp 65001 > nul
title 네이버 맵 사진 다운로더

echo ============================================================
echo    네이버 맵 대량 사진 다운로더 (Windows)
echo ============================================================
echo.

REM Python 설치 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았거나 PATH에 등록되지 않았습니다.
    echo.
    echo 해결 방법:
    echo 1. https://www.python.org/downloads/ 에서 Python 다운로드
    echo 2. 설치 시 "Add Python to PATH" 체크
    echo 3. 설치 후 명령 프롬프트 재시작
    echo.
    pause
    exit /b 1
)

echo ✅ Python 설치 확인: 
python --version
echo.

REM 필수 패키지 확인
echo 🔍 필수 패키지 확인 중...
pip show selenium > nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  selenium이 설치되지 않았습니다. 설치 중...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 패키지 설치 실패!
        pause
        exit /b 1
    )
) else (
    echo ✅ 필수 패키지 설치됨
)
echo.

REM Chrome 설치 확인
echo 🔍 Chrome 브라우저 확인 중...
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome 브라우저 설치됨
) else if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
    echo ✅ Chrome 브라우저 설치됨
) else (
    echo ⚠️  Chrome 브라우저가 설치되지 않았을 수 있습니다.
    echo    https://www.google.com/chrome/ 에서 다운로드하세요.
)
echo.

REM 현재 디렉토리 출력
echo 📂 현재 작업 폴더: %CD%
echo.

REM 엑셀 파일 선택
echo 📊 엑셀 파일을 선택하세요:
echo.
echo [1] 테스트_리스트.xlsx (3개 매장, 약 2분)
echo [2] 리스트_네이버지도링크추가.xlsx (45개 매장, 약 20분)
echo [3] 직접 입력
echo [4] 현재 폴더의 엑셀 파일 목록 보기
echo [Q] 종료
echo.

set /p choice="선택 (1/2/3/4/Q): "

if /i "%choice%"=="Q" exit /b 0
if /i "%choice%"=="q" exit /b 0

if "%choice%"=="4" (
    echo.
    echo 📋 현재 폴더의 엑셀 파일 목록:
    echo.
    python -c "import os; files = [f for f in os.listdir('.') if f.endswith('.xlsx')]; print('\n'.join(f'  - {f}' for f in files) if files else '  (엑셀 파일 없음)')"
    echo.
    set /p excel_file="사용할 파일명을 입력하세요: "
    goto checkfile
)

if "%choice%"=="1" (
    set "excel_file=테스트_리스트.xlsx"
) else if "%choice%"=="2" (
    set "excel_file=리스트_네이버지도링크추가.xlsx"
) else if "%choice%"=="3" (
    set /p excel_file="엑셀 파일명을 입력하세요: "
) else (
    echo ❌ 잘못된 선택입니다.
    pause
    exit /b 1
)

:checkfile
REM 엑셀 파일 존재 확인 (Python으로 UTF-8 경로 처리)
python -c "import os, sys; sys.exit(0 if os.path.exists('%excel_file%') else 1)"
if %errorlevel% neq 0 (
    echo.
    echo ❌ 파일을 찾을 수 없습니다: %excel_file%
    echo.
    echo 📋 현재 폴더의 엑셀 파일 목록:
    python -c "import os; files = [f for f in os.listdir('.') if f.endswith('.xlsx')]; print('\n'.join(f'  - {f}' for f in files) if files else '  (엑셀 파일 없음)')"
    echo.
    echo 💡 파일이 다른 위치에 있다면:
    echo    1. 엑셀 파일을 이 폴더로 복사하거나
    echo    2. 전체 경로를 입력하세요 (예: C:\Users\user\Desktop\파일.xlsx)
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 🚀 다운로더 시작
echo ============================================================
echo 📊 엑셀 파일: %excel_file%
echo 📁 저장 위치: %CD%\downloads
echo.
echo ⏳ 진행 중... (Ctrl+C로 중단 가능)
echo.

REM 실행
python naver_map_bulk_downloader.py "%excel_file%"

REM 결과 확인
if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo ✅ 다운로드 완료!
    echo ============================================================
    echo 📁 저장 위치: %CD%\downloads
    echo.
    
    REM 폴더 열기 여부 확인
    set /p open_folder="다운로드 폴더를 열까요? (Y/N): "
    if /i "%open_folder%"=="Y" (
        if exist "downloads" (
            explorer downloads
        )
    )
) else (
    echo.
    echo ❌ 오류가 발생했습니다.
    echo.
)

echo.
pause
