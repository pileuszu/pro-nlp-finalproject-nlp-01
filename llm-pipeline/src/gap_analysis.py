"""
Gap Analysis 모듈
- LangChain 기반 분석 체인
- PydanticOutputParser로 구조화된 출력
"""
from typing import List, Dict, Any

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.documents import Document

from config.settings import GOOGLE_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from src.schemas import GapAnalysisResult, ResumeGenerationResult, JobAnalysisResult
from src.prompt_templates import (
    GAP_ANALYSIS_PROMPT,
    RESUME_GENERATION_PROMPT,
    SIMPLE_RESUME_PROMPT,
    QUESTION_BASED_RESUME_PROMPT
)
from src.retrieval import HybridRetriever
from src.data_loader import load_company_data, load_user_data


def get_llm() -> ChatGoogleGenerativeAI:
    """LLM 인스턴스 생성"""
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=LLM_TEMPERATURE
    )


def analyze_gap(
    user_experiences: List[Document],
    job_requirements: str
) -> GapAnalysisResult:
    """
    Gap 분석 수행
    - 사용자 경험과 채용 요건 비교
    - PydanticOutputParser로 구조화된 결과 반환
    """
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=GapAnalysisResult)
    
    # 경험 텍스트 결합
    experiences_text = "\n\n---\n\n".join([
        f"[프로젝트: {doc.metadata.get('project_name', 'N/A')}]\n"
        f"역할: {doc.metadata.get('role', 'N/A')}\n"
        f"기술스택: {doc.metadata.get('tech_stack', 'N/A')}\n"
        f"내용:\n{doc.page_content}"
        for doc in user_experiences
    ])
    
    prompt = PromptTemplate(
        template=GAP_ANALYSIS_PROMPT,
        input_variables=["job_requirements", "user_experiences"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    
    result = chain.invoke({
        "job_requirements": job_requirements,
        "user_experiences": experiences_text
    })
    
    return result


def generate_resume(
    user_experiences: List[Document],
    gap_result: GapAnalysisResult,
    company_data: Dict[str, Any],
    question: Dict[str, Any] = None
) -> ResumeGenerationResult:
    """
    자소서 생성
    - Gap 분석 결과를 반영하여 자소서 작성
    - CoT 프롬프트로 논리적인 글 생성
    - question이 주어지면 해당 문항에 맞는 자소서 생성
    """
    llm = get_llm()
    parser = PydanticOutputParser(pydantic_object=ResumeGenerationResult)
    
    company_info = company_data.get("company_info", {})
    job_position = company_data.get("job_position", {})
    
    # 경험 텍스트 결합
    experiences_text = "\n\n---\n\n".join([
        f"[프로젝트: {doc.metadata.get('project_name', 'N/A')}]\n"
        f"역할: {doc.metadata.get('role', 'N/A')}\n"
        f"기술스택: {doc.metadata.get('tech_stack', 'N/A')}\n"
        f"내용:\n{doc.page_content}"
        for doc in user_experiences
    ])
    
    # 문항이 주어진 경우 해당 문항에 맞는 프롬프트 사용
    if question:
        template = QUESTION_BASED_RESUME_PROMPT
        input_vars = {
            "company_name": company_info.get("company_name", ""),
            "core_values": ", ".join(company_info.get("core_values", [])),
            "job_title": job_position.get("title", ""),
            "user_experiences": experiences_text,
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
    
    chain = prompt | llm | parser
    result = chain.invoke(input_vars)
    
    return result


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
        # 문항이 있으면 각 문항별로 자소서 생성
        for question in resume_questions:
            resume = generate_resume(relevant_experiences, gap_result, company_data, question)
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

