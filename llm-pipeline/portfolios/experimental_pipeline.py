import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file (current dir or parent)
env_path = Path(__file__).parent / ".env"
if not env_path.exists():
    env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Attempt to import Surya OCR (handle if not installed)
try:
    from surya.ocr import run_ocr
    from surya.model.detection import segformer
    from surya.model.recognition.model import load_model as load_rec_model
    from surya.model.recognition.processor import load_processor as load_rec_processor
    from PIL import Image
    SURYA_AVAILABLE = True
except ImportError:
    SURYA_AVAILABLE = False
    print("Warning: Surya OCR not found. Image extraction will fail.")

# Configuration (matching self_introduction where possible)
EMBEDDING_MODEL = "jhgan/ko-sroberta-multitask"
CHROMA_PERSIST_DIR = Path(__file__).parent / "chroma_db_experiment"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def check_api_key():
    if not GOOGLE_API_KEY:
        print("Error: GOOGLE_API_KEY not found in .env")
        sys.exit(1)

def extract_text_from_image(image_path: str) -> str:
    """Extracts text from an image using Surya OCR."""
    if not SURYA_AVAILABLE:
        raise ImportError("Surya OCR is not installed.")
    
    try:
        image = Image.open(image_path)
        langs = ["ko", "en"] # Mixed Korean and English
        
        # Load models (this might be slow on first run)
        det_processor, det_model = segformer.load_processor(), segformer.load_model()
        rec_model, rec_processor = load_rec_model(), load_rec_processor()

        predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)
        
        full_text = ""
        for result in predictions:
            for line in result.text_lines:
                full_text += line.text + "\n"
        
        return full_text
    except Exception as e:
        print(f"Error during Surya OCR extraction: {e}")
        return ""

def extract_text_from_file(file_path: str) -> str:
    """Extracts text from a file (Text, Markdown, or Image)."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = path.suffix.lower()
    
    if suffix in ['.txt', '.md']:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    elif suffix in ['.jpg', '.jpeg', '.png', '.bmp']:
        print(f"Detected image file. Using Surya OCR for {file_path}...")
        return extract_text_from_image(str(path))
    # Add PDF support here if needed using pypdf
    else:
        print(f"Unsupported file type: {suffix}. Treating as text.")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"

def refine_text_with_llm(raw_text: str) -> str:
    """Refines and structures the raw text using Gemini."""
    # TODO: API call and Prompt content will be modified later.
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY, temperature=0.7)
    
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
    chain = prompt | llm | StrOutputParser()
    
    print("Invoking LLM for text refinement...")
    result = chain.invoke({"raw_text": raw_text})
    return result

def vectorize_and_store(refined_text: str, source_file: str):
    """Converts text to embeddings and stores in Chroma DB."""
    print("Initializing Embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    print(f"Storing in Chroma DB at {CHROMA_PERSIST_DIR}...")
    
    # Create Document
    doc = Document(
        page_content=refined_text,
        metadata={"source": source_file}
    )
    
    # Store
    vectorstore = Chroma.from_documents(
        documents=[doc],
        embedding=embeddings,
        collection_name="portfolio_experiment",
        persist_directory=str(CHROMA_PERSIST_DIR)
    )
    print("Successfully stored in Chroma DB.")

def main():
    parser = argparse.ArgumentParser(description="Portfolio Processing Pipeline Experiment")
    parser.add_argument("file_path", help="Path to the portfolio file (Text or Image)")
    args = parser.parse_args()

    check_api_key()

    # 1. Extract
    print(f"--- Step 1: Extracting text from {args.file_path} ---")
    raw_text = extract_text_from_file(args.file_path)
    if not raw_text:
        print("Failed to extract text. Exiting.")
        return
    print(f"Extracted Text (first 200 chars):\n{raw_text[:200]}...\n")

    # 2. Refine
    print("--- Step 2: Refining text with LLM ---")
    refined_text = refine_text_with_llm(raw_text)
    print(f"Refined Text (first 200 chars):\n{refined_text[:200]}...\n")

    # 3. Embed & Store
    print("--- Step 3: Embedding and Storing ---")
    vectorize_and_store(refined_text, args.file_path)
    print("Done!")

if __name__ == "__main__":
    main()
