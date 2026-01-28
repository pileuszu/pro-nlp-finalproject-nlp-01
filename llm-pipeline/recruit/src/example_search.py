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
        # 실제 API 호출 활성화
        query_gen = QueryCreator()
        generated_queries = query_gen.generate_queries(user_data)
        
        # 테스트용 하드코딩된 쿼리는 주석 처리
        # generated_queries = {
        #     "query_a": "Python PyTorch Java Spring Boot NLP LLM RAG AWS Docker 기술 스택을 보유한 AI 백엔드 엔지니어",
        #     "query_b": "RAG 파이프라인 최적화 모델 성능 튜닝 TAPT 앙상블 데이터 중심 문제 해결 및 API 응답 속도 개선 경험",
        #     "query_c": "자연어 처리(NLP) 모델링 및 LLM 어플리케이션 개발 경험과 웹 서버 인프라 구축 역량을 겸비한 풀스택 AI 엔지니어"
        # }
        
        print("\n--- [RAG 테스트] 생성된 검색 쿼리 ---")
        for k, v in generated_queries.items():
            print(f"[{k.upper()}]: {v}")

        # 3. Recruit Indexer를 통한 검색
        indexer = RecruitIndexer()
        
        # 3-1. 통합 검색 및 필터링/중복 제거 로직
        all_candidates = []
        SCORE_THRESHOLD = 1  # 거리값이 0.5 이하인 것만 (낮을수록 유사)
        
        for q_type in ['query_a', 'query_b', 'query_c']:
            print(f"\n[쿼리 {q_type.upper()}] 검색 중...")
            search_query = generated_queries[q_type]
            results_with_scores = indexer.search_recruitments_with_scores(search_query, k=10)
            
            # 쿼리별 개별 결과 출력
            for i, (doc, score) in enumerate(results_with_scores):
                status = "✅" if score <= SCORE_THRESHOLD else "❌ (제외)"
                print(f"  - {status} {score:.4f} | {doc.metadata.get('company')} - {doc.metadata.get('title')}")
            
            all_candidates.extend(results_with_scores)
        
        # 중복 제거 및 필터링
        unique_candidates = {}
        for doc, score in all_candidates:
            if score > SCORE_THRESHOLD:
                continue
                
            # recruit_indexer.py에서 저장한 unique_id를 바로 사용
            uid = doc.metadata.get('unique_id')
            
            if uid not in unique_candidates or score < unique_candidates[uid]['score']:
                unique_candidates[uid] = {
                    'doc': doc,
                    'score': score
                }
        
        final_candidates = [v['doc'] for v in unique_candidates.values()]
        
        print(f"\n--- 최종 필터링 완료: {len(final_candidates)}개 후보군 ---")
        for i, doc in enumerate(final_candidates):
             print(f"  {i+1}. {doc.metadata.get('company')} - {doc.metadata.get('title')}")

        # 4. LLM 최종 추천 (Re-ranking)
        if not final_candidates:
            print("⚠️ 필터링 조건을 만족하는 공고가 없어 최종 추천을 진행하지 않습니다.")
        else:
            print("\n--- LLM 최종 추천 분석 중... ---")
            query_gen = QueryCreator() 
            final_result = query_gen.rank_final_recommendations(user_data, final_candidates)
            
            print("\n🎯 [최종 추천 TOP 3 공고]")
            for rec in final_result.get('recommendations', []):
                print(f"\n[{rec['rank']}위] {rec['company']} - {rec['title']}")
                print(f"✅ 추천 사유: {rec['reason']}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()
