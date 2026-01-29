import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from langchain_chroma import Chroma

from config.settings import CHROMA_PERSIST_DIR
from src.gap_analysis import analyze_gap, generate_resume
from src.data_loader import load_company_data
from src.retrieval import ChromaRetriever
from src.embeddings import get_embeddings  # CLOVAEmbeddings 사용

console = Console()

def get_chroma_vectorstore(user_id: str):
    """portfolios 모듈에서 생성한 ChromaDB 로드 (CLOVA 임베딩 사용)"""
    collection_name = f"user_{user_id}"
    persist_directory = Path(CHROMA_PERSIST_DIR) / collection_name
    
    if not persist_directory.exists():
        raise FileNotFoundError(f"벡터스토어를 찾을 수 없습니다: {persist_directory}")
    
    # CLOVAEmbeddings 사용 (HuggingFace 대신)
    embeddings = get_embeddings()
    
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_directory)
    )

def main():
    parser = argparse.ArgumentParser(description="ChromaDB 기반 자소서 생성기")
    parser.add_argument("--user_id", required=True, help="유저 ID (예: pileuszu, unknown_user)")
    parser.add_argument("--save", action="store_true", help="결과를 파일로 저장")
    args = parser.parse_args()

    console.print(Panel(f"[bold]🚀 ChromaDB 기반 자소서 생성 시작 (User: {args.user_id})[/bold]", style="bright_blue"))

    try:
        # 1. 데이터 로드
        console.print("[dim]데이터 및 벡터스토어 로딩 중...[/dim]")
        company_data = load_company_data()
        vectorstore = get_chroma_vectorstore(args.user_id)
        
        # 2. Retriever 생성
        retriever = ChromaRetriever(vectorstore)
        
        # 3. 채용 요건으로 관련 경험 검색
        job_requirements = company_data.get("job_requirements", {})
        query = job_requirements.get("summary", "")
        console.print(f"[bold cyan]🔍 검색 쿼리:[/bold cyan] {query[:50]}...")
        
        relevant_experiences = retriever.search(query)
        console.print(f"[green]✓ 관련 경험 {len(relevant_experiences)}개 추출 완료[/green]")
        
        # 4. Gap 분석
        console.print("\n[bold]📊 Gap 분석 중...[/bold]")
        job_req_text = (
            f"{job_requirements.get('summary', '')}\n\n"
            f"상세 업무:\n" + 
            "\n".join(f"- {r}" for r in job_requirements.get("detailed_responsibilities", []))
        )
        gap_result = analyze_gap(relevant_experiences, job_req_text)
        
        # 5. 자소서 생성
        resume_questions = company_data.get("resume_questions", [])
        resumes = []
        
        console.print("\n[bold]📝 자소서 문항 생성 중...[/bold]")
        for question in resume_questions:
            console.print(f"  • {question['question']} 생성 중...")
            resume = generate_resume(relevant_experiences, gap_result, company_data, question)
            resumes.append({
                "question_id": question.get("id"),
                "question": question.get("question"),
                "max_length": question.get("max_length"),
                "resume": resume
            })

        # 6. 결과 출력
        from main import display_gap_analysis, display_resume, save_resume_to_file
        
        display_gap_analysis(gap_result)
        for item in resumes:
            display_resume(item)

        # 7. 저장
        if args.save:
            result = {
                "user_id": args.user_id,
                "user_name": args.user_id, # 실제 이름은 DB에서 가져와야 하지만 여기서는 ID로 대체
                "company_name": company_data["company_info"]["company_name"],
                "resumes": resumes
            }
            output_dir = project_root / "output"
            saved_file = save_resume_to_file(result, output_dir)
            console.print(f"\n[bold green]✅ 자소서 저장 완료:[/bold green] {saved_file}")

    except Exception as e:
        console.print(f"\n[bold red]❌ 오류 발생:[/bold red] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
