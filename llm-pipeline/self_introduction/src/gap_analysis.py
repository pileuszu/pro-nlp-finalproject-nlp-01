"""
Gap Analysis 모듈
- LangChain 기반 분석 체인
- PydanticOutputParser로 구조화된 출력
- HyperCLOVA OpenAI 호환 API 사용
"""
from typing import List, Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.documents import Document

from config.settings import (
    CLOVA_API_KEY, CLOVA_BASE_URL, LLM_MODEL, LLM_TEMPERATURE,
    LLM_TOP_P, LLM_REPETITION_PENALTY, LLM_MAX_TOKENS
)
from src.schemas import GapAnalysisResult, ResumeGenerationResult, JobAnalysisResult, ResumeOutlineResult
from src.prompt_templates import (
    GAP_ANALYSIS_PROMPT,
    RESUME_GENERATION_PROMPT,
    SIMPLE_RESUME_PROMPT,
    QUESTION_BASED_RESUME_PROMPT,
    QUESTION_BASED_OUTLINE_PROMPT
)
from src.retrieval import HybridRetriever
from src.data_loader import load_company_data, load_user_data


def get_llm() -> ChatOpenAI:
    """LLM 인스턴스 생성 (HyperCLOVA OpenAI 호환 API)"""
    return ChatOpenAI(
        model=LLM_MODEL,
        api_key=CLOVA_API_KEY,
        base_url=CLOVA_BASE_URL,
        temperature=LLM_TEMPERATURE,
        extra_body={
            "topP": LLM_TOP_P,
            "repetitionPenalty": LLM_REPETITION_PENALTY,
            "maxTokens": LLM_MAX_TOKENS
        }
    )


def format_experiences(documents: List[Document]) -> str:
    """문서 리스트를 LLM 입력용 텍스트로 포맷팅"""
    return "\n\n---\n\n".join([
        f"[프로젝트: {doc.metadata.get('project_name', 'N/A')}]\n"
        f"역할: {doc.metadata.get('role', 'N/A')}\n"
        f"기술스택: {doc.metadata.get('tech_stack', 'N/A')}\n"
        f"내용:\n{doc.page_content}"
        for doc in documents
    ])


def parse_json_response(response_text: str, pydantic_class):
    """LLM 응답에서 JSON을 추출하여 Pydantic 객체로 변환"""
    import json
    import re
    
    text = response_text
    
    # 1. JSON 블록 추출 시도 (```json ... ``` 또는 ``` ... ```)
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    else:
        # 2. 중괄호로 시작하고 끝나는 부분 추출
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)
    
    try:
        data = json.loads(text)
        return pydantic_class(**data)
    except (json.JSONDecodeError, Exception) as e:
        # 파싱 실패 시 기본값 반환
        raise ValueError(f"JSON 파싱 실패: {str(e)}\n원본: {response_text[:500]}")


def analyze_gap(
    user_experiences: List[Document],
    job_requirements: str
) -> GapAnalysisResult:
    """
    Gap 분석 수행
    - 사용자 경험과 채용 요건 비교
    - HyperCLOVA 호환 JSON 파싱
    """
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=GapAnalysisResult)
    
    # 경험 텍스트 결합
    experiences_text = format_experiences(user_experiences)
    
    prompt = PromptTemplate(
        template=GAP_ANALYSIS_PROMPT,
        input_variables=["job_requirements", "user_experiences"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # LLM 호출 후 수동 파싱
    chain = prompt | llm
    response = chain.invoke({
        "job_requirements": job_requirements,
        "user_experiences": experiences_text
    })
    
    # 응답에서 content 추출
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    return parse_json_response(response_text, GapAnalysisResult)



def generate_resume(
    user_experiences: List[Document],
    gap_result: GapAnalysisResult,
    company_data: Dict[str, Any],
    question: Dict[str, Any] = None,
    used_experiences: List[str] = None  # 이전 문항에서 사용한 경험 목록
) -> ResumeGenerationResult:
    """
    자소서 생성
    - Gap 분석 결과를 반영하여 자소서 작성
    - CoT 프롬프트로 논리적인 글 생성
    - question이 주어지면 해당 문항에 맞는 자소서 생성
    - used_experiences: 이전 문항에서 사용한 프로젝트명 목록 (중복 방지용)
    """
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=ResumeGenerationResult)
    
    company_info = company_data.get("company_info", {})
    job_position = company_data.get("job_position", {})
    
    # 경험 텍스트 결합
    experiences_text = format_experiences(user_experiences)
    
    # 이전 사용 경험 정보 추가
    used_exp_text = ""
    if used_experiences:
        used_exp_text = f"\n⚠️ 다음 경험/프로젝트는 이전 문항에서 이미 사용했으므로 다른 경험을 우선 사용하세요: {', '.join(used_experiences)}"
    
    # 문항이 주어진 경우 해당 문항에 맞는 프롬프트 사용
    if question:
        template = QUESTION_BASED_RESUME_PROMPT
        input_vars = {
            "company_name": company_info.get("company_name", ""),
            "core_values": ", ".join(company_info.get("core_values", [])),
            "job_title": job_position.get("title", ""),
            "user_experiences": experiences_text + used_exp_text,
            "question": question.get("question", ""),
            "max_length": question.get("max_length", 1000),
            "hint": question.get("hint", ""),
            "matching_points": ", ".join(gap_result.matching_points) if gap_result.matching_points else "해당 없음",
            "missing_elements": ", ".join(gap_result.missing_elements) if gap_result.missing_elements else "해당 없음"
        }
    elif gap_result.is_gap_found:
        template = RESUME_GENERATION_PROMPT
        input_vars = {
            "company_name": company_info.get("company_name", ""),
            "core_values": ", ".join(company_info.get("core_values", [])),
            "job_title": job_position.get("title", ""),
            "user_experiences": experiences_text,
            "max_length": 1000,  # 기본값 또는 대표값
            "matching_points": ", ".join(gap_result.matching_points),
            "missing_elements": ", ".join(gap_result.missing_elements)
        }
    else:
        template = SIMPLE_RESUME_PROMPT
        input_vars = {
            "company_name": company_info.get("company_name", ""),
            "core_values": ", ".join(company_info.get("core_values", [])),
            "job_title": job_position.get("title", ""),
            "user_experiences": experiences_text,
            "max_length": 1000  # 기본값 또는 대표값
        }
    
    prompt = PromptTemplate(
        template=template,
        input_variables=list(input_vars.keys()),
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # LLM 호출 후 수동 파싱
    chain = prompt | llm
    response = chain.invoke(input_vars)
    
    # 응답에서 content 추출
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    return parse_json_response(response_text, ResumeGenerationResult)


def run_full_analysis(user_id: str) -> Dict[str, Any]:
    """
    전체 분석 파이프라인 실행
    1. 데이터 로드
    2. Hybrid 검색으로 관련 경험 추출
    3. Gap 분석
    4. 각 문항별 자소서 생성
    """
    from src.embeddings import load_user_vectorstore
    from src.data_loader import get_all_user_documents
    
    # 1. 데이터 로드
    company_data = load_company_data()
    user_data = load_user_data(user_id)
    user_documents = get_all_user_documents(user_id)
    
    # 2. 벡터스토어 로드 및 Hybrid Retriever 생성
    vectorstore = load_user_vectorstore(user_id)
    retriever = HybridRetriever(vectorstore, user_documents)
    
    # 3. 채용 요건으로 검색
    job_requirements = company_data.get("job_requirements", {})
    query = job_requirements.get("summary", "")
    relevant_experiences = retriever.search(query)
    
    # 4. Gap 분석
    job_req_text = (
        f"{job_requirements.get('summary', '')}\n\n"
        f"상세 업무:\n" + 
        "\n".join(f"- {r}" for r in job_requirements.get("detailed_responsibilities", []))
    )
    
    gap_result = analyze_gap(relevant_experiences, job_req_text)
    
    # 5. 각 문항별 자소서 생성
    resume_questions = company_data.get("resume_questions", [])
    resumes = []
    
    if resume_questions:
        # 문항별 경험 분배: 이전 문항에서 사용한 경험 추적
        used_experiences = []
        
        for question in resume_questions:
            # 각 문항에 사용할 경험 선택 (이전에 사용하지 않은 것 우선)
            available_experiences = [
                exp for exp in relevant_experiences 
                if exp.metadata.get("project_name") not in used_experiences
            ]
            
            # 사용 가능한 경험이 없으면 전체에서 선택
            if not available_experiences:
                available_experiences = relevant_experiences
            
            # 첫 번째 사용 가능한 경험의 프로젝트명 기록
            if available_experiences:
                primary_project = available_experiences[0].metadata.get("project_name", "")
                if primary_project:
                    used_experiences.append(primary_project)
            
            # 문항별로 할당된 경험 정보 전달
            resume = generate_resume(
                available_experiences, 
                gap_result, 
                company_data, 
                question,
                used_experiences=used_experiences[:-1]  # 현재 제외한 이전 사용 경험
            )
            resumes.append({
                "question_id": question.get("id"),
                "question": question.get("question"),
                "max_length": question.get("max_length"),
                "resume": resume
            })
    else:
        # 문항이 없으면 기본 자소서 생성
        resume = generate_resume(relevant_experiences, gap_result, company_data)
        resumes.append({
            "question_id": 0,
            "question": "자기소개서",
            "max_length": 1000,
            "resume": resume
        })
    
    return {
        "user_id": user_id,
        "user_name": user_data.get("profile", {}).get("name", "Unknown"),
        "company_name": company_data.get("company_info", {}).get("company_name", "Unknown"),
        "relevant_experiences": relevant_experiences,
        "gap_analysis": gap_result,
        "resumes": resumes  # 복수형으로 변경
    }


def run_single_question_analysis(user_id: str, question_id: int) -> Dict[str, Any]:
    """
    특정 문항에 대한 분석 및 자소서 생성
    """
    from src.embeddings import load_user_vectorstore
    from src.data_loader import get_all_user_documents
    
    # 1. 데이터 로드
    company_data = load_company_data()
    user_data = load_user_data(user_id)
    user_documents = get_all_user_documents(user_id)
    
    # 2. 벡터스토어 로드 및 Hybrid Retriever 생성
    vectorstore = load_user_vectorstore(user_id)
    retriever = HybridRetriever(vectorstore, user_documents)
    
    # 3. 채용 요건으로 검색
    job_requirements = company_data.get("job_requirements", {})
    query = job_requirements.get("summary", "")
    relevant_experiences = retriever.search(query)
    
    # 4. Gap 분석
    job_req_text = (
        f"{job_requirements.get('summary', '')}\n\n"
        f"상세 업무:\n" + 
        "\n".join(f"- {r}" for r in job_requirements.get("detailed_responsibilities", []))
    )
    
    gap_result = analyze_gap(relevant_experiences, job_req_text)
    
    # 5. 특정 문항 찾기
    resume_questions = company_data.get("resume_questions", [])
    target_question = None
    for q in resume_questions:
        if q.get("id") == question_id:
            target_question = q
            break
    
    if not target_question:
        raise ValueError(f"문항 {question_id}을 찾을 수 없습니다.")
    
    # 6. 해당 문항 자소서 생성
    resume = generate_resume(relevant_experiences, gap_result, company_data, target_question)
    
    return {
        "user_id": user_id,
        "user_name": user_data.get("profile", {}).get("name", "Unknown"),
        "company_name": company_data.get("company_info", {}).get("company_name", "Unknown"),
        "relevant_experiences": relevant_experiences,
        "gap_analysis": gap_result,
        "resumes": [{
            "question_id": target_question.get("id"),
            "question": target_question.get("question"),
            "max_length": target_question.get("max_length"),
            "resume": resume
        }]
    }


def generate_outline(
    user_experiences: List[Document],
    gap_result: GapAnalysisResult,
    company_data: Dict[str, Any],
    question: Dict[str, Any]
) -> ResumeOutlineResult:
    """
    자소서 가이드라인(Outline) 생성
    """
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=ResumeOutlineResult)
    
    company_info = company_data.get("company_info", {})
    job_position = company_data.get("job_position", {})
    
    # 경험 텍스트 결합
    experiences_text = format_experiences(user_experiences)
    
    input_vars = {
        "company_name": company_info.get("company_name", ""),
        "core_values": ", ".join(company_info.get("core_values", [])),
        "job_title": job_position.get("title", ""),
        "user_experiences": experiences_text,
        "question": question.get("question", ""),
        "hint": question.get("hint", ""),
        "matching_points": ", ".join(gap_result.matching_points) if gap_result.matching_points else "해당 없음",
        "missing_elements": ", ".join(gap_result.missing_elements) if gap_result.missing_elements else "해당 없음"
    }
    
    prompt = PromptTemplate(
        template=QUESTION_BASED_OUTLINE_PROMPT,
        input_variables=list(input_vars.keys()),
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    result = chain.invoke(input_vars)
    
    return result


def run_full_outline_analysis(user_id: str) -> Dict[str, Any]:
    """
    자소서 가이드라인(Outline) 전체 분석 파이프라인
    """
    from src.embeddings import load_user_vectorstore
    from src.data_loader import get_all_user_documents
    
    # 1. 데이터 로드
    company_data = load_company_data()
    user_data = load_user_data(user_id)
    user_documents = get_all_user_documents(user_id)
    
    # 2. 벡터스토어 로드
    vectorstore = load_user_vectorstore(user_id)
    retriever = HybridRetriever(vectorstore, user_documents)
    
    # 3. 채용 요건으로 검색
    job_requirements = company_data.get("job_requirements", {})
    query = job_requirements.get("summary", "")
    relevant_experiences = retriever.search(query)
    
    # 4. Gap 분석
    job_req_text = (
        f"{job_requirements.get('summary', '')}\n\n"
        f"상세 업무:\n" + 
        "\n".join(f"- {r}" for r in job_requirements.get("detailed_responsibilities", []))
    )
    gap_result = analyze_gap(relevant_experiences, job_req_text)
    
    # 5. 각 문항별 Outline 생성
    resume_questions = company_data.get("resume_questions", [])
    outlines = []
    
    if resume_questions:
        for question in resume_questions:
            outline = generate_outline(relevant_experiences, gap_result, company_data, question)
            outlines.append({
                "question_id": question.get("id"),
                "question": question.get("question"),
                "outline": outline
            })
    else:
        # 문항이 없으면 기본 문항으로 Outline 생성
        default_question = {"id": 0, "question": "자기소개 및 지원동기", "hint": ""}
        outline = generate_outline(relevant_experiences, gap_result, company_data, default_question)
        outlines.append({
            "question_id": 0,
            "question": default_question["question"],
            "outline": outline
        })
        
    return {
        "user_id": user_id,
        "user_name": user_data.get("profile", {}).get("name", "Unknown"),
        "company_name": company_data.get("company_info", {}).get("company_name", "Unknown"),
        "relevant_experiences": relevant_experiences,
        "gap_analysis": gap_result,
        "outlines": outlines
    }


if __name__ == "__main__":
    from rich import print as rprint
    
    rprint("[bold yellow]Testing Gap Analysis...[/bold yellow]")
    
    result = run_full_analysis("user1")
    
    rprint("\n[bold green]Gap Analysis Result:[/bold green]")
    rprint(result["gap_analysis"])
    
    rprint("\n[bold blue]Generated Resumes:[/bold blue]")
    for item in result["resumes"]:
        rprint(f"\n--- 문항 {item['question_id']}: {item['question']} ---")
        rprint(item["resume"])

