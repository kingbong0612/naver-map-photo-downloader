#!/usr/bin/env python3
"""
네이버 맵 디버깅 도구 - 페이지 구조 분석
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def analyze_naver_map(url):
    chrome_options = Options()
    # headless 모드 끄기 - 화면 보면서 디버깅
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"🌐 페이지 로딩: {url}")
        driver.get(url)
        time.sleep(5)  # 충분히 대기
        
        print("\n" + "="*60)
        print("📋 페이지 HTML 구조 분석")
        print("="*60)
        
        # 1. 모든 탭 찾기
        print("\n1️⃣ 모든 탭/버튼 찾기:")
        tab_selectors = [
            "//a", "//button", "//span", "//div[@role='tab']"
        ]
        
        all_texts = set()
        for selector in tab_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            for elem in elements[:50]:  # 처음 50개만
                try:
                    text = elem.text.strip()
                    if text and len(text) < 20:
                        all_texts.add(text)
                except:
                    pass
        
        print("   발견된 텍스트:", sorted(all_texts))
        
        # 2. 클래스 이름 분석
        print("\n2️⃣ 주요 div 클래스:")
        divs = driver.find_elements(By.XPATH, "//div[@class]")
        classes = set()
        for div in divs[:100]:
            try:
                class_name = div.get_attribute('class')
                if class_name:
                    classes.add(class_name)
            except:
                pass
        
        for cls in sorted(classes)[:20]:
            print(f"   - {cls}")
        
        # 3. iframe 확인
        print("\n3️⃣ iframe 확인:")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"   발견된 iframe: {len(iframes)}개")
        
        for idx, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute('src')
                id_attr = iframe.get_attribute('id')
                print(f"   [{idx}] src: {src[:50]}... id: {id_attr}")
            except:
                pass
        
        # 4. 사진 관련 요소 찾기
        print("\n4️⃣ '사진' 텍스트 포함 요소:")
        photo_elements = driver.find_elements(By.XPATH, "//*[contains(., '사진')]")
        print(f"   발견된 요소: {len(photo_elements)}개")
        
        for elem in photo_elements[:10]:
            try:
                tag = elem.tag_name
                text = elem.text[:30] if elem.text else ""
                class_name = elem.get_attribute('class')
                print(f"   - <{tag}> class='{class_name}' text='{text}'")
            except:
                pass
        
        # 5. 이미지 요소 확인
        print("\n5️⃣ 이미지 요소:")
        images = driver.find_elements(By.TAG_NAME, "img")
        print(f"   발견된 이미지: {len(images)}개")
        
        for img in images[:5]:
            try:
                src = img.get_attribute('src')
                alt = img.get_attribute('alt')
                print(f"   - src: {src[:50]}... alt: {alt}")
            except:
                pass
        
        # 6. 현재 URL 확인
        print(f"\n6️⃣ 현재 URL: {driver.current_url}")
        
        # 7. 페이지 소스 일부 저장
        print("\n7️⃣ HTML 저장 중...")
        with open('debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("   ✅ debug_page_source.html 저장 완료")
        
        # 8. 스크린샷
        print("\n8️⃣ 스크린샷 저장 중...")
        driver.save_screenshot('debug_screenshot.png')
        print("   ✅ debug_screenshot.png 저장 완료")
        
        print("\n" + "="*60)
        print("💡 디버깅 대기 중... (30초)")
        print("   Chrome 창을 보면서 수동으로 사진 탭을 찾아보세요")
        print("="*60)
        time.sleep(30)
        
    finally:
        driver.quit()
        print("\n✅ 분석 완료!")

if __name__ == "__main__":
    url = "https://naver.me/FfB3j16z"
    analyze_naver_map(url)
