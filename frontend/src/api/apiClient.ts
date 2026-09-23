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
    const statusMatch = String(error?.message || "").match(/^API error (\\d+):/);
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

export const api = {
  // Jobs
  async getJobs(params?: {
    search?: string;
    category?: string;
    job_type?: string;
    state?: string;
    qualification?: string;
    status?: string;
    is_featured?: boolean;
    is_new?: boolean;
    sort_by?: string;
    user_id?: string;
  }): Promise<{ count: number; jobs: Job[]; candidate_summary: any }> {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.append("search", params.search);
    if (params?.category) searchParams.append("category", params.category);
    if (params?.job_type) searchParams.append("job_type", params.job_type);
    if (params?.state) searchParams.append("state", params.state);
    if (params?.qualification) searchParams.append("qualification", params.qualification);
    if (params?.status) searchParams.append("status", params.status);
    if (params?.is_featured !== undefined) searchParams.append("is_featured", String(params.is_featured));
    if (params?.is_new !== undefined) searchParams.append("is_new", String(params.is_new));
    if (params?.sort_by) searchParams.append("sort_by", params.sort_by);
    searchParams.append("user_id", params?.user_id || DEFAULT_USER_ID);

    const queryStr = searchParams.toString();
    const response = await request<{
      items: any[];
      total: number;
      page: number;
      limit: number;
    }>(`/jobs${queryStr ? `?${queryStr}` : ""}`);

    const jobs: Job[] = response.items.map((item) => ({
      id: String(item.id),
      title: item.title,
      slug: String(item.id),
      board: item.organization_name,
      board_code: item.source_name || item.organization_name,
      job_type: item.source_name === "KARNATAKA_TEACHER" ? "State" : "Central",
      state: item.source_name === "KARNATAKA_TEACHER" ? "Karnataka" : "All India",
      category: item.opportunity_type || "Government Jobs",
      post_name: item.title,
      total_vacancies: 0,
      salary_scale: "See official notification",
      in_hand_salary: "See official notification",
      qualification_required: item.eligibility?.degree || item.eligibility?.education_level || "See official notification",
      qualification_details: item.eligibility?.qualification_text || "See official notification",
      min_age: item.eligibility?.minimum_age || 0,
      max_age: item.eligibility?.maximum_age || 0,
      domicile_rule: item.eligibility?.eligible_states || "See official notification",
      gender_eligibility: "See official notification",
      notification_date: item.application_start || item.created_at,
      start_date: item.application_start || "",
      last_date: item.application_end || "Not specified",
      exam_date: "",
      admit_card_date: "",
      official_apply_url: item.official_url,
      official_notification_pdf_url: item.notification_url || item.official_url,
      official_website_url: item.official_url,
      syllabus_overview: "See official notification",
      is_featured: false,
      is_new_today: false,
      is_closing_soon: Boolean(item.is_closing_soon),
      status: item.lifecycle_status || item.status,
      tags: [item.source_name || "Government"],
      created_at: item.created_at,
    }));

    return {
      count: response.total,
      jobs,
      candidate_summary: null,
    };
  },

  async getRecommendedJobs(user_id: string = DEFAULT_USER_ID): Promise<{
    candidate: CandidateProfile;
    high_match_count: number;
    high_match_jobs: Job[];
    eligible_jobs: Job[];
    need_attention_jobs: Job[];
  }> {
    return request(`/jobs/recommended?user_id=${user_id}`);
  },

  async getJobDetail(jobId: string, user_id: string = DEFAULT_USER_ID): Promise<Job> {
    return request<Job>(`/jobs/${jobId}?user_id=${user_id}`);
  },

  async triggerJobSync(): Promise<{
    status: string;
    synced_at: string;
    new_notifications_found: number;
    total_active_jobs: number;
    message: string;
  }> {
    return request("/jobs/sync-check", {
      method: "POST",
    });
  },

  // Candidate Profile
  async getProfile(user_id: string = DEFAULT_USER_ID): Promise<CandidateProfile> {
    return request<CandidateProfile>(`/profile?user_id=${user_id}`);
  },

  async updateProfile(
    profile: Partial<CandidateProfile>,
    user_id: string = DEFAULT_USER_ID
  ): Promise<CandidateProfile> {
    return request<CandidateProfile>(`/profile?user_id=${user_id}`, {
      method: "POST",
      body: JSON.stringify(profile),
    });
  },

  // Application Pipeline / Tracker
  async getTracker(user_id: string = DEFAULT_USER_ID): Promise<{
    all_tracked_count: number;
    saved: ApplicationTrackerItem[];
    applied: ApplicationTrackerItem[];
    admit_card: ApplicationTrackerItem[];
    exam_taken: ApplicationTrackerItem[];
    selected: ApplicationTrackerItem[];
  }> {
    try {
      return await request(
        `/tracker?user_id=${user_id}`,
        undefined,
        { suppressStatuses: [404] }
      );
    } catch (error: any) {
      if (String(error?.message || "").includes("API error 404")) {
        return {
          all_tracked_count: 0,
          saved: [],
          applied: [],
          admit_card: [],
          exam_taken: [],
          selected: [],
        };
      }
      throw error;
    }
  },

  async updateTrackerItem(
    item: {
      job_id: string;
      status: string;
      application_number?: string;
      roll_number?: string;
      exam_center?: string;
      applied_date?: string;
      exam_date?: string;
      notes?: string;
      reminder_enabled?: boolean;
    },
    user_id: string = DEFAULT_USER_ID
  ): Promise<ApplicationTrackerItem> {
    return request<ApplicationTrackerItem>(`/tracker?user_id=${user_id}`, {
      method: "POST",
      body: JSON.stringify(item),
    });
  },

  async removeFromTracker(job_id: string, user_id: string = DEFAULT_USER_ID): Promise<{ status: string }> {
    return request(`/tracker/${job_id}?user_id=${user_id}`, {
      method: "DELETE",
    });
  },

  // Exam Calendar
  async getCalendar(): Promise<{ count: number; events: CalendarEvent[] }> {
    return request<{ count: number; events: CalendarEvent[] }>("/calendar");
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
