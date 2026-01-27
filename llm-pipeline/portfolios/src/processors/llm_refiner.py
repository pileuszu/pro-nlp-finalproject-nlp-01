import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class LLMRefiner:
    """Refines text using LLM."""

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
        # TODO: API call and Prompt content will be modified later.
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key, temperature=0.7)

    def refine_text(self, raw_text: str) -> str:
        """
        Refines and structures the raw text.
        """
        # TODO: This template is temporary and will be updated.
        template = """
        You are an AI assistant that refines extracted portfolio text.
        The raw text may contain OCR errors or be unstructured.
        
        Please refine the following text:
        1. Correct any obvious OCR errors (typos, spacing).
        2. Organize the content into a readable format (e.g., Markdown).
        3. Keep the original meaning and core content intact.
        4. If it's a list of projects or experience, structure it clearly.
        
        Raw Text:
        {raw_text}
        
        Refined Text:
        """
        
        prompt = PromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({"raw_text": raw_text})
