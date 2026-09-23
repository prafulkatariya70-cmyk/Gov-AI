import {
  Job,
  CandidateProfile,
  ApplicationTrackerItem,
  DailyCapsule,
  CalendarEvent,
  CategorySummaryItem,
} from "@/src/types";

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_BACKEND_URL || "";
const API_BASE = `${BACKEND_URL}/api`;

const DEFAULT_USER_ID = "demo_candidate";

async function request<T>(
  endpoint: string,
  options?: RequestInit,
  config?: { suppressStatuses?: number[] }
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(options?.headers || {}),
      },
    });

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`API error ${response.status}: ${errorBody}`);
    }

    return await response.json();
  } catch (error: any) {
    const statusMatch = String(error?.message || "").match(/^API error (\d+):/);
    const statusCode = statusMatch ? Number(statusMatch[1]) : undefined;
    const shouldSuppress =
      statusCode !== undefined &&
      (config?.suppressStatuses || []).includes(statusCode);

    if (!shouldSuppress) {
      console.error(`[API Error] ${endpoint}:`, error);
    }
    throw error;
  }
}

type ModernJob = {
  id: number; title: string; organization_name: string; description?: string | null;
  official_url: string; notification_url?: string | null; application_start?: string | null;
  application_end?: string | null; status: string; opportunity_type: string;
  source_name?: string | null; created_at: string; lifecycle_status?: string;
  is_open?: boolean; is_upcoming?: boolean; is_closing_soon?: boolean;
  days_until_deadline?: number | null;
  eligibility?: { minimum_age?: number | null; maximum_age?: number | null;
    education_level?: string | null; degree?: string | null; branch?: string | null;
    qualification_text?: string | null; eligible_states?: string | null; eligible_categories?: string | null; } | null;
};

function calculateAge(dateOfBirth: string): number {
  const birth = new Date(dateOfBirth);
  if (Number.isNaN(birth.getTime())) return 0;
  const now = new Date();
  let age = now.getFullYear() - birth.getFullYear();
  const month = now.getMonth() - birth.getMonth();
  if (month < 0 || (month === 0 && now.getDate() < birth.getDate())) age -= 1;
  return Math.max(age, 0);
}

function mapJob(item: ModernJob, matchInfo?: any): Job {
  const isState = item.source_name === "KARNATAKA_TEACHER" || Boolean(item.source_name?.startsWith("STATE_"));
  const qualification = item.eligibility?.degree || item.eligibility?.education_level || "See official notification";
  return {
    id: String(item.id), title: item.title, slug: String(item.id), board: item.organization_name,
    board_code: item.source_name || item.organization_name, job_type: isState ? "State" : "Central",
    state: isState ? "Karnataka" : "All India", category: item.opportunity_type || "Government Jobs",
    post_name: item.title, total_vacancies: 0, salary_scale: "See official notification",
    in_hand_salary: "See official notification", qualification_required: qualification,
    qualification_details: item.eligibility?.qualification_text || "See official notification",
    min_age: item.eligibility?.minimum_age || 0, max_age: item.eligibility?.maximum_age || 0,
    domicile_rule: item.eligibility?.eligible_states || "See official notification",
    gender_eligibility: "See official notification", notification_date: item.application_start || item.created_at,
    start_date: item.application_start || "", last_date: item.application_end || "Not specified",
    exam_date: "", admit_card_date: "", official_apply_url: item.official_url,
    official_notification_pdf_url: item.notification_url || item.official_url,
    official_website_url: item.official_url, syllabus_overview: "See official notification",
    is_featured: false, is_new_today: false, is_closing_soon: Boolean(item.is_closing_soon),
    status: item.lifecycle_status || item.status, tags: [item.source_name || "Government"],
    created_at: item.created_at, match_info: matchInfo,
  };
}

function mapProfile(item: any): CandidateProfile {
  return {
    id: item.user_id ? String(item.user_id) : undefined, user_id: String(item.user_id || DEFAULT_USER_ID),
    full_name: item.full_name || "", email: item.email || "", phone: item.phone || "",
    dob: item.date_of_birth || "", age: item.date_of_birth ? calculateAge(item.date_of_birth) : 0,
    category: item.category || "General", gender: item.gender || "", domicile_state: item.state || "",
    qualification: item.education_level || item.degree || "", degree_name: item.degree || "",
    stream: item.branch || "", percentage_or_cgpa: item.percentage_or_cgpa || "",
    additional_certs: item.additional_certs || [], height_cm: Number(item.height_cm || 0),
    preferred_categories: item.preferred_categories || [], preferred_states: item.preferred_states || [],
    streak_count: Number(item.streak_count || 0), last_checkin_date: item.last_checkin_date || "",
    points: Number(item.points || 0), created_at: item.created_at, updated_at: item.updated_at,
  };
}

function mapApplication(item: any): ApplicationTrackerItem {
  const job = item.job;
  return {
    id: String(item.id), user_id: String(item.user_id || DEFAULT_USER_ID), job_id: String(item.job_id),
    job_title: job?.title || "Government Job", board_code: job?.source_name || job?.organization_name || "Government",
    status: item.status, application_number: item.application_number || undefined,
    roll_number: item.roll_number || undefined, exam_center: item.exam_center || undefined,
    applied_date: item.applied_at || undefined, notes: item.notes || undefined, reminder_enabled: false,
    created_at: item.created_at, updated_at: item.updated_at, job_details: job ? mapJob(job) : undefined,
  };
}
export const api = {
  // Jobs
  async getJobs(params?: {
    search?: string; category?: string; job_type?: string; state?: string;
    qualification?: string; status?: string; is_featured?: boolean; is_new?: boolean;
    sort_by?: string; user_id?: string;
  }): Promise<{ count: number; jobs: Job[]; candidate_summary: any }> {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.append("search", params.search);
    searchParams.append("limit", "100");
    const response = await request<{ items: ModernJob[]; total: number; page: number; limit: number }>(
      "/jobs?" + searchParams.toString()
    );
    let jobs = response.items.map((item) => mapJob(item));

    const categoryTerms: Record<string, string[]> = {
      "Civil Services": ["upsc", "civil", "gazetted probationer"],
      "Staff Selection": ["ssc", "staff selection"],
      "Railways": ["rrb", "railway"],
      "Banking & PSU": ["bank", "psu"],
      "Police & Paramilitary": ["police", "paramilitary", "constable"],
      "Defense": ["defence", "defense", "army", "navy", "air force"],
      "State PSC": ["kpsc", "psc", "public service commission"],
      "Teaching": ["teacher", "teaching", "gpt", "tet"],
      "Engineering & Tech": ["engineer", "engineering", "technical"],
    };

    const matchesTerms = (job: Job, terms: string[]) =>
      terms.some((term) =>
        [job.title, job.board, job.board_code, job.category, job.post_name]
          .join(" ").toLowerCase().includes(term)
      );

    if (params?.search) {
      const term = params.search.toLowerCase();
      jobs = jobs.filter((job) =>
        [job.title, job.board, job.board_code].join(" ").toLowerCase().includes(term)
      );
    }
    if (params?.category && categoryTerms[params.category]) {
      jobs = jobs.filter((job) => matchesTerms(job, categoryTerms[params.category]));
    }
    if (params?.job_type && params.job_type !== "All Types") {
      jobs = jobs.filter((job) => job.job_type === params.job_type);
    }
    if (params?.state && params.state !== "All India") {
      jobs = jobs.filter((job) => job.state === params.state);
    }
    if (params?.qualification && params.qualification !== "All Qualifications") {
      const term = params.qualification.toLowerCase().replace("b.tech/b.e.", "b.tech");
      jobs = jobs.filter((job) =>
        [job.qualification_required, job.qualification_details].join(" ").toLowerCase().includes(term)
      );
    }
    if (params?.status === "Closing Soon" || params?.sort_by === "closing_soon") {
      jobs = jobs.filter((job) => job.is_closing_soon);
    }
    jobs.sort((a, b) => String(a.last_date).localeCompare(String(b.last_date)));
    if (params?.sort_by === "latest") {
      jobs.sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
    }
    return { count: jobs.length, jobs, candidate_summary: null };
  },

  async getRecommendedJobs(user_id: string = DEFAULT_USER_ID): Promise<{
    candidate: CandidateProfile; high_match_count: number; high_match_jobs: Job[];
    eligible_jobs: Job[]; need_attention_jobs: Job[];
  }> {
    const [response, profileResponse] = await Promise.all([
      request<any[]>("/jobs/recommended?user_id=" + encodeURIComponent(user_id)),
      request<any>("/profile?user_id=" + encodeURIComponent(user_id)),
    ]);
    const mapped = (Array.isArray(response) ? response : []).map((item) =>
      mapJob(item, {
        match_percentage: Number(item.match_score ?? 0),
        is_fully_eligible: item.eligibility_status === "ELIGIBLE",
        age_check: { is_eligible: item.eligibility_status === "ELIGIBLE", candidate_age: calculateAge(profileResponse.date_of_birth || ""), allowed_range: "See official notification", base_max: item.eligibility?.maximum_age || 0, category_relaxation_years: 0, category: profileResponse.category || "General" },
        qualification_check: { is_eligible: item.eligibility_status === "ELIGIBLE", candidate_qualification: profileResponse.education_level || profileResponse.degree || "", required_qualification: item.eligibility?.degree || item.eligibility?.education_level || "See official notification", details: item.eligibility_reasons?.join(" ") || "See eligibility details" },
        domicile_check: { is_eligible: item.eligibility_status === "ELIGIBLE", candidate_domicile: profileResponse.state || "", job_location: item.eligibility?.eligible_states || "See official notification", job_type: item.source_name || "" },
        gender_check: { is_eligible: true, requirement: "See official notification" },
        reasons: item.eligibility_reasons || [],
      })
    );
    const highMatchJobs = mapped.filter((job) => (job.match_info?.match_percentage || 0) >= 80);
    const eligibleJobs = mapped.filter((job) => job.match_info?.is_fully_eligible);
    const needAttentionJobs = mapped.filter((job) => !job.match_info?.is_fully_eligible && (job.match_info?.match_percentage || 0) > 0);
    return { candidate: mapProfile(profileResponse), high_match_count: highMatchJobs.length, high_match_jobs: highMatchJobs, eligible_jobs: eligibleJobs, need_attention_jobs: needAttentionJobs };
  },

  async getJobDetail(jobId: string, user_id: string = DEFAULT_USER_ID): Promise<Job> {
    const item = await request<ModernJob>("/jobs/" + encodeURIComponent(jobId) + "?user_id=" + encodeURIComponent(user_id));
    return mapJob(item);
  },

  async triggerJobSync(): Promise<{
    status: string; synced_at: string; new_notifications_found: number;
    total_active_jobs: number; message: string;
  }> {
    const status = await request<any>("/ingestion/status");
    return {
      status: "success",
      synced_at: status.latest_run_at || new Date().toISOString(),
      new_notifications_found: 0,
      total_active_jobs: Number(status.jobs_count || 0),
      message: "Feed refreshed. Official-source ingestion runs automatically in the background.",
    };
  },

  // Candidate Profile
  async getProfile(user_id: string = DEFAULT_USER_ID): Promise<CandidateProfile> {
    const response = await request<any>("/profile?user_id=" + encodeURIComponent(user_id));
    return mapProfile(response);
  },

  async updateProfile(
    profile: Partial<CandidateProfile>, user_id: string = DEFAULT_USER_ID
  ): Promise<CandidateProfile> {
    const payload = {
      full_name: profile.full_name,
      date_of_birth: profile.dob || undefined,
      state: profile.domicile_state || undefined,
      education_level: profile.qualification || undefined,
      degree: profile.degree_name || profile.qualification || undefined,
      branch: profile.stream || undefined,
      category: profile.category || undefined,
    };
    const response = await request<any>("/profile?user_id=" + encodeURIComponent(user_id), {
      method: "PUT", body: JSON.stringify(payload),
    });
    return mapProfile(response);
  },

  // Application Pipeline / Tracker
  async getTracker(user_id: string = DEFAULT_USER_ID): Promise<{
    all_tracked_count: number; saved: ApplicationTrackerItem[]; applied: ApplicationTrackerItem[];
    admit_card: ApplicationTrackerItem[]; exam_taken: ApplicationTrackerItem[]; selected: ApplicationTrackerItem[];
  }> {
    const records = await request<any[]>("/applications?user_id=" + encodeURIComponent(user_id));
    const items = records.map(mapApplication);
    return {
      all_tracked_count: items.length,
      saved: items.filter((item) => item.status === "saved"),
      applied: items.filter((item) => item.status === "applied"),
      admit_card: items.filter((item) => item.status === "admit_card_ready"),
      exam_taken: items.filter((item) => item.status === "exam_taken"),
      selected: items.filter((item) => item.status === "selected"),
    };
  },

  async updateTrackerItem(
    item: { job_id: string; status: string; application_number?: string; roll_number?: string;
      exam_center?: string; applied_date?: string; exam_date?: string; notes?: string; reminder_enabled?: boolean; },
    user_id: string = DEFAULT_USER_ID
  ): Promise<ApplicationTrackerItem> {
    const records = await request<any[]>("/applications?user_id=" + encodeURIComponent(user_id));
    const existing = records.find((record) => String(record.job_id) === String(item.job_id));
    const payload = {
      status: item.status, application_number: item.application_number, roll_number: item.roll_number,
      exam_center: item.exam_center, applied_at: item.applied_date, notes: item.notes,
    };
    if (existing) {
      const response = await request<any>("/applications/" + existing.id, { method: "PATCH", body: JSON.stringify(payload) });
      return mapApplication(response);
    }
    const response = await request<any>("/applications", {
      method: "POST",
      body: JSON.stringify({ job_id: Number(item.job_id), ...payload }),
    });
    return mapApplication(response);
  },

  async removeFromTracker(job_id: string, user_id: string = DEFAULT_USER_ID): Promise<{ status: string }> {
    const records = await request<any[]>("/applications?user_id=" + encodeURIComponent(user_id));
    const existing = records.find((record) => String(record.job_id) === String(job_id));
    if (!existing) return { status: "not_found" };
    await request<any>("/applications/" + existing.id + "?user_id=" + encodeURIComponent(user_id), { method: "DELETE" });
    return { status: "deleted" };
  },

  // Exam Calendar
  async getCalendar(): Promise<{ count: number; events: CalendarEvent[] }> {
    const response = await request<any>("/jobs?limit=100");
    const events: CalendarEvent[] = response.items
      .filter((job: ModernJob) => Boolean(job.application_end))
      .map((job: ModernJob) => ({
        id: "deadline-" + job.id, job_id: String(job.id), title: job.title,
        board_code: job.source_name || job.organization_name, event_type: "Application Deadline",
        date: String(job.application_end),
        job_type: job.source_name === "KARNATAKA_TEACHER" ? "State" : "Central",
        state: job.source_name === "KARNATAKA_TEACHER" ? "Karnataka" : "All India",
        official_url: job.official_url, status: job.status,
      }));
    return { count: events.length, events };
  },

  // Daily Capsule & Streak
  async getDailyCapsule(user_id: string = DEFAULT_USER_ID): Promise<{
    capsule: DailyCapsule;
    user_streak: number;
    user_points: number;
    is_checked_in_today: boolean;
  }> {
    try {
      return await request(
        `/daily-capsule?user_id=${user_id}`,
        undefined,
        { suppressStatuses: [404] }
      );
    } catch (error: any) {
      if (String(error?.message || "").includes("API error 404")) {
        return {
          capsule: {
            date_str: new Date().toISOString().slice(0, 10),
            theme: "Coming soon",
            daily_quote: "Daily GK and current-affairs content is being connected.",
            current_affairs: [],
            quiz_questions: [],
          },
          user_streak: 0,
          user_points: 0,
          is_checked_in_today: false,
        };
      }
      throw error;
    }
  },

  async checkinDaily(user_id: string = DEFAULT_USER_ID): Promise<{
    status: string;
    message: string;
    streak_count: number;
    points: number;
    points_earned: number;
  }> {
    return request(`/daily-capsule/checkin?user_id=${user_id}`, {
      method: "POST",
    });
  },

  async submitQuiz(
    answers: Record<string, number>,
    user_id: string = DEFAULT_USER_ID
  ): Promise<{
    score: number;
    total: number;
    points_earned: number;
    results: Array<{
      id: string;
      question: string;
      user_selected?: number;
      correct_option_index: number;
      is_correct: boolean;
      explanation: string;
    }>;
    feedback: string;
  }> {
    return request(`/daily-capsule/quiz-submit?user_id=${user_id}`, {
      method: "POST",
      body: JSON.stringify({ answers }),
    });
  },

  // Categories & Stats
  async getCategoriesSummary(): Promise<{
    total_active_vacancies: number;
    total_notifications: number;
    categories: CategorySummaryItem[];
  }> {
    return request<{
      total_active_vacancies: number;
      total_notifications: number;
      categories: CategorySummaryItem[];
    }>("/categories-summary");
  },
};
