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
