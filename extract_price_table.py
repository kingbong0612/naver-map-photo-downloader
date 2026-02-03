#!/usr/bin/env python3
"""
네이버 지도 가격표 추출 도구 (네이버지도링크 사용)
사용법: python extract_price_table.py <엑셀파일경로>

기능:
- 엑셀의 네이버지도링크 사용
- '가격표 이미지로 보기' 자동 클릭
- 가격표 이미지 다운로드
- 각 매장의 업체 폴더에 저장
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
from urllib.parse import quote

class NaverMapPriceExtractor:
    def __init__(self, excel_path, base_folder="downloads"):
        self.excel_path = excel_path
        # 현재 스크립트 위치에서 downloads 폴더
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_folder = os.path.join(script_dir, base_folder)
        self.driver = None
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'no_folder': 0,
            'no_url': 0,
            'no_price': 0
        }
        
        # 실패한 매장 기록
        self.failed_stores = []
        
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
            
    def sanitize_filename(self, name):
        """파일명에 사용할 수 없는 문자 제거"""
        if pd.isna(name):
            return "unknown"
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = str(name).replace(char, '_')
        return name.strip()
        
    def get_store_folder(self, region, region_detail, store_name):
        """매장 폴더 경로 가져오기"""
        region = self.sanitize_filename(region)
        region_detail = self.sanitize_filename(region_detail)
        store_name = self.sanitize_filename(store_name)
        
        folder_path = os.path.join(self.base_folder, region, region_detail, store_name)
        
        # 폴더 존재 확인
        if not os.path.exists(folder_path):
            return None
            
        # 업체 폴더 경로
        company_folder = os.path.join(folder_path, "업체")
        
        # 업체 폴더 없으면 생성
        if not os.path.exists(company_folder):
            os.makedirs(company_folder, exist_ok=True)
            
        return company_folder
        
    def extract_price_table(self, naver_map_url, save_path):
        """네이버 지도에서 가격표 추출 - 홈 탭(정보)에서 '가격표 이미지로 보기' 클릭"""
        try:
            print(f"   🗺️  네이버 지도 접속 중...")
            self.driver.get(naver_map_url)
            time.sleep(4)  # 페이지 로딩 대기
            
            # iframe 확인 및 전환
            target_iframe_index = None
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            
            if iframes:
                print(f"   🔍 {len(iframes)}개 iframe 발견")
                
                # 홈 탭(정보) iframe 찾기 - '가격표'가 있지만 '업체사진', '방문자' 등은 없는 곳
                for i in range(len(iframes)-1, -1, -1):  # 역순으로 확인
                    try:
                        self.driver.switch_to.default_content()
                        self.driver.switch_to.frame(iframes[i])
                        
                        page_text = self.driver.page_source
                        
                        has_price = '가격표' in page_text
                        has_photo_tab = '업체사진' in page_text or '방문자 리뷰' in page_text
                        
                        print(f"      iframe [{i+1}]: 가격표={'O' if has_price else 'X'}, 사진탭={'O' if has_photo_tab else 'X'}")
                        
                        # 가격표는 있지만 사진탭은 아닌 곳 (홈 탭)
                        if has_price and not has_photo_tab:
                            print(f"   ✅ iframe [{i+1}]에서 홈 탭(정보) 발견")
                            target_iframe_index = i
                            break
                            
                    except Exception as e:
                        self.driver.switch_to.default_content()
                        continue
            
            if target_iframe_index is None:
                print("   ⚠️  홈 탭을 찾을 수 없음, 메인 페이지에서 시도...")
                self.driver.switch_to.default_content()
            
            # '가격표 이미지로 보기' 링크 찾기 및 클릭
            price_button_found = False
            
            # 방법 1: '가격표' 텍스트가 있는 요소 찾기
            try:
                elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '가격표')]")
                print(f"   🔍 '가격표' 포함 요소 {len(elements)}개 발견")
                
                for elem in elements:
                    try:
                        text = elem.text.strip()
                        if not text:
                            continue
                            
                        print(f"      - '{text}'")
                        
                        # '가격표 이미지로 보기' 또는 '가격표' (카테고리명 제외)
                        if '가격표' in text and not any(x in text for x in ['업체', '방문자', '클립', '블로그']):
                            print(f"   ✅ 클릭 시도: '{text}'")
                            
                            # 클릭
                            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elem)
                            time.sleep(0.5)
                            self.driver.execute_script("arguments[0].click();", elem)
                            time.sleep(5)  # 충분한 대기
                            price_button_found = True
                            print(f"   ✅ 클릭 완료")
                            break
                            
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"   ⚠️  오류: {str(e)[:50]}")
            
            if not price_button_found:
                print("   ⚠️  가격표 링크를 찾을 수 없음")
                self.stats['no_price'] += 1
                return False
            
            # 가격표 이미지 페이지 로딩 대기
            print("   📋 가격표 이미지 페이지 로딩 중...")
            time.sleep(5)  # 로딩 대기 시간 증가
            
            # 가격표 페이지인지 확인
            page_source = self.driver.page_source
            
            # 가격표 관련 키워드 확인
            has_price_keyword = any(keyword in page_source for keyword in [
                '가격표', 'price', '메뉴판', 'menu'
            ])
            
            # 업체 사진 페이지 키워드 확인 (이러면 안됨)
            has_photo_keyword = any(keyword in page_source for keyword in [
                '업체사진', '방문자', '클립', '블로그'
            ])
            
            if has_photo_keyword and not has_price_keyword:
                print("   ⚠️  업체 사진 페이지에 있음 - 가격표 페이지가 아닙니다!")
                print("   💡 가격표 버튼 클릭이 제대로 되지 않았습니다.")
                self.stats['no_price'] += 1
                return False
            
            print(f"   🔍 페이지 확인: 가격표 키워드={'있음' if has_price_keyword else '없음'}")
            
            # 스크롤하여 모든 이미지 로드
            print("   🔄 스크롤하여 이미지 로딩...")
            self.scroll_photo_area()
            time.sleep(2)  # 스크롤 후 추가 대기
            
            price_images = []
            
            # 모든 이미지 요소에서 직접 URL 추출
            all_images = self.driver.find_elements(By.TAG_NAME, "img")
            print(f"   🔍 총 {len(all_images)}개 이미지 요소 발견")
            
            for img in all_images:
                try:
                    src = img.get_attribute('src')
                    size = img.size
                    
                    # 네이버 CDN 이미지만 추출 + 크기 필터 (너무 작은 아이콘 제외)
                    if src and 'phinf.pstatic.net' in src:
                        # 가격표는 일반적으로 큰 이미지 (최소 200px)
                        if size['width'] >= 150 or size['height'] >= 150:
                            # 원본 크기로 변환
                            original_src = self.convert_to_original_size(src)
                            
                            if original_src not in price_images:
                                price_images.append(original_src)
                                print(f"      ├── 이미지 발견: {size['width']}x{size['height']}px")
                            
                except:
                    continue
            
            # data-src 속성도 확인
            all_images_with_data_src = self.driver.find_elements(By.XPATH, "//*[@data-src]")
            if all_images_with_data_src:
                print(f"   🔍 data-src 속성 확인: {len(all_images_with_data_src)}개")
                
            for img in all_images_with_data_src:
                try:
                    src = img.get_attribute('data-src')
                    if src and 'phinf.pstatic.net' in src:
                        try:
                            size = img.size
                            if size['width'] >= 150 or size['height'] >= 150:
                                original_src = self.convert_to_original_size(src)
                                if original_src not in price_images:
                                    price_images.append(original_src)
                                    print(f"      ├── data-src 이미지: {size['width']}x{size['height']}px")
                        except:
                            # 크기 확인 실패해도 추가 시도
                            original_src = self.convert_to_original_size(src)
                            if original_src not in price_images:
                                price_images.append(original_src)
                except:
                    continue
            
            if not price_images:
                print("   ❌ 가격표 이미지를 찾을 수 없음")
                print("   💡 디버깅: 페이지 소스 일부 출력")
                try:
                    page_text = self.driver.page_source[:2000]
                    if '가격표' in page_text:
                        print("      - 페이지에 '가격표' 텍스트 존재")
                    if 'phinf.pstatic.net' in page_text:
                        print("      - 페이지에 네이버 CDN 이미지 존재")
                    if '업체사진' in page_text or '방문자' in page_text:
                        print("      - ⚠️  업체 사진 페이지에 머물러 있습니다!")
                except:
                    pass
                return False
            
            print(f"   ✅ {len(price_images)}개 가격표 이미지 발견")
            
            # 이미지 다운로드
            print(f"   💾 다운로드 시작...")
            for idx, img_url in enumerate(price_images, 1):
                try:
                    response = requests.get(img_url, timeout=15, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Referer': 'https://map.naver.com/'
                    })
                    
                    if response.status_code == 200:
                        # 확장자 결정
                        ext = '.jpg'
                        content_type = response.headers.get('Content-Type', '')
                        if 'png' in content_type:
                            ext = '.png'
                        elif 'webp' in content_type:
                            ext = '.webp'
                        
                        # 파일명
                        if len(price_images) == 1:
                            filename = f"가격표{ext}"
                        else:
                            filename = f"가격표_{idx}{ext}"
                        
                        filepath = os.path.join(save_path, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        file_size = len(response.content)
                        print(f"   ✅ 저장 완료: {filename} ({file_size // 1024}KB)")
                        
                except Exception as e:
                    print(f"   ⚠️  다운로드 실패 [{idx}]: {str(e)[:50]}")
            
            return len(price_images) > 0
                
        except Exception as e:
            print(f"   ❌ 가격표 추출 실패: {e}")
            traceback.print_exc()
            return False
        finally:
            # iframe에서 나오기
            try:
                self.driver.switch_to.default_content()
            except:
                pass
    
    def scroll_photo_area(self):
        """사진 영역 스크롤하여 모든 썸네일 로드"""
        try:
            # 현재 페이지에서 스크롤 가능한 영역 찾기
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            for i in range(5):  # 최대 5번 스크롤
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.8)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                
        except Exception as e:
            print(f"      ⚠️  스크롤 오류 (무시): {e}")
            pass
    
    def convert_to_original_size(self, url):
        """썸네일 URL을 원본 크기로 변환"""
        import re
        
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
            # 매장 폴더 찾기
            company_folder = self.get_store_folder(region, region_detail, store_name)
            
            if not company_folder:
                print(f"   ⚠️  매장 폴더를 찾을 수 없음")
                print(f"   💡 먼저 V4 다운로더를 실행하여 폴더를 생성하세요")
                self.stats['no_folder'] += 1
                return
            
            print(f"   📁 저장 위치: {company_folder}")
            
            # 이미 가격표 파일이 있는지 확인
            existing_files = [f for f in os.listdir(company_folder) if f.startswith('가격표')]
            if existing_files:
                print(f"   ℹ️  이미 가격표 파일이 존재함 - 건너뜀")
                self.stats['success'] += 1
                return
            
            # 가격표 추출
            if self.extract_price_table(naver_url, company_folder):
                self.stats['success'] += 1
            else:
                self.stats['failed'] += 1
                # 실패한 매장 기록
                self.failed_stores.append({
                    '지역': region,
                    '지역상세': region_detail,
                    '매장명': store_name,
                    '네이버지도링크': naver_url
                })
                
        except Exception as e:
            print(f"   ❌ 처리 실패: {e}")
            traceback.print_exc()
            self.stats['failed'] += 1
    
    def run(self):
        """전체 프로세스 실행"""
        start_time = time.time()
        
        print("\n" + "="*60)
        print("💰 네이버 지도 가격표 추출 도구 시작")
        print("="*60 + "\n")
        
        df = self.read_excel()
        self.stats['total'] = len(df)
        
        self.setup_driver()
        
        try:
            for idx, row in df.iterrows():
                self.process_single_store(idx, row)
                
                progress = (idx + 1) / len(df) * 100
                print(f"\n📊 진행률: {progress:.1f}% ({idx + 1}/{len(df)})")
                
                # 3개마다 잠깐 대기
                if (idx + 1) % 3 == 0:
                    print("   ⏳ 3개 처리마다 2초 대기 중...")
                    time.sleep(2)
                    
        except KeyboardInterrupt:
            print("\n\n⚠️  사용자에 의해 중단되었습니다.")
            
        finally:
            if self.driver:
                self.driver.quit()
                
        elapsed_time = time.time() - start_time
        self.print_final_stats(elapsed_time)
        
        # 실패한 매장 목록 저장
        if self.failed_stores:
            self.save_failed_stores()
    
    def print_final_stats(self, elapsed_time):
        """최종 통계 출력"""
        print("\n" + "="*60)
        print("📊 최종 통계")
        print("="*60)
        print(f"총 처리 대상: {self.stats['total']}개")
        print(f"✅ 성공: {self.stats['success']}개")
        print(f"❌ 실패: {self.stats['failed']}개")
        print(f"⚠️  폴더 없음: {self.stats['no_folder']}개")
        print(f"⚠️  링크 없음: {self.stats['no_url']}개")
        print(f"💰 가격표 없음: {self.stats['no_price']}개")
        print(f"⏱️  소요 시간: {elapsed_time/60:.1f}분")
        print(f"📁 저장 위치: {os.path.abspath(self.base_folder)}")
        print("="*60 + "\n")
        
        if self.stats['no_folder'] > 0:
            print("💡 팁: 폴더가 없는 매장은 먼저 V4 다운로더를 실행하세요\n")
    
    def save_failed_stores(self):
        """가격표 추출 실패한 매장 목록을 텍스트 파일로 저장"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            failed_file = os.path.join(script_dir, "가격표추출_실패_목록.txt")
            
            with open(failed_file, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("네이버 지도 가격표 추출 실패 목록\n")
                f.write("="*60 + "\n")
                f.write(f"생성 날짜: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}\n")
                f.write(f"실패 건수: {len(self.failed_stores)}개\n")
                f.write("="*60 + "\n\n")
                
                for idx, store in enumerate(self.failed_stores, 1):
                    f.write(f"[{idx}] {store['지역']} > {store['지역상세']} > {store['매장명']}\n")
                    f.write(f"    네이버지도링크: {store['네이버지도링크']}\n")
                    f.write("\n")
                
                f.write("="*60 + "\n")
                f.write("💡 수동 추출 방법:\n")
                f.write("1. 위의 네이버지도링크를 클릭\n")
                f.write("2. '가격표 이미지로 보기' 클릭\n")
                f.write("3. 이미지를 마우스 우클릭 → 다른 이름으로 저장\n")
                f.write("4. downloads/지역/지역상세/매장명/업체/ 폴더에 저장\n")
                f.write("5. 파일명: 가격표.jpg 또는 가격표.png\n")
                f.write("="*60 + "\n")
            
            print(f"\n📝 실패 목록 저장: {failed_file}")
            print(f"   {len(self.failed_stores)}개 매장의 정보가 저장되었습니다.")
            print(f"   파일을 열어서 수동으로 추출하세요.\n")
            
        except Exception as e:
            print(f"⚠️  실패 목록 저장 오류: {e}")

def main():
    if len(sys.argv) < 2:
        print("사용법: python extract_price_table.py <엑셀파일경로>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    if not os.path.exists(excel_path):
        print(f"❌ 파일을 찾을 수 없습니다: {excel_path}")
        sys.exit(1)
    
    extractor = NaverMapPriceExtractor(excel_path)
    extractor.run()

if __name__ == "__main__":
    main()
