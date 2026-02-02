
import json
import os
from pathlib import Path

# 경로 설정
RECRUIT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = RECRUIT_DIR / "data" / "recruit_data"

# 파일명 설정
RECRUIT_FILE = DATA_DIR / "final_recruitment_all_items.json"
QUESTION_FILE = DATA_DIR / "jasoseol_questions.json"
OUTPUT_FILE = DATA_DIR / "final_recruitment_with_questions.json"

def normalize_text(text):
    """비교를 위해 텍스트 정규화 (공백 제거, 대소문자 통일, 특수문자 제거)"""
    if not text:
        return ""
    # 불필요한 수식어 제거 (자소설과 사람인의 표기 차이 극복용)
    removals = ["(주)", "주식회사", "(유)", "유한회사", " ", "\t", "\n"]
    text = text.lower()
    for r in removals:
        text = text.replace(r, "")
    return text

def merge_questions():
    print("=== 질문 데이터 병합 시작 ===")
    
    # 1. 파일 존재 확인 및 로드
    if not RECRUIT_FILE.exists():
        print(f"오류: 공고 파일이 없습니다. ({RECRUIT_FILE})")
        return
    if not QUESTION_FILE.exists():
        print(f"오류: 질문 파일이 없습니다. ({QUESTION_FILE})")
        return

    with open(RECRUIT_FILE, "r", encoding="utf-8") as f:
        recruit_data = json.load(f)
    
    with open(QUESTION_FILE, "r", encoding="utf-8") as f:
        question_data = json.load(f)

    print(f"공고 데이터: {len(recruit_data)}건")
    print(f"질문 데이터: {len(question_data)}건")

    # 2. 질문 데이터를 매칭하기 쉽게 변환 (회사명 기준 그룹화)
    # 한 회사가 여러 공고를 낼 수 있으므로 {normalized_company: [items]} 구조로 만듦
    question_map = {}
    for q_item in question_data:
        norm_company = normalize_text(q_item.get("company_name", ""))
        if norm_company not in question_map:
            question_map[norm_company] = []
        question_map[norm_company].append(q_item)

    # 3. 매칭 및 병합
    merged_count = 0
    for r_item in recruit_data:
        company = r_item.get("company", "")
        norm_company = normalize_text(company)
        title = r_item.get("title", "")
        norm_title = normalize_text(title)

        # 해당 회사의 질문 리스트가 있는지 확인
        if norm_company in question_map:
            potential_matches = question_map[norm_company]
            
            # 제목 유사도 확인 (여기서는 제목이 포함되거나 유사한지 간단히 체크)
            best_match = None
            for p_match in potential_matches:
                p_title = normalize_text(p_match.get("title", ""))
                
                # 조건 1: 제목이 완전히 일치하거나 서로 포함관계인 경우
                if norm_title in p_title or p_title in norm_title:
                    best_match = p_match
                    break
            
            # 매칭된 결과가 있으면 질문 추가
            if best_match:
                # 질문 텍스트만 리스트로 추출
                questions = [q.get("question") for q in best_match.get("questions", []) if q.get("question")]
                r_item["self_intro_questions"] = questions
                merged_count += 1
                print(f"  [매칭 성공] {company} - {title}")

    # 4. 결과 저장
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(recruit_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 병합 완료 ===")
    print(f"최종 저장 위치: {OUTPUT_FILE}")
    print(f"질문이 추가된 공고: {merged_count}건 / 전체 {len(recruit_data)}건")

if __name__ == "__main__":
    merge_questions()
