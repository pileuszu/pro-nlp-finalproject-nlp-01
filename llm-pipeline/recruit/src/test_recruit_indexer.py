import shutil
import sys
from pathlib import Path
from recruit_indexer import RecruitIndexer
from langchain_chroma import Chroma

# Sample Data from User Request
SAMPLE_DATA = {
  "title": "한국남동발전 2026년 신입사원 채용 - ICT",
  "company": "한국남동발전",
  "link": "https://inthiswork.com/archives/298091",
  "deadline": "2026년 2월 14일",
  "location": "전국 사업소 (본사 및 발전소)",
  "experience": "신입 (경력무관)",
  "education": "대졸 이상 (학사 이상)",
  "employment_type": "정규직",
  "salary": "회사 내규에 따름",
  "job_sector": "ICT",
  "key_responsibilities": "정보 시스템 개발 및 운영, 네트워크 관리, 정보보안, 스마트 발전소 기술 적용 등",
  "required_qualifications": "컴퓨터공학, 정보통신, 소프트웨어 등 관련 전공 학사 이상, 정보처리기사 등 관련 기사 자격증 소지자",
  "preferred_qualifications": "정보보안 관련 자격증(정보보안기사 등), 프로그래밍 언어(Java, Python 등) 활용 능력 우수자, 클라우드 시스템 이해 및 경험",
  "summary_for_embedding": "한국남동발전 2026년 신입사원 채용 (ICT). 정보 시스템 개발 및 운영, 네트워크 관리, 정보보안 담당. 컴퓨터/정보통신/소프트웨어 전공 대졸 이상, 정보처리기사 등 자격증 필수. 전국 사업소 근무 정규직."
}

def clean_test_env():
    """Clean up invalid/old test data"""
    test_db_path = Path(__file__).resolve().parent.parent / "data" / "chroma_db"
    if test_db_path.exists():
        shutil.rmtree(test_db_path)
        print(f"Cleaned up {test_db_path}")

def test_single_document_embedding():
    print(">>> Starting Test: Single Document Embedding & Indexing")
    
    indexer = RecruitIndexer()
    
    # 1. Index the sample data
    print("Indexing sample data...")
    indexer.create_vectorstore([SAMPLE_DATA])
    
    # 2. Verify Search
    query = "정보보안 및 시스템 운영"
    print(f"Searching for: '{query}'")
    results = indexer.search_recruitments(query, k=1)
    
    if not results:
        print("[FAIL] No results found.")
        sys.exit(1)
        
    top_result = results[0]
    top_result = results[0]
    
    # 3. Verify Unique ID Logic (company_title)
    print("Verifying Unique ID Generation...")
    expected_id = f"{SAMPLE_DATA['company']}_{SAMPLE_DATA['title']}"
    
    # Instantiate Chroma to validte ID existence directly
    vectorstore = Chroma(
        collection_name="recruit_collection",
        embedding_function=indexer.embedding_model,
        persist_directory=indexer.persist_dir
    )
    
    get_result = vectorstore.get(ids=[expected_id])
    if get_result and len(get_result['ids']) > 0:
        print(f"[PASS] Successfully retrieved document by ID: {expected_id}")
    else:
        print(f"[FAIL] Could not find document with expected ID: {expected_id}")
        # Debug: check what IDs are there
        all_ids = vectorstore.get()['ids']
        print(f"Existing IDs sample: {all_ids[:5]}")
        sys.exit(1)
    
    # 3. Verify Metadata Policy (All 13 fields should be present)
    print("Verifying Metadata...")
    metadata = top_result.metadata
    
    missing_fields = []
    for key in SAMPLE_DATA.keys():
        if key not in metadata:
            missing_fields.append(key)
            
    if missing_fields:
        print(f"[FAIL] Missing metadata fields: {missing_fields}")
        sys.exit(1)
    else:
        print("[PASS] All metadata fields preserved.")
        
    # 4. Verify Content Concatenation Policy
    print("Verifying Page Content...")
    content = top_result.page_content
    expected_parts = [
        "주요 업무: 정보 시스템 개발 및 운영",
        "자격 요건: 컴퓨터공학",
        "우대 사항: 정보보안 관련 자격증"
    ]
    
    for part in expected_parts:
        if part not in content:
            print(f"[FAIL] Content missing part: '{part}'")
            print(f"Actual content: {content}")
            sys.exit(1)
            
    print("[PASS] Content concatenation logic verified.")
    print(">>> All Tests Passed!")

if __name__ == "__main__":
    # clean_test_env() # Optional: clean before run
    test_single_document_embedding()
