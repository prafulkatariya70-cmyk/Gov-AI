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
