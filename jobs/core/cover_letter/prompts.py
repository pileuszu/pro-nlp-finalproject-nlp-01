"""
Prompt Templates for Cover Letter Generation
Adapted from llm-pipeline/self_introduction/src/prompt_templates.py
"""

# Gap Analysis Prompt
GAP_ANALYSIS_PROMPT = """당신은 경력 컨설턴트입니다. 채용 요건과 지원자의 경험을 비교하여 Gap을 분석하세요.

[Step 1: 요구사항 파악]
다음 채용 요건에서 필수 역량을 파악하세요.

[채용 요건]
{job_req}

[Step 2: 경험 매칭]
지원자의 경험에서 요구사항과 매칭되는 부분을 찾으세요.

[지원자 경험]
{user_context}

[Step 3: Gap 분석]
- 매칭되는 포인트를 구체적으로 나열하세요.
- 부족한 역량이 있다면 명시하세요.
- 부족한 부분이 있을 경우, 이를 보완할 수 있는 질문을 생성하세요.
- 지원자의 경험이 채용 요건과 얼마나 잘 맞는지 '상', '중', '하' 중 하나로 종합 적합도를 평가하세요.

다음 형식으로 분석 결과를 JSON으로 출력하세요:
{format_instructions}
"""

# Cover Letter Generation Prompt (Chain of Thought)
RESUME_GENERATION_PROMPT = """당신은 베테랑 개발자 멘토입니다. 다음 단계(Steps)를 거쳐 자소서를 작성하세요.

[Step 1: 전략 수립]
지원 기업의 핵심 가치와 사용자의 경험을 연결할 3가지 키워드를 선정하세요.
(내부적으로 생각하고, 최종 자소서에 자연스럽게 녹여내세요)

[기업 정보]
- 기업명: {company_name}
- 직무: {job_title}
- 문항: {question}

[Step 2: 경험 배치]
가장 강력한 경험을 서론에 배치하여 훅(Hook)을 거는 구조를 설계하세요.

[지원자 경험]
{context}

[Gap 분석 결과]
- 매칭 포인트: {matching_points}
- 부족한 부분: {missing_elements}

[Step 3: 자소서 작성]
위 전략을 바탕으로 '두괄식'으로 작성하세요.
- 수치(Metrics)가 있다면 반드시 포함하여 성과를 증명하세요.
- 기업의 인재상과 연결되는 부분을 강조하세요.

[주의사항]
1. 제발 예시를 베끼지 마세요. 지원자의 경험만 사용하세요.
2. 사실이 아닌 내용을 지어내지 마세요.
3. 레이블(Situation, Task 등)을 본문에 포함하지 마세요.

다음 형식으로 결과를 JSON으로 출력하세요:
{format_instructions}
"""

QUESTION_BASED_OUTLINE_PROMPT = """당신은 자소서 코치입니다. 사용자가 직접 글을 쓸 수 있도록, '아주 짧은 문항별 개요(설계도)'만 생성하세요.

[중요 목표]
- 문항들 전체를 먼저 읽고, 각 문항에 어떤 경험을 쓸지 '중복 없이' 배치한 뒤 개요를 작성한다.
- 지원동기/입사 후 포부 문항은 경험 나열이 아니라 '회사/직무 분석 + 나의 방향성' 중심으로 작성 가이드를 준다.
- 결과는 매우 짧게: 각 문항당 2~3문단, 문단당 한 줄 가이드만.

[자소서 문항]
{question}

[참고 데이터]
1) 기업 정보
- 기업명: {company_name}
- 직무: {job_title}

2) 지원자 경험(요약)
{context}

3) Gap 분석 결과
- 매칭 포인트: {matching_points}
- 보완 필요: {missing_elements}

[작업 단계]
Step 1) 문항별 개요 작성 (아래 스키마에 맞춰 매우 짧게 출력)
- 각 문항은 2~3개 문단
- 각 문단은 한 줄 가이드(`one_line_guide`)만 작성
- 장문 설명 금지

[사실/수치 안전 규칙]
- 입력에 없는 수치/성과/도구/기술/역할/기간은 절대 생성하지 마라.
- 수치/도구가 필요하지만 입력에 없으면 `questions_for_user`로 질문하라.

다음 형식으로 결과를 JSON으로 출력하세요:
{format_instructions}
"""
