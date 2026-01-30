import json
import logging
from typing import Dict
from langchain_naver import ChatClovaX
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from common.config import settings

logger = logging.getLogger(__name__)

class CoverLetterGenerator:
    """
    Handles AI interactions for Cover Letter generation using HyperCLOVA X.
    """
    def __init__(self):
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            api_key = settings.NCP_CLOVASTUDIO_API_KEY
            if not api_key:
                logger.error("NCP_CLOVASTUDIO_API_KEY is not set. AI features will not work.")
                raise ValueError("NCP API Key is missing")
            
            self._llm = ChatClovaX(
                model="HCX-007",
                api_key=api_key,
                temperature=0.5,
                max_tokens=2048,
            )
        return self._llm

    def analyze_gap(self, user_context: str, job_req: str) -> Dict:
        """
        Analyzes the gap between user experience and job requirements.
        """
        prompt = PromptTemplate.from_template(
            """당신은 채용 분석 전문가입니다. 
            지원자의 경험과 채용 공고를 비교하여 분석 결과를 JSON으로 출력하세요.
            
            [채용 공고 요약]
            {job_req}
            
            [지원자 경험]
            {user_context}
            
            반드시 아래 JSON 형식으로만 출력하세요:
            {{
                "matching_points": ["매칭점1", "매칭점2"],
                "missing_elements": ["부족한점1", "부족한점2"],
                "overall_fit": "상/중/하 판단"
            }}
            """
        )
        chain = prompt | self.llm | JsonOutputParser()
        try:
            return chain.invoke({"job_req": job_req, "user_context": user_context})
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            return {}

    def generate_answer(self, company_name, job_title, question, context, gap_analysis, tone) -> Dict:
        """
        Generates the cover letter answer.
        """
        prompt = PromptTemplate.from_template(
            """당신은 {tone} 톤앤매너를 구사하는 전문 자기소개서 컨설턴트입니다.
            지원자의 경험을 바탕으로 해당 문항에 대한 최적의 답변을 작성하세요.
            
            **기업**: {company_name}
            **직무**: {job_title}
            **문항**: {question}
            
            **참고 경험**:
            {context}
            
            **분석 참고**:
            {gap_analysis}
            
            답변은 다음 JSON 구조로 작성하세요:
            {{
                "content": "작성된 자기소개서 본문 (700자 내외)",
                "key_points": ["강조된 역량1", "강조된 역량2"],
                "suggested_improvements": ["개선 제안1", "개선 제안2"]
            }}
            """
        )
        chain = prompt | self.llm | JsonOutputParser()
        return chain.invoke({
            "company_name": company_name,
            "job_title": job_title,
            "question": question,
            "context": context,
            "gap_analysis": json.dumps(gap_analysis, ensure_ascii=False),
            "tone": tone
        })
