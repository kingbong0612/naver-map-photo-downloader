#!/usr/bin/env python3
"""
네이버 맵 대량 사진 다운로더 (엑셀 기반) - 개선 버전
사용법: python naver_map_bulk_downloader_v2.py <엑셀파일경로>
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
import traceback
from datetime import datetime

class NaverMapBulkDownloaderV2:
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
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
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
        """네이버 맵 URL에서 사진 추출 - 개선된 버전"""
        photos = []
        photo_categories = {}
        
        try:
            print(f"   🌐 페이지 로딩: {url}")
            self.driver.get(url)
            time.sleep(4)  # 페이지 완전히 로드될 때까지 대기
            
            # 사진 탭 클릭
            if not self.click_photo_tab():
                print("   ⚠️  사진 탭을 찾을 수 없음")
                return [], {}
            
            time.sleep(3)  # 사진 로드 대기
            
            # 원형 카테고리 버튼 찾기 (업체, 클립, 방문자, 블로그 등)
            categories = self.find_circle_categories()
            
            if categories:
                print(f"   📂 발견된 카테고리: {', '.join(categories)}")
                
                for category in categories:
                    print(f"   🔍 '{category}' 카테고리 처리 중...")
                    category_photos = self.extract_photos_from_category(category)
                    if category_photos:
                        photo_categories[category] = category_photos
                        photos.extend(category_photos)
                        print(f"      ✅ {len(category_photos)}개 발견")
            else:
                # 카테고리가 없으면 전체 사진 추출
                print("   📸 전체 사진 추출 중...")
                photos = self.extract_all_photos_new_method()
                if photos:
                    photo_categories['전체사진'] = photos
            
            # 중복 제거
            photos = list(dict.fromkeys(photos))
            
            print(f"   ✅ 총 {len(photos)}개 사진 URL 추출 완료")
            
            return photos, photo_categories
            
        except Exception as e:
            print(f"   ❌ 사진 추출 오류: {e}")
            traceback.print_exc()
            return [], {}
    
    def click_photo_tab(self):
        """사진 탭 클릭"""
        photo_tab_selectors = [
            "//a[contains(@class, 'tab') and contains(., '사진')]",
            "//button[contains(@class, 'tab') and contains(., '사진')]",
            "//a[contains(text(), '사진')]",
            "//span[contains(text(), '사진')]/parent::a",
            "//*[@role='tab' and contains(., '사진')]"
        ]
        
        for selector in photo_tab_selectors:
            try:
                photo_tab = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                photo_tab.click()
                print("   📷 사진 탭 클릭 완료")
                return True
            except:
                continue
        
        return False
    
    def find_circle_categories(self):
        """원형 카테고리 버튼 찾기 (업체, 클립, 방문자, 블로그)"""
        categories = []
        
        try:
            # 다양한 카테고리 선택자 시도
            category_selectors = [
                "//div[contains(@class, 'flick')]//span[contains(@class, 'text')]",
                "//div[contains(@class, 'category')]//button",
                "//a[contains(@class, 'item') and contains(@class, 'photo')]",
                "//div[contains(@class, 'photo_category')]//span"
            ]
            
            for selector in category_selectors:
                try:
                    elements = self.driver.find_elements(By.XPATH, selector)
                    if elements:
                        for elem in elements:
                            text = elem.text.strip()
                            if text and text not in categories and text not in ['사진', 'Photo', '전체']:
                                categories.append(text)
                except:
                    continue
                    
            return list(dict.fromkeys(categories))[:10]  # 최대 10개
            
        except Exception as e:
            print(f"   ⚠️  카테고리 찾기 오류: {e}")
            return []
    
    def extract_photos_from_category(self, category):
        """특정 카테고리의 사진 추출"""
        photos = []
        
        try:
            # 카테고리 버튼 클릭
            category_button_selectors = [
                f"//div[contains(@class, 'flick')]//span[contains(text(), '{category}')]/parent::*",
                f"//button[contains(text(), '{category}')]",
                f"//a[contains(text(), '{category}')]"
            ]
            
            clicked = False
            for selector in category_button_selectors:
                try:
                    button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    button.click()
                    time.sleep(2)
                    clicked = True
                    break
                except:
                    continue
            
            if not clicked:
                print(f"      ⚠️ '{category}' 버튼 클릭 실패")
                return []
            
            # 사진 추출
            photos = self.extract_all_photos_new_method()
            
        except Exception as e:
            print(f"      ⚠️ '{category}' 추출 오류: {e}")
            
        return photos
    
    def extract_all_photos_new_method(self):
        """새로운 방식으로 모든 사진 추출 - 클릭하여 원본 가져오기"""
        photos = []
        
        try:
            # 스크롤하여 썸네일 모두 로드
            self.scroll_photo_area()
            
            # 썸네일 클릭 가능한 요소 찾기
            thumbnail_selectors = [
                "//div[contains(@class, 'photo')]//img",
                "//a[contains(@class, 'thumb')]//img",
                "//li[contains(@class, 'item')]//img[@src]"
            ]
            
            thumbnails = []
            for selector in thumbnail_selectors:
                try:
                    elems = self.driver.find_elements(By.XPATH, selector)
                    if elems:
                        thumbnails = elems
                        break
                except:
                    continue
            
            print(f"      📸 {len(thumbnails)}개 썸네일 발견")
            
            # 각 썸네일 클릭하여 원본 이미지 URL 가져오기
            for idx, thumb in enumerate(thumbnails[:50], 1):  # 최대 50개
                try:
                    # 썸네일 클릭
                    ActionChains(self.driver).move_to_element(thumb).click().perform()
                    time.sleep(0.5)
                    
                    # 확대된 이미지 찾기
                    expanded_img_selectors = [
                        "//div[contains(@class, 'viewer')]//img[@src]",
                        "//div[contains(@class, 'image_viewer')]//img",
                        "//div[contains(@class, 'modal')]//img[@src]"
                    ]
                    
                    for img_selector in expanded_img_selectors:
                        try:
                            expanded_img = WebDriverWait(self.driver, 2).until(
                                EC.presence_of_element_located((By.XPATH, img_selector))
                            )
                            src = expanded_img.get_attribute('src')
                            if src and 'http' in src and src not in photos:
                                # 원본 크기로 변환
                                src = self.convert_to_original_size(src)
                                photos.append(src)
                                print(f"         [{idx}] 원본 이미지 획득")
                            break
                        except:
                            continue
                    
                    # ESC 또는 닫기 버튼으로 뷰어 닫기
                    try:
                        ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                    except:
                        pass
                    
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"         ⚠️ [{idx}] 썸네일 처리 실패")
                    continue
            
            # 추가: 페이지의 모든 고해상도 이미지 URL도 수집
            all_images = self.driver.find_elements(By.XPATH, "//img[@src]")
            for img in all_images:
                src = img.get_attribute('src')
                if src and any(x in src for x in ['phinf', 'blogpfthumb']):
                    src = self.convert_to_original_size(src)
                    if src not in photos:
                        photos.append(src)
                        
        except Exception as e:
            print(f"      ⚠️ 사진 추출 오류: {e}")
            
        return photos
    
    def scroll_photo_area(self):
        """사진 영역 스크롤"""
        try:
            for _ in range(5):
                self.driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(0.5)
        except:
            pass
    
    def convert_to_original_size(self, url):
        """썸네일 URL을 원본 크기로 변환"""
        replacements = [
            ('?type=w120', '?type=w1200'),
            ('?type=w240', '?type=w1200'),
            ('?type=w360', '?type=w1200'),
            ('?type=w480', '?type=w1200'),
            ('?type=a340', '?type=w1200'),
            ('?type=m1', '?type=w1200'),
            ('/type=m1/', '/type=w1200/'),
        ]
        
        for old, new in replacements:
            if old in url:
                url = url.replace(old, new)
                break
                
        return url
    
    def download_photos(self, photos, photo_categories, folder_path, store_name):
        """사진 다운로드"""
        if not photos:
            print("   ℹ️  다운로드할 사진이 없습니다.")
            return 0
            
        downloaded_count = 0
        
        if photo_categories:
            for category, category_photos in photo_categories.items():
                category_folder = os.path.join(folder_path, self.sanitize_filename(category))
                os.makedirs(category_folder, exist_ok=True)
                
                print(f"   📁 카테고리: {category} ({len(category_photos)}개)")
                
                for idx, url in enumerate(category_photos, 1):
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
                            
                            filename = f"{category}_{idx:03d}{ext}"
                            filepath = os.path.join(category_folder, filename)
                            
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            
                            downloaded_count += 1
                            
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
            print(f"   📁 폴더 생성: {folder_path}")
            
            link_file = self.save_link_file(folder_path, store_name, naver_url)
            print(f"   🔗 링크 파일 저장: {os.path.basename(link_file)}")
            
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
        print("🚀 네이버 맵 대량 사진 다운로더 시작 (개선 버전)")
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
        print("사용법: python naver_map_bulk_downloader_v2.py <엑셀파일경로>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    if not os.path.exists(excel_path):
        print(f"❌ 파일을 찾을 수 없습니다: {excel_path}")
        sys.exit(1)
    
    downloader = NaverMapBulkDownloaderV2(excel_path)
    downloader.run()

if __name__ == "__main__":
    main()
