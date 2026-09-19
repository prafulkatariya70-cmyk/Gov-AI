#================================================================================================

## Eligibility API Slice - Pre-Test State
backend:
  - task: "Public job eligibility requirements API"
    implemented: true
    working: "NA"
    file: "backend/app/api/routes/jobs.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added a read-only job eligibility requirements endpoint backed by persisted PostgreSQL JobEligibility data. This endpoint intentionally does not perform user-specific eligibility decisions because authentication is not implemented yet."

metadata:
  test_sequence: 7

test_plan:
  current_focus:
    - "Run shared-URL multi-post ingestion regression"
    - "Run current UPSC Advertisement 11 parser compatibility test"
    - "Run document processing regression"
    - "Run job ingestion plus lifecycle status regression"
    - "Run full parser/normalizer/evaluator/persistence suite"
    - "Run Alembic upgrade through 0006"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "Before testing, hardened multi-post source identity again: when an explicit vacancy number exists but no matching source/job exists, ingestion no longer falls back to shared official/PDF URLs. Added a regression proving two vacancy numbers sharing one PDF create two jobs and two sources."

## Multi-post ingestion regression - Pre-Test State
backend:
  - task: "Shared-URL multi-post ingestion regression"
    implemented: true
    working: "NA"
    file: "backend/tests/test_job_ingestion.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Run #242 showed the regression fixture was using the base parser, while production document processing uses NotificationParserEnhancer for UPSC identity/title enrichment. The fixture is being aligned with the production parser boundary; no production ingestion logic is changed."
metadata:
  test_sequence: 8

test_plan:
  current_focus:
    - "Run shared-URL multi-post ingestion regression"
    - "Run current UPSC Advertisement 11 parser compatibility test"
    - "Run document processing regression"
    - "Run job ingestion plus lifecycle status regression"
    - "Run full parser/normalizer/evaluator/persistence suite"
    - "Run Alembic upgrade through 0006"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "Run #242 passed the earlier ingestion cases but failed only because the shared-URL regression instantiated NotificationParser directly; production processing instantiates NotificationParserEnhancer. Aligning the regression with the production boundary keeps the test focused on source isolation rather than parser capability."


## Job lifecycle status regression - Pre-Test State
backend:
  - task: "Job lifecycle status boundary regression"
    implemented: true
    working: "NA"
    file: "backend/tests/test_job_status.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Run #246 reached the lifecycle status suite after the parser/ingestion fixes. One test fixture used a deadline exactly three days away while the production contract intentionally marks 0..closing_soon_days days as closing soon. The fixture is being moved outside the three-day boundary; production logic remains unchanged."
metadata:
  test_sequence: 9

test_plan:
  current_focus:
    - "Run job lifecycle status regression"
    - "Run current UPSC Advertisement 11 parser compatibility test"
    - "Run document processing regression"
    - "Run source discovery and notification queue regressions"
    - "Run full parser/normalizer/evaluator/persistence suite"
    - "Run Alembic upgrade through 0006"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "Run #246 passed the preceding suites and failed only at the lifecycle fixture boundary. Correcting the contradictory fixture rather than changing the closing-soon production rule."


## UPSC enhancer regression - Pre-Test State
backend:
  - task: "UPSC organization casing regression"
    implemented: true
    working: "NA"
    file: "backend/tests/test_upsc_notification_enhancer.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Run #248 reached the UPSC enhancer suite. Two assertions expected title-cased organization text while the parser intentionally preserves source casing and returned the exact official uppercase heading. Tests are being made case-insensitive; production parser behavior is unchanged."
metadata:
  test_sequence: 10

test_plan:
  current_focus:
    - "Run UPSC enhancer regression"
    - "Run document processing regression"
    - "Run source discovery and notification queue regressions"
    - "Run full parser/normalizer/evaluator/persistence suite"
    - "Run Alembic upgrade through 0006"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "Run #248 passed earlier suites and failed only on two organization-casing expectations. The parser preserves official source casing, so the regression should validate semantic identity rather than presentation casing."


## Production API contract coverage - Pre-Test State
backend:
  - task: "Core FastAPI contract coverage for health, jobs, job detail, and eligibility requirements"
    implemented: true
    working: "NA"
    file: "backend/tests/test_api_contract.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added isolated TestClient coverage for the production /api/v1 contract, including health, filtered job listing, job detail, persisted eligibility requirements, and 404 behavior. No production route behavior was changed."
metadata:
  test_sequence: 11

test_plan:
  current_focus:
    - "Run core production API contract tests"
    - "Run full backend foundation verification"
    - "Verify Alembic remains at head"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "API contract coverage is now added before touching frontend integration. The goal is to lock the production /api/v1 behavior with isolated tests before changing the client contract."
