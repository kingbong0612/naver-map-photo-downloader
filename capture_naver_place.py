#!/usr/bin/env python3
"""
네이버 플레이스 캡처 도구 (엑셀 기반)
사용법: python capture_naver_place.py <엑셀파일경로>

기능:
- 네이버 검색으로 매장 찾기
- 플레이스 카드 영역 캡처
- 각 매장의 업체 폴더에 저장
"""

import os
import sys
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from PIL import Image
import traceback
from datetime import datetime

class NaverPlaceCapturer:
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
            'no_folder': 0
        }
        
        # 실패한 매장 기록
        self.failed_stores = []
        
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        # headless 모드 비활성화 (캡처 확인용)
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
        
    def capture_naver_place(self, region, region_detail, store_name, save_path):
        """네이버 플레이스 캡처 - 플레이스 카드만 정확히"""
        try:
            # 네이버 검색 (지역 + 지역상세 + 매장명 + 세신)
            # 따옴표로 감싸서 검색어 변경 방지
            search_query = f'"{region} {region_detail} {store_name}" 세신'
            search_url = f"https://search.naver.com/search.naver?query={search_query}"
            print(f"   🔍 검색: {search_query}")
            
            self.driver.get(search_url)
            
            # #loc-main-section-root 요소가 나타날 때까지 대기
            try:
                wait = WebDriverWait(self.driver, 10)
                
                # 플레이스 카드 영역을 찾기 위해 더 구체적인 선택자 사용
                # api_subject_bx는 플레이스 카드 내부에만 있음
                place_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#loc-main-section-root .api_subject_bx"))
                )
                
                # 플레이스 내용이 로드될 때까지 추가 대기
                time.sleep(3)
                
                # 부모 요소 (#loc-main-section-root) 찾기
                place_root = self.driver.find_element(By.CSS_SELECTOR, "#loc-main-section-root")
                
                # 플레이스인지 확인 (api_subject_bx 클래스 존재 여부)
                if "api_subject_bx" not in place_root.get_attribute("innerHTML"):
                    print(f"   ⚠️  플레이스 카드를 찾을 수 없음 (뉴스/다른 콘텐츠)")
                    return False
                
                # 스크린샷 저장
                screenshot_path = os.path.join(save_path, "네이버플레이스_캡처.png")
                place_root.screenshot(screenshot_path)
                
                # 파일 크기 확인
                if os.path.exists(screenshot_path):
                    file_size = os.path.getsize(screenshot_path)
                    if file_size >= 1000:
                        print(f"   ✅ 캡처 완료: {file_size // 1024}KB")
                        return True
                    else:
                        print(f"   ❌ 캡처 실패: 파일 너무 작음")
                        return False
                else:
                    print(f"   ❌ 캡처 실패")
                    return False
                    
            except Exception as e:
                print(f"   ❌ 플레이스 영역 찾기 실패: {str(e)[:100]}")
                return False
                
        except Exception as e:
            print(f"   ❌ 캡처 실패: {e}")
            traceback.print_exc()
            return False
    
    def process_single_store(self, row_idx, row):
        """개별 매장 처리"""
        region = row.get('지역', 'unknown')
        region_detail = row.get('지역상세', 'unknown')
        store_name = row.get('매장명', 'unknown')
        
        print(f"\n{'='*60}")
        print(f"[{row_idx + 1}/{self.stats['total']}] 처리 중: {region} > {region_detail} > {store_name}")
        print(f"{'='*60}")
        
        try:
            # 매장 폴더 찾기
            company_folder = self.get_store_folder(region, region_detail, store_name)
            
            if not company_folder:
                print(f"   ⚠️  매장 폴더를 찾을 수 없음")
                print(f"   💡 먼저 V4 다운로더를 실행하여 폴더를 생성하세요")
                self.stats['no_folder'] += 1
                return
            
            print(f"   📁 저장 위치: {company_folder}")
            
            # 이미 캡처 파일이 있는지 확인
            existing_capture = os.path.join(company_folder, "네이버플레이스_캡처.png")
            if os.path.exists(existing_capture):
                print(f"   ℹ️  이미 캡처 파일이 존재함 - 덮어쓰기")
            
            # 네이버 플레이스 캡처
            if self.capture_naver_place(region, region_detail, store_name, company_folder):
                self.stats['success'] += 1
            else:
                self.stats['failed'] += 1
                # 실패한 매장 기록
                self.failed_stores.append({
                    '지역': region,
                    '지역상세': region_detail,
                    '매장명': store_name,
                    '검색어': f"{region} {region_detail} {store_name} 세신"
                })
                
        except Exception as e:
            print(f"   ❌ 처리 실패: {e}")
            traceback.print_exc()
            self.stats['failed'] += 1
    
    def run(self):
        """전체 프로세스 실행"""
        start_time = time.time()
        
        print("\n" + "="*60)
        print("📸 네이버 플레이스 캡처 도구 시작")
        print("="*60 + "\n")
        
        df = self.read_excel()
        self.stats['total'] = len(df)
        
        self.setup_driver()
        
        try:
            for idx, row in df.iterrows():
                self.process_single_store(idx, row)
                
                progress = (idx + 1) / len(df) * 100
                print(f"\n📊 진행률: {progress:.1f}% ({idx + 1}/{len(df)})")
                
                # 3개마다 잠깐 대기 (네이버 서버 부담 줄이기)
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
        print(f"⏱️  소요 시간: {elapsed_time/60:.1f}분")
        print(f"📁 저장 위치: {os.path.abspath(self.base_folder)}")
        print("="*60 + "\n")
        
        if self.stats['no_folder'] > 0:
            print("💡 팁: 폴더가 없는 매장은 먼저 V4 다운로더를 실행하세요")
            print("   실행_V4.bat → 사진 다운로드 → 캡처 도구 실행\n")
    
    def save_failed_stores(self):
        """캡처 실패한 매장 목록을 텍스트 파일로 저장"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            failed_file = os.path.join(script_dir, "캡처_실패_목록.txt")
            
            with open(failed_file, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("네이버 플레이스 캡처 실패 목록\n")
                f.write("="*60 + "\n")
                f.write(f"생성 날짜: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}\n")
                f.write(f"실패 건수: {len(self.failed_stores)}개\n")
                f.write("="*60 + "\n\n")
                
                for idx, store in enumerate(self.failed_stores, 1):
                    f.write(f"[{idx}] {store['지역']} > {store['지역상세']} > {store['매장명']}\n")
                    f.write(f"    검색어: {store['검색어']}\n")
                    f.write(f"    검색 URL: https://search.naver.com/search.naver?query={store['검색어']}\n")
                    f.write("\n")
                
                f.write("="*60 + "\n")
                f.write("💡 수동 캡처 방법:\n")
                f.write("1. 위의 검색 URL을 클릭하여 네이버에서 검색\n")
                f.write("2. 플레이스 카드 화면을 캡처 (Windows: Win + Shift + S)\n")
                f.write("3. downloads/지역/지역상세/매장명/업체/ 폴더에 저장\n")
                f.write("4. 파일명: 네이버플레이스_캡처.png\n")
                f.write("="*60 + "\n")
            
            print(f"\n📝 실패 목록 저장: {failed_file}")
            print(f"   {len(self.failed_stores)}개 매장의 정보가 저장되었습니다.")
            print(f"   파일을 열어서 수동으로 캡처하세요.\n")
            
        except Exception as e:
            print(f"⚠️  실패 목록 저장 오류: {e}")

def main():
    if len(sys.argv) < 2:
        print("사용법: python capture_naver_place.py <엑셀파일경로>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    if not os.path.exists(excel_path):
        print(f"❌ 파일을 찾을 수 없습니다: {excel_path}")
        sys.exit(1)
    
    capturer = NaverPlaceCapturer(excel_path)
    capturer.run()

if __name__ == "__main__":
    main()
