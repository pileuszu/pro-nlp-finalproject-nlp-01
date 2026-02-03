from query_creator import QueryCreator
from recruit_indexer import RecruitIndexer
import json

def main():
    # 1. 사용자 데이터 정의 (예시)
    user_data = {
    "profile": {
        "user_id": "USER_001",
        "name": "김준비",
        "job_title": "Backend Developer (3년차)",
        "summary": "트래픽이 몰리는 상황에서의 시스템 안정성을 최우선으로 생각하며, 비동기 아키텍처를 통해 성능을 극대화한 경험이 있습니다."
    },
    "projects": [
        {
            "project_name": "이커머스 타임세일 선착순 시스템 구축",
            "period": "2024.01 - 2024.06",
            "role": "Backend Lead",
            "tech_stack": ["Python", "FastAPI", "Redis", "Kafka", "Docker"],
            # RAG 임베딩의 핵심이 될 상세 설명 (Chunking 대상)
            "description_for_embedding": """
            [문제 상황]
            특가 이벤트 오픈 시 순간적으로 트래픽이 몰려 서버가 다운되고, 동기 방식의 주문 처리로 인해 응답 지연(Latency)이 3초 이상 발생하는 문제가 있었습니다.

            [해결 과정: 대용량 트래픽 처리]
            초당 10,000건(10,000 TPS)의 동시 접속 요청을 감당하기 위해 Redis Sorted Set 기반의 '대기열 시스템'을 설계했습니다. 
            이를 통해 DB에 직접적인 부하가 가는 것을 막고, 유량 제어(Flow Control)를 구현하여 시스템 다운을 방지했습니다.

            [해결 과정: 비동기 아키텍처 도입]
            기존 Django의 동기(Synchronous) 방식 주문 로직을 FastAPI와 Asyncio를 활용한 비동기 논블로킹(Asynchronous Non-blocking) 구조로 전면 전환했습니다.
            그 결과, I/O 대기 시간을 획기적으로 줄여 평균 응답 속도를 200ms 이내로 50% 이상 단축시켰습니다.
            또한, 주문 완료 후 알림 발송 로직은 Kafka 메시지 큐로 분리하여 메인 트랜잭션의 부하를 덜어냈습니다.
            """
        },
        {
            "project_name": "레거시 결제 모듈 리팩토링",
            "period": "2023.05 - 2023.11",
            "role": "Backend Developer",
            "tech_stack": ["Python", "Django", "PostgreSQL"],
            "description_for_embedding": """
            [문제 상황]
            5년 넘게 운영된 레거시 모놀리식 코드에서 결제 로직이 여러 곳에 산재되어 있어, 수정 시 사이드 이펙트(Side Effect)가 빈번하게 발생했습니다.

            [해결 과정: 리팩토링]
            결제 로직을 별도의 모듈로 응집시키고, 의존성을 주입(Dependency Injection)하는 방식으로 구조를 개선했습니다. 
            복잡하게 얽힌 중복 쿼리를 ORM 최적화하여 쿼리 실행 계획(Explain Analyze) 기준으로 비용을 30% 절감했습니다.
            """
        }
    ],
    "skills": ["High Traffic Handling", "Async/Await", "System Architecture", "Performance Tuning"]
    }

    # 2. Query Creator 초기화 및 쿼리 생성
    try:
        query_gen = QueryCreator()
        generated_queries = query_gen.generate_queries(user_data)
        
        print(f"\n--- [RAG 테스트] 생성된 검색 쿼리: 총 {len(generated_queries)}개 ---")
        for i, q in enumerate(generated_queries):
            print(f"[{i+1}] {q}")

        # 3. Recruit Indexer를 통한 검색
        indexer = RecruitIndexer()
        
        # 3-1. 통합 검색 및 필터링/중복 제거 로직
        all_candidates = []
        SCORE_THRESHOLD = 1.2  # 기준 완화 (범위를 넓혀서 다양하게 가져옴)
        
        print("\n--- 통합 검색 시작 ---")
        for idx, search_query in enumerate(generated_queries):
            print(f"\n[쿼리 {idx+1}] '{search_query}' 검색 중...")
            
            # Hybrid Search (returns List[Document])
            results = indexer.search_hybrid(search_query, k=5)
            
            for rank, doc in enumerate(results):
                # Synthetic score generation (Rank based)
                # Lower is better in our downstream logic. 
                # Rank 0 -> 0.1, Rank 1 -> 0.15, etc.
                score = 0.1 + (rank * 0.05)
                
                # 점수 확인용 로그
                print(f"  -> ({score:.4f}) [Hybrid Rank {rank}] {doc.metadata.get('company')} - {doc.metadata.get('title')}")
                # 임시로 모든 결과 수집
                all_candidates.append((doc, score))
        
        # 중복 제거 (unique_id 기준, 점수가 더 낮은(좋은) 것을 유지)
        unique_candidates = {}
        for doc, score in all_candidates:
            if score > SCORE_THRESHOLD:
                continue
                
            uid = doc.metadata.get('unique_id')
            if not uid: # ID가 없는 경우 본문 해시 등으로 대체하거나 건너뜀 (여기선 title+company로 가정 or 건너뜀)
                continue
            
            # 이미 존재하면 점수가 더 좋을때만 교체
            if uid not in unique_candidates or score < unique_candidates[uid]['score']:
                unique_candidates[uid] = {
                    'doc': doc,
                    'score': score
                }
        
        # 딕셔너리 값들만 추출 후 점수순 정렬
        sorted_candidates = sorted(
            unique_candidates.values(), 
            key=lambda x: x['score']
        )
        
        # 상위 10~15개만 LLM에게 전달
        final_candidates = [item['doc'] for item in sorted_candidates[:15]]
        
        print(f"\n--- 최종 필터링 및 중복 제거 완료: {len(final_candidates)}개 후보군 ---")
        for i, doc in enumerate(final_candidates):
            score = unique_candidates[doc.metadata.get('unique_id')]['score']
            print(f"  {i+1}. [{score:.4f}] {doc.metadata.get('company')} - {doc.metadata.get('title')}")

        # 4. LLM 최종 추천 (Re-ranking)
        if not final_candidates:
            print("⚠️ 필터링 조건을 만족하는 공고가 없어 최종 추천을 진행하지 않습니다.")
        else:
            print("\n--- LLM 최종 추천 분석 중... ---")
            
            final_result = query_gen.rank_final_recommendations(user_data, final_candidates)
            
            print("\n🎯 [최종 추천 TOP 3 공고]")
            recommendations = final_result.get('recommendations', [])
            
            # ID로 Document를 찾기 위한 매핑 생성
            candidate_map = {doc.metadata.get('unique_id'): doc for doc in final_candidates}
            # Debug: Print available IDs
            # print(f"DEBUG: Available IDs in map: {list(candidate_map.keys())}")
            
            for rec in recommendations:
                print(f"\n[{rec.get('rank', '?')}위] {rec.get('company', 'Unknown')} - {rec.get('title', 'Unknown')}")
                
                # URL 찾기
                rec_id = rec.get('unique_id')
                # print(f"DEBUG: LLM returned ID: '{rec_id}'")
                
                if rec_id and rec_id in candidate_map:
                    link = candidate_map[rec_id].metadata.get('link', 'Link not found')
                    print(f"🔗 링크: {link}")
                else:
                    # Fallback: ID mismatch, try matching by Company + Title
                    found_doc = None
                    rec_company = rec.get('company', '').strip()
                    rec_title = rec.get('title', '').strip()
                    
                    for doc in candidate_map.values():
                        doc_company = doc.metadata.get('company', '').strip()
                        doc_title = doc.metadata.get('title', '').strip()
                        
                        # Compare loosely (in case of minor spacing diffs)
                        if (doc_company == rec_company or doc_company in rec_company or rec_company in doc_company) and \
                           (doc_title == rec_title or doc_title in rec_title or rec_title in doc_title):
                            found_doc = doc
                            break
                    
                    if found_doc:
                        link = found_doc.metadata.get('link', 'Link not found')
                        print(f"🔗 링크: {link} (유사 매칭 성공)")
                    else:
                        print(f"⚠️ 링크를 찾을 수 없음 (ID/정보 불일치: '{rec_id}')")
                
                print(f"✅ 추천 사유: {rec.get('reason', 'N/A')}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
