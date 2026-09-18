#====================================================================================================
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
  - task: "Persisted eligibility evaluation service"
    implemented: true
    working: "NA"
    file: "backend/app/services/eligibility/job_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added a production service that loads a PostgreSQL job eligibility record and user profile, reconstructs normalized rule trees, maps profile data into the existing CandidateProfile contract, and delegates decisions to the existing evaluator without duplicating business rules."
  - task: "Eligibility persistence repository"
    implemented: true
    working: "NA"
    file: "backend/app/repositories/job_eligibility.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Added repository lookup for job eligibility and user profile records using SQLAlchemy."
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
        comment: "Added deterministic SQLite-backed tests for persisted rule reconstruction, eligible age evaluation, missing-profile data producing NEEDS_REVIEW, and missing job eligibility handling."
  - task: "PostgreSQL SQLAlchemy ORM foundation"
    implemented: true
    working: true
    file: "backend/app/models/"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Foundation gate is green in GitHub Actions, including ORM smoke and Alembic verification."
  - task: "Alembic initial migration"
    implemented: true
    working: true
    file: "backend/alembic/versions/0001_initial_schema.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Alembic upgrade reached head 0002 in the latest green foundation CI run."
  - task: "Eligibility intelligence integration boundary"
    implemented: true
    working: true
    file: "backend/app/services/eligibility/"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Existing parser-normalizer-evaluator boundary remains green and is reused by the persisted eligibility service."
  - task: "Notification parser integration"
    implemented: true
    working: true
    file: "backend/app/services/documents/parsing/notification_parser.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Full verified parser remains unchanged by this work."
frontend: []

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 5
  run_ui: false

test_plan:
  current_focus:
    - "Run persisted eligibility service regression tests"
    - "Run full backend foundation suite"
    - "Verify Alembic head remains 0002"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: "Next production slice connects PostgreSQL-stored eligibility rules and user profiles to the existing evaluator. No business-rule duplication and no Emergent credits used. Testing agent tooling is unavailable, so GitHub Actions is the validation gate."
