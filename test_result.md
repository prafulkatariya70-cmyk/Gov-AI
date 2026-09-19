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
    - "Verify persisted eligibility requirements API route registration"
    - "Verify job eligibility repository lookup"
    - "Run full backend foundation regression suite"
    - "Run Alembic upgrade through revision 0003"
    - "Verify migration current reports 0003 as head"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "CI run #90 passed all existing foundation tests and Alembic reached 0003_profile_eligibility_fields (head). The next slice exposes persisted job eligibility requirements through the production API without introducing unauthenticated candidate-specific decisions."
====
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data.
#
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"
##     needs_retesting: false
##     status_history:
##         -working: true
##         -agent: "main"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"
##
## agent_communication:
##     -agent: "main"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication`
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - Pay special attention to the stuck_tasks list
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about which tasks need testing, authentication details, specific scenarios, and known edge cases.
#
# IMPORTANT: Main agent must ALWAYS update `test_result.md` BEFORE calling the testing agent.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

#====================================================================================================
# Testing Data - Main Agent and Testing sub agent both should log testing data below this section

user_problem_statement: "Productionize GovCareerAI foundation without breaking the existing working prototype."
backend:
  - task: "Structured eligibility profile fields"
    implemented: true
    working: "NA"
    file: "backend/app/models/user_profile.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added persisted profile fields required by the evaluator: government service, analogous post, service years, pay level, parent cadre, qualifying examination, training, relevant experience, and experience areas."
  - task: "Eligibility profile migration"
    implemented: true
    working: "NA"
    file: "backend/alembic/versions/0003_profile_eligibility_fields.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added Alembic revision 0003 after the existing 0002 head."
  - task: "Persisted eligibility evaluation service"
    implemented: true
    working: "NA"
    file: "backend/app/services/eligibility/job_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: true
        agent: "main"
        comment: "Foundation CI run #74 passed the initial persisted service tests. This slice now maps all structured profile inputs into CandidateProfile and requires migration validation."
  - task: "Production eligibility regression tests"
    implemented: true
    working: "NA"
    file: "backend/tests/test_job_eligibility_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Extended tests to verify all structured candidate fields reach the evaluator contract."
frontend: []

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 6
  run_ui: false

test_plan:
  current_focus:
    - "Run persisted eligibility tests with full candidate mapping"
    - "Run ORM smoke tests"
    - "Run Alembic upgrade through revision 0003"
    - "Verify migration current reports 0003 as head"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
- agent: "main"
    message: "CI run #86 exposed a test-fixture defect, not an application defect: the new mapping test seeded only DOB, so the structured profile fields were correctly read as NULL. The fixture is now corrected; rerun the full gate before proceeding."


backend:
  - task: "JWT authentication foundation"
    implemented: true
    working: "NA"
    file: "backend/app/api/routes/auth.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added registration, login, authenticated /me, bcrypt password hashing, JWT access tokens, and authenticated-user dependency. Existing User.password_hash is reused; no migration required."

metadata:
  test_sequence: 8

test_plan:
  current_focus:
    - "Verify authentication route registration"
    - "Verify password hashing and JWT round trip"
    - "Verify registration, login, /me, duplicate registration, and invalid credentials"
    - "Run full backend foundation regression suite"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "Authentication is intentionally built before personalized eligibility. No demo user or unauthenticated candidate identity is introduced."


# Authentication verification update
backend:
  - task: "JWT authentication foundation"
    implemented: true
    working: "NA"
    file: "backend/app/api/routes/auth.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Auth implementation is present, but the CI workflow did not yet execute test_auth.py. Added an explicit authentication test step with JWT_SECRET to the foundation workflow; this push will trigger the verification gate."

metadata:
  test_sequence: 9

test_plan:
  current_focus:
    - "Run authentication tests in CI"
    - "Verify password hashing and JWT round trip"
    - "Verify register, login, /me, duplicate registration, invalid credentials, and unauthenticated access"
    - "Run full backend foundation regression suite"
    - "Verify Alembic upgrade remains at 0003"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "Before adding the profile API, the auth gate must be executed. The workflow now explicitly runs test_auth.py; no personalized endpoint work will be started until this gate passes."


# Authenticated profile API update
backend:
  - task: "Authenticated user profile API"
    implemented: true
    working: "NA"
    file: "backend/app/api/routes/profile.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added authenticated GET /api/v1/profile and idempotent PUT /api/v1/profile. Profile records are resolved exclusively from the authenticated user ID; no client-supplied user ID is accepted. Structured eligibility fields are persisted through the existing UserProfile model."

metadata:
  test_sequence: 10

test_plan:
  current_focus:
    - "Run authentication tests including the newly explicit CI step"
    - "Run authenticated profile GET/PUT tests"
    - "Verify profile data is scoped to the authenticated user"
    - "Run full backend foundation regression suite"
    - "Verify Alembic upgrade remains at 0003"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "Profile API is implemented only after the auth foundation was wired into CI. The next verification must cover auth and profile together before personalized eligibility is exposed."


# Personalized eligibility API update
backend:
  - task: "Authenticated personalized job eligibility API"
    implemented: true
    working: "NA"
    file: "backend/app/api/routes/jobs.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added GET /api/v1/jobs/{identifier}/eligibility/me. The endpoint authenticates the user, resolves the job by slug or UUID, loads persisted PostgreSQL eligibility rules and the authenticated profile, then delegates the final decision to the existing evaluator. A test fixture was aligned with the evaluator's exact persisted rule names before verification."

metadata:
  test_sequence: 11

test_plan:
  current_focus:
    - "Run authentication tests"
    - "Run profile API tests"
    - "Run personalized eligibility API tests"
    - "Run eligibility engine and parser regression tests"
    - "Run ORM and persisted eligibility service tests"
    - "Verify Alembic upgrade remains at 0003"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "The personalized eligibility endpoint now completes the authenticated request-time path. It does not parse PDFs during requests; it evaluates only persisted normalized rules, preserving the production separation between ingestion and evaluation."


# Real job ingestion foundation update
backend:
  - task: "Parsed notification to PostgreSQL job ingestion"
    implemented: true
    working: "NA"
    file: "backend/app/services/jobs/ingestion.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added deterministic ingestion of already-parsed official notifications into jobs, job_sources, and job_eligibility. Ingestion records official source URLs, content hashes, normalized eligibility, core job fields, and is idempotent for repeated processing of the same source/content."

metadata:
  test_sequence: 12

test_plan:
  current_focus:
    - "Run job ingestion idempotency test"
    - "Run authentication and profile API tests"
    - "Run personalized eligibility API test"
    - "Run parser, normalizer, evaluator and persistence regression tests"
    - "Run Alembic upgrade through 0003"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "The ingestion slice deliberately stops at parsed notification input. Network retrieval, PDF extraction/OCR, source discovery and scheduling remain separate concerns so ingestion can be tested deterministically before introducing external-source automation."


# Document processing pipeline update
backend:
  - task: "Official PDF fetch, extraction, parsing and ingestion pipeline"
    implemented: true
    working: "NA"
    file: "backend/app/services/documents/processing.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added bounded HTTP(S) document fetching, native PDF text extraction with OCR fallback, and an orchestration service that passes extracted notification text through the proven parser and idempotent PostgreSQL ingestion service. Network retrieval remains outside request-time eligibility evaluation."

metadata:
  test_sequence: 13

test_plan:
  current_focus:
    - "Run deterministic PDF processing pipeline test"
    - "Run job ingestion idempotency test"
    - "Run authentication, profile and personalized eligibility API tests"
    - "Run parser/normalizer/evaluator/persistence regression tests"
    - "Run Alembic upgrade through 0003"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "The document pipeline is intentionally deterministic at the orchestration boundary: CI uses an in-memory generated PDF and a fake fetcher, while production can supply official notification URLs. OCR is a fallback, not the default path when native PDF text exists."


# Official source discovery update
backend:
  - task: "Official listing registry and PDF discovery"
    implemented: true
    working: "NA"
    file: "backend/app/services/jobs/source_discovery.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added a PostgreSQL-backed registry for official government listing pages, due-check logic, and deterministic PDF-link discovery constrained to the supplied official listing page. This is intentionally not a broad web crawler."

metadata:
  test_sequence: 14

test_plan:
  current_focus:
    - "Run deterministic official source discovery test"
    - "Run Alembic upgrade through 0004"
    - "Run document processing and job ingestion tests"
    - "Run authentication, profile and personalized eligibility API tests"
    - "Run parser/normalizer/evaluator/persistence regression tests"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "Source discovery is deliberately constrained to registered official listing pages and PDF links. It does not search the open web or ingest arbitrary domains. Scheduling is represented by due-source metadata; external cron/worker execution will be added after deterministic discovery is verified."


# Official source bootstrap update
backend:
  - task: "Initial official recruitment source allowlist"
    implemented: true
    working: "NA"
    file: "backend/app/services/jobs/official_sources.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added an idempotent allowlist/bootstrap for UPSC recruitment advertisements, UPSC recruitment-test notices, and IBPS recruitment listings. These URLs are official domains selected from current official source pages; no third-party aggregator is used."

metadata:
  test_sequence: 15

test_plan:
  current_focus:
    - "Run official source allowlist test"
    - "Run deterministic source discovery test"
    - "Run Alembic upgrade through 0004"
    - "Run document processing and job ingestion tests"
    - "Run authentication, profile and personalized eligibility API tests"
    - "Run parser/normalizer/evaluator/persistence regression tests"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "The initial source registry is intentionally small and allowlisted. Expansion to SSC, RRB, state commissions and other boards will happen source-by-source with dedicated verification rather than broad scraping."


# Notification queue and worker update
backend:
  - task: "Discovered notification queue with retry and processing states"
    implemented: true
    working: "NA"
    file: "backend/app/services/jobs/queue.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added a PostgreSQL notification queue with unique PDF URLs, PENDING/PROCESSING/PROCESSED/FAILED states, bounded retries, exponential backoff, and a worker service that invokes the existing document-processing pipeline. Added migration 0005."

metadata:
  test_sequence: 16

test_plan:
  current_focus:
    - "Run queue enqueue and retry-state tests"
    - "Run source discovery and official-source allowlist tests"
    - "Run document processing and job ingestion tests"
    - "Run Alembic upgrade through 0005"
    - "Run authentication, profile and personalized eligibility API tests"
    - "Run parser/normalizer/evaluator/persistence regression tests"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "The worker is intentionally callable as a service rather than embedded in FastAPI startup. Production scheduling can run it from a separate worker/cron process, preventing long-running PDF/OCR work from blocking API requests."


# Ingestion cycle orchestration update
backend:
  - task: "Source discovery to queue to worker orchestration"
    implemented: true
    working: "NA"
    file: "backend/app/services/jobs/ingestion_cycle.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added one bounded ingestion-cycle service that checks due official sources, enqueues newly discovered PDFs idempotently, and processes a bounded number of pending queue items. It is callable by an external scheduler/worker and is not executed inside FastAPI startup."

metadata:
  test_sequence: 17

test_plan:
  current_focus:
    - "Run ingestion-cycle orchestration tests with fake discovery and processor"
    - "Run notification queue tests"
    - "Run official source and source discovery tests"
    - "Run document processing and job ingestion tests"
    - "Run Alembic upgrade through 0005"
    - "Run authentication, profile and personalized eligibility API tests"
    - "Run parser/normalizer/evaluator/persistence regression tests"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "The ingestion cycle is deliberately a bounded orchestration primitive, not an always-on process. Deployment can invoke it every few minutes from a scheduler or worker environment without tying background work to FastAPI lifecycle."


# Production job data-contract hardening update
backend:
  - task: "Separate official source URLs from application URLs and harden job identity"
    implemented: true
    working: "NA"
    file: "backend/app/services/jobs/ingestion.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Hardened ingestion so an official listing/source URL is never silently presented as an application URL. Application URL is now optional and source provenance remains explicit. Job slugs receive a deterministic source fingerprint to prevent collisions across similarly named recruitment notices. Eligibility response list defaults are also being converted to safe factories."

metadata:
  test_sequence: 18

test_plan:
  current_focus:
    - "Run ingestion identity and URL contract tests"
    - "Run ingestion cycle and notification queue tests"
    - "Run document processing, source discovery and official-source tests"
    - "Run full parser/normalizer/evaluator/persistence regression suite"
    - "Run Alembic upgrade through 0005"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "The data contract now distinguishes source provenance from user-facing application destinations. If a listing only exposes a notification PDF, GovCareerAI will retain the official source rather than inventing an application URL."


# Real UPSC notification compatibility update
backend:
  - task: "UPSC recruitment notification enrichment"
    implemented: true
    working: "NA"
    file: "backend/app/services/documents/parsing/notification_enhancer.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "A real current UPSC Advertisement No. 52/2026 was inspected from the official UPSC recruitment advertisement page. Its wording uses 'Eighty vacancies for the post of...', category-specific ages, and 'closing date for submission...' patterns that the generic parser did not recognize in a local compatibility check. Added a narrow post-parser enrichment layer rather than modifying the large proven parser wholesale."

metadata:
  test_sequence: 19

test_plan:
  current_focus:
    - "Run real UPSC text compatibility test"
    - "Run document processing regression with enriched parser"
    - "Run job ingestion and ingestion-cycle tests"
    - "Run full parser/normalizer/evaluator/persistence regression suite"
    - "Run Alembic upgrade through 0005"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "The real-notification check exposed a parser vocabulary gap before production ingestion. The fix is intentionally narrow: preserve the proven parser and enrich only documented UPSC-style vacancy/title/age/date/pay patterns, with evidence and conservative confidence."


# Job lifecycle status hardening update
backend:
  - task: "Deterministic job lifecycle status"
    implemented: true
    working: "NA"
    file: "backend/app/services/jobs/status.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added deterministic UPCOMING/OPEN/CLOSED/NO_DEADLINE derivation from application dates, a three-day closing-soon flag, new-today handling from notification date, and invalid-window validation. Ingestion now refreshes lifecycle flags instead of hard-coding every imported job as Open/new."
  - task: "Job API response schema integrity"
    implemented: true
    working: "NA"
    file: "backend/app/schemas/job.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Restored complete JobSummary and JobListResponse models with lifecycle fields and SQLAlchemy from_attributes support so the production jobs route has a valid response contract."

metadata:
  test_sequence: 20

test_plan:
  current_focus:
    - "Run deterministic job lifecycle status tests"
    - "Run job ingestion idempotency and status regression"
    - "Run jobs API and ORM smoke tests"
    - "Run full parser/normalizer/evaluator/persistence regression suite"
    - "Run Alembic upgrade through 0005"
  stuck_tasks: []
  test_all: true
  test_priority: "high_first"

agent_communication:
- agent: "main"
  message: "This slice removes a production-critical hard-coded Open status. The lifecycle is now derived from actual application dates, so expired notifications such as the inspected UPSC Advertisement 52/2026 will not be surfaced as Open. The API schema was also restored to match the jobs route contract before verification."
