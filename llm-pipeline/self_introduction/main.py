"""
AI 자소서 컨설턴트 - CLI 메인 진입점
"""
import argparse
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint

from config.settings import CLOVA_API_KEY
from src.gap_analysis import run_full_analysis, run_single_question_analysis
from src.embeddings import create_all_vectorstores

console = Console()


def check_api_key():
    """API 키 확인"""
    if not CLOVA_API_KEY or CLOVA_API_KEY == "your_api_key_here":
        console.print(
            "[bold red]Error:[/bold red] CLOVA_API_KEY가 설정되지 않았습니다.\n"
            ".env 파일을 생성하고 API 키를 설정하세요.",
            style="red"
        )
        console.print("\n[dim].env.example 파일을 참고하세요.[/dim]")
        sys.exit(1)


def display_gap_analysis(gap_result):
    """Gap 분석 결과 표시"""
    console.print("\n")
    console.print(Panel("[bold]📊 Gap 분석 결과[/bold]", style="cyan"))
    
    # 매칭 포인트
    if gap_result.matching_points:
        console.print("\n[bold green]✅ 매칭되는 역량:[/bold green]")
        for point in gap_result.matching_points:
            console.print(f"  • {point}")
    
    # 부족한 역량
    if gap_result.missing_elements:
        console.print("\n[bold yellow]⚠️ 보완이 필요한 역량:[/bold yellow]")
        for element in gap_result.missing_elements:
            console.print(f"  • {element}")
    
    # Gap 여부
    if gap_result.is_gap_found:
        console.print("\n[bold red]🔍 Gap 발견됨[/bold red]")
        if gap_result.question_to_user:
            console.print(f"\n[italic]💡 추가 질문: {gap_result.question_to_user}[/italic]")
    else:
        console.print("\n[bold green]✨ 채용 요건에 잘 부합합니다![/bold green]")
    
    # 판단 근거
    console.print("\n[bold]📝 분석 근거:[/bold]")
    console.print(f"  {gap_result.reasoning}")


def display_resume(resume_item):
    """생성된 자소서 표시 (문항별)"""
    question = resume_item.get("question", "자기소개서")
    resume_result = resume_item.get("resume")
    max_length = resume_item.get("max_length", 800)
    
    console.print("\n")
    console.print(Panel(f"[bold]📄 문항: {question}[/bold]\n[dim]({max_length}자 이내)[/dim]", style="blue"))
    
    console.print(f"\n[bold underline]{resume_result.title}[/bold underline]\n")
    console.print(resume_result.content)


def save_resume_to_file(result, output_dir: Path):
    """자소서를 파일로 저장 (문항별)"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    user_id = result["user_id"]
    company_name = result["company_name"]
    resumes = result["resumes"]
    
    filename = output_dir / f"resume_{user_id}_{company_name.replace(' ', '_').replace('(', '').replace(')', '')}.md"
    
    content = f"""# {company_name} 지원 자소서

**지원자**: {result["user_name"]}

---

"""
    
    for item in resumes:
        resume = item["resume"]
        content += f"""## 문항 {item['question_id']}: {item['question']}

{resume.content}

---

"""
    
    content += "\n*AI 자소서 컨설턴트에 의해 생성됨*\n"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    
    return filename


def main():
    # 사용자 목록 동적 감지
    from config.settings import DATA_DIR
    user_files = list(Path(DATA_DIR).glob("*_data.json"))
    user_ids = [f.stem.replace("_data", "") for f in user_files if f.stem != "company_data"]
    
    if not user_ids:
        console.print("[bold red]Error:[/bold red] data 폴더에 사용자 데이터가 없습니다.", style="red")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="AI 자소서 컨설턴트")
    parser.add_argument(
        "--user",
        type=str,
        choices=user_ids,
        required=True,
        help=f"분석할 사용자 ({', '.join(user_ids)})"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="벡터스토어 초기화 (최초 실행 시 필요)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="생성된 자소서를 파일로 저장"
    )
    parser.add_argument(
        "--question",
        type=int,
        choices=[1, 2, 3],
        help="특정 문항만 생성 (1, 2, 또는 3)"
    )
    
    args = parser.parse_args()
    
    # API 키 확인
    check_api_key()
    
    # 벡터스토어 초기화
    if args.init:
        console.print("[bold yellow]벡터스토어 초기화 중...[/bold yellow]")
        create_all_vectorstores()
        console.print("[bold green]✓ 초기화 완료[/bold green]\n")
    
    # 헤더 표시
    console.print(Panel.fit(
        "[bold]🤖 AI 자소서 컨설턴트[/bold]\n"
        "[dim]RAG & LangChain 기반 맞춤형 자소서 생성[/dim]",
        border_style="bright_blue"
    ))
    
    console.print(f"\n[bold]📋 분석 대상:[/bold] {args.user}")
    if args.question:
        console.print(f"[bold]📝 생성할 문항:[/bold] {args.question}번")
    console.print("[dim]분석 중... (최초 실행 시 시간이 걸릴 수 있습니다)[/dim]\n")
    
    try:
        # 분석 실행
        with console.status("[bold green]분석 진행 중..."):
            if args.question:
                result = run_single_question_analysis(args.user, args.question)
            else:
                result = run_full_analysis(args.user)
        
        # 결과 표시
        console.print(f"\n[bold]👤 지원자:[/bold] {result['user_name']}")
        console.print(f"[bold]🏢 지원 기업:[/bold] {result['company_name']}")
        
        display_gap_analysis(result["gap_analysis"])
        
        # 각 문항별 자소서 표시
        console.print("\n")
        console.print(Panel("[bold]📝 생성된 자소서 목록[/bold]", style="green"))
        
        for item in result["resumes"]:
            display_resume(item)
        
        # 파일 저장
        if args.save:
            output_dir = project_root / "output"
            saved_file = save_resume_to_file(result, output_dir)
            console.print(f"\n[bold green]✓ 자소서 저장됨:[/bold green] {saved_file}")
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}", style="red")
        raise


if __name__ == "__main__":
    main()

