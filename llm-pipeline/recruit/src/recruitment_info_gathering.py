import os
import time
import random
import json
import base64
import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import BytesIO
from pathlib import Path
from dotenv import load_dotenv

# .env 로드
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # pro-nlp-finalproject-nlp-01
env_path = BASE_DIR / "backend" / ".env" # Pointing to backend .env
if not env_path.exists():
    env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# 경로 설정
RECRUIT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = RECRUIT_DIR / "data" / "recruit_data"
SAVE_FILE_CSV = DATA_DIR / "recruitment_results_full.csv"
SAVE_FILE_OCR_CSV = DATA_DIR / "recruitment_results_full_ocr.csv"
SAVE_FILE_JSON = DATA_DIR / "final_recruitment_all_items.json"

# 디렉토리 생성
DATA_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------
# 설정
# -----------------------------------------------------
TARGET_PAGES = 1

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
NCP_API_KEY = os.getenv("NCP_CLOVASTUDIO_API_KEY")
NCP_BASE_URL = os.getenv("NCP_CLOVASTUDIO_BASE_URL", "https://clovastudio.stream.ntruss.com")

if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY not found. OCR will not work.")
if not NCP_API_KEY:
    print("Warning: NCP_CLOVASTUDIO_API_KEY not found. Parsing will not work.")

# -----------------------------------------------------
# Helper: Google Vision OCR
# -----------------------------------------------------
def google_vision_ocr(image_url: str) -> str:
    if not GOOGLE_API_KEY: return ""
    
    try:
        # 1. Download Image
        resp = requests.get(image_url, timeout=10)
        if resp.status_code != 200: return ""
        content = resp.content
        
        # 2. Base64 Encode
        image_content = base64.b64encode(content).decode("utf-8")
        
        # 3. Call Vision API
        url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_API_KEY}"
        payload = {
            "requests": [
                {
                    "image": {"content": image_content},
                    "features": [{"type": "TEXT_DETECTION"}]
                }
            ]
        }
        
        vision_resp = requests.post(url, json=payload, timeout=20)
        if vision_resp.status_code != 200:
            print(f"Vision API Error: {vision_resp.text}")
            return ""
            
        result = vision_resp.json()
        text_annotations = result.get("responses", [{}])[0].get("textAnnotations", [])
        if text_annotations:
            return text_annotations[0].get("description", "")
        return ""
        
    except Exception as e:
        print(f"OCR Error ({image_url}): {e}")
        return ""

# -----------------------------------------------------
# Helper: NCP Chat Completion
# -----------------------------------------------------
def analyze_job_with_ncp(df_row):
    """
    NCP HCX-DASH-002를 사용하여 채용 공고 텍스트를 JSON으로 변환
    """
    if not NCP_API_KEY: return "[]"

    existing_text = str(df_row['content_text']) if pd.notna(df_row['content_text']) else ""
    
    # OCR 처리 (텍스트가 너무 적을 경우)
    img_urls = str(df_row['content_images']).split(',') if pd.notna(df_row['content_images']) else []
    ocr_text_all = ""
    
    if "(이미지 자동 추출 텍스트)" not in existing_text and len(existing_text) < 200:
        for url in img_urls:
            url = url.strip()
            if not url: continue
            text = google_vision_ocr(url)
            if text:
                ocr_text_all += f"\n[이미지 추출 텍스트]:\n{text}\n"

    full_text = f"""
    회사명: {df_row['company']}
    공고 제목: {df_row['title']}
    원본 링크: {df_row['url']}
    지원 링크: {df_row['apply_url']}
    
    [본문 텍스트]:
    {existing_text}
    
    {ocr_text_all}
    """

    system_prompt = """
    당신은 채용 공고 데이터 파싱 전문가입니다. 입력된 채용 공고 텍스트를 분석하여 구조화된 JSON 리스트로 출력하세요.
    
    규칙:
    1. 한 공고 내에 여러 직무(예: 백엔드, 프론트엔드)가 있다면 각각 독립된 객체로 분리하여 리스트로 만드세요.
    2. 응답은 오직 JSON 리스트만 출력하세요. (Markdown ```json 등 제외)
    3. 스키마:
       - title (직무명 + 공고제목)
       - company
       - link (지원링크가 있으면 지원링크, 없으면 원본링크)
       - deadline (YYYY-MM-DD 또는 '상시채용')
       - location
       - experience (경력 무관, 3년 이상 등)
       - education
       - employment_type (정규직 등)
       - salary
       - job_sector (개발, 디자인 등)
       - key_responsibilities (주요 업무 - 줄바꿈 된 문자열)
       - required_qualifications (자격 요건 - 줄바꿈 된 문자열)
       - preferred_qualifications (우대 사항 - 줄바꿈 된 문자열)
       - content (전체 원문 요약)
    """

    url = f"{NCP_BASE_URL}/v3/chat-completions/HCX-DASH-002"
    headers = {
        "Authorization": f"Bearer {NCP_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_text}
        ],
        "maxTokens": 3000,
        "temperature": 0.1,
        "topP": 0.8,
        "topK": 0
    }
    
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            result = resp.json()
            if result.get("status", {}).get("code") == "20000":
                content = result.get("result", {}).get("message", {}).get("content", "")
                return content
        print(f"NCP Error: {resp.text}")
        return "[]"
    except Exception as e:
        print(f"NCP Call Error: {e}")
        return "[]"

# -----------------------------------------------------
# 크롤링 함수들
# -----------------------------------------------------
def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    }

def get_job_list(pages=1):
    print("=== 공고 목록 수집 시작 ===")
    all_jobs = []
    session = requests.Session()
    
    for page in range(1, pages + 1):
        url = "https://inthiswork.com/it" if page == 1 else f"https://inthiswork.com/it?paged1={page}"
        print(f"[{page}페이지] {url}")
        
        try:
            resp = session.get(url, headers=get_headers(), timeout=15)
            if resp.status_code != 200: continue
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            # 2024년 기준 inthiswork 구조에 맞게 선택자 조정 필요 시 수정
            # 여기서는 기존 로직 유지
            entries = soup.select('.dpt-entry') or soup.select('.dpt-entry-wrapper')
            
            print(f"  → {len(entries)}개 공고 발견")
            for entry in entries:
                link_obj = entry.select_one('a.dpt-title-link') or entry.select_one('.dpt-title a')
                if not link_obj: continue
                
                full_url = link_obj.get('href')
                full_text = link_obj.get_text(strip=True)
                
                if '/archives/' not in full_url: continue
                
                parts = full_text.split('|', 1) if '|' in full_text else (full_text.split('｜', 1) if '｜' in full_text else ["-", full_text])
                company = parts[0].strip() if len(parts) > 1 else "-"
                title = parts[1].strip() if len(parts) > 1 else parts[0].strip()

                if company == "-" or "IN THIS WORK" in company.upper(): continue
                
                if not any(j['url'] == full_url for j in all_jobs):
                    all_jobs.append({'company': company, 'title': title, 'url': full_url})
                        
        except Exception as e:
            print(f"  → 에러: {e}")
            
    return all_jobs

def get_job_detail(url):
    time.sleep(1) # Politeness delay
    try:
        resp = requests.get(url, headers=get_headers(), timeout=15)
        if resp.status_code != 200: return "", "", ""

        soup = BeautifulSoup(resp.text, 'html.parser')
        content_area = (
            soup.select_one('.fusion-content-tb') or 
            soup.select_one('.post-content') or 
            soup.select_one('.entry-content') or
            soup.find('body')
        )
        
        # apply url
        apply_url = ""
        for a in content_area.select('a'):
            if "지원하러" in a.get_text() or "지원하기" in a.get_text():
                apply_url = a.get('href', '')
                break

        # images
        images = [img.get('src') for img in content_area.select('img') if img.get('src')]
        images_str = ", ".join(images)

        text_content = content_area.get_text(separator='\n', strip=True)
        return text_content[:5000], images_str, apply_url

    except Exception as e:
        print(f"  → 상세 에러: {e}")
        return "", "", ""

# -----------------------------------------------------
# 메인
# -----------------------------------------------------
def main():
    # 1. Crawl List
    job_list = get_job_list(pages=TARGET_PAGES)
    
    full_data = []
    print(f"\n=== 상세 정보 수집 대상: {len(job_list)}건 ===")
    
    for idx, job in enumerate(job_list):
        print(f"[{idx+1}/{len(job_list)}] {job['company']} - {job['title']}")
        text, imgs, apply_url = get_job_detail(job['url'])
        job['content_text'] = text
        job['content_images'] = imgs
        job['apply_url'] = apply_url
        full_data.append(job)

    # 2. Analyze with NCP (OCR + LLM)
    print("\n=== 데이터 분석 및 변환 (NCP HCX) ===")
    final_json_results = []
    
    for idx, row in enumerate(full_data):
        print(f"[{idx+1}/{len(full_data)}] 분석 중...")
        json_str = analyze_job_with_ncp(row)
        
        # Clean JSON
        json_str = json_str.replace("```json", "").replace("```", "").strip()
        
        try:
            parsed = json.loads(json_str)
            if isinstance(parsed, list):
                final_json_results.extend(parsed)
            else:
                final_json_results.append(parsed)
        except Exception as e:
            print(f"JSON Parsing Failed: {e}")

    # 3. Save
    with open(SAVE_FILE_JSON, "w", encoding="utf-8") as f:
        json.dump(final_json_results, f, ensure_ascii=False, indent=2)
    print(f"\n[완료] 결과 저장됨: {SAVE_FILE_JSON}")

if __name__ == "__main__":
    main()
