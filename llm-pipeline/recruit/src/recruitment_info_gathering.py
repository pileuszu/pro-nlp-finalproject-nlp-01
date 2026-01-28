import os
import time
import random
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# OCR 관련 라이브러리 (surya-ocr)
from surya.detection import DetectionPredictor
from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.common.surya.schema import TaskNames

# Gemini 관련 라이브러리
from google import genai
from google.genai import types

# .env 로드 (프로젝트 루트의 .env 탐색)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # pro-nlp-finalproject-nlp-01
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# 경로 설정
RECRUIT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = RECRUIT_DIR / "data" / "recruit_data"
FINAL_DATA_DIR = RECRUIT_DIR / "data" / "recruit_data"

# 파일명 설정
SAVE_FILE_CSV = DATA_DIR / "recruitment_results_full.csv"
SAVE_FILE_OCR_CSV = DATA_DIR / "recruitment_results_full_ocr.csv"
SAVE_FILE_JSON = FINAL_DATA_DIR / "final_recruitment_all_items.json"

# 디렉토리 생성
DATA_DIR.mkdir(parents=True, exist_ok=True)
FINAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------
# 설정 및 모델 로드
# -----------------------------------------------------
# (위에서 정의한 경로 변수 사용)
TARGET_PAGES = 1

# Gemini 설정
GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_ID = 'gemini-2.5-flash'  # 노트북에서는 gemini-2.5-flash로 되어있으나 오타일 수 있으므로 2.0으로 설정

SYSTEM_PROMPT = """채용 공고 전문가로서 다음 지침에 따라 공고 데이터를 분석하여 JSON 리스트로 변환하세요.
1. 한 공고 내에 여러 직무(백엔드, 프론트엔드 등)가 있다면 각각 독립된 JSON 객체로 분리하여 리스트로 만드세요.
2. 표(Table) 형식의 데이터는 행과 열의 관계를 정확히 파악하여 각 직무에 맞게 할당하세요.
3. 출력 형식은 반드시 아래 키를 포함하는 JSON 리스트여야 합니다:
   keys: [title, company, link, deadline, location, experience, education, employment_type, salary, job_sector, key_responsibilities, required_qualifications, preferred_qualifications]
"""

# Surya OCR 모델 로드 (전역 로드)
print("Surya OCR 모델 로딩 중...")
foundation_predictor = FoundationPredictor()
det_predictor = DetectionPredictor()
rec_predictor = RecognitionPredictor(foundation_predictor)
print("모델 로딩 완료.")

# -----------------------------------------------------
# 크롤링 함수들
# -----------------------------------------------------

def get_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Referer': 'https://inthiswork.com/'
    }

def get_job_list(pages=1):
    print("=== 공고 목록 수집 시작 ===")
    all_jobs = []
    session = requests.Session()
    
    for page in range(1, pages + 1):
        if page == 1:
            url = "https://inthiswork.com/it"
        else:
            url = f"https://inthiswork.com/it?paged1={page}"
            
        time.sleep(random.uniform(2, 4))
        print(f"[{page}페이지] 목록 수집 중... ({url})")
        
        try:
            resp = session.get(url, headers=get_headers(), timeout=15)
            if resp.status_code != 200:
                print(f"  → 에러: 접속 실패 (상태 코드 {resp.status_code})")
                continue
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            entries = soup.select('.dpt-entry')
            if not entries:
                entries = soup.select('.dpt-entry-wrapper')
            
            print(f"  → {len(entries)}개 공고 발견")
            for entry in entries:
                link_obj = entry.select_one('a.dpt-title-link') or entry.select_one('.dpt-title a')
                
                if link_obj and link_obj.get('href'):
                    full_url = link_obj.get('href')
                    full_text = link_obj.get_text(strip=True)
                    
                    if '/archives/' not in full_url: 
                        continue
                    
                    if '｜' in full_text:
                        parts = full_text.split('｜', 1)
                    elif '|' in full_text:
                        parts = full_text.split('|', 1)
                    else:
                        parts = ["-", full_text]
                    
                    company = parts[0].strip() if len(parts) > 1 else "-"
                    title = parts[1].strip() if len(parts) > 1 else parts[0].strip()

                    # 회사명이 없거나(-) 혹은 "IN THIS WORK"를 포함하는 경우(인터뷰/콘텐츠) 제외
                    if company == "-" or "IN THIS WORK" in company.upper():
                        print(f"  → 제외: {company} | {title}") # 제외되는 공고 로그 출력 (선택 사항)
                        continue
                    
                    if not any(j['url'] == full_url for j in all_jobs):
                        all_jobs.append({
                            'company': company,
                            'title': title,
                            'url': full_url
                        })
                        
        except Exception as e:
            print(f"  → 에러 발생: {e}")
            
    return all_jobs

def get_job_detail(url):
    time.sleep(random.uniform(2, 6))
    try:
        resp = requests.get(url, headers=get_headers(), timeout=15)
        if resp.status_code != 200:
            print(f"  → 접속 거부됨 ({resp.status_code}): {url}")
            return "", "", ""

        soup = BeautifulSoup(resp.text, 'html.parser')
        content_area = (
            soup.select_one('.fusion-content-tb') or 
            soup.select_one('.fusion-content-tb-1') or 
            soup.select_one('.fusion-content-tb-2') or 
            soup.select_one('.post-content') or 
            soup.select_one('.entry-content')
        )
        
        if not content_area:
            if len(resp.text) > 2000:
                content_area = soup.find('body')
            else:
                return "", "", ""
        
        apply_link_obj = content_area.select_one('a.maxbutton')
        if not apply_link_obj:
            for a in content_area.select('a'):
                if "지원하러" in a.get_text() or "지원하기" in a.get_text():
                    apply_link_obj = a
                    break
        
        apply_url = ""
        if apply_link_obj:
            apply_url = apply_link_obj.get('href', '')
            apply_link_obj.decompose()

        images = content_area.select('img')
        image_links = [img.get('src') for img in images if img.get('src')]
        images_str = ", ".join(image_links)

        text_content = content_area.get_text(separator='\n', strip=True)
        return text_content[:5000], images_str, apply_url

    except Exception as e:
        print(f"  → 상세 에러({url}): {e}")
        return "", "", ""

# -----------------------------------------------------
# OCR 및 Gemini 관련 함수들
# -----------------------------------------------------

def read_text_from_image_url(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200: return ""
        
        image_bytes = BytesIO(response.content)
        image = Image.open(image_bytes).convert("RGB")
        
        predictions = rec_predictor(
            [image], 
            [TaskNames.ocr_with_boxes], 
            det_predictor=det_predictor
        )
        
        if predictions and predictions[0].text_lines:
            full_text = "\n".join([line.text for line in predictions[0].text_lines])
            return full_text
        
        return ""
    except Exception as e:
        print(f"OCR 에러 ({url}): {e}")
        return ""

def analyze_job_with_gemini(df_row):
    """
    OCR 결과와 텍스트를 통합하여 Gemini를 통해 JSON 추출
    (노트북의 '방식 A' 기반)
    """
    existing_text = str(df_row['content_text']) if pd.notna(df_row['content_text']) else ""
    
    # 이미지가 있고 텍스트가 부족할 경우 실시간 OCR 수행 (필요한 경우만)
    img_urls = str(df_row['content_images']).split(',') if pd.notna(df_row['content_images']) else []
    ocr_text_all = ""
    
    # 만약 이미 content_text에 OCR 결과가 포함되어 있지 않다면 수행
    if "(이미지 자동 추출 텍스트)" not in existing_text and len(existing_text) < 200:
        for url in img_urls:
            url = url.strip()
            if not url: continue
            text = read_text_from_image_url(url) 
            ocr_text_all += f"\n[이미지 추출 텍스트]:\n{text}\n"

    combined_input = f"""
    회사명: {df_row['company']}
    공고 제목: {df_row['title']}
    원본 링크: {df_row['url']}
    지원 링크: {df_row['apply_url']}
    
    [본문 텍스트]:
    {existing_text}
    
    {ocr_text_all}
    """

    try:
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=f"다음 데이터를 분석해:\n{combined_input}",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json"
            )
        )
        return response.text
    except Exception as e:
        print(f"Gemini 호출 에러: {e}")
        return "[]"

# -----------------------------------------------------
# 메인 실행 흐름
# -----------------------------------------------------

def main():
    # 1. 공고 목록 및 상세 수집
    job_list = get_job_list(pages=TARGET_PAGES)
    
    full_data = []
    if job_list:
        print("\n=== 상세 정보 수집 시작 ===")
        for idx, job in enumerate(job_list):
            print(f"[{idx+1}/{len(job_list)}] {job['title'][:15]}...")
            text, imgs, apply_url = get_job_detail(job['url'])
            
            job['content_text'] = text
            job['content_images'] = imgs
            job['apply_url'] = apply_url
            full_data.append(job)

        # 2. 결과 저장 (CSV)
        df = pd.DataFrame(full_data)
        if os.path.exists(SAVE_FILE_CSV):
            df.to_csv(SAVE_FILE_CSV, mode='a', header=False, index=False, encoding='utf-8-sig')
            print(f"\n[추가 완료] {SAVE_FILE_CSV}에 {len(df)}건 추가됨.")
        else:
            df.to_csv(SAVE_FILE_CSV, mode='w', header=True, index=False, encoding='utf-8-sig')
            print(f"\n[저장 완료] {SAVE_FILE_CSV} 생성됨.")

        # 3. 텍스트 부족 시 OCR 수행
        print("\n=== OCR 처리 시작 (필요 시) ===")
        df['content_text'] = df['content_text'].fillna('')
        target_mask = (df['content_text'].str.len() < 50) & (df['content_images'] != "")
        
        for idx, row in df[target_mask].iterrows():
            print(f"[{idx}] '{row['title']}' OCR 수전 중...")
            img_urls = str(row['content_images']).split(',')
            ocr_text_all = []
            for img_url in img_urls:
                img_url = img_url.strip()
                if not img_url: continue
                text = read_text_from_image_url(img_url)
                if text: ocr_text_all.append(text)
            
            if ocr_text_all:
                full_ocr_text = "(이미지 자동 추출 텍스트)\n" + "\n---\n".join(ocr_text_all)
                df.at[idx, 'content_text'] = full_ocr_text
                print("  -> 변환 완료")

        df.to_csv(SAVE_FILE_OCR_CSV, index=False, encoding='utf-8-sig')
        print(f"[완료] {SAVE_FILE_OCR_CSV} 저장됨.")

        # 4. Gemini를 통한 최종 JSON 생성
        print("\n=== Gemini 데이터 분석(JSON 생성) 시작 ===")
        final_json_results = []
        for idx, row in df.iterrows():
            print(f"[{idx+1}/{len(df)}] {row['company']} - {row['title']} 분석 중...")
            json_str = analyze_job_with_gemini(row)
            try:
                job_json_list = json.loads(json_str)
                if isinstance(job_json_list, list):
                    final_json_results.extend(job_json_list)
                else:
                    final_json_results.append(job_json_list)
            except Exception as e:
                print(f"  -> JSON 파싱 실패: {e}")

        # 5. 최종 JSON 저장
        with open(SAVE_FILE_JSON, "w", encoding="utf-8") as f:
            json.dump(final_json_results, f, ensure_ascii=False, indent=2)
        print(f"\n[최종 완료] {SAVE_FILE_JSON}가 생성되었습니다.")

if __name__ == "__main__":
    main()
