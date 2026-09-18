from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, BeforeValidator
from typing import List, Optional, Dict, Any, Annotated
import uuid
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Helper for PyObjectId
PyObjectId = Annotated[str, BeforeValidator(str)]

class BaseDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_mongo(self) -> dict:
        data = self.model_dump()
        data["_id"] = data.pop("id", str(uuid.uuid4()))
        return data

    @classmethod
    def from_mongo(cls, doc: dict):
        if not doc:
            return None
        doc_copy = dict(doc)
        if "_id" in doc_copy:
            doc_copy["id"] = str(doc_copy.pop("_id"))
        return cls(**doc_copy)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

app = FastAPI(title="SarkariSeva AI API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Models
class VacanciesBreakdown(BaseModel):
    UR: int = 0
    OBC: int = 0
    SC: int = 0
    ST: int = 0
    EWS: int = 0
    PwD: Optional[int] = 0
    Female: Optional[int] = 0

class AgeRelaxation(BaseModel):
    OBC: int = 3
    SC_ST: int = 5
    PwD: int = 10
    Ex_Servicemen: int = 5
    EWS: int = 0

class ApplicationFee(BaseModel):
    General_OBC_EWS: str = "₹100"
    SC_ST_Female_PwD: str = "Exempted / ₹0"

class ExamStage(BaseModel):
    stage_num: int
    name: str
    type: str # MCQ / Descriptive / Skill / Physical / Interview
    marks: Optional[int] = 100
    duration: Optional[str] = "2 Hours"
    description: str

class JobModel(BaseDocument):
    title: str
    slug: str
    board: str
    board_code: str
    job_type: str # Central / State
    state: str # All India or State name
    category: str # UPSC / SSC / Railways / Banking & PSU / Police & Paramilitary / Defense / State PSC / Teaching / Engineering & Tech
    post_name: str
    total_vacancies: int
    vacancies_breakdown: Dict[str, Any] = Field(default_factory=dict)
    salary_scale: str
    in_hand_salary: str
    qualification_required: str # 10th Pass, 12th Pass, Diploma, Graduate, B.Tech/B.E., Post Graduate, MBBS, LLB, B.Ed
    qualification_details: str
    preferred_streams: List[str] = Field(default_factory=list)
    min_age: int
    max_age: int
    age_relaxation: Dict[str, int] = Field(default_factory=lambda: {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 0})
    domicile_rule: str
    gender_eligibility: str = "All (Male & Female)" # All, Male Only, Female Only
    physical_requirements: Optional[Dict[str, Any]] = None
    application_fee: Dict[str, str] = Field(default_factory=dict)
    notification_date: str
    start_date: str
    last_date: str
    exam_date: str
    admit_card_date: str
    result_date: Optional[str] = "To be announced"
    official_apply_url: str
    official_notification_pdf_url: str
    official_website_url: str
    syllabus_overview: str
    exam_pattern: List[Dict[str, Any]] = Field(default_factory=list)
    selection_steps: List[str] = Field(default_factory=list)
    important_instructions: List[str] = Field(default_factory=list)
    is_featured: bool = False
    is_new_today: bool = False
    is_closing_soon: bool = False
    status: str = "Open" # Open, Closing Soon, Admit Card Out, Exam Scheduled, Result Declared
    tags: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CandidateProfile(BaseDocument):
    user_id: str = "demo_candidate"
    full_name: str = "Aarav Sharma"
    email: str = "aarav.sharma@example.com"
    phone: str = "+91 98765 43210"
    dob: str = "2000-08-14"
    age: int = 25
    category: str = "OBC-NCL" # General, OBC-NCL, SC, ST, EWS, PwD, Ex-Servicemen
    gender: str = "Male" # Male, Female, Other
    domicile_state: str = "Uttar Pradesh"
    qualification: str = "B.Tech/B.E." # 10th Pass, 12th Pass, Diploma, Graduate, B.Tech/B.E., Post Graduate, MBBS, LLB, B.Ed
    degree_name: str = "Bachelor of Technology"
    stream: str = "Computer Science & Engineering"
    percentage_or_cgpa: str = "78%"
    additional_certs: List[str] = Field(default_factory=lambda: ["CCC Computer Certification", "Typing Speed 35 WPM English", "Driving License LMV"])
    height_cm: int = 175
    preferred_categories: List[str] = Field(default_factory=lambda: ["UPSC / Civil Services", "SSC", "Railways", "Banking & PSU", "Defense", "State PSC", "Police & Paramilitary"])
    preferred_states: List[str] = Field(default_factory=lambda: ["All India", "Uttar Pradesh", "Delhi", "Bihar", "Rajasthan", "Madhya Pradesh"])
    streak_count: int = 5
    last_checkin_date: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    points: int = 340
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CandidateProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    dob: Optional[str] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    domicile_state: Optional[str] = None
    qualification: Optional[str] = None
    degree_name: Optional[str] = None
    stream: Optional[str] = None
    percentage_or_cgpa: Optional[str] = None
    additional_certs: Optional[List[str]] = None
    height_cm: Optional[int] = None
    preferred_categories: Optional[List[str]] = None
    preferred_states: Optional[List[str]] = None

class ApplicationTrackerItem(BaseDocument):
    user_id: str = "demo_candidate"
    job_id: str
    job_title: str
    board_code: str
    status: str = "saved" # saved, applied, admit_card_ready, exam_taken, selected, rejected
    application_number: Optional[str] = ""
    roll_number: Optional[str] = ""
    exam_center: Optional[str] = ""
    applied_date: Optional[str] = ""
    exam_date: Optional[str] = ""
    notes: Optional[str] = ""
    reminder_enabled: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ApplicationTrackerCreate(BaseModel):
    job_id: str
    status: str = "saved"
    application_number: Optional[str] = ""
    roll_number: Optional[str] = ""
    exam_center: Optional[str] = ""
    applied_date: Optional[str] = ""
    exam_date: Optional[str] = ""
    notes: Optional[str] = ""
    reminder_enabled: bool = True

class QuizQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    question: str
    options: List[str]
    correct_option_index: int
    explanation: str
    subject: str # Indian Polity, History, Economy, Current Affairs, Science & Tech

class CurrentAffairsItem(BaseModel):
    title: str
    category: str
    date: str
    summary: str
    exam_relevance: str

class DailyCapsule(BaseDocument):
    date_str: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    theme: str = "Indian Constitution & Digital Public Infrastructure"
    daily_quote: str = "Success is not final, failure is not fatal: it is the courage to continue that counts. — Dedication towards Public Service."
    current_affairs: List[Dict[str, Any]] = Field(default_factory=list)
    quiz_questions: List[Dict[str, Any]] = Field(default_factory=list)

# Eligibility Calculation Engine
QUALIFICATION_HIERARCHY = {
    "10th Pass": 1,
    "12th Pass": 2,
    "Diploma": 3,
    "Graduate": 4,
    "B.Tech/B.E.": 4,
    "LLB": 4,
    "MBBS": 4,
    "B.Ed": 4,
    "Post Graduate": 5,
    "Ph.D": 6
}

def calculate_candidate_age(dob_str: str) -> int:
    try:
        birth_date = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = datetime.now(timezone.utc).date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except Exception:
        return 25

def match_job_eligibility(job: Dict[str, Any], candidate: Dict[str, Any]) -> Dict[str, Any]:
    dob = candidate.get("dob", "2000-08-14")
    candidate_age = calculate_candidate_age(dob)
    cand_category = candidate.get("category", "General")
    cand_gender = candidate.get("gender", "Male")
    cand_domicile = candidate.get("domicile_state", "Uttar Pradesh")
    cand_qual = candidate.get("qualification", "Graduate")
    cand_stream = candidate.get("stream", "")
    cand_height = candidate.get("height_cm", 170)

    # 1. Age Calculation with category relaxation
    min_age = job.get("min_age", 18)
    max_age_base = job.get("max_age", 30)
    age_relax_map = job.get("age_relaxation", {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 0})
    
    relaxation = 0
    if cand_category in ["OBC", "OBC-NCL"]:
        relaxation = age_relax_map.get("OBC", 3)
    elif cand_category in ["SC", "ST"]:
        relaxation = age_relax_map.get("SC_ST", 5)
    elif cand_category == "PwD":
        relaxation = age_relax_map.get("PwD", 10)
    elif cand_category == "Ex-Servicemen":
        relaxation = age_relax_map.get("Ex_Servicemen", 5)
    
    effective_max_age = max_age_base + relaxation
    age_eligible = (candidate_age >= min_age) and (candidate_age <= effective_max_age)
    
    age_pts = 0
    if age_eligible:
        age_pts = 35
    elif candidate_age < min_age:
        age_pts = 10
    elif candidate_age <= effective_max_age + 2:
        age_pts = 15
    else:
        age_pts = 0

    # 2. Qualification Matching
    job_qual = job.get("qualification_required", "Graduate")
    cand_rank = QUALIFICATION_HIERARCHY.get(cand_qual, 4)
    job_rank = QUALIFICATION_HIERARCHY.get(job_qual, 4)
    
    qual_eligible = False
    qual_pts = 0
    
    # Specific degree requirements check
    if job_qual in ["B.Tech/B.E.", "Engineering"]:
        if cand_qual in ["B.Tech/B.E."] or "Engineering" in cand_stream or "Technology" in cand_stream:
            qual_eligible = True
            qual_pts = 35
        elif cand_rank >= 4:
            qual_eligible = False
            qual_pts = 15
    elif job_qual == "LLB":
        if cand_qual == "LLB" or "Law" in cand_stream:
            qual_eligible = True
            qual_pts = 35
        else:
            qual_pts = 10
    elif job_qual == "B.Ed":
        if "B.Ed" in cand_qual or "B.Ed" in candidate.get("additional_certs", []):
            qual_eligible = True
            qual_pts = 35
        else:
            qual_pts = 15
    else:
        # General hierarchical comparison
        if cand_rank >= job_rank:
            qual_eligible = True
            qual_pts = 35
        elif cand_rank == job_rank - 1:
            qual_pts = 20
        else:
            qual_pts = 5

    # 3. Domicile Matching
    job_type = job.get("job_type", "Central")
    job_state = job.get("state", "All India")
    domicile_eligible = True
    domicile_pts = 0
    
    if job_type == "Central" or job_state in ["All India", "Central Govt"]:
        domicile_eligible = True
        domicile_pts = 15
    elif job_state.lower() == cand_domicile.lower():
        domicile_eligible = True
        domicile_pts = 15
    else:
        # Other state candidate applying for state jobs usually allowed under UR/General
        domicile_eligible = True
        domicile_pts = 10

    # 4. Gender & Physical Standards
    gender_req = job.get("gender_eligibility", "All (Male & Female)")
    gender_eligible = True
    if "Male Only" in gender_req and cand_gender == "Female":
        gender_eligible = False
    elif "Female Only" in gender_req and cand_gender == "Male":
        gender_eligible = False
    
    gender_pts = 15 if gender_eligible else 0

    # Physical checks for police/defense if specified
    physical_req = job.get("physical_requirements")
    physical_eligible = True
    if physical_req and isinstance(physical_req, dict):
        min_h = physical_req.get("min_height_male_cm", 165) if cand_gender == "Male" else physical_req.get("min_height_female_cm", 152)
        if cand_height < min_h:
            physical_eligible = False

    # Calculate overall match score
    total_score = age_pts + qual_pts + domicile_pts + gender_pts
    if not age_eligible:
        total_score = min(total_score, 60)
    if not qual_eligible:
        total_score = min(total_score, 50)
    if not gender_eligible or not physical_eligible:
        total_score = min(total_score, 40)
        
    match_percentage = min(100, max(15, total_score))

    reasons = []
    if age_eligible:
        reasons.append(f"Age {candidate_age} meets limit ({min_age}-{effective_max_age} yrs for {cand_category})")
    else:
        reasons.append(f"Age {candidate_age} exceeds {effective_max_age} yrs (Max for {cand_category})")

    if qual_eligible:
        reasons.append(f"{cand_qual} fulfills required {job_qual}")
    else:
        reasons.append(f"Requires {job_qual} (You have {cand_qual})")

    if job_type == "Central":
        reasons.append("All India Citizen Eligibility")
    elif job_state.lower() == cand_domicile.lower():
        reasons.append(f"Home State ({cand_domicile}) Domicile Benefit")
    else:
        reasons.append(f"Other State candidate (Eligible under General/Open Quota)")

    return {
        "match_percentage": match_percentage,
        "is_fully_eligible": (age_eligible and qual_eligible and gender_eligible and physical_eligible),
        "age_check": {
            "is_eligible": age_eligible,
            "candidate_age": candidate_age,
            "allowed_range": f"{min_age} to {effective_max_age} years",
            "base_max": max_age_base,
            "category_relaxation_years": relaxation,
            "category": cand_category
        },
        "qualification_check": {
            "is_eligible": qual_eligible,
            "candidate_qualification": cand_qual,
            "required_qualification": job_qual,
            "details": job.get("qualification_details", "")
        },
        "domicile_check": {
            "is_eligible": domicile_eligible,
            "candidate_domicile": cand_domicile,
            "job_location": job_state,
            "job_type": job_type
        },
        "gender_check": {
            "is_eligible": gender_eligible,
            "requirement": gender_req
        },
        "reasons": reasons
    }

# Rich Seed Data for Central & State Government Jobs
SEED_JOBS = [
    {
        "title": "UPSC Civil Services Examination (CSE) 2026",
        "slug": "upsc-cse-2026",
        "board": "Union Public Service Commission",
        "board_code": "UPSC",
        "job_type": "Central",
        "state": "All India",
        "category": "Civil Services",
        "post_name": "IAS, IPS, IFS, IRS & Central Group A Services",
        "total_vacancies": 1150,
        "vacancies_breakdown": {"UR": 480, "OBC": 310, "SC": 175, "ST": 85, "EWS": 100, "PwD": 40},
        "salary_scale": "Level 10: ₹56,100 - ₹1,77,500 (7th CPC)",
        "in_hand_salary": "₹82,000 / month + Govt Accommodation & Perks",
        "qualification_required": "Graduate",
        "qualification_details": "Bachelor's degree in any discipline from a recognized University.",
        "preferred_streams": ["Any Stream", "Arts", "Engineering", "Commerce", "Science"],
        "min_age": 21,
        "max_age": 32,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 0},
        "domicile_rule": "Citizen of India",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹100", "SC_ST_Female_PwD": "₹0 (Exempted)"},
        "notification_date": "2026-02-14",
        "start_date": "2026-02-14",
        "last_date": "2026-03-05",
        "exam_date": "2026-05-24 (Prelims)",
        "admit_card_date": "2026-05-10",
        "result_date": "2026-06-20",
        "official_apply_url": "https://upsconline.nic.in",
        "official_notification_pdf_url": "https://upsc.gov.in/sites/default/files/Notif-CSP-2026-engl.pdf",
        "official_website_url": "https://upsc.gov.in",
        "syllabus_overview": "Prelims: General Studies Paper I (100 Qs, 200 Marks) & CSAT Paper II (80 Qs, 200 Marks, 33% qualifying). Mains: 9 Descriptive papers including Essay, GS 1-4 & Optional.",
        "exam_pattern": [
            {"stage_num": 1, "name": "Civil Services Preliminary Exam", "type": "Objective MCQ (2 Papers)", "marks": 400, "duration": "4 Hours", "description": "GS Paper 1 (Merit) + CSAT Paper 2 (Qualifying 33%)"},
            {"stage_num": 2, "name": "Civil Services Main Examination", "type": "Descriptive Written (9 Papers)", "marks": 1750, "duration": "5 Days", "description": "Essay, GS I-IV, 2 Optional Papers, 2 Language Papers"},
            {"stage_num": 3, "name": "Personality Test / Interview", "type": "Oral Interview", "marks": 275, "duration": "45 Mins", "description": "Assessment of mental caliber, integrity and leadership traits"}
        ],
        "selection_steps": ["Preliminary Examination", "Main Written Examination", "Personality Test (Interview)", "Medical Examination", "Final All-India Merit List"],
        "important_instructions": [
            "OTR (One Time Registration) on UPSC portal is mandatory before filling application form.",
            "Candidate must upload live photograph with date stamp as per recent UPSC guidelines.",
            "Choose Optional subject and examination center carefully as changes are not allowed later."
        ],
        "is_featured": True,
        "is_new_today": False,
        "is_closing_soon": False,
        "status": "Open",
        "tags": ["IAS", "IPS", "Central Govt", "Top Prestige", "Group A"]
    },
    {
        "title": "SSC Combined Graduate Level (CGL) 2026",
        "slug": "ssc-cgl-2026",
        "board": "Staff Selection Commission",
        "board_code": "SSC",
        "job_type": "Central",
        "state": "All India",
        "category": "Staff Selection",
        "post_name": "Assistant Section Officer (ASO), Income Tax Inspector, GST Inspector, CBI SI, Auditor",
        "total_vacancies": 14500,
        "vacancies_breakdown": {"UR": 6100, "OBC": 3850, "SC": 2150, "ST": 1100, "EWS": 1300, "PwD": 500},
        "salary_scale": "Level 4 to Level 7: ₹25,500 - ₹1,42,400 (7th CPC)",
        "in_hand_salary": "₹55,000 - ₹78,000 / month based on post and city",
        "qualification_required": "Graduate",
        "qualification_details": "Bachelor's Degree in any discipline from a recognized University.",
        "preferred_streams": ["Any Graduate", "B.A", "B.Com", "B.Sc", "B.Tech", "BBA"],
        "min_age": 18,
        "max_age": 30,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 0},
        "domicile_rule": "Open to All Indian Citizens",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹100", "SC_ST_Female_PwD": "₹0 (Exempted)"},
        "notification_date": "2026-03-01",
        "start_date": "2026-03-01",
        "last_date": "2026-03-31",
        "exam_date": "2026-06-15 to 2026-06-30 (Tier 1)",
        "admit_card_date": "2026-06-05",
        "result_date": "2026-08-10",
        "official_apply_url": "https://ssc.gov.in",
        "official_notification_pdf_url": "https://ssc.gov.in/api/assets/uploads/cgl_2026_notice.pdf",
        "official_website_url": "https://ssc.gov.in",
        "syllabus_overview": "Tier 1: General Intelligence (25 Qs), General Awareness (25 Qs), Quantitative Aptitude (25 Qs), English Comprehension (25 Qs). Tier 2: Mathematical Abilities, Reasoning, English, General Awareness, Computer Knowledge & Data Entry.",
        "exam_pattern": [
            {"stage_num": 1, "name": "Tier-I Computer Based Examination", "type": "CBE Objective MCQ (100 Qs)", "marks": 200, "duration": "60 Mins", "description": "4 Sections: Reasoning, Quant, English, GK (Negative marking 0.50)"},
            {"stage_num": 2, "name": "Tier-II Computer Based Examination", "type": "CBE Paper 1 (Sectional)", "marks": 390, "duration": "2 Hrs 15 Mins", "description": "Math, Reasoning, English, GK + Computer Test (60 marks) + DEST Typing"}
        ],
        "selection_steps": ["Tier 1 Examination (Qualifying)", "Tier 2 Examination (Merit)", "DEST Typing Skill Test", "Document Verification"],
        "important_instructions": [
            "Apply strictly on new official SSC portal ssc.gov.in with live photo capture.",
            "Ensure graduation result declaration date is prior to the crucial closing date."
        ],
        "is_featured": True,
        "is_new_today": True,
        "is_closing_soon": False,
        "status": "Open",
        "tags": ["Income Tax", "GST Inspector", "Central Ministries", "ASO", "High Vacancy"]
    },
    {
        "title": "RRB Non-Technical Popular Categories (NTPC) 2026",
        "slug": "rrb-ntpc-2026",
        "board": "Railway Recruitment Control Board",
        "board_code": "RRB",
        "job_type": "Central",
        "state": "All India",
        "category": "Railways",
        "post_name": "Station Master, Goods Train Manager, Senior Clerk cum Typist, Commercial Apprentice",
        "total_vacancies": 11558,
        "vacancies_breakdown": {"UR": 4600, "OBC": 3120, "SC": 1730, "ST": 868, "EWS": 1240, "PwD": 350},
        "salary_scale": "Level 5 & 6: ₹29,200 - ₹92,300 (7th CPC) + Running Allowances",
        "in_hand_salary": "₹48,000 - ₹68,000 / month",
        "qualification_required": "Graduate",
        "qualification_details": "University degree in any discipline or equivalent from recognized institute.",
        "preferred_streams": ["Any Graduate", "Science", "Commerce", "Arts", "Engineering"],
        "min_age": 18,
        "max_age": 36,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 0},
        "domicile_rule": "Indian Citizen (Can apply to any 1 RRB Zone)",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹500 (₹400 refunded after CBT-1)", "SC_ST_Female_PwD": "₹250 (Full refunded after CBT-1)"},
        "notification_date": "2026-01-20",
        "start_date": "2026-01-25",
        "last_date": "2026-03-12",
        "exam_date": "2026-05-15 to 2026-06-10 (CBT-1)",
        "admit_card_date": "2026-05-05",
        "result_date": "2026-07-30",
        "official_apply_url": "https://www.rrbapply.gov.in",
        "official_notification_pdf_url": "https://www.rrbcdg.gov.in/uploads/CEN_05_2026_NTPC_Detailed_Notice.pdf",
        "official_website_url": "https://indianrailways.gov.in",
        "syllabus_overview": "CBT-1: General Awareness (40 Qs), Mathematics (30 Qs), General Intelligence & Reasoning (30 Qs). Total 100 questions in 90 minutes. CBT-2: 120 questions.",
        "exam_pattern": [
            {"stage_num": 1, "name": "1st Stage Computer Based Test (CBT-1)", "type": "Objective CBT (100 Qs)", "marks": 100, "duration": "90 Mins", "description": "Screening test for shortlisting candidates for CBT-2"},
            {"stage_num": 2, "name": "2nd Stage Computer Based Test (CBT-2)", "type": "Objective CBT (120 Qs)", "marks": 120, "duration": "90 Mins", "description": "Level-wise separate CBT-2 for Level 5 & Level 6 posts"},
            {"stage_num": 3, "name": "CBAT / Typing Skill Test", "type": "Aptitude / Typing", "marks": 100, "duration": "45 Mins", "description": "CBAT for Station Master, Typing test for Senior Clerk"}
        ],
        "selection_steps": ["CBT 1 (Screening)", "CBT 2 (Score Merit)", "Computer Based Aptitude Test (CBAT) / Typing", "Document Verification & Medical (A-2 standard for SM)"],
        "important_instructions": [
            "Medical Standard A-2 is mandatory for Station Master (Vision 6/9, 6/9 without glasses).",
            "Candidates can apply to only ONE RRB zone across India."
        ],
        "is_featured": True,
        "is_new_today": False,
        "is_closing_soon": True,
        "status": "Closing Soon",
        "tags": ["Indian Railways", "Station Master", "Goods Guard", "Central Govt"]
    },
    {
        "title": "State Bank of India (SBI) PO Recruitment 2026",
        "slug": "sbi-po-2026",
        "board": "State Bank of India",
        "board_code": "SBI",
        "job_type": "Central",
        "state": "All India",
        "category": "Banking & PSU",
        "post_name": "Probationary Officer (Scale-I)",
        "total_vacancies": 2000,
        "vacancies_breakdown": {"UR": 810, "OBC": 540, "SC": 300, "ST": 150, "EWS": 200, "PwD": 80},
        "salary_scale": "JMGS-I: Basic ₹41,960 + 4 advance increments",
        "in_hand_salary": "₹72,000 / month + Leased Accommodation & Medical",
        "qualification_required": "Graduate",
        "qualification_details": "Graduation in any discipline from a recognized University or final year appearing.",
        "preferred_streams": ["Any Graduate", "B.Com", "B.Tech", "Economics", "Management", "Science"],
        "min_age": 21,
        "max_age": 30,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 0},
        "domicile_rule": "Open to All Indian Citizens",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹750", "SC_ST_Female_PwD": "₹0 (Exempted)"},
        "notification_date": "2026-02-28",
        "start_date": "2026-03-01",
        "last_date": "2026-03-25",
        "exam_date": "2026-05-02 & 2026-05-03 (Prelims)",
        "admit_card_date": "2026-04-20",
        "result_date": "2026-06-15",
        "official_apply_url": "https://bank.sbi/careers",
        "official_notification_pdf_url": "https://sbi.co.in/documents/po_recruitment_2026_detailed.pdf",
        "official_website_url": "https://bank.sbi/careers",
        "syllabus_overview": "Prelims: English Language (30 Qs), Quantitative Aptitude (35 Qs), Reasoning Ability (35 Qs) in 60 mins. Mains: Reasoning & Computer (40 Qs), Data Analysis & Interpretation (30 Qs), General/Economy/Banking Awareness (50 Qs), English (35 Qs) + Descriptive Test (50 marks).",
        "exam_pattern": [
            {"stage_num": 1, "name": "Phase-I: Preliminary Examination", "type": "Online Objective Test", "marks": 100, "duration": "1 Hour", "description": "Sectional timed 20 mins each: English, Quant, Reasoning"},
            {"stage_num": 2, "name": "Phase-II: Main Examination & Descriptive", "type": "Objective + Descriptive English", "marks": 250, "duration": "3.5 Hours", "description": "Advanced DI, Reasoning, Banking Awareness + Letter/Essay writing"},
            {"stage_num": 3, "name": "Phase-III: Psychometric Test, GE & Interview", "type": "Group Discussion & Interview", "marks": 50, "duration": "30 Mins", "description": "Group Exercise (20 marks) + Personal Interview (30 marks)"}
        ],
        "selection_steps": ["Preliminary Examination", "Main Examination & Descriptive Test", "Psychometric Test", "Group Exercise & Personal Interview", "Final Merit List"],
        "important_instructions": [
            "Number of chances for General category candidates is capped at 4 attempts.",
            "Final year candidates can apply provided they submit proof of passing graduation before 31st August."
        ],
        "is_featured": True,
        "is_new_today": True,
        "is_closing_soon": False,
        "status": "Open",
        "tags": ["Banking", "SBI PO", "High Salary", "Premier Bank", "Scale 1 Officer"]
    },
    {
        "title": "UP Police Sub Inspector (SI) Recruitment 2026",
        "slug": "up-police-si-2026",
        "board": "Uttar Pradesh Police Recruitment and Promotion Board",
        "board_code": "UPPRPB",
        "job_type": "State",
        "state": "Uttar Pradesh",
        "category": "Police & Paramilitary",
        "post_name": "Sub Inspector (Civil Police), Platoon Commander (PAC) & Fire Officer-II",
        "total_vacancies": 9534,
        "vacancies_breakdown": {"UR": 3815, "OBC": 2574, "SC": 2002, "ST": 190, "EWS": 953, "Female": 1900},
        "salary_scale": "Pay Band 9300-34800, Grade Pay 4200 (Level 6: ₹35,400 - ₹1,12,400)",
        "in_hand_salary": "₹52,000 / month + Uniform & Special Allowances",
        "qualification_required": "Graduate",
        "qualification_details": "Graduation degree in any stream from recognized Indian University.",
        "preferred_streams": ["Any Graduate", "B.A", "B.Sc", "B.Tech", "B.Com"],
        "min_age": 21,
        "max_age": 28,
        "age_relaxation": {"OBC": 5, "SC_ST": 5, "PwD": 0, "Ex_Servicemen": 3, "EWS": 0},
        "domicile_rule": "UP Domicile candidates receive reservation benefits; Other states eligible under UR quota",
        "gender_eligibility": "All (Male & Female)",
        "physical_requirements": {
            "min_height_male_cm": 168,
            "min_height_female_cm": 152,
            "chest_male_cm": "79-84 cm (5 cm expansion)",
            "running_male": "4.8 km in 28 minutes",
            "running_female": "2.4 km in 16 minutes"
        },
        "application_fee": {"General_OBC_EWS": "₹400", "SC_ST_Female_PwD": "₹400"},
        "notification_date": "2026-02-10",
        "start_date": "2026-02-15",
        "last_date": "2026-03-20",
        "exam_date": "2026-06-20 to 2026-06-28",
        "admit_card_date": "2026-06-10",
        "result_date": "2026-08-30",
        "official_apply_url": "https://uppbpb.gov.in",
        "official_notification_pdf_url": "https://uppbpb.gov.in/notices/SI_Civil_Recruitment_2026.pdf",
        "official_website_url": "https://uppbpb.gov.in",
        "syllabus_overview": "General Hindi (100 Marks), Basic Law / Constitution / General Knowledge (100 Marks), Numerical & Mental Ability Test (100 Marks), Mental Aptitude / IQ Test / Reasoning (100 Marks). Total 400 Marks.",
        "exam_pattern": [
            {"stage_num": 1, "name": "Online Written Examination (400 Marks)", "type": "Objective CBT (160 Qs)", "marks": 400, "duration": "120 Mins", "description": "4 Sections: Hindi, Law/Constitution, Maths, Reasoning (35% sectional cutoff required)"},
            {"stage_num": 2, "name": "Document Verification & Physical Standard Test (PST)", "type": "Physical Measurement", "marks": 0, "duration": "1 Day", "description": "Height, Chest measurement and certificate scrutiny"},
            {"stage_num": 3, "name": "Physical Efficiency Test (PET - Race)", "type": "Qualifying Running Test", "marks": 0, "duration": "30 Mins", "description": "Male: 4.8 km in 28 mins; Female: 2.4 km in 16 mins"},
            {"stage_num": 4, "name": "Medical Examination & Final Merit List", "type": "Medical Checkup", "marks": 0, "duration": "1 Day", "description": "Eye vision, color blindness, flat foot, knock knee checks"}
        ],
        "selection_steps": ["Written Examination (400 Marks)", "DV & PST", "PET Running Test", "Medical Test", "Merit List"],
        "important_instructions": [
            "Candidate must obtain minimum 35% marks in each subject and 50% overall in written exam.",
            "UP Domicile certificate issued after 01-Apr-2025 is mandatory for claiming reservation."
        ],
        "is_featured": True,
        "is_new_today": True,
        "is_closing_soon": False,
        "status": "Open",
        "tags": ["UP Police", "Sub Inspector", "Uniform Job", "UP Govt", "High Vacancies"]
    },
    {
        "title": "71st BPSC Combined Competitive Examination (CCE) 2026",
        "slug": "71st-bpsc-cce-2026",
        "board": "Bihar Public Service Commission",
        "board_code": "BPSC",
        "job_type": "State",
        "state": "Bihar",
        "category": "State PSC",
        "post_name": "SDM (Bihar Administrative Service), DSP (Bihar Police Service), Commercial Tax Officer, BDO",
        "total_vacancies": 1920,
        "vacancies_breakdown": {"UR": 760, "OBC": 380, "EBC": 420, "SC": 300, "ST": 20, "EWS": 190, "Female": 670},
        "salary_scale": "Level 9: ₹53,100 - ₹1,67,800 (7th CPC)",
        "in_hand_salary": "₹74,000 / month + Official Bungalow & Vehicle",
        "qualification_required": "Graduate",
        "qualification_details": "Graduation in any discipline from a recognized University or equivalent.",
        "preferred_streams": ["Any Graduate", "Arts", "Science", "Commerce", "Engineering", "Law"],
        "min_age": 20,
        "max_age": 37,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 3, "EWS": 0},
        "domicile_rule": "Bihar Domicile candidates receive category reservation & 35% horizontal female quota",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹600", "SC_ST_Female_PwD": "₹150"},
        "notification_date": "2026-02-01",
        "start_date": "2026-02-05",
        "last_date": "2026-03-10",
        "exam_date": "2026-05-30 (Prelims)",
        "admit_card_date": "2026-05-18",
        "result_date": "2026-07-15",
        "official_apply_url": "https://onlinebpsc.bihar.gov.in",
        "official_notification_pdf_url": "https://www.bpsc.bih.nic.in/Advt/NB-2026-71th-CCE.pdf",
        "official_website_url": "https://www.bpsc.bih.nic.in",
        "syllabus_overview": "Prelims: General Studies (150 Marks, 150 Qs, Negative marking 1/3rd). Mains: General Hindi (100 Marks qualifying), GS Paper 1 (300 Marks), GS Paper 2 (300 Marks), Essay (300 Marks), Optional (100 Marks MCQ qualifying).",
        "exam_pattern": [
            {"stage_num": 1, "name": "Preliminary Integrated Examination", "type": "Objective MCQ (150 Qs)", "marks": 150, "duration": "2 Hours", "description": "History, Bihar Special GK, Geography, Polity, Science, Current Affairs & Math"},
            {"stage_num": 2, "name": "Main Written Examination", "type": "Descriptive (GS1, GS2, Essay)", "marks": 900, "duration": "3 Days", "description": "GS-1 (300) + GS-2 (300) + Essay (300). Optional & Hindi are qualifying only"},
            {"stage_num": 3, "name": "Interview / Personality Test", "type": "Oral Interview", "marks": 120, "duration": "30 Mins", "description": "Evaluation of administrative acumen and suitability"}
        ],
        "selection_steps": ["Preliminary Examination", "Main Written Examination", "Personal Interview", "Document Verification & Medical"],
        "important_instructions": [
            "Biometric thumb impression and live photo capture during application.",
            "Negative marking of 0.33 marks per wrong answer in Prelims."
        ],
        "is_featured": True,
        "is_new_today": False,
        "is_closing_soon": True,
        "status": "Closing Soon",
        "tags": ["BPSC", "SDM", "DSP", "Bihar Govt", "State Administrative Service"]
    },
    {
        "title": "Indian Air Force AFCAT 01/2026 (Air Force Common Admission Test)",
        "slug": "iaf-afcat-2026",
        "board": "Indian Air Force",
        "board_code": "IAF",
        "job_type": "Central",
        "state": "All India",
        "category": "Defense",
        "post_name": "Flying Branch, Ground Duty (Technical & Non-Technical) Officers",
        "total_vacancies": 317,
        "vacancies_breakdown": {"Flying": 35, "Ground_Duty_Tech": 156, "Ground_Duty_NonTech": 126},
        "salary_scale": "Level 10: ₹56,100 - ₹1,77,500 + Flying Pay ₹25,000/mo + Military Service Pay ₹15,500/mo",
        "in_hand_salary": "₹95,000 - ₹1,20,000 / month + Free Ration, Defense Housing & Canteen",
        "qualification_required": "Graduate",
        "qualification_details": "Graduation with minimum 60% marks and 50% in Maths & Physics in 10+2, OR B.E/B.Tech degree.",
        "preferred_streams": ["B.Tech/B.E.", "B.Sc (Maths/Physics)", "Any Graduate with 12th PCM", "B.Com/BBA"],
        "min_age": 20,
        "max_age": 24,
        "age_relaxation": {"OBC": 0, "SC_ST": 0, "PwD": 0, "Ex_Servicemen": 0, "EWS": 0},
        "domicile_rule": "Unmarried Indian Citizens",
        "gender_eligibility": "All (Male & Female)",
        "physical_requirements": {
            "min_height_male_cm": 162.5,
            "min_height_female_cm": 162.5,
            "eye_vision": "6/6 without glasses for Flying Branch"
        },
        "application_fee": {"General_OBC_EWS": "₹550", "SC_ST_Female_PwD": "₹550"},
        "notification_date": "2026-02-18",
        "start_date": "2026-02-20",
        "last_date": "2026-03-22",
        "exam_date": "2026-05-16 to 2026-05-18",
        "admit_card_date": "2026-05-02",
        "result_date": "2026-06-25",
        "official_apply_url": "https://afcat.cdac.in",
        "official_notification_pdf_url": "https://afcat.cdac.in/AFCAT/assets/images/news/AFCAT_01_2026_Notification.pdf",
        "official_website_url": "https://careerindianairforce.cdac.in",
        "syllabus_overview": "AFCAT Online Test: General Awareness, Verbal Ability in English, Numerical Ability and Reasoning and Military Aptitude Test. 100 Qs for 300 Marks.",
        "exam_pattern": [
            {"stage_num": 1, "name": "AFCAT Online Examination", "type": "Objective CBT (100 Qs)", "marks": 300, "duration": "2 Hours", "description": "English, Reasoning, Military Aptitude, Maths & Current Affairs"},
            {"stage_num": 2, "name": "Air Force Selection Board (AFSB Interview)", "type": "5-Day SSB Process", "marks": 300, "duration": "5 Days", "description": "Stage 1: OIR & PPDT screening; Stage 2: Psychological tests, GTO tasks, Personal Interview & Conference"},
            {"stage_num": 3, "name": "CPSS & Medical Board", "type": "Computerized Pilot Selection System", "marks": 0, "duration": "1 Day", "description": "CPSS for Flying Branch aspirants + Comprehensive IAM aviation medical test"}
        ],
        "selection_steps": ["AFCAT Written Test", "AFSB Interview (5 Days)", "CPSS Machine Test (Flying only)", "Aviation Medical Examination", "All India Merit List"],
        "important_instructions": [
            "Candidates must be unmarried at the time of commencement of course.",
            "Flying branch requires strict anthropometric measurements (Leg length, Thigh length, Sitting height)."
        ],
        "is_featured": False,
        "is_new_today": True,
        "is_closing_soon": False,
        "status": "Open",
        "tags": ["Indian Air Force", "Pilot", "Commissioned Officer", "AFCAT", "High Salary"]
    },
    {
        "title": "ISRO Scientist / Engineer 'SC' Recruitment 2026",
        "slug": "isro-scientist-engineer-sc-2026",
        "board": "Indian Space Research Organisation",
        "board_code": "ISRO",
        "job_type": "Central",
        "state": "All India",
        "category": "Engineering & Tech",
        "post_name": "Scientist / Engineer 'SC' (Computer Science, Electronics, Mechanical, Civil)",
        "total_vacancies": 340,
        "vacancies_breakdown": {"UR": 140, "OBC": 92, "SC": 51, "ST": 25, "EWS": 32, "PwD": 14},
        "salary_scale": "Level 10: ₹56,100 - ₹1,77,500 (7th CPC)",
        "in_hand_salary": "₹84,000 / month + Space Agency Allowances + ISRO Quarters",
        "qualification_required": "B.Tech/B.E.",
        "qualification_details": "B.E/B.Tech or equivalent in CSE, ECE, Mechanical or Civil with minimum 65% marks or 6.84 CGPA.",
        "preferred_streams": ["Computer Science", "Information Technology", "Electronics & Communication", "Mechanical", "Civil Engineering"],
        "min_age": 18,
        "max_age": 28,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 0},
        "domicile_rule": "Open to All Indian Citizens",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹250", "SC_ST_Female_PwD": "₹250 (Refundable upon appearing)"},
        "notification_date": "2026-02-25",
        "start_date": "2026-02-28",
        "last_date": "2026-03-25",
        "exam_date": "2026-06-14",
        "admit_card_date": "2026-05-30",
        "result_date": "2026-08-01",
        "official_apply_url": "https://www.isro.gov.in/Careers.html",
        "official_notification_pdf_url": "https://www.isro.gov.in/media_isro/pdf/recruitment_docs/ICRB_01_2026.pdf",
        "official_website_url": "https://www.isro.gov.in",
        "syllabus_overview": "Part A (Core Technical Discipline - 80 Qs, 80 Marks), Part B (Aptitude/Reasoning - 15 Qs, 20 Marks). Total 100 Marks. Gate-level difficulty.",
        "exam_pattern": [
            {"stage_num": 1, "name": "Written Test (CBT)", "type": "Objective Technical CBT", "marks": 100, "duration": "120 Mins", "description": "80 marks core branch questions + 20 marks general aptitude"},
            {"stage_num": 2, "name": "Technical Interview", "type": "In-depth Technical Interview", "marks": 100, "duration": "45 Mins", "description": "Conceptual questioning by ISRO scientist board in Bangalore/Trivandrum"}
        ],
        "selection_steps": ["Written Examination (Shortlisting 1:5 ratio)", "Personal Technical Interview (60% weightage)", "Final Merit List"],
        "important_instructions": [
            "Minimum 50% in written exam and minimum 60% in interview required to be empaneled.",
            "Final year B.Tech students who finish before July 2026 can apply."
        ],
        "is_featured": False,
        "is_new_today": True,
        "is_closing_soon": False,
        "status": "Open",
        "tags": ["ISRO", "Scientist", "Space Research", "Tech Job", "Level 10"]
    },
    {
        "title": "Delhi Subordinate Services DSSSB TGT & PGT Teacher Recruitment 2026",
        "slug": "dsssb-teacher-recruitment-2026",
        "board": "Delhi Subordinate Services Selection Board",
        "board_code": "DSSSB",
        "job_type": "State",
        "state": "Delhi",
        "category": "Teaching",
        "post_name": "Trained Graduate Teacher (TGT) & Post Graduate Teacher (PGT) in Directorate of Education",
        "total_vacancies": 5118,
        "vacancies_breakdown": {"UR": 2100, "OBC": 1380, "SC": 780, "ST": 390, "EWS": 468, "PwD": 180},
        "salary_scale": "Level 7 (TGT) & Level 8 (PGT): ₹44,900 - ₹1,51,100 + Delhi HRA (27%)",
        "in_hand_salary": "₹68,000 - ₹79,000 / month",
        "qualification_required": "B.Ed",
        "qualification_details": "Bachelor's / Master's degree in respective subject with B.Ed degree and CTET Paper-2 qualified for TGT.",
        "preferred_streams": ["B.Ed", "B.A B.Ed", "B.Sc B.Ed", "M.A", "M.Sc", "M.Com"],
        "min_age": 18,
        "max_age": 32,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 0},
        "domicile_rule": "Open to all; OBC Delhi candidates get OBC quota, outside OBC considered in UR",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹100", "SC_ST_Female_PwD": "₹0 (Exempted)"},
        "notification_date": "2026-02-12",
        "start_date": "2026-02-18",
        "last_date": "2026-03-19",
        "exam_date": "2026-06-08 to 2026-06-18",
        "admit_card_date": "2026-05-28",
        "result_date": "2026-08-20",
        "official_apply_url": "https://dsssbonline.nic.in",
        "official_notification_pdf_url": "https://dsssb.delhi.gov.in/sites/default/files/DSSSB_Advt_02_2026_TGT.pdf",
        "official_website_url": "https://dsssb.delhi.gov.in",
        "syllabus_overview": "Section A (General - 100 Marks): GK, Reasoning, Maths, Hindi, English (20 Qs each). Section B (Concerned Subject & Teaching Methodology - 100 Marks). Total 200 Marks in 2 Hours.",
        "exam_pattern": [
            {"stage_num": 1, "name": "Tier-I Technical One-Tier Exam", "type": "Objective Online CBT (200 Qs)", "marks": 200, "duration": "120 Mins", "description": "100 marks General Studies & Pedagogy + 100 marks Subject specialization (0.25 negative marking)"}
        ],
        "selection_steps": ["Tier 1 Online Examination (Merit based)", "Document Verification in Delhi DoE", "Medical Fitness & Appointment"],
        "important_instructions": [
            "CTET certificate is mandatory at the time of online application.",
            "Only OBC certificates issued by Govt of NCT of Delhi are accepted for OBC reservation."
        ],
        "is_featured": False,
        "is_new_today": False,
        "is_closing_soon": False,
        "status": "Open",
        "tags": ["DSSSB", "Govt Teacher", "Delhi Govt", "TGT", "PGT", "CTET"]
    },
    {
        "title": "Rajasthan Public Service Commission (RPSC) RAS / RTS 2026",
        "slug": "rpsc-ras-2026",
        "board": "Rajasthan Public Service Commission",
        "board_code": "RPSC",
        "job_type": "State",
        "state": "Rajasthan",
        "category": "State PSC",
        "post_name": "RAS (Rajasthan Administrative Service), RPS (Police Service), Accounts Service",
        "total_vacancies": 1024,
        "vacancies_breakdown": {"UR": 410, "OBC": 215, "SC": 164, "ST": 133, "EWS": 102, "PwD": 40},
        "salary_scale": "Level 14: Grade Pay 5400 (Level 14: ₹56,100 - ₹1,77,500)",
        "in_hand_salary": "₹69,000 / month + Govt Bungalow & DA",
        "qualification_required": "Graduate",
        "qualification_details": "Degree of recognized University in India or equivalent qualification.",
        "preferred_streams": ["Any Graduate", "Arts", "Science", "Commerce", "Engineering"],
        "min_age": 21,
        "max_age": 40,
        "age_relaxation": {"OBC": 5, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 5},
        "domicile_rule": "Rajasthan Domicile gets category reservation; Other state candidates apply under General",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹600", "SC_ST_Female_PwD": "₹400"},
        "notification_date": "2026-02-05",
        "start_date": "2026-02-10",
        "last_date": "2026-03-15",
        "exam_date": "2026-06-25 (Prelims)",
        "admit_card_date": "2026-06-12",
        "result_date": "2026-08-15",
        "official_apply_url": "https://sso.rajasthan.gov.in",
        "official_notification_pdf_url": "https://rpsc.rajasthan.gov.in/Static/RecruitmentAdvertisements/RAS_2026_Advt.pdf",
        "official_website_url": "https://rpsc.rajasthan.gov.in",
        "syllabus_overview": "Prelims: General Knowledge & General Science (150 Qs, 200 Marks). Mains: 4 Papers of 200 marks each (GS 1, GS 2, GS 3, General Hindi & English).",
        "exam_pattern": [
            {"stage_num": 1, "name": "Preliminary Examination", "type": "Objective MCQ (150 Qs)", "marks": 200, "duration": "3 Hours", "description": "Rajasthan History, Culture, Geography, Indian Polity, Economy, Science & Reasoning"},
            {"stage_num": 2, "name": "Main Written Examination", "type": "Descriptive 4 Papers", "marks": 800, "duration": "2 Days", "description": "Paper I, II, III (GS) + Paper IV (General Hindi 120 marks, General English 80 marks)"},
            {"stage_num": 3, "name": "Personality & Viva-Voce Examination", "type": "Personal Interview", "marks": 100, "duration": "30 Mins", "description": "Assessment of personality, knowledge of Rajasthani culture and leadership"}
        ],
        "selection_steps": ["Prelims Exam", "Mains Written Exam", "Personality Test (Interview)", "Final Merit List"],
        "important_instructions": [
            "Application via SSO ID on Rajasthan portal is mandatory.",
            "High weightage given to Rajasthan-specific history, heritage and economy."
        ],
        "is_featured": False,
        "is_new_today": False,
        "is_closing_soon": True,
        "status": "Closing Soon",
        "tags": ["RPSC", "RAS", "RPS", "Rajasthan Govt", "State Service"]
    },
    {
        "title": "IBPS PO (Probationary Officers / Management Trainees XV) 2026",
        "slug": "ibps-po-xv-2026",
        "board": "Institute of Banking Personnel Selection",
        "board_code": "IBPS",
        "job_type": "Central",
        "state": "All India",
        "category": "Banking & PSU",
        "post_name": "Probationary Officer (PO/MT) in 11 Participating Public Sector Banks (PNB, Canara, BoB, etc.)",
        "total_vacancies": 4450,
        "vacancies_breakdown": {"UR": 1820, "OBC": 1200, "SC": 665, "ST": 335, "EWS": 430, "PwD": 180},
        "salary_scale": "Scale I: ₹36,000 - ₹63,840 (Revised under 12th BPS)",
        "in_hand_salary": "₹65,000 / month + Bank Quarters + Fuel & Newspaper Allowance",
        "qualification_required": "Graduate",
        "qualification_details": "A Degree (Graduation) in any discipline from a University recognized by the Govt. of India.",
        "preferred_streams": ["Any Graduate", "Commerce", "Engineering", "Arts", "Science", "BBA"],
        "min_age": 20,
        "max_age": 30,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 0},
        "domicile_rule": "Open to All Indian Citizens",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹850", "SC_ST_Female_PwD": "₹175"},
        "notification_date": "2026-03-02",
        "start_date": "2026-03-04",
        "last_date": "2026-03-26",
        "exam_date": "2026-05-23 & 2026-05-24 (Prelims)",
        "admit_card_date": "2026-05-12",
        "result_date": "2026-06-30",
        "official_apply_url": "https://ibpsonline.ibps.in",
        "official_notification_pdf_url": "https://www.ibps.in/wp-content/uploads/Detailed_Advt_CRP_PO_XV.pdf",
        "official_website_url": "https://www.ibps.in",
        "syllabus_overview": "Prelims: English (30 Qs, 20 mins), Quantitative Aptitude (35 Qs, 20 mins), Reasoning Ability (35 Qs, 20 mins). Mains: Reasoning & Computer (45 Qs), General/Banking Awareness (40 Qs), English (35 Qs), Data Analysis (35 Qs) + Descriptive writing (25 marks).",
        "exam_pattern": [
            {"stage_num": 1, "name": "Preliminary Examination", "type": "Online CBT (100 Qs)", "marks": 100, "duration": "60 Mins", "description": "Sectional timed screening test"},
            {"stage_num": 2, "name": "Main Examination & Letter/Essay", "type": "Objective + Descriptive", "marks": 225, "duration": "3.5 Hours", "description": "Score considered for final merit list"},
            {"stage_num": 3, "name": "Common Interview", "type": "Personal Interview by Nodal Banks", "marks": 100, "duration": "25 Mins", "description": "Minimum qualifying 40% (35% for SC/ST/OBC)"}
        ],
        "selection_steps": ["Online Preliminary Exam", "Online Main Exam", "Common Interview", "Provisional Bank Allotment"],
        "important_instructions": [
            "Participating banks include PNB, Bank of Baroda, Canara Bank, Union Bank, Indian Bank, Bank of India.",
            "Candidate preference order of banks must be filled during online application."
        ],
        "is_featured": False,
        "is_new_today": True,
        "is_closing_soon": False,
        "status": "Open",
        "tags": ["Banking", "IBPS PO", "Public Sector Banks", "Scale 1", "Pan India"]
    },
    {
        "title": "SSC Junior Engineer (JE) Examination 2026",
        "slug": "ssc-je-2026",
        "board": "Staff Selection Commission",
        "board_code": "SSC",
        "job_type": "Central",
        "state": "All India",
        "category": "Engineering & Tech",
        "post_name": "Junior Engineer (Civil, Mechanical, Electrical) in CPWD, MES, BRO & CWC",
        "total_vacancies": 2860,
        "vacancies_breakdown": {"UR": 1210, "OBC": 760, "SC": 430, "ST": 210, "EWS": 250, "PwD": 80},
        "salary_scale": "Level 6: ₹35,400 - ₹1,12,400 (7th CPC)",
        "in_hand_salary": "₹54,000 / month + DA & HRA",
        "qualification_required": "Diploma",
        "qualification_details": "Diploma or Degree in Civil / Electrical / Mechanical Engineering from a recognized University/Institute.",
        "preferred_streams": ["Civil Engineering", "Electrical Engineering", "Mechanical Engineering", "Diploma", "B.Tech/B.E."],
        "min_age": 18,
        "max_age": 30,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 10, "Ex_Servicemen": 5, "EWS": 0},
        "domicile_rule": "Open to All Indian Citizens",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹100", "SC_ST_Female_PwD": "₹0 (Exempted)"},
        "notification_date": "2026-02-22",
        "start_date": "2026-02-25",
        "last_date": "2026-03-24",
        "exam_date": "2026-06-02 to 2026-06-05",
        "admit_card_date": "2026-05-20",
        "result_date": "2026-07-28",
        "official_apply_url": "https://ssc.gov.in",
        "official_notification_pdf_url": "https://ssc.gov.in/api/assets/uploads/Notice_SSC_JE_2026.pdf",
        "official_website_url": "https://ssc.gov.in",
        "syllabus_overview": "Paper 1 (CBT - 200 Marks): General Intelligence & Reasoning (50 Qs), General Awareness (50 Qs), General Engineering - Civil/Elec/Mech (100 Qs). Paper 2 (CBT - 300 Marks): Core Engineering Subject.",
        "exam_pattern": [
            {"stage_num": 1, "name": "Paper-I Computer Based Exam", "type": "Objective MCQ (200 Qs)", "marks": 200, "duration": "2 Hours", "description": "General Intelligence (50), GK (50), Domain Engineering (100)"},
            {"stage_num": 2, "name": "Paper-II Computer Based Exam", "type": "Objective Domain CBT (100 Qs)", "marks": 300, "duration": "2 Hours", "description": "In-depth engineering concept questions (3 marks each, 1 mark negative)"}
        ],
        "selection_steps": ["Paper 1 CBT", "Paper 2 CBT", "Document Verification", "Medical & Department Allocation"],
        "important_instructions": [
            "CPWD and MES postings available nationwide.",
            "Both 3-year Polytechnic Diploma and 4-year B.Tech graduates are eligible."
        ],
        "is_featured": False,
        "is_new_today": False,
        "is_closing_soon": False,
        "status": "Open",
        "tags": ["SSC JE", "CPWD", "Engineering", "Civil", "Electrical", "Mechanical"]
    },
    {
        "title": "Maharashtra Public Service Commission (MPSC) Civil Services 2026",
        "slug": "mpsc-civil-services-2026",
        "board": "Maharashtra Public Service Commission",
        "board_code": "MPSC",
        "job_type": "State",
        "state": "Maharashtra",
        "category": "State PSC",
        "post_name": "Deputy Collector, DSP, Tehsildar, Assistant Commissioner of State Tax",
        "total_vacancies": 845,
        "vacancies_breakdown": {"UR": 340, "OBC": 160, "SC": 110, "ST": 60, "EWS": 85, "SEBC": 90},
        "salary_scale": "S-20: ₹56,100 - ₹1,77,500 (7th CPC)",
        "in_hand_salary": "₹72,000 / month + Perks",
        "qualification_required": "Graduate",
        "qualification_details": "Bachelor's Degree in any faculty from a recognized University with proficiency in Marathi.",
        "preferred_streams": ["Any Graduate", "Arts", "Science", "Commerce", "Engineering", "Law"],
        "min_age": 19,
        "max_age": 38,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 7, "Ex_Servicemen": 5, "EWS": 3},
        "domicile_rule": "Maharashtra Domicile mandatory for reservation and fee concessions",
        "gender_eligibility": "All (Male & Female)",
        "application_fee": {"General_OBC_EWS": "₹394", "SC_ST_Female_PwD": "₹294"},
        "notification_date": "2026-02-08",
        "start_date": "2026-02-12",
        "last_date": "2026-03-08",
        "exam_date": "2026-05-10 (Prelims)",
        "admit_card_date": "2026-04-28",
        "result_date": "2026-07-10",
        "official_apply_url": "https://mpsconline.gov.in",
        "official_notification_pdf_url": "https://mpsc.gov.in/downloadFile/notice/MPSC_Rajyaseva_2026.pdf",
        "official_website_url": "https://mpsc.gov.in",
        "syllabus_overview": "Prelims: Paper 1 GS (200 Marks) & Paper 2 CSAT (200 Marks, qualifying). Mains: Descriptive pattern aligned with UPSC syllabus with Maharashtra focus.",
        "exam_pattern": [
            {"stage_num": 1, "name": "Preliminary Examination", "type": "Objective MCQ", "marks": 400, "duration": "4 Hours", "description": "Paper 1 GS + Paper 2 CSAT (Qualifying 33%)"},
            {"stage_num": 2, "name": "Main Written Examination", "type": "Descriptive (9 Papers)", "marks": 1750, "duration": "5 Days", "description": "Language papers (Marathi/English) + Essay + GS 1-4 + Optional"},
            {"stage_num": 3, "name": "Interview / Personality Test", "type": "Personal Interview", "marks": 275, "duration": "30 Mins", "description": "Assessment by MPSC panel in Mumbai"}
        ],
        "selection_steps": ["Preliminary Examination", "Main Examination", "Personal Interview", "Final Merit List"],
        "important_instructions": [
            "Knowledge of Marathi language (reading, writing, speaking) is mandatory.",
            "Non-Creamy Layer (NCL) certificate required for OBC/SEBC."
        ],
        "is_featured": False,
        "is_new_today": False,
        "is_closing_soon": True,
        "status": "Closing Soon",
        "tags": ["MPSC", "Deputy Collector", "DSP", "Maharashtra Govt", "Rajyaseva"]
    },
    {
        "title": "SSC Constable (GD) in CAPFs, SSF, Rifleman in Assam Rifles 2026",
        "slug": "ssc-gd-constable-2026",
        "board": "Staff Selection Commission",
        "board_code": "SSC",
        "job_type": "Central",
        "state": "All India",
        "category": "Police & Paramilitary",
        "post_name": "General Duty Constable in BSF, CISF, CRPF, SSB, ITBP, AR, SSF",
        "total_vacancies": 39481,
        "vacancies_breakdown": {"UR": 15800, "OBC": 9800, "SC": 5900, "ST": 4100, "EWS": 3881, "Female": 4500},
        "salary_scale": "Pay Level 3: ₹21,700 - ₹69,100 (7th CPC)",
        "in_hand_salary": "₹36,000 - ₹44,000 / month (depending on posting risk allowance)",
        "qualification_required": "10th Pass",
        "qualification_details": "Matriculation or 10th Class pass from a recognized Board/University.",
        "preferred_streams": ["10th Pass", "12th Pass", "Any Stream"],
        "min_age": 18,
        "max_age": 23,
        "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 0, "Ex_Servicemen": 3, "EWS": 0},
        "domicile_rule": "State/UT wise vacancies with border and naxal affected district quotas",
        "gender_eligibility": "All (Male & Female)",
        "physical_requirements": {
            "min_height_male_cm": 170,
            "min_height_female_cm": 157,
            "running_male": "5 km in 24 minutes",
            "running_female": "1.6 km in 8.5 minutes"
        },
        "application_fee": {"General_OBC_EWS": "₹100", "SC_ST_Female_PwD": "₹0 (Exempted)"},
        "notification_date": "2026-01-15",
        "start_date": "2026-01-18",
        "last_date": "2026-02-28",
        "exam_date": "2026-04-15 to 2026-05-10",
        "admit_card_date": "2026-04-01",
        "result_date": "2026-06-30",
        "official_apply_url": "https://ssc.gov.in",
        "official_notification_pdf_url": "https://ssc.gov.in/api/assets/uploads/Notice_GD_2026.pdf",
        "official_website_url": "https://ssc.gov.in",
        "syllabus_overview": "Computer Based Exam (80 Qs, 160 Marks): General Intelligence (20 Qs), General Knowledge (20 Qs), Elementary Mathematics (20 Qs), English/Hindi (20 Qs). Duration: 60 Minutes.",
        "exam_pattern": [
            {"stage_num": 1, "name": "Computer Based Examination (CBE)", "type": "Objective CBT (80 Qs)", "marks": 160, "duration": "60 Mins", "description": "0.25 negative marking per wrong answer; multilingual in 13 regional languages"},
            {"stage_num": 2, "name": "Physical Standard Test (PST) & Physical Efficiency Test (PET)", "type": "Race & Measurement", "marks": 0, "duration": "1 Day", "description": "5 km race in 24 min for Male; 1.6 km in 8.5 min for Female"},
            {"stage_num": 3, "name": "Detailed Medical Examination (DME) & Review Medical", "type": "Medical Check", "marks": 0, "duration": "1 Day", "description": "Comprehensive defense paramedic fitness examination"}
        ],
        "selection_steps": ["CBE Online Exam", "Physical Standard & Efficiency Test", "Detailed Medical Examination", "Final Force Allocation"],
        "important_instructions": [
            "Available in 13 regional Indian languages in addition to Hindi & English.",
            "Bonus marks awarded for NCC A, B, and C certificate holders."
        ],
        "is_featured": False,
        "is_new_today": False,
        "is_closing_soon": False,
        "status": "Exam Scheduled",
        "tags": ["SSC GD", "CRPF", "BSF", "CISF", "10th Pass", "High Vacancy", "Paramilitary"]
    }
]

# Daily GK & Current Affairs Seed Capsule
DAILY_CAPSULES_SEED = {
    "date_str": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    "theme": "Indian Polity, Governance & Space Missions",
    "daily_quote": "The best way to find yourself is to lose yourself in the service of others. — Dedication to Public Welfare.",
    "current_affairs": [
        {
            "title": "PM Surya Ghar Muft Bijli Yojana Expansion",
            "category": "Govt Schemes & Economy",
            "date": "Today",
            "summary": "Government reaches milestone of 1 crore registrations under rooftop solar scheme, providing up to 300 units of free electricity per month.",
            "exam_relevance": "Important for UPSC GS-3, SSC CGL Economics & State PSC Prelims questions on renewable energy targets."
        },
        {
            "title": "ISRO Gaganyaan Crew Module Atmospheric Re-entry Test",
            "category": "Science & Technology",
            "date": "Today",
            "summary": "ISRO successfully conducts drogue parachute deployment test at the Terminal Ballistics Research Laboratory for the upcoming uncrewed mission.",
            "exam_relevance": "Direct question expected in UPSC Prelims Science & Tech and Defense/AFCAT exams."
        },
        {
            "title": "Finance Commission Recommendations on State Devolution",
            "category": "Indian Polity & Fiscal Federalism",
            "date": "Today",
            "summary": "Key discussion on tax devolution formula under Article 280, balancing demographic performance and equity criteria across states.",
            "exam_relevance": "High yield for UPSC Mains GS-2 and BPSC/UPPSC Administrative service exams."
        },
        {
            "title": "India's Unified Payments Interface (UPI) Linked with International Hubs",
            "category": "Economy & Banking",
            "date": "Today",
            "summary": "Cross-border real-time remittance network expands to new Southeast Asian and Gulf corridors, lowering transaction costs by 40%.",
            "exam_relevance": "Crucial for SBI PO, IBPS PO and RBI Grade B economic awareness sections."
        },
        {
            "title": "Supreme Court 7-Judge Bench on Sub-Classification of Reservation",
            "category": "Constitutional Law",
            "date": "Today",
            "summary": "Landmark ruling clarifying states' powers to create sub-quotas within SC/ST categories to target the most marginalized communities.",
            "exam_relevance": "Must-know for Judicial exams, UPSC Civil Services GS-2 and State PSCs."
        }
    ],
    "quiz_questions": [
        {
            "id": "q1",
            "question": "Under which Article of the Indian Constitution is the Finance Commission constituted by the President?",
            "options": ["Article 268", "Article 280", "Article 312", "Article 324"],
            "correct_option_index": 1,
            "explanation": "Article 280 of the Constitution provides for a Finance Commission as a quasi-judicial body constituted by the President every fifth year.",
            "subject": "Indian Polity"
        },
        {
            "id": "q2",
            "question": "Which among the following is the headquarters of the Indian Space Research Organisation (ISRO)?",
            "options": ["Thiruvananthapuram", "Sriharikota", "Bengaluru", "Hyderabad"],
            "correct_option_index": 2,
            "explanation": "ISRO is headquartered in Bengaluru, Karnataka, while its launch site is the Satish Dhawan Space Centre at Sriharikota, Andhra Pradesh.",
            "subject": "Science & Tech"
        },
        {
            "id": "q3",
            "question": "What is the maximum permissible age relaxation for OBC (Non-Creamy Layer) candidates in UPSC Civil Services Examination?",
            "options": ["2 Years", "3 Years", "5 Years", "7 Years"],
            "correct_option_index": 1,
            "explanation": "OBC-NCL candidates receive an age relaxation of up to 3 years and a maximum of 9 attempts in the UPSC Civil Services Examination.",
            "subject": "Exam Guidelines"
        },
        {
            "id": "q4",
            "question": "Which schedule of the Indian Constitution contains the list of 22 officially recognized languages?",
            "options": ["7th Schedule", "8th Schedule", "9th Schedule", "10th Schedule"],
            "correct_option_index": 1,
            "explanation": "The Eighth Schedule to the Constitution of India lists the 22 official languages of the Republic of India.",
            "subject": "Indian Polity"
        },
        {
            "id": "q5",
            "question": "Under the 7th Central Pay Commission, what is the starting basic pay for Pay Level 10 (Group A / IAS / IPS / Scientist SC)?",
            "options": ["₹44,900", "₹56,100", "₹67,700", "₹78,800"],
            "correct_option_index": 1,
            "explanation": "Level 10 under the 7th CPC has an initial entry basic pay of ₹56,100, which corresponds to the pre-revised Grade Pay of ₹5,400 (PB-3).",
            "subject": "Govt Pay Scale"
        }
    ]
}

# Startup Event: Seed database if empty
@app.on_event("startup")
async def seed_initial_data():
    try:
        jobs_count = await db.jobs.count_documents({})
        if jobs_count == 0:
            logger.info("Seeding initial authentic Government Jobs into MongoDB...")
            job_docs = []
            for item in SEED_JOBS:
                job_obj = JobModel(**item)
                job_docs.append(job_obj.to_mongo())
            if job_docs:
                await db.jobs.insert_many(job_docs)
                logger.info(f"Successfully seeded {len(job_docs)} jobs.")
        
        # Seed Profile if empty
        cand = await db.candidate_profiles.find_one({"user_id": "demo_candidate"})
        if not cand:
            default_prof = CandidateProfile()
            await db.candidate_profiles.insert_one(default_prof.to_mongo())
            logger.info("Default candidate profile seeded.")
        
        # Seed Daily Capsule if empty
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        capsule = await db.daily_capsules.find_one({"date_str": today_str})
        if not capsule:
            daily_obj = DailyCapsule(**DAILY_CAPSULES_SEED)
            await db.daily_capsules.insert_one(daily_obj.to_mongo())
            logger.info("Seeded today's daily capsule.")

        # Seed 2 sample application trackers
        trackers_count = await db.application_trackers.count_documents({})
        if trackers_count == 0:
            first_job = await db.jobs.find_one({"board_code": "UPSC"})
            second_job = await db.jobs.find_one({"board_code": "SSC"})
            if first_job:
                t1 = ApplicationTrackerItem(
                    job_id=str(first_job["_id"]),
                    job_title=first_job["title"],
                    board_code=first_job["board_code"],
                    status="applied",
                    application_number="UPSC2026-9812450",
                    roll_number="0812940",
                    exam_center="New Delhi (Zone 1)",
                    applied_date="2026-02-18",
                    exam_date=first_job["exam_date"],
                    notes="Completed GS Paper 1 and CSAT revisions. Mock test score: 114/200."
                )
                await db.application_trackers.insert_one(t1.to_mongo())
            if second_job:
                t2 = ApplicationTrackerItem(
                    job_id=str(second_job["_id"]),
                    job_title=second_job["title"],
                    board_code=second_job["board_code"],
                    status="saved",
                    notes="Reviewing vacancy breakup for Income Tax Inspector vs ASO MEA."
                )
                await db.application_trackers.insert_one(t2.to_mongo())
    except Exception as e:
        logger.error(f"Error during startup seeding: {str(e)}")

# Routes

@api_router.get("/")
async def root():
    return {"status": "ok", "service": "SarkariSeva AI Government Job Portal API", "version": "1.0.0"}

# 1. Candidate Profile Endpoints
@api_router.get("/profile", response_model=CandidateProfile)
async def get_candidate_profile(user_id: str = "demo_candidate"):
    prof_doc = await db.candidate_profiles.find_one({"user_id": user_id})
    if not prof_doc:
        default_prof = CandidateProfile(user_id=user_id)
        await db.candidate_profiles.insert_one(default_prof.to_mongo())
        return default_prof
    return CandidateProfile.from_mongo(prof_doc)

@api_router.post("/profile", response_model=CandidateProfile)
async def update_candidate_profile(payload: CandidateProfileUpdate, user_id: str = "demo_candidate"):
    prof_doc = await db.candidate_profiles.find_one({"user_id": user_id})
    if not prof_doc:
        current = CandidateProfile(user_id=user_id).model_dump()
    else:
        current = CandidateProfile.from_mongo(prof_doc).model_dump()

    update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    
    # Recalculate age if dob updated
    if "dob" in update_data:
        update_data["age"] = calculate_candidate_age(update_data["dob"])

    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    current.update(update_data)
    
    updated_obj = CandidateProfile(**current)
    await db.candidate_profiles.update_one(
        {"user_id": user_id},
        {"$set": updated_obj.to_mongo()},
        upsert=True
    )
    return updated_obj

# 2. Jobs Feed & Filter Endpoints
@api_router.get("/jobs")
async def get_jobs_feed(
    search: Optional[str] = None,
    category: Optional[str] = None,
    job_type: Optional[str] = None, # Central / State
    state: Optional[str] = None,
    qualification: Optional[str] = None,
    status: Optional[str] = None,
    is_featured: Optional[bool] = None,
    is_new: Optional[bool] = None,
    sort_by: Optional[str] = "recommended", # recommended, closing_soon, vacancies, latest
    user_id: str = "demo_candidate"
):
    # Fetch candidate profile for dynamic match calculation
    cand_doc = await db.candidate_profiles.find_one({"user_id": user_id})
    candidate = CandidateProfile.from_mongo(cand_doc).model_dump() if cand_doc else CandidateProfile().model_dump()

    query: Dict[str, Any] = {}
    
    if search:
        search_regex = {"$regex": search, "$options": "i"}
        query["$or"] = [
            {"title": search_regex},
            {"board": search_regex},
            {"board_code": search_regex},
            {"post_name": search_regex},
            {"state": search_regex},
            {"category": search_regex},
            {"tags": search_regex}
        ]

    if category and category not in ["All", "All Categories"]:
        query["category"] = {"$regex": category, "$options": "i"}
    
    if job_type and job_type not in ["All", "All Types"]:
        query["job_type"] = job_type
        
    if state and state not in ["All", "All India", "All States"]:
        query["$or"] = [
            {"state": {"$regex": state, "$options": "i"}},
            {"state": "All India"}
        ]
        
    if qualification and qualification not in ["All", "All Qualifications"]:
        query["qualification_required"] = {"$regex": qualification, "$options": "i"}
        
    if status and status not in ["All", "All Statuses"]:
        query["status"] = status

    if is_featured is not None:
        query["is_featured"] = is_featured

    if is_new is not None:
        query["is_new_today"] = is_new

    jobs_cursor = db.jobs.find(query)
    raw_jobs = await jobs_cursor.to_list(200)

    # Calculate match breakdown for every job
    results = []
    for raw in raw_jobs:
        job_obj = JobModel.from_mongo(raw)
        job_dict = job_obj.model_dump()
        match_info = match_job_eligibility(job_dict, candidate)
        job_dict["match_info"] = match_info
        results.append(job_dict)

    # Sort results
    if sort_by == "recommended":
        results.sort(key=lambda x: (x["match_info"]["match_percentage"], x["total_vacancies"]), reverse=True)
    elif sort_by == "closing_soon":
        results.sort(key=lambda x: x["last_date"])
    elif sort_by == "vacancies":
        results.sort(key=lambda x: x["total_vacancies"], reverse=True)
    elif sort_by == "latest":
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return {
        "count": len(results),
        "jobs": results,
        "candidate_summary": {
            "name": candidate.get("full_name"),
            "category": candidate.get("category"),
            "qualification": candidate.get("qualification"),
            "domicile_state": candidate.get("domicile_state"),
            "age": candidate.get("age", 25)
        }
    }

@api_router.get("/jobs/recommended")
async def get_recommended_jobs(user_id: str = "demo_candidate"):
    cand_doc = await db.candidate_profiles.find_one({"user_id": user_id})
    candidate = CandidateProfile.from_mongo(cand_doc).model_dump() if cand_doc else CandidateProfile().model_dump()

    all_jobs_raw = await db.jobs.find().to_list(200)
    
    high_match = []
    eligible_jobs = []
    need_attention = []

    for raw in all_jobs_raw:
        job_obj = JobModel.from_mongo(raw)
        job_dict = job_obj.model_dump()
        match_info = match_job_eligibility(job_dict, candidate)
        job_dict["match_info"] = match_info
        
        if match_info["is_fully_eligible"] and match_info["match_percentage"] >= 80:
            high_match.append(job_dict)
        elif match_info["is_fully_eligible"]:
            eligible_jobs.append(job_dict)
        else:
            need_attention.append(job_dict)

    high_match.sort(key=lambda x: x["match_info"]["match_percentage"], reverse=True)
    eligible_jobs.sort(key=lambda x: x["match_info"]["match_percentage"], reverse=True)
    need_attention.sort(key=lambda x: x["match_info"]["match_percentage"], reverse=True)

    return {
        "candidate": candidate,
        "high_match_count": len(high_match),
        "high_match_jobs": high_match,
        "eligible_jobs": eligible_jobs,
        "need_attention_jobs": need_attention
    }

@api_router.get("/jobs/{job_id}")
async def get_job_detail(job_id: str, user_id: str = "demo_candidate"):
    # Try finding by string id or mongo ObjectId
    job_doc = await db.jobs.find_one({"_id": job_id})
    if not job_doc:
        job_doc = await db.jobs.find_one({"slug": job_id})
    
    if not job_doc:
        raise HTTPException(status_code=404, detail="Job posting not found")

    job_obj = JobModel.from_mongo(job_doc)
    job_dict = job_obj.model_dump()

    # Candidate Match info
    cand_doc = await db.candidate_profiles.find_one({"user_id": user_id})
    candidate = CandidateProfile.from_mongo(cand_doc).model_dump() if cand_doc else CandidateProfile().model_dump()
    job_dict["match_info"] = match_job_eligibility(job_dict, candidate)

    # Check if tracked
    tracker_item = await db.application_trackers.find_one({"user_id": user_id, "job_id": job_obj.id})
    job_dict["tracker_status"] = tracker_item.get("status") if tracker_item else None
    job_dict["tracker_data"] = ApplicationTrackerItem.from_mongo(tracker_item).model_dump() if tracker_item else None

    return job_dict

# 3. Live Auto-Sync / Crawler Simulation Endpoint
@api_router.post("/jobs/sync-check")
async def trigger_live_job_sync():
    """Simulates real-time checking & ingestion of newly posted Central and State government job notifications."""
    simulated_fresh_jobs = [
        {
            "title": "Central Armed Police Forces (CAPF AC) 2026",
            "slug": f"upsc-capf-ac-2026-{uuid.uuid4().hex[:6]}",
            "board": "Union Public Service Commission",
            "board_code": "UPSC",
            "job_type": "Central",
            "state": "All India",
            "category": "Defense",
            "post_name": "Assistant Commandant (Group A) in BSF, CRPF, CISF, ITBP, SSB",
            "total_vacancies": 506,
            "vacancies_breakdown": {"UR": 210, "OBC": 135, "SC": 75, "ST": 38, "EWS": 48},
            "salary_scale": "Level 10: ₹56,100 - ₹1,77,500 (7th CPC)",
            "in_hand_salary": "₹86,000 / month + High Altitude & Risk Pay",
            "qualification_required": "Graduate",
            "qualification_details": "Bachelor's degree of a University incorporated by an Act of the Central or State Legislature.",
            "preferred_streams": ["Any Graduate", "Science", "Engineering", "Arts", "Commerce"],
            "min_age": 20,
            "max_age": 25,
            "age_relaxation": {"OBC": 3, "SC_ST": 5, "PwD": 0, "Ex_Servicemen": 5, "EWS": 0},
            "domicile_rule": "Open to All Indian Citizens",
            "gender_eligibility": "All (Male & Female)",
            "physical_requirements": {"min_height_male_cm": 165, "min_height_female_cm": 157, "running_male": "100m in 16s & 800m in 3m45s"},
            "application_fee": {"General_OBC_EWS": "₹200", "SC_ST_Female_PwD": "₹0 (Exempted)"},
            "notification_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "start_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "last_date": (datetime.now(timezone.utc) + timedelta(days=21)).strftime("%Y-%m-%d"),
            "exam_date": (datetime.now(timezone.utc) + timedelta(days=90)).strftime("%Y-%m-%d"),
            "admit_card_date": (datetime.now(timezone.utc) + timedelta(days=75)).strftime("%Y-%m-%d"),
            "result_date": "To be announced",
            "official_apply_url": "https://upsconline.nic.in",
            "official_notification_pdf_url": "https://upsc.gov.in/sites/default/files/CAPF_2026_Notice.pdf",
            "official_website_url": "https://upsc.gov.in",
            "syllabus_overview": "Paper 1: General Ability and Intelligence (250 Marks). Paper 2: General Studies, Essay and Comprehension (200 Marks).",
            "exam_pattern": [
                {"stage_num": 1, "name": "Written Examination (Paper 1 & Paper 2)", "type": "Objective & Descriptive", "marks": 450, "duration": "5 Hours", "description": "Paper 1 (250 Marks MCQ) + Paper 2 (200 Marks Descriptive)"},
                {"stage_num": 2, "name": "Physical Standards/PET & Medical Exam", "type": "Physical Test", "marks": 0, "duration": "1 Day", "description": "100m race, 800m race, Long jump & Shot put"},
                {"stage_num": 3, "name": "Personality Test / Interview", "type": "Oral Interview", "marks": 150, "duration": "30 Mins", "description": "Conducted at UPSC Dholpur House, New Delhi"}
            ],
            "selection_steps": ["Written Exam", "PET & Medical Standards", "Personality Test (Interview)", "Merit List"],
            "important_instructions": [
                "Candidates must possess NCC 'B' or 'C' certificate for preference during interview.",
                "Direct entry into Group A Gazetted Assistant Commandant rank."
            ],
            "is_featured": True,
            "is_new_today": True,
            "is_closing_soon": False,
            "status": "Open",
            "tags": ["UPSC", "CAPF", "Assistant Commandant", "BSF", "CRPF", "Defense"]
        }
    ]

    added_count = 0
    for job_data in simulated_fresh_jobs:
        existing = await db.jobs.find_one({"title": job_data["title"]})
        if not existing:
            job_obj = JobModel(**job_data)
            await db.jobs.insert_one(job_obj.to_mongo())
            added_count += 1

    total_jobs = await db.jobs.count_documents({})
    return {
        "status": "success",
        "synced_at": datetime.now(timezone.utc).isoformat(),
        "new_notifications_found": added_count,
        "total_active_jobs": total_jobs,
        "message": f"Sync complete! Found {added_count} new government job notification(s)."
    }

# 4. Application Tracker Endpoints
@api_router.get("/tracker")
async def get_application_pipeline(user_id: str = "demo_candidate"):
    trackers = await db.application_trackers.find({"user_id": user_id}).to_list(100)
    
    saved_items = []
    applied_items = []
    admit_card_items = []
    exam_taken_items = []
    selected_items = []

    for t in trackers:
        item = ApplicationTrackerItem.from_mongo(t).model_dump()
        # Fetch associated job details
        job_doc = await db.jobs.find_one({"_id": item["job_id"]})
        if job_doc:
            item["job_details"] = JobModel.from_mongo(job_doc).model_dump()
        else:
            item["job_details"] = None

        if item["status"] == "saved":
            saved_items.append(item)
        elif item["status"] == "applied":
            applied_items.append(item)
        elif item["status"] == "admit_card_ready":
            admit_card_items.append(item)
        elif item["status"] == "exam_taken":
            exam_taken_items.append(item)
        elif item["status"] == "selected":
            selected_items.append(item)

    return {
        "all_tracked_count": len(trackers),
        "saved": saved_items,
        "applied": applied_items,
        "admit_card": admit_card_items,
        "exam_taken": exam_taken_items,
        "selected": selected_items
    }

@api_router.post("/tracker", response_model=ApplicationTrackerItem)
async def add_or_update_tracker(payload: ApplicationTrackerCreate, user_id: str = "demo_candidate"):
    job_doc = await db.jobs.find_one({"_id": payload.job_id})
    if not job_doc:
        raise HTTPException(status_code=404, detail="Referenced Job not found")

    job_title = job_doc.get("title", "")
    board_code = job_doc.get("board_code", "")
    exam_date = payload.exam_date or job_doc.get("exam_date", "")

    existing = await db.application_trackers.find_one({"user_id": user_id, "job_id": payload.job_id})
    
    if existing:
        update_data = payload.model_dump()
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        update_data["job_title"] = job_title
        update_data["board_code"] = board_code
        update_data["exam_date"] = exam_date
        await db.application_trackers.update_one(
            {"_id": existing["_id"]},
            {"$set": update_data}
        )
        updated_doc = await db.application_trackers.find_one({"_id": existing["_id"]})
        return ApplicationTrackerItem.from_mongo(updated_doc)
    else:
        new_item = ApplicationTrackerItem(
            user_id=user_id,
            job_id=payload.job_id,
            job_title=job_title,
            board_code=board_code,
            status=payload.status,
            application_number=payload.application_number or "",
            roll_number=payload.roll_number or "",
            exam_center=payload.exam_center or "",
            applied_date=payload.applied_date or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            exam_date=exam_date,
            notes=payload.notes or "",
            reminder_enabled=payload.reminder_enabled
        )
        await db.application_trackers.insert_one(new_item.to_mongo())
        return new_item

@api_router.delete("/tracker/{job_id}")
async def remove_from_tracker(job_id: str, user_id: str = "demo_candidate"):
    result = await db.application_trackers.delete_many({"user_id": user_id, "job_id": job_id})
    return {"status": "success", "deleted_count": result.deleted_count}

# 5. Exam Calendar & Deadlines Timeline
@api_router.get("/calendar")
async def get_exam_calendar():
    jobs = await db.jobs.find().to_list(100)
    
    events = []
    for j in jobs:
        job = JobModel.from_mongo(j)
        
        # 1. Application Deadline event
        events.append({
            "id": f"deadline-{job.id}",
            "job_id": job.id,
            "title": f"Deadline: {job.title}",
            "board_code": job.board_code,
            "event_type": "Application Deadline",
            "date": job.last_date,
            "job_type": job.job_type,
            "state": job.state,
            "official_url": job.official_apply_url,
            "status": "Urgent" if job.is_closing_soon else "Open"
        })

        # 2. Admit Card event
        if job.admit_card_date:
            events.append({
                "id": f"admit-{job.id}",
                "job_id": job.id,
                "title": f"Admit Card: {job.title}",
                "board_code": job.board_code,
                "event_type": "Admit Card Release",
                "date": job.admit_card_date,
                "job_type": job.job_type,
                "state": job.state,
                "official_url": job.official_website_url,
                "status": "Upcoming"
            })

        # 3. Exam Date event
        if job.exam_date:
            events.append({
                "id": f"exam-{job.id}",
                "job_id": job.id,
                "title": f"Exam: {job.title}",
                "board_code": job.board_code,
                "event_type": "Exam Date",
                "date": job.exam_date,
                "job_type": job.job_type,
                "state": job.state,
                "official_url": job.official_website_url,
                "status": "Scheduled"
            })

    # Sort events by date string
    events.sort(key=lambda x: x["date"])

    return {
        "count": len(events),
        "events": events
    }

# 6. Daily Habit Check-in & GK Capsule Endpoints
@api_router.get("/daily-capsule")
async def get_daily_capsule(user_id: str = "demo_candidate"):
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    capsule_doc = await db.daily_capsules.find_one({"date_str": today_str})
    
    if not capsule_doc:
        daily_obj = DailyCapsule(**DAILY_CAPSULES_SEED)
        await db.daily_capsules.insert_one(daily_obj.to_mongo())
        capsule_data = daily_obj.model_dump()
    else:
        capsule_data = DailyCapsule.from_mongo(capsule_doc).model_dump()

    # Get candidate check-in status
    cand_doc = await db.candidate_profiles.find_one({"user_id": user_id})
    cand = CandidateProfile.from_mongo(cand_doc) if cand_doc else CandidateProfile()
    
    is_checked_in_today = (cand.last_checkin_date == today_str)

    return {
        "capsule": capsule_data,
        "user_streak": cand.streak_count,
        "user_points": cand.points,
        "is_checked_in_today": is_checked_in_today
    }

@api_router.post("/daily-capsule/checkin")
async def perform_daily_checkin(user_id: str = "demo_candidate"):
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday_str = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    cand_doc = await db.candidate_profiles.find_one({"user_id": user_id})
    cand = CandidateProfile.from_mongo(cand_doc) if cand_doc else CandidateProfile(user_id=user_id)

    if cand.last_checkin_date == today_str:
        return {
            "status": "already_checked_in",
            "message": "You've already claimed today's daily streak reward!",
            "streak_count": cand.streak_count,
            "points": cand.points,
            "points_earned": 0
        }

    # Calculate streak
    if cand.last_checkin_date == yesterday_str:
        new_streak = cand.streak_count + 1
    else:
        new_streak = 1

    points_earned = 20 + (5 * min(new_streak, 10))
    new_points = cand.points + points_earned

    await db.candidate_profiles.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "streak_count": new_streak,
                "last_checkin_date": today_str,
                "points": new_points,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )

    return {
        "status": "success",
        "message": f"Daily Check-in Complete! 🔥 {new_streak} Day Streak!",
        "streak_count": new_streak,
        "points": new_points,
        "points_earned": points_earned
    }

class QuizSubmitRequest(BaseModel):
    answers: Dict[str, int] # question_id -> selected_option_index

@api_router.post("/daily-capsule/quiz-submit")
async def submit_daily_quiz(payload: QuizSubmitRequest, user_id: str = "demo_candidate"):
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    capsule_doc = await db.daily_capsules.find_one({"date_str": today_str})
    if not capsule_doc:
        capsule_doc = DAILY_CAPSULES_SEED

    questions = capsule_doc.get("quiz_questions", [])
    
    score = 0
    total = len(questions)
    results = []

    for q in questions:
        q_id = q.get("id", "")
        correct_idx = q.get("correct_option_index", 0)
        user_idx = payload.answers.get(q_id)
        is_correct = (user_idx is not None and user_idx == correct_idx)
        
        if is_correct:
            score += 1
            
        results.append({
            "id": q_id,
            "question": q.get("question"),
            "user_selected": user_idx,
            "correct_option_index": correct_idx,
            "is_correct": is_correct,
            "explanation": q.get("explanation")
        })

    points_earned = score * 10
    cand_doc = await db.candidate_profiles.find_one({"user_id": user_id})
    if cand_doc:
        await db.candidate_profiles.update_one(
            {"user_id": user_id},
            {"$inc": {"points": points_earned}}
        )

    return {
        "score": score,
        "total": total,
        "points_earned": points_earned,
        "results": results,
        "feedback": "Outstanding performance! High mastery in GK." if score >= 4 else "Good attempt! Keep reviewing daily capsules."
    }

# 7. Categories & Stats Summary
@api_router.get("/categories-summary")
async def get_categories_summary():
    categories = [
        {"name": "Civil Services", "code": "UPSC", "icon": "shield", "count": 1, "vacancies": 1150},
        {"name": "Staff Selection", "code": "SSC", "icon": "briefcase", "count": 3, "vacancies": 56841},
        {"name": "Railways", "code": "RRB", "icon": "train", "count": 1, "vacancies": 11558},
        {"name": "Banking & PSU", "code": "BANK", "icon": "landmark", "count": 2, "vacancies": 6450},
        {"name": "Police & Paramilitary", "code": "POLICE", "icon": "badge-check", "count": 2, "vacancies": 49015},
        {"name": "Defense", "code": "DEFENSE", "icon": "crosshair", "count": 1, "vacancies": 317},
        {"name": "State PSC", "code": "PSC", "icon": "building-2", "count": 3, "vacancies": 3789},
        {"name": "Teaching", "code": "TEACH", "icon": "graduation-cap", "count": 1, "vacancies": 5118},
        {"name": "Engineering & Tech", "code": "TECH", "icon": "cpu", "count": 2, "vacancies": 3200}
    ]
    
    total_vacancies = sum(c["vacancies"] for c in categories)
    total_openings = sum(c["count"] for c in categories)

    return {
        "total_active_vacancies": total_vacancies,
        "total_notifications": total_openings,
        "categories": categories
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
