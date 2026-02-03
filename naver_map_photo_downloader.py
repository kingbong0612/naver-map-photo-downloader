#!/usr/bin/env python3
"""
네이버 맵 사진 다운로더
사용법: python naver_map_photo_downloader.py <네이버맵 URL>
예: python naver_map_photo_downloader.py https://naver.me/FfB3j16z
"""

import os
import sys
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse, parse_qs
import json

class NaverMapPhotoDownloader:
    def __init__(self, url):
        self.url = url
        self.download_folder = "naver_map_photos"
        self.driver = None
        
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 헤드리스 모드
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
    def get_place_info(self):
        """장소 정보 가져오기"""
        print(f"페이지 로딩 중: {self.url}")
        self.driver.get(self.url)
        time.sleep(3)  # 페이지 로딩 대기
        
        # 단축 URL인 경우 실제 URL로 리다이렉션
        current_url = self.driver.current_url
        print(f"리다이렉트된 URL: {current_url}")
        
        return current_url
        
    def extract_photos(self):
        """사진 URL 추출"""
        photos = []
        
        try:
            # 사진 탭 찾기 및 클릭
            photo_tab_selectors = [
                "//a[contains(text(), '사진')]",
                "//button[contains(text(), '사진')]",
                "//span[contains(text(), '사진')]",
                "//*[@class='place_section_content']//a[contains(@class, 'pic')]"
            ]
            
            photo_tab = None
            for selector in photo_tab_selectors:
                try:
                    photo_tab = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if photo_tab:
                print("사진 탭 클릭")
                photo_tab.click()
                time.sleep(2)
            
            # 스크롤하여 더 많은 사진 로드
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            scroll_count = 0
            max_scrolls = 10
            
            while scroll_count < max_scrolls:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                    
                last_height = new_height
                scroll_count += 1
            
            # 사진 이미지 찾기
            image_selectors = [
                "//img[contains(@class, 'place_thumb')]",
                "//img[contains(@class, 'photo')]",
                "//div[contains(@class, 'photo')]//img",
                "//a[contains(@class, 'pic')]//img",
                "//div[contains(@class, 'flicking-camera')]//img"
            ]
            
            for selector in image_selectors:
                try:
                    images = self.driver.find_elements(By.XPATH, selector)
                    if images:
                        print(f"선택자 '{selector}'로 {len(images)}개 이미지 발견")
                        for img in images:
                            src = img.get_attribute('src')
                            if src and ('http' in src) and ('sslphinf' in src or 'blogpfthumb' in src or 'phinf' in src):
                                # 원본 크기로 변환
                                src = src.replace('?type=w120', '?type=w1200')
                                src = src.replace('?type=w240', '?type=w1200')
                                src = src.replace('?type=w360', '?type=w1200')
                                if src not in photos:
                                    photos.append(src)
                except Exception as e:
                    continue
            
            # 배경 이미지도 확인
            try:
                elements = self.driver.find_elements(By.XPATH, "//*[contains(@style, 'background-image')]")
                for elem in elements:
                    style = elem.get_attribute('style')
                    if 'url(' in style:
                        url_start = style.find('url(') + 4
                        url_end = style.find(')', url_start)
                        img_url = style[url_start:url_end].strip('"\'')
                        if img_url and 'http' in img_url and img_url not in photos:
                            img_url = img_url.replace('?type=w120', '?type=w1200')
                            photos.append(img_url)
            except:
                pass
                
        except Exception as e:
            print(f"사진 추출 중 오류: {e}")
        
        return photos
        
    def download_photos(self, photo_urls):
        """사진 다운로드"""
        if not photo_urls:
            print("다운로드할 사진이 없습니다.")
            return
            
        # 다운로드 폴더 생성
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
            
        print(f"\n총 {len(photo_urls)}개의 사진을 다운로드합니다...")
        
        for idx, url in enumerate(photo_urls, 1):
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # 파일 확장자 결정
                    ext = '.jpg'
                    if 'image/png' in response.headers.get('Content-Type', ''):
                        ext = '.png'
                    
                    filename = f"photo_{idx:03d}{ext}"
                    filepath = os.path.join(self.download_folder, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"[{idx}/{len(photo_urls)}] 다운로드 완료: {filename}")
                else:
                    print(f"[{idx}/{len(photo_urls)}] 다운로드 실패: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f"[{idx}/{len(photo_urls)}] 다운로드 오류: {e}")
                
        print(f"\n다운로드 완료! 저장 위치: {os.path.abspath(self.download_folder)}")
        
    def run(self):
        """전체 프로세스 실행"""
        try:
            self.setup_driver()
            self.get_place_info()
            
            photos = self.extract_photos()
            
            if photos:
                print(f"\n{len(photos)}개의 사진 URL을 찾았습니다.")
                
                # URL 목록 저장
                with open('photo_urls.txt', 'w', encoding='utf-8') as f:
                    for url in photos:
                        f.write(url + '\n')
                print("사진 URL 목록이 photo_urls.txt에 저장되었습니다.")
                
                self.download_photos(photos)
            else:
                print("사진을 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"오류 발생: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                self.driver.quit()

def main():
    if len(sys.argv) < 2:
        print("사용법: python naver_map_photo_downloader.py <네이버맵 URL>")
        print("예: python naver_map_photo_downloader.py https://naver.me/FfB3j16z")
        sys.exit(1)
    
    url = sys.argv[1]
    downloader = NaverMapPhotoDownloader(url)
    downloader.run()

if __name__ == "__main__":
    main()
