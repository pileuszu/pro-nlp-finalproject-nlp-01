import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

from src.extractors.file_extractor import FileExtractor
from src.extractors.github_extractor import GitHubExtractor
from src.extractors.notion_extractor import NotionExtractor
from src.processors.llm_refiner import LLMRefiner
from src.storage.vector_store import PortfolioVectorStore

def main():
    parser = argparse.ArgumentParser(description="Portfolio Processing Pipeline")
    parser.add_argument("--source_type", required=True, choices=["file", "github", "notion"], help="Type of source")
    parser.add_argument("--source_path", required=True, help="Path or URL to the source")
    args = parser.parse_args()

    print(f"--- Step 1: Extracting from {args.source_type} ({args.source_path}) ---")
    
    if args.source_type == "file":
        extractor = FileExtractor()
    elif args.source_type == "github":
        extractor = GitHubExtractor()
    elif args.source_type == "notion":
        extractor = NotionExtractor()
    else:
        print("Invalid source type")
        return

    raw_text = extractor.extract(args.source_path)
    if not raw_text or "Error" in raw_text: # Simple error check
        print(f"Extraction Failed: {raw_text}")
        return
    
    print(f"Extracted Text (first 200 chars):\n{raw_text[:200]}...\n")

    print("--- Step 2: Refining text with LLM ---")
    try:
        refiner = LLMRefiner()
        refined_text = refiner.refine_text(raw_text)
        print(f"Refined Text (first 200 chars):\n{refined_text[:200]}...\n")
    except Exception as e:
        print(f"Refinement Failed: {e}")
        return

    print("--- Step 3: Embedding and Storing ---")
    try:
        vector_store = PortfolioVectorStore()
        metadata = {"source": args.source_path, "type": args.source_type}
        vector_store.save(refined_text, metadata)
        print("Done! Data stored in Chroma DB.")
    except Exception as e:
        print(f"Storage Failed: {e}")

if __name__ == "__main__":
    main()
