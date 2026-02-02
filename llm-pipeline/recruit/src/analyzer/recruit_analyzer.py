
import os
import sys
import json
import argparse
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# 모듈 경로 추가 (src 디렉토리를 sys.path에 추가하여 common 패키지 import 가능하게 함)
CURRENT_DIR = Path(__file__).resolve().parent
SRC_DIR = CURRENT_DIR.parent
sys.path.append(str(SRC_DIR))

from common.clova_client import ClovaStudioClient

# .env 로드
BASE_DIR = SRC_DIR.parent.parent.parent  # pro-nlp-finalproject-nlp-01
RECRUIT_DIR = Path(__file__).resolve().parent.parent.parent
env_path = RECRUIT_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# 경로 설정 (기본값)
DATA_DIR = SRC_DIR.parent / "data" / "recruit_data"

SYSTEM_PROMPT = """채용 공고 전문가로서 다음 지침에 따라 공고 데이터를 분석하여 JSON 리스트로 변환하세요.
1. 한 공고 내에 여러 직무(백엔드, 프론트엔드 등)가 있다면 각각 독립된 JSON 객체로 분리하여 리스트로 만드세요.
2. 표(Table) 형식의 데이터는 행과 열의 관계를 정확히 파악하여 각 직무에 맞게 할당하세요.
3. 출력 형식은 반드시 아래 키를 포함하는 JSON 리스트여야 합니다 (Code Block 없이 순수 JSON만 출력):
   keys: [title, company, link, deadline, location, experience, education, employment_type, salary, job_sector, key_responsibilities, required_qualifications, preferred_qualifications]
"""

def get_row_content(row):
    """
    다양한 크롤러 포맷(InThisWork, Saramin 등)에 맞춰 필드를 통합하여 반환
    """
    # 1. 공통 필드 시도
    company = row.get('company', '') or row.get('Company', '')
    title = row.get('title', '') or row.get('Title', '')
    url = row.get('url', '') or row.get('Link', '')
    apply_url = row.get('apply_url', '') # Saramin은 Link 자체가 지원 링크일 수 있음
    
    # 2. 본문 텍스트 통합
    content_text = ""
    
    # CASE A: InThisWork (content_text)
    if 'content_text' in row:
        content_text = str(row['content_text'])
    
    # CASE B: Saramin (Main Text, Qualifications, Preferred)
    parts = []
    if 'Main Text' in row and pd.notna(row['Main Text']) and row['Main Text'] != 'N/A':
        parts.append(f"[상세 본문]\n{row['Main Text']}")
    if 'Qualifications' in row and pd.notna(row['Qualifications']) and row['Qualifications'] != 'N/A':
        parts.append(f"[자격 요건]\n{row['Qualifications']}")
    if 'Preferred' in row and pd.notna(row['Preferred']) and row['Preferred'] != 'N/A':
        parts.append(f"[우대 사항]\n{row['Preferred']}")
        
    if parts:
        content_text += "\n\n".join(parts)

    return company, title, url, apply_url, content_text

def analyze_job(client: ClovaStudioClient, row):
    company, title, url, apply_url, content_text = get_row_content(row)
    
    # NaN 처리
    if pd.isna(content_text): content_text = ""
    
    user_prompt = f"""
    회사명: {company}
    공고 제목: {title}
    원본 링크: {url}
    지원 링크: {apply_url}
    
    [본문 텍스트]:
    {content_text}
    """
    
    print(f"  -> Clova 분석 요청: {company} - {title}")
    result_text = client.generate_content(SYSTEM_PROMPT, user_prompt)
    
    # JSON 파싱 전처리
    clean_text = result_text.strip()
    if clean_text.startswith('```json'):
        clean_text = clean_text[7:]
    if clean_text.startswith('```'):
        clean_text = clean_text[3:]
    if clean_text.endswith('```'):
        clean_text = clean_text[:-3]
        
    return clean_text.strip()

def main():
    parser = argparse.ArgumentParser(description="Recruit Data Analyzer (Clova Studio)")
    parser.add_argument("--input", "-i", type=str, required=False, help="Input CSV file path")
    parser.add_argument("--output", "-o", type=str, required=False, help="Output JSON file path")
    args = parser.parse_args()

    # 기본값 설정
    input_csv = Path(args.input) if args.input else DATA_DIR / "recruitment_results_full_ocr.csv"
    output_json = Path(args.output) if args.output else DATA_DIR / "final_recruitment_all_items.json"

    if not input_csv.exists():
        print(f"입력 파일이 없습니다: {input_csv}")
        return

    print(f"=== 채용 공고 분석기 (Clova Studio) 시작 ===")
    print(f"입력: {input_csv}")
    print(f"출력: {output_json}")
    
    # CSV 로드
    df = pd.read_csv(input_csv)
    df = df.fillna('')
    
    # Client 초기화
    client = ClovaStudioClient()
    
    final_json_results = []
    
    for idx, row in df.iterrows():
        print(f"[{idx+1}/{len(df)}] 분석 중...")
        json_str = analyze_job(client, row)
        
        if not json_str:
            print("  -> 결과 없음 (API 에러 또는 빈 응답)")
            continue
            
        try:
            job_data = json.loads(json_str)
            if isinstance(job_data, list):
                final_json_results.extend(job_data)
            elif isinstance(job_data, dict):
                final_json_results.append(job_data)
            else:
                print(f"  -> 파싱 실패: 리스트나 객체가 아님. ({json_str[:50]}...)")
        except json.JSONDecodeError:
            print(f"  -> JSON 디코딩 에러. 응답 내용: {json_str[:100]}...")
        except Exception as e:
            print(f"  -> 알 수 없는 에러: {e}")

    # 결과 저장 (Append 모드가 아니라 Overwrite 모드로 동작)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    
    # 기존 파일이 있다면 상황에 따라 합칠 수도 있겠지만, 여기선 덮어쓰거나 별도로 저장
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(final_json_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n[최종 완료] {output_json}가 생성되었습니다. (총 {len(final_json_results)}건)")

if __name__ == "__main__":
    main()
