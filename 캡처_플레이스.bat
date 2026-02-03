@echo off
chcp 65001 > nul
cd /d "%~dp0"

title 네이버 플레이스 캡처 도구

echo ============================================================
echo           📸 네이버 플레이스 캡처 도구
echo ============================================================
echo.
echo 🎯 기능:
echo    - 네이버 검색으로 매장 찾기
echo    - 플레이스 카드 영역 자동 캡처
echo    - 각 매장의 업체 폴더에 저장
echo.
echo 📋 사용 순서:
echo    1단계: 실행_V4.bat (사진 다운로드)
echo    2단계: 캡처_플레이스.bat (플레이스 캡처) ← 지금 여기
echo.
echo ============================================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo.
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

echo ============================================================
echo 📋 엑셀 파일 선택
echo ============================================================
echo.
echo [1] 테스트_리스트.xlsx ^(3개 매장^)
echo [2] 리스트_네이버지도링크추가.xlsx ^(45개 매장^)
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

REM 파일 존재 확인
python -c "import os; import sys; sys.exit(0 if os.path.exists(r'%excel_file%') else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ❌ 파일을 찾을 수 없습니다: %excel_file%
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 📸 캡처 시작
echo ============================================================
echo 📄 엑셀 파일: %excel_file%
echo 💾 저장 위치: downloads/지역/지역상세/매장명/업체/
echo 📝 파일명: 네이버플레이스_캡처.png
echo.
echo ⏳ 처리 중... ^(Chrome 창에서 진행 상황 확인 가능^)
echo.

REM 캡처 스크립트 실행
python capture_naver_place.py "%excel_file%"

if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo ✅ 캡처 완료!
    echo ============================================================
    echo.
    echo 📁 결과 확인: downloads 폴더
    echo 📝 파일명: 네이버플레이스_캡처.png
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
    echo 💡 문제 해결:
    echo    - 먼저 실행_V4.bat을 실행하여 폴더를 생성하세요
    echo    - Chrome 브라우저가 설치되어 있는지 확인하세요
    echo    - 인터넷 연결을 확인하세요
    echo.
)

pause
