# 🪟 Windows 환경 설치 및 실행 가이드

## 📋 목차
1. [Python 설치](#1-python-설치)
2. [Chrome 설치](#2-chrome-설치)
3. [프로젝트 파일 준비](#3-프로젝트-파일-준비)
4. [패키지 설치](#4-패키지-설치)
5. [실행 방법](#5-실행-방법)
6. [Windows 전용 배치 파일](#6-windows-전용-배치-파일)

---

## 1. Python 설치

### 1-1. Python 다운로드
1. https://www.python.org/downloads/ 접속
2. **Download Python 3.11.x** (또는 최신 버전) 클릭
3. 다운로드된 설치 파일 실행

### 1-2. 설치 시 주의사항
⚠️ **매우 중요!**
- ✅ **"Add Python to PATH"** 체크박스 **반드시 선택**
- ✅ "Install Now" 클릭

### 1-3. 설치 확인
```cmd
# 명령 프롬프트(cmd) 또는 PowerShell 실행
python --version
```

출력 예시:
```
Python 3.11.7
```

---

## 2. Chrome 설치

### 2-1. Chrome 다운로드
1. https://www.google.com/chrome/ 접속
2. Chrome 다운로드 및 설치

### 2-2. 설치 확인
Chrome 브라우저가 정상적으로 실행되는지 확인

---

## 3. 프로젝트 파일 준비

### 3-1. 작업 폴더 만들기
```cmd
# 예: C:\Users\사용자명\Desktop 에 폴더 생성
cd Desktop
mkdir naver_map_downloader
cd naver_map_downloader
```

### 3-2. 필요한 파일 복사
다음 파일들을 작업 폴더에 복사:
- ✅ `naver_map_bulk_downloader.py`
- ✅ `requirements.txt`
- ✅ `리스트_네이버지도링크추가.xlsx`

---

## 4. 패키지 설치

### 4-1. 명령 프롬프트 열기
1. **Windows 키** + **R**
2. `cmd` 입력 후 **Enter**

### 4-2. 작업 폴더로 이동
```cmd
cd Desktop\naver_map_downloader
```

### 4-3. 패키지 설치
```cmd
pip install -r requirements.txt
```

설치되는 패키지:
- selenium
- requests
- pandas
- openpyxl

### 4-4. 설치 확인
```cmd
pip list | findstr selenium
pip list | findstr pandas
```

---

## 5. 실행 방법

### 방법 1: 명령 프롬프트에서 실행 (권장)

```cmd
# 작업 폴더로 이동
cd Desktop\naver_map_downloader

# 테스트 실행 (3개 매장)
python naver_map_bulk_downloader.py 테스트_리스트.xlsx

# 전체 실행 (45개 매장)
python naver_map_bulk_downloader.py 리스트_네이버지도링크추가.xlsx
```

### 방법 2: PowerShell에서 실행

```powershell
# 작업 폴더로 이동
cd Desktop\naver_map_downloader

# 실행
python naver_map_bulk_downloader.py 리스트_네이버지도링크추가.xlsx
```

### 방법 3: Windows 배치 파일 사용 (가장 쉬움!)

아래에서 설명할 `실행.bat` 파일을 더블클릭!

---

## 6. Windows 전용 배치 파일

### 6-1. 실행.bat 파일 사용

`실행.bat` 파일을 더블클릭하면 자동으로 실행됩니다.

**사용법:**
1. `실행.bat` 파일 더블클릭
2. 엑셀 파일명 입력 (예: `리스트_네이버지도링크추가.xlsx`)
3. 자동 실행 완료!

---

## 📊 실행 화면 예시

```
============================================================
🚀 네이버 맵 대량 사진 다운로더 시작
============================================================

📊 엑셀 파일 로드: 45개 행 발견
✅ Chrome 드라이버 초기화 완료

============================================================
[1/45] 처리 중: 서울 > 중구 > 온아2호
============================================================
   📁 폴더 생성: downloads\서울\중구\온아2호
   🔗 링크 파일 저장: 네이버지도_링크.html
   🌐 페이지 로딩: https://naver.me/FfB3j16z
   📷 사진 탭 클릭 완료
   📂 발견된 카테고리: 업체사진, 외부, 내부
   ✅ 총 24개 사진 URL 추출 완료
   📁 카테고리: 업체사진 (12개)
   📁 카테고리: 외부 (8개)
   📁 카테고리: 내부 (4개)
   ✅ 24개 사진 다운로드 완료

📊 진행률: 2.2% (1/45)
```

---

## 📁 생성되는 폴더 (Windows)

```
C:\Users\사용자명\Desktop\naver_map_downloader\
├── downloads\
│   └── 서울\
│       └── 중구\
│           ├── 온아2호\
│           │   ├── 네이버지도_링크.html
│           │   ├── 업체사진\
│           │   │   ├── 업체사진_001.jpg
│           │   │   └── 업체사진_002.jpg
│           │   ├── 외부\
│           │   │   └── 외부_001.jpg
│           │   └── 내부\
│           │       └── 내부_001.jpg
│           ├── 라힌\
│           └── 수련\
```

---

## 🐛 Windows 환경 문제 해결

### ❌ Python을 찾을 수 없다는 오류

**증상:**
```
'python'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

**해결:**
1. Python 재설치
2. **"Add Python to PATH"** 체크 확인
3. 명령 프롬프트 재시작

또는 Microsoft Store에서 Python 설치:
```cmd
# Microsoft Store 앱 열기
ms-windows-store://pdp/?ProductId=9NRWMJP3717K
```

### ❌ pip를 찾을 수 없다는 오류

**해결:**
```cmd
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### ❌ Chrome 드라이버 오류

**증상:**
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```

**해결:**
1. Chrome 브라우저가 설치되어 있는지 확인
2. Chrome 업데이트 확인
3. 다음 명령어 실행:
```cmd
pip install --upgrade selenium
```

### ❌ 한글 파일명 오류

**증상:**
```
UnicodeEncodeError: 'ascii' codec can't encode characters
```

**해결:**
명령 프롬프트에서 코드 페이지 변경:
```cmd
chcp 65001
```

### ❌ 권한 오류

**증상:**
```
PermissionError: [WinError 32]
```

**해결:**
1. 관리자 권한으로 명령 프롬프트 실행
   - **시작** 메뉴에서 `cmd` 검색
   - **마우스 오른쪽 클릭** → **관리자 권한으로 실행**

2. 또는 다른 폴더(예: `C:\naver_map`)에서 실행

---

## 💡 Windows 팁

### 1. 명령 프롬프트 빠른 열기
- 작업 폴더에서 **Shift** + **마우스 오른쪽 클릭**
- **"여기에 PowerShell 창 열기"** 또는 **"명령 창 여기에 열기"** 선택

### 2. 경로 복사
- 폴더 주소창 클릭 → **Ctrl + C**
- 명령 프롬프트에서 **마우스 오른쪽 클릭** → 붙여넣기

### 3. 실행 중 중단
- **Ctrl + C** 키 누르기

### 4. 결과 폴더 빠른 열기
- 명령 프롬프트에서:
```cmd
explorer downloads
```

---

## ⏱️ 예상 소요 시간 (Windows)

- **3개 매장 테스트**: 약 2~3분
- **45개 매장 전체**: 약 20~30분
- **100개 매장**: 약 45~60분

*PC 성능과 인터넷 속도에 따라 다를 수 있습니다.*

---

## 🎯 빠른 시작 체크리스트

- [ ] Python 설치 (PATH 추가 확인)
- [ ] Chrome 설치
- [ ] 작업 폴더 생성
- [ ] 파일 복사 (py, txt, xlsx)
- [ ] `pip install -r requirements.txt` 실행
- [ ] `실행.bat` 더블클릭 또는 명령 프롬프트에서 실행

---

## 📞 도움이 필요하면

1. 오류 메시지 전체 복사
2. Python 버전 확인: `python --version`
3. pip 버전 확인: `pip --version`
4. Chrome 버전 확인: Chrome 설정 → 정보

---

**Windows 사용자를 위한 가이드였습니다!** 🪟✨
