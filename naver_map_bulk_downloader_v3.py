#!/usr/bin/env python3
"""
네이버 맵 대량 사진 다운로더 V3 (엑셀 기반) - 완전히 새로운 접근
사용법: python naver_map_bulk_downloader_v3.py <엑셀파일경로>

핵심 변경사항:
1. 실제 네이버 지도 페이지 구조에 맞춘 정확한 셀렉터
2. iframe 처리 추가
3. 더 긴 대기 시간과 안정적인 클릭
4. 실제 원본 이미지 URL 추출
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

class NaverMapBulkDownloaderV3:
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
        """네이버 맵 URL에서 사진 추출 - V3 완전히 새로운 방식"""
        photos = []
        photo_categories = {}
        
        try:
            print(f"   🌐 페이지 로딩 중...")
            self.driver.get(url)
            time.sleep(5)  # 충분한 로딩 시간
            
            # 먼저 메인 페이지에서 사진 탭 찾기 시도
            print(f"   🔍 메인 페이지에서 사진 탭 찾는 중...")
            if self.find_and_click_photo_tab():
                print("   ✅ 메인 페이지에서 사진 탭 클릭 성공!")
            else:
                # 메인 페이지에서 실패하면 iframe 확인
                print(f"   ⚠️  메인 페이지에서 사진 탭을 찾지 못함")
                print(f"   🔍 iframe 확인 중...")
                
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    print(f"   📦 {len(iframes)}개의 iframe 발견")
                    
                    # 각 iframe을 순회하면서 사진 탭 찾기
                    found_in_iframe = False
                    for i, iframe in enumerate(iframes):
                        try:
                            print(f"      🔍 iframe [{i+1}] 확인 중...")
                            self.driver.switch_to.frame(iframe)
                            time.sleep(1)
                            
                            # iframe 내부에서 사진 탭 찾기
                            if self.find_and_click_photo_tab():
                                print(f"      ✅ iframe [{i+1}]에서 사진 탭 찾음!")
                                found_in_iframe = True
                                break
                            else:
                                # 이 iframe에 없으면 메인으로 돌아가기
                                self.driver.switch_to.default_content()
                        except Exception as e:
                            print(f"      ⚠️  iframe [{i+1}] 오류: {e}")
                            self.driver.switch_to.default_content()
                            continue
                    
                    if not found_in_iframe:
                        print("   ⚠️  모든 iframe에서 사진 탭을 찾지 못함")
                        return [], {}
                else:
                    print("   ⚠️  iframe도 없고 사진 탭도 찾지 못함")
                    return [], {}
            
            print("   ✅ 사진 탭 클릭 성공!")
            time.sleep(4)  # 사진 로드 대기
            
            # 카테고리 버튼 찾기 (업체, 클립, 방문자, 블로그)
            categories = self.find_photo_categories()
            
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
                        print(f"      ⚠️  사진 없음")
            else:
                # 카테고리가 없으면 전체 사진 추출
                print("   📸 카테고리 없이 전체 사진 추출 중...")
                photos = self.extract_all_visible_photos()
                if photos:
                    photo_categories['전체사진'] = photos
            
            # 중복 제거
            photos = list(dict.fromkeys(photos))
            
            print(f"   ✅ 총 {len(photos)}개 사진 URL 추출 완료")
            
            # iframe에서 나오기 (안전하게)
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            
            return photos, photo_categories
            
        except Exception as e:
            print(f"   ❌ 사진 추출 오류: {e}")
            traceback.print_exc()
            # iframe에서 안전하게 나오기
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return [], {}
    
    def find_and_click_photo_tab(self):
        """사진 탭 찾기 및 클릭 - 모든 가능한 방법 시도"""
        
        # 방법 1: 텍스트로 직접 찾기 (가장 확실함)
        try:
            print("   🔍 방법 1: 텍스트로 '사진' 탭 찾는 중...")
            # 모든 요소 찾기
            all_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '사진')]")
            print(f"      발견된 '사진' 포함 요소: {len(all_elements)}개")
            
            for elem in all_elements:
                try:
                    # 클릭 가능한 요소인지 확인
                    if elem.is_displayed() and elem.is_enabled():
                        text = elem.text.strip()
                        print(f"      시도 중: '{text}' (tag: {elem.tag_name})")
                        
                        # '사진'이라는 텍스트만 있는 요소 찾기
                        if text == '사진' or text.startswith('사진'):
                            # JavaScript로 강제 클릭
                            self.driver.execute_script("arguments[0].click();", elem)
                            time.sleep(2)
                            return True
                except Exception as e:
                    continue
        except Exception as e:
            print(f"      방법 1 실패: {e}")
        
        # 방법 2: a 태그 찾기
        try:
            print("   🔍 방법 2: <a> 태그로 사진 탭 찾는 중...")
            photo_links = self.driver.find_elements(By.XPATH, "//a[contains(., '사진')]")
            print(f"      발견된 링크: {len(photo_links)}개")
            
            for link in photo_links:
                try:
                    if link.is_displayed():
                        print(f"      클릭 시도: {link.text}")
                        self.driver.execute_script("arguments[0].click();", link)
                        time.sleep(2)
                        return True
                except:
                    continue
        except Exception as e:
            print(f"      방법 2 실패: {e}")
        
        # 방법 3: span 태그 찾기
        try:
            print("   🔍 방법 3: <span> 태그로 사진 탭 찾는 중...")
            photo_spans = self.driver.find_elements(By.XPATH, "//span[contains(., '사진')]")
            print(f"      발견된 span: {len(photo_spans)}개")
            
            for span in photo_spans:
                try:
                    if span.is_displayed():
                        parent = span.find_element(By.XPATH, "..")
                        print(f"      클릭 시도: {span.text} (부모 태그: {parent.tag_name})")
                        self.driver.execute_script("arguments[0].click();", parent)
                        time.sleep(2)
                        return True
                except:
                    continue
        except Exception as e:
            print(f"      방법 3 실패: {e}")
        
        # 방법 4: CSS 클래스로 탭 찾기
        try:
            print("   🔍 방법 4: CSS 클래스로 탭 찾는 중...")
            tab_selectors = [
                "[class*='tab']",
                "[class*='Tab']",
                "[role='tab']",
                "[class*='menu'] a",
                "[class*='nav'] a"
            ]
            
            for selector in tab_selectors:
                try:
                    tabs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for tab in tabs:
                        if tab.is_displayed() and '사진' in tab.text:
                            print(f"      클릭 시도: {tab.text}")
                            self.driver.execute_script("arguments[0].click();", tab)
                            time.sleep(2)
                            return True
                except:
                    continue
        except Exception as e:
            print(f"      방법 4 실패: {e}")
        
        # 방법 5: 모든 클릭 가능한 요소 검사
        try:
            print("   🔍 방법 5: 모든 클릭 가능한 요소 검사 중...")
            clickable_elements = self.driver.find_elements(By.XPATH, "//*[@onclick or @href or @role='button' or self::a or self::button]")
            
            for elem in clickable_elements:
                try:
                    if elem.is_displayed() and '사진' in elem.text:
                        print(f"      클릭 시도: {elem.text} (tag: {elem.tag_name})")
                        self.driver.execute_script("arguments[0].click();", elem)
                        time.sleep(2)
                        return True
                except:
                    continue
        except Exception as e:
            print(f"      방법 5 실패: {e}")
        
        return False
    
    def find_photo_categories(self):
        """사진 카테고리 버튼 찾기 (업체, 클립, 방문자, 블로그)"""
        categories = []
        
        try:
            # 카테고리 키워드
            category_keywords = ['업체', '클립', '방문자', '블로그', '전체']
            
            # 모든 버튼과 링크 찾기
            potential_buttons = self.driver.find_elements(By.XPATH, "//button | //a | //span[@role='button']")
            
            for btn in potential_buttons:
                try:
                    text = btn.text.strip()
                    if text in category_keywords and text not in categories:
                        categories.append(text)
                        print(f"      🏷️  카테고리 발견: {text}")
                except:
                    continue
            
            # '전체' 제외
            if '전체' in categories:
                categories.remove('전체')
                    
            return categories
            
        except Exception as e:
            print(f"   ⚠️  카테고리 찾기 오류: {e}")
            return []
    
    def extract_photos_from_category(self, category):
        """특정 카테고리의 사진 추출"""
        photos = []
        
        try:
            # 카테고리 버튼 클릭
            print(f"      🖱️  '{category}' 버튼 찾는 중...")
            
            # 정확히 해당 텍스트를 가진 요소 찾기
            category_buttons = self.driver.find_elements(By.XPATH, f"//*[text()='{category}']")
            
            clicked = False
            for btn in category_buttons:
                try:
                    if btn.is_displayed():
                        print(f"      🖱️  '{category}' 버튼 클릭 시도...")
                        self.driver.execute_script("arguments[0].click();", btn)
                        time.sleep(3)
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                print(f"      ⚠️  '{category}' 버튼 클릭 실패")
                return []
            
            # 사진 추출
            photos = self.extract_all_visible_photos()
            
        except Exception as e:
            print(f"      ⚠️  '{category}' 추출 오류: {e}")
            
        return photos
    
    def extract_all_visible_photos(self):
        """현재 보이는 모든 사진 URL 추출"""
        photos = []
        
        try:
            # 스크롤하여 모든 이미지 로드
            self.scroll_to_load_all_images()
            
            # 모든 img 태그 찾기
            all_images = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"      🖼️  총 {len(all_images)}개 이미지 발견")
            
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
            
            # 추가: data-src 속성도 확인
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
            
            print(f"      ✅ {len(photos)}개 사진 URL 추출")
                        
        except Exception as e:
            print(f"      ⚠️  사진 추출 오류: {e}")
            
        return photos
    
    def scroll_to_load_all_images(self):
        """스크롤하여 모든 이미지 로드"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for i in range(10):  # 최대 10번 스크롤
                # 아래로 스크롤
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                # 새로운 높이
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
        print("🚀 네이버 맵 대량 사진 다운로더 V3 시작")
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
        print("사용법: python naver_map_bulk_downloader_v3.py <엑셀파일경로>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    if not os.path.exists(excel_path):
        print(f"❌ 파일을 찾을 수 없습니다: {excel_path}")
        sys.exit(1)
    
    downloader = NaverMapBulkDownloaderV3(excel_path)
    downloader.run()

if __name__ == "__main__":
    main()
