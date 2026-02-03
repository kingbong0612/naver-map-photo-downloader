#!/bin/bash

# 네이버 맵 대량 다운로더 실행 스크립트

echo "======================================"
echo "네이버 맵 대량 사진 다운로더"
echo "======================================"
echo ""

# 엑셀 파일 확인
EXCEL_FILE="리스트_네이버지도링크추가.xlsx"

if [ -f "uploaded_files/$EXCEL_FILE" ]; then
    EXCEL_PATH="uploaded_files/$EXCEL_FILE"
elif [ -f "$EXCEL_FILE" ]; then
    EXCEL_PATH="$EXCEL_FILE"
else
    echo "❌ 엑셀 파일을 찾을 수 없습니다: $EXCEL_FILE"
    echo ""
    echo "사용법:"
    echo "  ./run_bulk_downloader.sh"
    echo "  또는"
    echo "  python naver_map_bulk_downloader.py <엑셀파일경로>"
    exit 1
fi

echo "📊 엑셀 파일: $EXCEL_PATH"
echo ""

# 필수 패키지 확인
echo "🔍 필수 패키지 확인 중..."
pip list | grep -q selenium
if [ $? -ne 0 ]; then
    echo "⚠️  selenium이 설치되지 않았습니다. 설치 중..."
    pip install -r requirements.txt -q
fi

echo "✅ 패키지 확인 완료"
echo ""

# Chrome 확인
echo "🔍 Chrome 브라우저 확인 중..."
if command -v google-chrome &> /dev/null; then
    CHROME_VERSION=$(google-chrome --version)
    echo "✅ Chrome 설치됨: $CHROME_VERSION"
elif command -v chromium-browser &> /dev/null; then
    CHROME_VERSION=$(chromium-browser --version)
    echo "✅ Chromium 설치됨: $CHROME_VERSION"
else
    echo "⚠️  Chrome/Chromium이 설치되지 않았습니다."
    echo "   설치 방법:"
    echo "   Ubuntu: sudo apt-get install chromium-browser"
    echo "   macOS: brew install --cask google-chrome"
fi
echo ""

# 실행
echo "🚀 다운로더 시작..."
echo "   (진행 중 Ctrl+C로 중단 가능)"
echo ""

python3 naver_map_bulk_downloader.py "$EXCEL_PATH"

# 결과 확인
if [ -d "downloads" ]; then
    echo ""
    echo "======================================"
    echo "📁 다운로드 완료!"
    echo "======================================"
    echo "저장 위치: $(pwd)/downloads"
    echo ""
    echo "폴더 구조:"
    tree downloads -L 3 2>/dev/null || find downloads -type d | head -20
fi
