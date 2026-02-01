import json
import logging
from typing import Dict, Any
from langchain_naver import ChatClovaX
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from common.config import settings
from jobs.core.cover_letter.prompts import GAP_ANALYSIS_PROMPT, RESUME_GENERATION_PROMPT, QUESTION_BASED_OUTLINE_PROMPT
from jobs.core.cover_letter.schemas import GapAnalysisResult, ResumeGenerationResult, ResumeOutlineResult

logger = logging.getLogger(__name__)

class CoverLetterGenerator:
    """
    Handles AI interactions for Cover Letter generation using HyperCLOVA X.
    Updated to use PydanticOutputParser and CoT prompts.
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
                max_tokens=4096, # Increased for CoT
            )
        return self._llm

    def analyze_gap(self, user_context: str, job_req: str) -> Dict[str, Any]:
        """
        Analyzes the gap between user experience and job requirements.
        Returns a dict compatible with GapAnalysisResult schema.
        """
        parser = PydanticOutputParser(pydantic_object=GapAnalysisResult)
        
        prompt = PromptTemplate(
            template=GAP_ANALYSIS_PROMPT,
            input_variables=["job_req", "user_context"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({"job_req": job_req, "user_context": user_context})
            return result.model_dump()
        except Exception as e:
            logger.error(f"Gap analysis failed: {e}")
            # Return empty/safe default to prevent crash
            return {
                "is_gap_found": False, 
                "matching_points": [], 
                "missing_elements": [], 
                "question_to_user": "", 
                "reasoning": "분석에 실패했습니다."
            }

    def generate_answer(self, company_name, job_title, question, context, gap_analysis, tone) -> Dict[str, Any]:
        """
        Generates the cover letter answer using CoT.
        """
        parser = PydanticOutputParser(pydantic_object=ResumeGenerationResult)
        
        # Format gap analysis for prompt
        matching_points = ", ".join(gap_analysis.get("matching_points", []))
        missing_elements = ", ".join(gap_analysis.get("missing_elements", []))

        prompt = PromptTemplate(
            template=RESUME_GENERATION_PROMPT,
            input_variables=["company_name", "job_title", "question", "context", "matching_points", "missing_elements"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                "company_name": company_name,
                "job_title": job_title,
                "question": question,
                "context": context,
                "matching_points": matching_points,
                "missing_elements": missing_elements
            })
            return result.model_dump()
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def generate_outline(self, company_name, job_title, question, context, gap_analysis) -> Dict[str, Any]:
        """
        Generates a structural outline for the cover letter instead of full text.
        """
        parser = PydanticOutputParser(pydantic_object=ResumeOutlineResult)
        
        # Format gap analysis for prompt
        matching_points = ", ".join(gap_analysis.get("matching_points", []))
        missing_elements = ", ".join(gap_analysis.get("missing_elements", []))

        prompt = PromptTemplate(
            template=QUESTION_BASED_OUTLINE_PROMPT,
            input_variables=["company_name", "job_title", "question", "context", "matching_points", "missing_elements"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        chain = prompt | self.llm | parser
        
        try:
            result = chain.invoke({
                "company_name": company_name,
                "job_title": job_title,
                "question": question,
                "context": context,
                "matching_points": matching_points,
                "missing_elements": missing_elements
            })
            return result.model_dump()
        except Exception as e:
            logger.error(f"Outline generation failed: {e}")
            raise
