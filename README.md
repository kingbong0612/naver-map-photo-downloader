# 🗺️ 네이버 맵 사진 대량 다운로더

엑셀 파일 기반으로 네이버 지도의 여러 장소에서 사진을 자동으로 다운로드하는 Python 도구입니다.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-4.15+-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

## ✨ 주요 기능

- ✅ **엑셀 기반 대량 처리**: 여러 매장을 한 번에 처리
- ✅ **체계적인 폴더 구조**: `지역/지역상세/매장명` 3단계 자동 생성
- ✅ **카테고리별 분류**: 업체사진, 외부, 내부 등 자동 분류
- ✅ **크로스체크 링크**: 각 매장 폴더에 HTML 링크 파일 생성
- ✅ **고화질 원본**: 썸네일이 아닌 원본 크기 다운로드
- ✅ **진행률 표시**: 실시간 처리 현황 확인
- ✅ **Windows 최적화**: 배치 파일로 더블클릭만으로 실행

## 📂 폴더 구조

```
downloads/
└── 서울/
    └── 중구/
        ├── 온아2호/
        │   ├── 네이버지도_링크.html  ← 크로스체크용
        │   ├── 업체사진/
        │   │   ├── 업체사진_001.jpg
        │   │   └── 업체사진_002.jpg
        │   ├── 외부/
        │   │   └── 외부_001.jpg
        │   └── 내부/
        │       └── 내부_001.jpg
        ├── 라힌/
        └── 수련/
```

## 🚀 빠른 시작

### Windows 사용자 (권장)

1. **파일 다운로드**
   ```bash
   git clone https://github.com/kingbong0612/naver-map-photo-downloader.git
   cd naver-map-photo-downloader
   ```

2. **설치**
   - `설치.bat` 더블클릭

3. **실행**
   - `실행.bat` 더블클릭
   - 메뉴에서 선택 후 Enter

### Linux / macOS 사용자

```bash
# 1. 저장소 클론
git clone https://github.com/kingbong0612/naver-map-photo-downloader.git
cd naver-map-photo-downloader

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 실행 (쉘 스크립트)
./run_bulk_downloader.sh

# 또는 직접 실행
python naver_map_bulk_downloader.py 엑셀파일.xlsx
```

## 📋 엑셀 파일 형식

| 지역 | 지역상세 | 매장명 | 네이버지도링크 |
|------|---------|--------|---------------|
| 서울 | 중구 | 온아2호 | https://naver.me/FfB3j16z |
| 서울 | 중구 | 라힌 | https://naver.me/xt4x64Wj |

**필수 컬럼:**
- `지역`: 대분류 지역
- `지역상세`: 소분류 지역
- `매장명`: 매장/업체 이름
- `네이버지도링크`: 네이버 지도 URL

## 📦 설치 요구사항

- **Python**: 3.8 이상
- **Chrome**: 최신 버전
- **인터넷 연결**: 필수

### Python 패키지
```
selenium>=4.15.0
requests>=2.31.0
pandas>=2.0.0
openpyxl>=3.1.0
```

## 📖 상세 가이드

### Windows 사용자
- [Windows 빠른시작](Windows_빠른시작.md) - 초보자 필독! 🎯
- [Windows 설치가이드](Windows_설치가이드.md) - 상세 설치 방법
- [Windows 최종가이드](Windows_최종가이드.md) - 전체 요약

### 모든 사용자
- [사용가이드](사용가이드.md) - 종합 사용법 및 문제 해결
- [프로젝트 요약](프로젝트_요약.md) - 프로젝트 개요
- [대량 다운로더 README](README_BULK.md) - 대량 처리 상세

### 단일 URL 사용자
- [단일 다운로더 README](README.md) - 단일 URL 처리

## 🎯 사용 예시

### 1. 테스트 실행 (3개 매장)
```bash
python naver_map_bulk_downloader.py 테스트_리스트.xlsx
```

### 2. 전체 실행
```bash
python naver_map_bulk_downloader.py 리스트_네이버지도링크추가.xlsx
```

### 3. Windows 배치 파일
```
실행.bat 더블클릭 → "2" 입력 → Enter
```

## 📊 예상 결과

- **처리 속도**: 매장당 약 20~40초
- **총 소요 시간**: 45개 매장 기준 약 18~25분
- **다운로드 사진**: 매장당 평균 10~20장
- **디스크 사용**: 매장당 약 5~15MB

## 🔍 크로스체크 방법

1. 각 매장 폴더의 `네이버지도_링크.html` 파일 열기
2. "네이버 지도에서 보기" 버튼 클릭
3. 실제 네이버 지도와 다운로드된 사진 비교

## 🐛 문제 해결

### Chrome 드라이버 오류
```bash
# Chrome 업데이트 확인
# Selenium 재설치
pip install --upgrade selenium
```

### 패키지 설치 실패
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 패키지 재설치
pip install -r requirements.txt --upgrade
```

### 한글 깨짐 (Windows)
```cmd
# 명령 프롬프트에서 UTF-8 설정
chcp 65001
```

자세한 문제 해결은 [사용가이드.md](사용가이드.md)를 참조하세요.

## ⚠️ 주의사항

1. **저작권**: 다운로드한 사진은 개인적인 용도로만 사용하세요
2. **서버 부하**: 과도한 요청은 IP 차단의 원인이 될 수 있습니다
3. **네트워크**: 안정적인 인터넷 연결이 필요합니다
4. **디스크 공간**: 충분한 저장 공간을 확보하세요

## 🤝 기여

버그 리포트, 기능 제안, Pull Request 환영합니다!

## 📄 라이선스

개인적인 용도로 자유롭게 사용하세요.

## 📞 지원

- 이슈 등록: [GitHub Issues](https://github.com/kingbong0612/naver-map-photo-downloader/issues)
- 문서: 프로젝트 내 각종 가이드 문서 참조

## 🎉 특징

### Windows 사용자를 위한 특별 기능
- 🖱️ **더블클릭만으로 실행**: 배치 파일 제공
- 📝 **자동 설치**: Python, 패키지, Chrome 자동 확인
- 🌐 **한글 완벽 지원**: UTF-8 인코딩 자동 설정
- 📂 **폴더 자동 열기**: 완료 후 결과 폴더 자동 열기
- ✨ **사용자 친화적**: 초보자도 쉽게 사용 가능

### 모든 사용자를 위한 기능
- 🤖 **완전 자동화**: 엑셀만 있으면 끝
- 📊 **진행률 표시**: 실시간 처리 상황 확인
- 🛡️ **에러 처리**: 안정적인 처리 및 자동 복구
- 📈 **통계 리포트**: 최종 다운로드 통계 제공
- 🔗 **크로스체크**: HTML 링크 파일로 쉬운 확인

---

**⭐ 이 프로젝트가 도움이 되셨다면 Star를 눌러주세요!**

Made with ❤️ for easier Naver Map photo downloading
