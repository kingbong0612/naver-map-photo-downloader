#!/usr/bin/env python3
"""
네이버 맵 대량 사진 다운로더 V4 (엑셀 기반) - 완전 재작성
사용법: python naver_map_bulk_downloader_v4.py <엑셀파일경로>

V4 주요 개선사항:
1. iframe 캐싱으로 속도 대폭 향상
2. 업체 사진만 다운로드 (블로그, 클립 등 제외)
3. 깔끔한 로그 출력
4. 안정적인 에러 처리
"""

import os
import sys
import time
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import traceback
from datetime import datetime
import re

class NaverMapBulkDownloaderV4:
    def __init__(self, excel_path, base_folder="downloads"):
        self.excel_path = excel_path
        # 현재 스크립트 위치에서 downloads 폴더 생성
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_folder = os.path.join(script_dir, base_folder)
        self.driver = None
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'no_url': 0,
            'total_photos': 0
        }
        
        # 🔥 iframe 캐싱 변수
        self.cached_iframe_index = None  # None=모름, 0=메인, 1~N=iframe번호
        
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        # headless 모드 비활성화 (디버깅용)
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--lang=ko-KR')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 이미지 로드 활성화
        prefs = {
            "profile.managed_default_content_settings.images": 1,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        print("✅ Chrome 드라이버 초기화 완료\n")
        
    def read_excel(self):
        """엑셀 파일 읽기"""
        try:
            df = pd.read_excel(self.excel_path)
            print(f"📊 엑셀 파일 로드: {len(df)}개 행 발견")
            print(f"컬럼: {df.columns.tolist()}\n")
            return df
        except Exception as e:
            print(f"❌ 엑셀 파일 읽기 실패: {e}")
            sys.exit(1)
            
    def create_folder_structure(self, region, region_detail, store_name):
        """폴더 구조 생성: 지역/지역상세/매장명"""
        region = self.sanitize_filename(region)
        region_detail = self.sanitize_filename(region_detail)
        store_name = self.sanitize_filename(store_name)
        
        folder_path = os.path.join(self.base_folder, region, region_detail, store_name)
        os.makedirs(folder_path, exist_ok=True)
        return folder_path
        
    def sanitize_filename(self, name):
        """파일명에 사용할 수 없는 문자 제거"""
        if pd.isna(name):
            return "unknown"
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = str(name).replace(char, '_')
        return name.strip()
        
    def save_link_file(self, folder_path, store_name, url):
        """네이버 지도 링크를 HTML 파일로 저장"""
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{store_name} - 네이버 지도</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #03c75a;
            margin-bottom: 20px;
        }}
        .info {{
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border-left: 4px solid #03c75a;
        }}
        .link {{
            word-break: break-all;
            color: #1e88e5;
            text-decoration: none;
            font-size: 16px;
        }}
        .link:hover {{
            text-decoration: underline;
        }}
        .button {{
            display: inline-block;
            margin-top: 20px;
            padding: 12px 30px;
            background: #03c75a;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }}
        .button:hover {{
            background: #02b350;
        }}
        .timestamp {{
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📍 {store_name}</h1>
        
        <div class="info">
            <strong>네이버 지도 링크:</strong><br>
            <a href="{url}" class="link" target="_blank">{url}</a>
        </div>
        
        <a href="{url}" class="button" target="_blank">🗺️ 네이버 지도에서 보기</a>
        
        <div class="timestamp">
            다운로드 날짜: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}
        </div>
    </div>
</body>
</html>
"""
        
        link_file = os.path.join(folder_path, "네이버지도_링크.html")
        with open(link_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return link_file
        
    def extract_photos_from_url(self, url):
        """네이버 맵 URL에서 사진 추출 - V4 캐싱 버전"""
        photos = []
        photo_categories = {}
        
        try:
            print(f"   🌐 페이지 로딩 중...")
            self.driver.get(url)
            time.sleep(5)  # 충분한 로딩 시간
            
            # 🔥 캐싱 사용
            if self.cached_iframe_index is not None:
                print(f"   ⚡ [캐시 사용] iframe [{self.cached_iframe_index}]로 바로 이동")
                success = self.try_cached_iframe()
                if not success:
                    print("   ⚠️  캐시 실패 - 전체 검색으로 전환")
                    self.cached_iframe_index = None
                    return self.extract_photos_from_url(url)  # 재시도
            else:
                print(f"   🔍 [첫 검색] 사진 탭 위치 찾는 중...")
                if not self.find_photo_tab_first_time():
                    print("   ❌ 사진 탭을 찾을 수 없음")
                    return [], {}
            
            print("   ✅ 사진 탭 접근 성공!")
            time.sleep(3)  # 사진 로드 대기
            
            # 업체 카테고리만 찾기
            if self.click_company_category():
                print("   📂 업체 카테고리 선택 완료")
                time.sleep(2)
            else:
                print("   ℹ️  업체 카테고리 버튼 없음 - 전체 사진 추출")
            
            # 사진 추출
            photos = self.extract_all_visible_photos()
            if photos:
                photo_categories['업체'] = photos
            
            print(f"   ✅ 총 {len(photos)}개 사진 URL 추출 완료")
            
            # iframe에서 안전하게 나오기
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            
            return photos, photo_categories
            
        except Exception as e:
            print(f"   ❌ 사진 추출 오류: {e}")
            traceback.print_exc()
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return [], {}
    
    def try_cached_iframe(self):
        """캐시된 iframe으로 바로 이동"""
        try:
            if self.cached_iframe_index == 0:
                # 메인 페이지
                return self.click_photo_tab_simple()
            else:
                # iframe
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                if len(iframes) >= self.cached_iframe_index:
                    self.driver.switch_to.frame(iframes[self.cached_iframe_index - 1])
                    time.sleep(1)
                    return self.click_photo_tab_simple()
                else:
                    return False
        except:
            return False
    
    def find_photo_tab_first_time(self):
        """첫 번째로 사진 탭 위치 찾기 (캐싱용)"""
        # 메인 페이지 시도
        if self.click_photo_tab_simple():
            self.cached_iframe_index = 0
            print(f"   💾 [캐시 저장] 메인 페이지")
            return True
        
        # iframe 순회
        iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
        if not iframes:
            return False
        
        print(f"   📦 {len(iframes)}개 iframe 발견 - 순회 시작")
        
        for i, iframe in enumerate(iframes, 1):
            try:
                print(f"      [{i}/{len(iframes)}] 확인 중...", end=" ")
                self.driver.switch_to.frame(iframe)
                time.sleep(0.5)
                
                if self.click_photo_tab_simple():
                    self.cached_iframe_index = i
                    print(f"✅ 발견!")
                    print(f"   💾 [캐시 저장] iframe [{i}]")
                    return True
                else:
                    print("❌")
                    self.driver.switch_to.default_content()
            except Exception as e:
                print(f"⚠️ 오류")
                self.driver.switch_to.default_content()
                continue
        
        return False
    
    def click_photo_tab_simple(self):
        """사진 탭 클릭 (간단 버전)"""
        try:
            # 방법 1: XPath로 '사진' 텍스트 찾기
            elements = self.driver.find_elements(By.XPATH, "//*[text()='사진']")
            for elem in elements:
                try:
                    if elem.is_displayed() and elem.is_enabled():
                        self.driver.execute_script("arguments[0].click();", elem)
                        time.sleep(1)
                        return True
                except:
                    continue
            
            # 방법 2: 포함 검색
            elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '사진')]")
            for elem in elements:
                try:
                    if elem.is_displayed() and '사진' == elem.text.strip():
                        self.driver.execute_script("arguments[0].click();", elem)
                        time.sleep(1)
                        return True
                except:
                    continue
            
            return False
        except:
            return False
    
    def click_company_category(self):
        """업체 카테고리 버튼 클릭"""
        try:
            # '업체' 버튼 찾기
            buttons = self.driver.find_elements(By.XPATH, "//*[text()='업체']")
            for btn in buttons:
                try:
                    if btn.is_displayed():
                        self.driver.execute_script("arguments[0].click();", btn)
                        return True
                except:
                    continue
            return False
        except:
            return False
    
    def extract_all_visible_photos(self):
        """현재 보이는 모든 사진 URL 추출"""
        photos = []
        
        try:
            # 스크롤하여 모든 이미지 로드
            self.scroll_to_load_all_images()
            
            # 모든 img 태그 찾기
            all_images = self.driver.find_elements(By.TAG_NAME, "img")
            
            for img in all_images:
                try:
                    src = img.get_attribute('src')
                    
                    # 네이버 CDN 이미지만 추출
                    if src and any(domain in src for domain in ['phinf.pstatic.net', 'blogpfthumb', 'postfiles']):
                        # 원본 크기로 변환
                        original_src = self.convert_to_original_size(src)
                        
                        if original_src not in photos:
                            photos.append(original_src)
                            
                except:
                    continue
            
            # data-src 속성도 확인
            all_images_with_data_src = self.driver.find_elements(By.XPATH, "//*[@data-src]")
            for img in all_images_with_data_src:
                try:
                    src = img.get_attribute('data-src')
                    if src and any(domain in src for domain in ['phinf.pstatic.net', 'blogpfthumb', 'postfiles']):
                        original_src = self.convert_to_original_size(src)
                        if original_src not in photos:
                            photos.append(original_src)
                except:
                    continue
                        
        except Exception as e:
            print(f"      ⚠️  사진 추출 오류: {e}")
            
        return photos
    
    def scroll_to_load_all_images(self):
        """스크롤하여 모든 이미지 로드"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for i in range(10):  # 최대 10번 스크롤
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.8)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                
        except:
            pass
    
    def convert_to_original_size(self, url):
        """썸네일 URL을 원본 크기로 변환"""
        # type 파라미터 변경
        type_patterns = [
            (r'\?type=w\d+', '?type=w1200'),
            (r'\?type=m\d+', '?type=w1200'),
            (r'\?type=a\d+', '?type=w1200'),
            (r'/type=w\d+/', '/type=w1200/'),
        ]
        
        for pattern, replacement in type_patterns:
            url = re.sub(pattern, replacement, url)
        
        # 썸네일 크기 제거
        url = re.sub(r'_[0-9]+x[0-9]+', '', url)
        
        return url
    
    def download_photos(self, photos, photo_categories, folder_path, store_name):
        """사진 다운로드"""
        if not photos:
            print("   ℹ️  다운로드할 사진이 없습니다.")
            return 0
            
        downloaded_count = 0
        
        # 업체 폴더 생성
        company_folder = os.path.join(folder_path, "업체")
        os.makedirs(company_folder, exist_ok=True)
        
        print(f"   📥 다운로드 시작: {len(photos)}개")
        
        for idx, url in enumerate(photos, 1):
            try:
                response = requests.get(url, timeout=15, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://map.naver.com/'
                })
                
                if response.status_code == 200:
                    ext = '.jpg'
                    content_type = response.headers.get('Content-Type', '')
                    if 'png' in content_type:
                        ext = '.png'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    
                    filename = f"업체_{idx:03d}{ext}"
                    filepath = os.path.join(company_folder, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    downloaded_count += 1
                    
                    # 진행률 표시
                    if idx % 5 == 0 or idx == len(photos):
                        print(f"      [{idx}/{len(photos)}] 완료")
                    
            except Exception as e:
                print(f"   ⚠️  다운로드 실패 [{idx}]: {str(e)[:50]}")
        
        print(f"   ✅ {downloaded_count}개 사진 다운로드 완료")
        return downloaded_count
    
    def process_single_store(self, row_idx, row):
        """개별 매장 처리"""
        region = row.get('지역', 'unknown')
        region_detail = row.get('지역상세', 'unknown')
        store_name = row.get('매장명', 'unknown')
        naver_url = row.get('네이버지도링크', None)
        
        print(f"\n{'='*60}")
        print(f"[{row_idx + 1}/{self.stats['total']}] 처리 중: {region} > {region_detail} > {store_name}")
        print(f"{'='*60}")
        
        if pd.isna(naver_url) or not naver_url:
            print("   ⚠️  네이버 지도 링크가 없습니다. 건너뜁니다.")
            self.stats['no_url'] += 1
            return
        
        try:
            folder_path = self.create_folder_structure(region, region_detail, store_name)
            print(f"   📁 폴더: {folder_path}")
            
            link_file = self.save_link_file(folder_path, store_name, naver_url)
            print(f"   🔗 링크 저장: {os.path.basename(link_file)}")
            
            photos, photo_categories = self.extract_photos_from_url(naver_url)
            
            if photos:
                downloaded = self.download_photos(photos, photo_categories, folder_path, store_name)
                self.stats['total_photos'] += downloaded
                self.stats['success'] += 1
            else:
                print("   ℹ️  사진을 찾을 수 없습니다.")
                self.stats['success'] += 1
                
        except Exception as e:
            print(f"   ❌ 처리 실패: {e}")
            traceback.print_exc()
            self.stats['failed'] += 1
    
    def run(self):
        """전체 프로세스 실행"""
        start_time = time.time()
        
        print("\n" + "="*60)
        print("🚀 네이버 맵 대량 사진 다운로더 V4 시작")
        print("="*60 + "\n")
        
        df = self.read_excel()
        self.stats['total'] = len(df)
        
        self.setup_driver()
        
        try:
            for idx, row in df.iterrows():
                self.process_single_store(idx, row)
                
                progress = (idx + 1) / len(df) * 100
                print(f"\n📊 진행률: {progress:.1f}% ({idx + 1}/{len(df)})")
                
                if (idx + 1) % 5 == 0:
                    print("   ⏳ 5개 처리마다 3초 대기 중...")
                    time.sleep(3)
                    
        except KeyboardInterrupt:
            print("\n\n⚠️  사용자에 의해 중단되었습니다.")
            
        finally:
            if self.driver:
                self.driver.quit()
                
        elapsed_time = time.time() - start_time
        self.print_final_stats(elapsed_time)
    
    def print_final_stats(self, elapsed_time):
        """최종 통계 출력"""
        print("\n" + "="*60)
        print("📊 최종 통계")
        print("="*60)
        print(f"총 처리 대상: {self.stats['total']}개")
        print(f"✅ 성공: {self.stats['success']}개")
        print(f"❌ 실패: {self.stats['failed']}개")
        print(f"⚠️  링크 없음: {self.stats['no_url']}개")
        print(f"📷 다운로드한 총 사진 수: {self.stats['total_photos']}개")
        print(f"⏱️  소요 시간: {elapsed_time/60:.1f}분")
        print(f"📁 저장 위치: {os.path.abspath(self.base_folder)}")
        print("="*60 + "\n")

def main():
    if len(sys.argv) < 2:
        print("사용법: python naver_map_bulk_downloader_v4.py <엑셀파일경로>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    if not os.path.exists(excel_path):
        print(f"❌ 파일을 찾을 수 없습니다: {excel_path}")
        sys.exit(1)
    
    downloader = NaverMapBulkDownloaderV4(excel_path)
    downloader.run()

if __name__ == "__main__":
    main()
