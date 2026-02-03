@echo off
chcp 65001 > nul
title 네이버 맵 사진 다운로더 V2

REM 배치 파일이 있는 디렉토리로 이동
cd /d "%~dp0"

echo ============================================================
echo    네이버 맵 대량 사진 다운로더 V2 (개선 버전)
echo ============================================================
echo.
echo 💡 개선사항:
echo    - 사진 클릭하여 원본 이미지 다운로드
echo    - 카테고리별 분류 개선
echo    - 현재 디렉토리 문제 수정
echo.

REM Python 설치 확인
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python이 설치되지 않았거나 PATH에 등록되지 않았습니다.
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
    echo ⚠️  패키지를 설치합니다...
    pip install -r requirements.txt
)
echo ✅ 필수 패키지 설치됨
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
python -c "import os, sys; sys.exit(0 if os.path.exists('%excel_file%') else 1)"
if %errorlevel% neq 0 (
    echo.
    echo ❌ 파일을 찾을 수 없습니다: %excel_file%
    echo.
    echo 📋 현재 폴더의 엑셀 파일 목록:
    python -c "import os; files = [f for f in os.listdir('.') if f.endswith('.xlsx')]; print('\n'.join(f'  - {f}' for f in files) if files else '  (엑셀 파일 없음)')"
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo 🚀 다운로더 시작 (개선 버전)
echo ============================================================
echo 📊 엑셀 파일: %excel_file%
echo 📁 저장 위치: %CD%\downloads
echo.
echo ⏳ 진행 중... (Ctrl+C로 중단 가능)
echo.

REM 개선된 버전 실행
python naver_map_bulk_downloader_v2.py "%excel_file%"

REM 결과 확인
if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo ✅ 다운로드 완료!
    echo ============================================================
    echo 📁 저장 위치: %CD%\downloads
    echo.
    
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
