export interface VacanciesBreakdown {
  UR?: number;
  OBC?: number;
  SC?: number;
  ST?: number;
  EWS?: number;
  PwD?: number;
  Female?: number;
  [key: string]: number | undefined;
}

export interface AgeRelaxation {
  OBC?: number;
  SC_ST?: number;
  PwD?: number;
  Ex_Servicemen?: number;
  EWS?: number;
  [key: string]: number | undefined;
}

export interface ExamStage {
  stage_num: number;
  name: string;
  type: string;
  marks?: number;
  duration?: string;
  description: string;
}

export interface AgeCheck {
  is_eligible: boolean;
  candidate_age: number;
  allowed_range: string;
  base_max: number;
  category_relaxation_years: number;
  category: string;
}

export interface QualificationCheck {
  is_eligible: boolean;
  candidate_qualification: string;
  required_qualification: string;
  details: string;
}

export interface DomicileCheck {
  is_eligible: boolean;
  candidate_domicile: string;
  job_location: string;
  job_type: string;
}

export interface GenderCheck {
  is_eligible: boolean;
  requirement: string;
}

export interface MatchInfo {
  match_percentage: number;
  is_fully_eligible: boolean;
  age_check: AgeCheck;
  qualification_check: QualificationCheck;
  domicile_check: DomicileCheck;
  gender_check: GenderCheck;
  reasons: string[];
}

export interface Job {
  id: string;
  title: string;
  slug: string;
  board: string;
  board_code: string;
  job_type: "Central" | "State" | string;
  state: string;
  category: string;
  post_name: string;
  total_vacancies: number;
  vacancies_breakdown?: VacanciesBreakdown;
  salary_scale: string;
  in_hand_salary: string;
  qualification_required: string;
  qualification_details: string;
  preferred_streams?: string[];
  min_age: number;
  max_age: number;
  age_relaxation?: AgeRelaxation;
  domicile_rule: string;
  gender_eligibility: string;
  physical_requirements?: Record<string, any>;
  application_fee?: Record<string, string>;
  notification_date: string;
  start_date: string;
  last_date: string;
  exam_date: string;
  admit_card_date: string;
  result_date?: string;
  official_apply_url: string;
  official_notification_pdf_url: string;
  official_website_url: string;
  syllabus_overview: string;
  exam_pattern?: ExamStage[];
  selection_steps?: string[];
  important_instructions?: string[];
  is_featured: boolean;
  is_new_today: boolean;
  is_closing_soon: boolean;
  status: "Open" | "Closing Soon" | "Admit Card Out" | "Exam Scheduled" | "Result Declared" | string;
  tags?: string[];
  created_at: string;
  match_info?: MatchInfo;
  tracker_status?: string | null;
  tracker_data?: ApplicationTrackerItem | null;
}

export interface CandidateProfile {
  id?: string;
  user_id: string;
  full_name: string;
  email: string;
  phone: string;
  dob: string;
  age: number;
  category: "General" | "OBC-NCL" | "SC" | "ST" | "EWS" | "PwD" | "Ex-Servicemen" | string;
  gender: "Male" | "Female" | "Other" | string;
  domicile_state: string;
  qualification: string;
  degree_name: string;
  stream: string;
  percentage_or_cgpa?: string;
  additional_certs: string[];
  height_cm: number;
  preferred_categories: string[];
  preferred_states: string[];
  streak_count: number;
  last_checkin_date: string;
  points: number;
  created_at?: string;
  updated_at?: string;
}

export interface ApplicationTrackerItem {
  id?: string;
  user_id: string;
  job_id: string;
  job_title: string;
  board_code: string;
  status: "saved" | "applied" | "admit_card_ready" | "exam_taken" | "selected" | "rejected";
  application_number?: string;
  roll_number?: string;
  exam_center?: string;
  applied_date?: string;
  exam_date?: string;
  notes?: string;
  reminder_enabled?: boolean;
  created_at?: string;
  updated_at?: string;
  job_details?: Job;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correct_option_index: number;
  explanation: string;
  subject: string;
}

export interface CurrentAffairsItem {
  title: string;
  category: string;
  date: string;
  summary: string;
  exam_relevance: string;
}

export interface DailyCapsule {
  id?: string;
  date_str: string;
  theme: string;
  daily_quote: string;
  current_affairs: CurrentAffairsItem[];
  quiz_questions: QuizQuestion[];
}

export interface CalendarEvent {
  id: string;
  job_id: string;
  title: string;
  board_code: string;
  event_type: "Application Deadline" | "Admit Card Release" | "Exam Date" | string;
  date: string;
  job_type: string;
  state: string;
  official_url: string;
  status: string;
}

export interface CategorySummaryItem {
  name: string;
  code: string;
  icon: string;
  count: number;
  vacancies: number;
}
