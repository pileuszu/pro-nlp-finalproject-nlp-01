import os
import json
from pathlib import Path
from typing import Dict, Optional, List, Any

from dotenv import load_dotenv

# 현재 파일 위치: /data/ephemeral/git/pro-nlp-finalproject-nlp-01/llm-pipeline/recruit/query_creator.py
# .env 위치: /data/ephemeral/git/pro-nlp-finalproject-nlp-01/.env
# 현재 파일 위치: .../llm-pipeline/recruit/src/query_creator.py
# .env 위치: .../llm-pipeline/recruit/.env
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"

# .env 파일 로드 (절대 경로 지정)
load_dotenv(dotenv_path=env_path)

# 현재 파일 위치: /data/ephemeral/git/pro-nlp-finalproject-nlp-01/llm-pipeline/recruit/query_creator.py
# .env 위치: /data/ephemeral/git/pro-nlp-finalproject-nlp-01/.env
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
env_path = BASE_DIR / ".env"

# .env 파일 로드 (절대 경로 지정)
load_dotenv(dotenv_path=env_path)

from common.clova_client import ClovaStudioClient

class QueryCreator:
    """
    사용자의 포트폴리오 데이터를 분석하여 HyperClovaX를 통해 
    Recruit Indexer 검색에 최적화된 3가지 유형의 쿼리를 생성하는 클래스입니다.
    """
    def __init__(self):
        self.client = ClovaStudioClient()
        
        self.system_prompt = """
        당신은 AI 기반 채용 매칭 전문가입니다. 
        제공된 사용자의 프로젝트 경험을 바탕으로, 검색 엔진(Vector DB)에서 가장 적합한 공고를 찾기 위한 검색 쿼리를 생성해주세요.
        
        각 프로젝트마다 다음 3가지 관점의 쿼리를 생성해야 합니다:
        1. 기술 스택 중심: 해당 프로젝트에서 사용된 핵심 기술 및 프레임워크 (예: Python, FastAPI, Redis 등)
        2. 문제 해결 중심: 프로젝트에서 해결한 주요 과제나 성과 (예: 대용량 트래픽 처리, 쿼리 최적화 등)
        3. 도메인/주제 중심: 프로젝트의 산업 분야나 서비스 특성 (예: 이커머스, 핀테크, 추천 시스템 등)

        입력된 모든 프로젝트에 대해 각각 3개씩 쿼리를 생성하여, 총 (프로젝트 수 * 3)개의 쿼리 리스트를 반환하세요.
        출력은 반드시 문자열 리스트(Array of strings) 형식의 JSON이어야 합니다.
        """

    def generate_queries(self, user_data: Dict) -> List[str]:
        """
        입력받은 user_data의 프로젝트들을 분석하여 프로젝트당 3개의 검색 쿼리를 생성합니다.
        반환값은 쿼리 문자열들의 리스트입니다.
        """
        
        projects = user_data.get("projects", [])
        if not projects:
            return ["백엔드 개발자 채용", "서버 개발 경험", "Python 웹 개발"]

        user_input = f"""
        다음 사용자의 프로젝트 내역을 분석해서 프로젝트별로 검색용 쿼리를 3개씩(기술, 문제해결, 도메인) 생성해줘.
        
        [프로젝트 목록]
        {json.dumps(projects, ensure_ascii=False)}
        
        총 {len(projects) * 3}개의 쿼리가 포함된 단일 리스트로 반환해줘.
        """

        try:
            # HyperClovaX 호출
            response_text = self.client.generate_content(
                system_prompt=self.system_prompt,
                user_prompt=user_input,
                max_tokens=2000
            )
            
            if not isinstance(response_text, str):
                print(f"Error: Clova API returned non-string response: {response_text}")
                raise ValueError(f"API call failed with status code: {response_text}")

            # JSON 파싱 시도 (Markdown code block 제거 등 전처리 필요할 수 있음)
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text.replace("```json", "").replace("```", "")
            elif clean_text.startswith("```"):
                clean_text = clean_text.replace("```", "")
                
            queries = json.loads(clean_text)
            
            # 만약 { "queries": [...] } 형태로 올 경우 처리
            if isinstance(queries, dict):
                queries = queries.get("queries", list(queries.values())[0])
            
            if not isinstance(queries, list):
                # 형식이 맞지 않으면 기본값 반환 (강제 변환 시도)
                return [str(queries)]

            return [str(q) for q in queries]
            
        except Exception as e:
            print(f"Error generating queries: {e}")
            # Fallback: 간단한 조합으로 생성
            base_queries = []
            for p in projects:
                tech = " ".join(p.get("tech_stack", []))
                base_queries.append(f"{tech} 개발자")
                base_queries.append(f"{p.get('project_name')} 경험")
                base_queries.append("백엔드 시스템 구축")
            return base_queries

    def rank_final_recommendations(self, user_data: Dict, candidates: List[Any]) -> Dict:
        """
        검색된 후보 공고 리스트와 사용자 데이터를 비교하여 
        최종 추천 TOP 3 공고와 그 선정 사유를 생성합니다.
        unique_id를 포함하여 반환합니다.
        """
        if not candidates:
            return {"recommendations": [], "message": "추천할 후보 공고가 없습니다."}

        # 후보 공고 텍스트 요약 (LLM에게 전달할 양 조절)
        candidate_texts = []
        for i, doc in enumerate(candidates):
            meta = doc.metadata
            summary = (
                f"[공고 {i+1}]\n"
                f"ID: {meta.get('unique_id')}\n"
                f"회사: {meta.get('company')}\n"
                f"직무: {meta.get('title')}\n"
                f"주요업무: {doc.page_content[:300]}...\n"
                "-------------------\n"
            )
            candidate_texts.append(summary)

        prompt = f"""
        아래 사용자의 포트폴리오와 검색된 공고 후보군을 비교하여, 가장 적합한 TOP 3 공고를 선정하고 추천 사유를 작성해주세요.

        [사용자 데이터]
        {json.dumps(user_data, ensure_ascii=False)}

        [후보 공고 리스트]
        {"".join(candidate_texts)}

        ### 요구 사항:
        1. 후보군 중에서 사용자의 기술 스택과 강점(성과)에 가장 잘 맞는 공고를 최대 3개 선정하세요.
        2. 각 추천 공고마다 왜 이 공고가 사용자에게 적합한지 '추천 사유'를 구체적으로 작성하세요.
        3. 각 공고에 부여된 고유 ID(ID 필드값)를 정확히 응답에 포함하세요.
        4. 반드시 아래 JSON 형식으로만 응답하세요.

        ### 응답 형식:
        {{
            "recommendations": [
                {{
                    "rank": 1,
                    "unique_id": "해당 공고의 고유 ID(예: 회사명_공고제목)",
                    "company": "회사명",
                    "title": "공고 제목",
                    "reason": "추천 사유 (사용자의 어떤 경험이 이 공고의 어떤 부분에 기여할 수 있는지)"
                }}
            ]
        }}
        """

        try:
            response_text = self.client.generate_content(
                system_prompt="당신은 정교한 매칭을 수행하는 채용 컨설턴트입니다.",
                user_prompt=prompt,
                max_tokens=2000
            )
            
            if not isinstance(response_text, str):
                print(f"Error: Clova API returned non-string response: {response_text}")
                return {"recommendations": [], "error": f"API call failed with status code: {response_text}"}

            # JSON 파싱 시도
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text.replace("```json", "").replace("```", "")
            elif clean_text.startswith("```"):
                clean_text = clean_text.replace("```", "")

            return json.loads(clean_text)
        except Exception as e:
            print(f"Error in ranking: {e}")
            return {"recommendations": [], "error": str(e)}

# if __name__ == "__main__":
#     # 테스트용 Sample Data
#     sample_user_data = {
#         "profile": {
#             "user_id": "USER_001",
#             "name": "김준비",
#             "job_title": "Backend Developer (3년차)",
#             "summary": "트래픽이 몰리는 상황에서의 시스템 안정성을 최우선으로 생각하며, 비동기 아키텍처를 통해 성능을 극대화한 경험이 있습니다."
#         },
#         "projects": [
#             {
#                 "project_name": "이커머스 타임세일 선착순 시스템 구축",
#                 "tech_stack": ["Python", "FastAPI", "Redis", "Kafka"],
#                 "description_for_embedding": "초당 10,000건의 트래픽을 처리하는 Redis 대기열 시스템 설계 및 비동기 전환."
#             }
#         ],
#         "skills": ["High Traffic Handling", "Async/Await"]
#     }

#     try:
#         creator = QueryCreator()
#         queries = creator.generate_queries(sample_user_data)
#         print(json.dumps(queries, indent=2, ensure_ascii=False))
#     except Exception as e:
#         print(f"실행 오류: {e}")

# if __name__ == "__main__":
#     # 테스트용 Sample Data
#     sample_user_data = {
#         "profile": {
#             "user_id": "USER_001",
#             "name": "김준비",
#             "job_title": "Backend Developer (3년차)",
#             "summary": "트래픽이 몰리는 상황에서의 시스템 안정성을 최우선으로 생각하며, 비동기 아키텍처를 통해 성능을 극대화한 경험이 있습니다."
#         },
#         "projects": [
#             {
#                 "project_name": "이커머스 타임세일 선착순 시스템 구축",
#                 "period": "2024.01 - 2024.06",
#                 "role": "Backend Lead",
#                 "tech_stack": ["Python", "FastAPI", "Redis", "Kafka", "Docker"],
#                 "description_for_embedding": """
#                 [문제 상황]
#                 특가 이벤트 오픈 시 순간적으로 트래픽이 몰려 서버가 다운되고, 동기 방식의 주문 처리로 인해 응답 지연(Latency)이 3초 이상 발생하는 문제가 있었습니다.
#                 [해결 과정: 대용량 트래픽 처리]
#                 초당 10,000건(10,000 TPS)의 동시 접속 요청을 감당하기 위해 Redis Sorted Set 기반의 '대기열 시스템'을 설계했습니다. 
#                 이를 통해 DB에 직접적인 부하가 가는 것을 막고, 유량 제어(Flow Control)를 구현하여 시스템 다운을 방지했습니다.
#                 [해결 과정: 비동기 아키텍처 도입]
#                 기존 Django의 동기(Synchronous) 방식 주문 로직을 FastAPI와 Asyncio를 활용한 비동기 논블로킹(Asynchronous Non-blocking) 구조로 전면 전환했습니다.
#                 그 결과, I/O 대기 시간을 획기적으로 줄여 평균 응답 속도를 200ms 이내로 50% 이상 단축시켰습니다.
#                 """
#             }
#         ],
#         "skills": ["High Traffic Handling", "Async/Await", "System Architecture", "Performance Tuning"]
#     }

#     # 사용 예시
#     try:
#         # GEMINI_API_KEY 환경변수가 설정되어 있어야 합니다.
#         creator = QueryCreator()
#         queries = creator.generate_queries(sample_user_data)
        
#         print("\n=== 생성된 검색 쿼리 ===")
#         print(f"A (기술/역량): {queries['query_a']}")
#         print(f"B (문제 해결): {queries['query_b']}")
#         print(f"C (프로젝트): {queries['query_c']}")
        
#     except Exception as e:
#         print(f"실행 오류: {e}")
