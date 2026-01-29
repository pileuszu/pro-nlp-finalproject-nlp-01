"""
Pydantic 출력 스키마 정의
- PydanticOutputParser를 위한 구조화된 출력 형식
- LLM 출력을 JSON 객체로 강제
"""
from typing import List
from pydantic import BaseModel, Field


class GapAnalysisResult(BaseModel):
    """Gap 분석 결과 스키마"""
    
    is_gap_found: bool = Field(
        description="필수 역량이 누락되었으면 True, 충분히 매칭되면 False"
    )
    
    matching_points: List[str] = Field(
        description="사용자 경험과 채용 요건이 매칭되는 포인트 리스트 (한글로 작성)"
    )
    
    missing_elements: List[str] = Field(
        description="채용 요건 중 사용자 경험에서 부족한 역량 리스트 (한글로 작성)"
    )
    
    question_to_user: str = Field(
        description="Gap을 보완하기 위해 사용자에게 던질 질문 (Gap이 없으면 빈 문자열, 정중한 한국어 경어체 사용)"
    )
    
    reasoning: str = Field(
        description="판단의 근거를 한글로 상세히 서술하세요"
    )


class ResumeGenerationResult(BaseModel):
    """자소서 생성 결과 스키마 - 제출용 자연스러운 형식"""
    
    title: str = Field(
        description="자소서 항목 제목 (예: '지원동기', '성장과정' 등)"
    )
    
    content: str = Field(
        description="생성된 자소서 본문. 실제 제출 가능한 자연스러운 문장으로 작성. 레이블(Situation, Task 등) 없이 매끄럽게 연결된 글. 600~800자."
    )


class JobAnalysisResult(BaseModel):
    """직무 분석 결과 스키마"""
    
    core_requirements: List[str] = Field(
        description="채용 공고에서 추출한 핵심 필수 요건 리스트"
    )
    
    preferred_skills: List[str] = Field(
        description="우대 사항 리스트"
    )
    
    key_keywords: List[str] = Field(
        description="자소서 작성 시 반드시 언급해야 할 핵심 키워드"
    )
    
    company_culture: str = Field(
        description="기업의 인재상 및 문화 요약"
    )
