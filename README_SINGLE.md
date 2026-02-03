# 네이버 맵 사진 다운로더

네이버 맵의 특정 장소에 등록된 사진들을 자동으로 다운로드하는 Python 스크립트입니다.

## 기능

- 네이버 맵 단축 URL (naver.me) 지원
- 자동으로 사진 탭 찾기 및 스크롤
- 원본 고화질 이미지 다운로드
- 다운로드한 사진 URL 목록 저장

## 설치 방법

### 1. Python 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. Chrome 및 ChromeDriver 설치

#### Ubuntu/Debian:
```bash
# Chrome 설치
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

# ChromeDriver는 selenium-manager가 자동으로 처리
```

#### macOS:
```bash
brew install --cask google-chrome
# ChromeDriver는 selenium-manager가 자동으로 처리
```

#### Windows:
- Chrome 브라우저 다운로드 및 설치: https://www.google.com/chrome/
- ChromeDriver는 selenium-manager가 자동으로 처리

## 사용 방법

```bash
python naver_map_photo_downloader.py <네이버맵 URL>
```

### 예시

```bash
python naver_map_photo_downloader.py https://naver.me/FfB3j16z
```

또는 전체 URL:

```bash
python naver_map_photo_downloader.py "https://map.naver.com/p/entry/place/1234567890"
```

## 실행 결과

- `naver_map_photos/` 폴더에 사진들이 다운로드됩니다
- `photo_urls.txt` 파일에 다운로드한 사진 URL 목록이 저장됩니다

## 주의사항

1. **저작권**: 다운로드한 사진은 개인적인 용도로만 사용하세요
2. **속도 제한**: 과도한 요청은 IP 차단의 원인이 될 수 있습니다
3. **네트워크**: 안정적인 인터넷 연결이 필요합니다

## 문제 해결

### ChromeDriver 오류
- Selenium 4.6 이상 버전은 자동으로 ChromeDriver를 관리합니다
- Chrome 브라우저가 설치되어 있는지 확인하세요

### 사진을 찾을 수 없는 경우
- 해당 장소에 등록된 사진이 있는지 확인하세요
- 네이버 맵 페이지 구조가 변경되었을 수 있습니다

### 다운로드 실패
- 인터넷 연결을 확인하세요
- 방화벽이나 프록시 설정을 확인하세요

## 라이선스

개인적인 용도로 자유롭게 사용하세요.
