"""
프롬프트 템플릿 모듈
- Chain of Thought (CoT) 프롬프트 적용
- 단계별 사고 유도로 논리적인 글 생성
"""

# 직무 분석 프롬프트
JOB_ANALYSIS_PROMPT = """당신은 채용 전문가입니다. 다음 채용 공고를 분석하여 핵심 요구사항을 추출하세요.

[채용 공고]
{job_posting}

[기업 정보]
- 기업명: {company_name}
- 인재상: {core_values}

다음 형식으로 분석 결과를 JSON으로 출력하세요:
{format_instructions}
"""

# Gap 분석 프롬프트
GAP_ANALYSIS_PROMPT = """당신은 경력 컨설턴트입니다. 채용 요건과 지원자의 경험을 비교하여 Gap을 분석하세요.

[Step 1: 요구사항 파악]
다음 채용 요건에서 필수 역량을 파악하세요.

[채용 요건]
{job_requirements}

[Step 2: 경험 매칭]
지원자의 경험에서 요구사항과 매칭되는 부분을 찾으세요.

[지원자 경험]
{user_experiences}

[Step 3: Gap 분석]
- 매칭되는 포인트를 구체적으로 나열하세요.
- 부족한 역량이 있다면 명시하세요.
- 부족한 부분이 있을 경우, 이를 보완할 수 있는 질문을 생성하세요.

다음 형식으로 분석 결과를 JSON으로 출력하세요:
{format_instructions}
"""

# 자소서 생성 프롬프트 (Chain of Thought 적용)
RESUME_GENERATION_PROMPT = """당신은 베테랑 개발자 멘토입니다. 다음 단계(Steps)를 거쳐 자소서를 작성하세요.

[Step 1: 전략 수립]
지원 기업의 핵심 가치와 사용자의 경험을 연결할 3가지 키워드를 선정하세요.
(내부적으로 생각하고, 최종 자소서에 자연스럽게 녹여내세요)

[기업 정보]
- 기업명: {company_name}
- 인재상: {core_values}
- 직무: {job_title}

[Step 2: 경험 배치]
가장 강력한 경험을 서론에 배치하여 훅(Hook)을 거는 구조를 설계하세요.

[지원자 경험]
{user_experiences}

[Gap 분석 결과]
- 매칭 포인트: {matching_points}
- 부족한 부분: {missing_elements}

[Step 3: 자소서 작성]
위 전략을 바탕으로 '두괄식'으로 작성하세요.
- 수치(Metrics)가 있다면 반드시 포함하여 성과를 증명하세요.
- 기업의 인재상과 연결되는 부분을 강조하세요.
- {max_length}자 내외의 분량으로 작성하세요.

다음 형식으로 결과를 JSON으로 출력하세요:
{format_instructions}
"""

# 간단한 자소서 작성 프롬프트 (Gap이 없는 경우)
SIMPLE_RESUME_PROMPT = """당신은 시니어 개발자 멘토입니다. 다음 정보를 바탕으로 자소서를 작성하세요.

[기업 정보]
- 기업명: {company_name}
- 직무: {job_title}
- 인재상: {core_values}

[지원자 경험]
{user_experiences}

[작성 지침]
1. 두괄식으로 작성하세요 (결론 먼저, 근거 나중에).
2. 구체적인 수치와 성과를 포함하세요.
3. 기업의 인재상과 연결하세요.
4. {max_length}자 내외의 분량으로 작성하세요.

다음 형식으로 결과를 JSON으로 출력하세요:
{format_instructions}
"""

# 문항 기반 자소서 생성 프롬프트
QUESTION_BASED_RESUME_PROMPT = """당신은 베테랑 개발자 멘토입니다. 다음 자소서 문항에 맞는 답변을 작성하세요.

[자소서 문항]
{question}

[작성 힌트]
{hint}

[글자 수 제한]
{max_length}자 이내

---

[Step 1: 전략 수립]
문항의 의도를 파악하고, 지원자의 경험에서 가장 적합한 사례를 선택하세요.

[기업 정보]
- 기업명: {company_name}
- 인재상: {core_values}
- 직무: {job_title}

[지원자 경험]
{user_experiences}

[Gap 분석 결과]
- 매칭 포인트: {matching_points}
- 보완 필요: {missing_elements}

[Step 2: 답변 작성]
1. 두괄식으로 작성하세요 (결론 먼저, 근거 나중에).
2. 구체적인 수치와 성과를 포함하세요.
3. 문항에서 요구하는 내용에 집중하세요.
4. 글자 수 제한을 준수하세요.

다음 형식으로 결과를 JSON으로 출력하세요:
{format_instructions}
"""

