@echo off
chcp 65001 > nul
cd /d "%~dp0"

title 네이버 맵 사진 다운로더 V4

echo ============================================================
echo              🗺️  네이버 맵 사진 다운로더 V4
echo ============================================================
echo.
echo 🎯 V4 핵심 개선사항:
echo    ⚡ iframe 캐싱으로 속도 3~4분 단축
echo    📸 업체 사진만 다운로드 (블로그/클립 제외)
echo    🎨 깔끔한 로그 출력
echo    🛡️  안정적인 에러 처리
echo.
echo ============================================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo.
    echo 📥 Python 설치 페이지를 여는 중...
    start https://www.python.org/downloads/
    echo.
    echo Python 설치 후 다시 실행해주세요.
    pause
    exit /b 1
)

echo ✅ Python 버전:
python --version
echo.

REM Selenium 설치 확인
python -c "import selenium" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 필수 패키지 설치 중...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 패키지 설치 실패
        pause
        exit /b 1
    )
)

echo ✅ 필수 패키지 확인 완료
echo.

REM Chrome 설치 확인
where chrome >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Chrome 브라우저가 필요합니다.
    echo    https://www.google.com/chrome/ 에서 다운로드하세요.
    echo.
)

echo ============================================================
echo 📋 엑셀 파일 선택
echo ============================================================
echo.
echo [1] 테스트_리스트.xlsx ^(3개 매장, 약 1~2분^)
echo [2] 리스트_네이버지도링크추가.xlsx ^(45개 매장, 약 15~18분^)
echo [3] 직접 입력
echo [4] 현재 폴더의 엑셀 파일 목록 보기
echo [Q] 종료
echo.
set /p choice="선택 (1/2/3/4/Q): "

if /i "%choice%"=="Q" exit /b 0
if /i "%choice%"=="q" exit /b 0

if "%choice%"=="4" (
    echo.
    echo 📂 현재 폴더: %cd%
    echo.
    echo 📋 엑셀 파일 목록:
    python -c "import os; import sys; files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]; [print(f'   - {f}') for f in files] if files else print('   엑셀 파일이 없습니다.')"
    echo.
    pause
    goto :eof
)

if "%choice%"=="1" (
    set excel_file=테스트_리스트.xlsx
) else if "%choice%"=="2" (
    set excel_file=리스트_네이버지도링크추가.xlsx
) else if "%choice%"=="3" (
    echo.
    set /p excel_file="엑셀 파일명 또는 전체 경로 입력: "
) else (
    echo ❌ 잘못된 선택입니다.
    pause
    exit /b 1
)

REM 파일 존재 확인 (Python으로 UTF-8 처리)
python -c "import os; import sys; sys.exit(0 if os.path.exists(r'%excel_file%') else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ 파일을 찾을 수 없습니다: %excel_file%
    echo.
    echo 📂 현재 폴더: %cd%
    echo.
    echo 📋 현재 폴더의 엑셀 파일:
    python -c "import os; files = [f for f in os.listdir('.') if f.endswith(('.xlsx', '.xls'))]; [print(f'   - {f}') for f in files] if files else print('   파일 없음')"
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 🚀 V4 다운로더 시작
echo ============================================================
echo 📄 엑셀 파일: %excel_file%
echo 💾 저장 위치: 현재 경로의 downloads 폴더
echo ⚡ 캐싱: 2번째 매장부터 자동 가속
echo 📸 대상: 업체 사진만
echo.
echo ⏳ 처리 중... ^(Chrome 창에서 진행 상황 확인 가능^)
echo.

REM V4 스크립트 실행
python naver_map_bulk_downloader_v4.py "%excel_file%"

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo ✅ 다운로드 완료!
    echo ============================================================
    echo.
    set /p open_folder="📁 결과 폴더를 열까요? (Y/N): "
    if /i "!open_folder!"=="Y" (
        start "" "%cd%\downloads"
    )
) else (
    echo.
    echo ============================================================
    echo ❌ 오류가 발생했습니다
    echo ============================================================
    echo.
)

pause
