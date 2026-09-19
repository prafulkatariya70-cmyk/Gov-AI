import { Job, CandidateProfile } from "@/src/types";
import { storage } from "@/src/utils/storage";

const BACKEND_URL = (
  process.env.EXPO_PUBLIC_BACKEND_URL ||
  process.env.EXPO_BACKEND_URL ||
  ""
).replace(/\/$/, "");
const API_BASE = `${BACKEND_URL}/api/v1`;

const ACCESS_TOKEN_KEY = "govcareerai.access_token";

export interface AuthUser {
  id: string;
  email: string;
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  user: AuthUser;
}

export interface EligibilityDecision {
  status: string;
  reasons: string[];
  failed_requirements: string[];
  unknown_requirements: string[];
  passed_requirements: string[];
  evidence: Array<Record<string, unknown>>;
  score: number | null;
  confidence: string | null;
}

async function getAccessToken(): Promise<string | null> {
  return storage.secureGet<string | null>(ACCESS_TOKEN_KEY, null);
}

export async function clearAccessToken(): Promise<void> {
  await storage.secureRemove(ACCESS_TOKEN_KEY);
}

async function request<T>(
  endpoint: string,
  options: RequestInit = {},
  authenticated = true,
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const token = authenticated ? await getAccessToken() : null;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {}),
      },
    });

    if (response.status === 401 && authenticated) {
      await clearAccessToken();
    }

    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(`API error ${response.status}: ${errorBody}`);
    }

    return (await response.json()) as T;
  } catch (error) {
    console.error(`[API Error] ${endpoint}:`, error);
    throw error;
  }
}

function mapJob(job: any): Job {
  const salary = job.salary_scale || "Salary details unavailable";
  return {
    ...job,
    salary_scale: salary,
    in_hand_salary: salary,
    qualification_required: job.qualification_required || "Not specified",
    qualification_details: job.qualification_details || "",
    min_age: job.min_age ?? 0,
    max_age: job.max_age ?? 0,
    exam_date: job.exam_date || "",
    admit_card_date: job.admit_card_date || "",
    syllabus_overview: job.syllabus_overview || "",
    is_featured: Boolean(job.is_featured),
    is_new_today: Boolean(job.is_new_today),
    is_closing_soon: Boolean(job.is_closing_soon),
  };
}

export const api = {
  async register(email: string, password: string): Promise<AuthResponse> {
    const response = await request<AuthResponse>(
      "/auth/register",
      {
        method: "POST",
        body: JSON.stringify({ email, password }),
      },
      false,
    );
    await storage.secureSet(ACCESS_TOKEN_KEY, response.access_token);
    return response;
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await request<AuthResponse>(
      "/auth/login",
      {
        method: "POST",
        body: JSON.stringify({ email, password }),
      },
      false,
    );
    await storage.secureSet(ACCESS_TOKEN_KEY, response.access_token);
    return response;
  },

  async getCurrentUser(): Promise<AuthUser> {
    return request<AuthUser>("/auth/me");
  },

  async logout(): Promise<void> {
    await clearAccessToken();
  },

  async hasAccessToken(): Promise<boolean> {
    return Boolean(await getAccessToken());
  },

  async getJobs(params?: {
    search?: string;
    category?: string;
    job_type?: string;
    state?: string;
    qualification?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ count: number; page: number; page_size: number; jobs: Job[]; candidate_summary: any }> {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.append("search", params.search);
    if (params?.category) searchParams.append("category", params.category);
    if (params?.job_type) searchParams.append("job_type", params.job_type);
    if (params?.state) searchParams.append("state", params.state);
    if (params?.qualification) searchParams.append("qualification", params.qualification);
    if (params?.status) searchParams.append("status", params.status);
    if (params?.page) searchParams.append("page", String(params.page));
    if (params?.page_size) searchParams.append("page_size", String(params.page_size));\n    // Legacy UI filters are accepted by the client contract; the production API\n    // currently ignores unsupported recommendation flags.\n    void params?.sort_by;\n    void params?.is_featured;\n    void params?.is_new;

    const query = searchParams.toString();
    const response = await request<{
      count: number;
      page: number;
      page_size: number;
      jobs: any[];
    }>(`/jobs${query ? `?${query}` : ""}`);

    return {
      ...response,
      jobs: response.jobs.map(mapJob),
    };
  },

  async getJobDetail(identifier: string): Promise<Job> {
    const job = await request<any>(`/jobs/${encodeURIComponent(identifier)}`);
    return mapJob(job);
  },

  async getJobEligibility(identifier: string) {
    return request<{
      id: string;
      job_id: string;
      normalized_rules: Record<string, unknown> | null;
      qualification_text: string | null;
      experience_requirement: string | null;
      service_requirement: string | null;
      department_requirement: string | null;
      special_requirements: string | null;
    }>(`/jobs/${encodeURIComponent(identifier)}/eligibility`);
  },

  async getMyJobEligibility(identifier: string): Promise<EligibilityDecision> {
    return request<EligibilityDecision>(
      `/jobs/${encodeURIComponent(identifier)}/eligibility/me`,
    );
  },

  async triggerJobSync(): Promise<{ message: string; sources_checked: number; notifications_queued: number; notifications_processed: number }> {\n    return request("/sync", { method: "POST" });\n  },\n\n  async getTracker(): Promise<{ saved: any[]; applied: any[] }> {\n    return request<{ saved: any[]; applied: any[] }>("/tracker");\n  },\n\n  async updateTrackerItem(payload: { job_id: string; status: string; application_number?: string; roll_number?: string; exam_center?: string; applied_date?: string; exam_date?: string; notes?: string; reminder_enabled?: boolean }) {\n    return request<any>("/tracker", { method: "PUT", body: JSON.stringify(payload) });\n  },\n\n  async removeFromTracker(jobId: string): Promise<void> {\n    await request<void>("/tracker/" + encodeURIComponent(jobId), { method: "DELETE" });\n  },\n\n  async getProfile(): Promise<CandidateProfile> {
    const profile = await request<any>("/profile");
    return {
      ...profile,
      additional_certs: typeof profile.additional_certs === "string"\n        ? profile.additional_certs.split(",").map((value: string) => value.trim()).filter(Boolean)\n        : profile.additional_certs || [],
      preferred_categories: profile.preferred_categories
        ? profile.preferred_categories.split(",").map((value: string) => value.trim()).filter(Boolean)
        : [],
      preferred_states: profile.preferred_states
        ? profile.preferred_states.split(",").map((value: string) => value.trim()).filter(Boolean)
        : [],
    };
  },

  async updateProfile(profile: Partial<CandidateProfile>): Promise<CandidateProfile> {
    const payload = {
      full_name: profile.full_name || "",
      phone: profile.phone || null,
      dob: profile.dob || null,
      category: profile.category || null,
      gender: profile.gender || null,
      domicile_state: profile.domicile_state || null,
      qualification: profile.qualification || null,
      degree_name: profile.degree_name || null,
      stream: profile.stream || null,
      percentage_or_cgpa: profile.percentage_or_cgpa || null,
      additional_certs: Array.isArray(profile.additional_certs)\n        ? profile.additional_certs.join(", ")\n        : profile.additional_certs || null,
      height_cm: profile.height_cm ?? null,
      preferred_categories: Array.isArray(profile.preferred_categories)
        ? profile.preferred_categories.join(", ")
        : profile.preferred_categories || null,
      preferred_states: Array.isArray(profile.preferred_states)
        ? profile.preferred_states.join(", ")
        : profile.preferred_states || null,
    };

    const updated = await request<any>("/profile", {
      method: "PUT",
      body: JSON.stringify(payload),
    });

    return {
      ...updated,
      additional_certs: typeof updated.additional_certs === "string"\n        ? updated.additional_certs.split(",").map((value: string) => value.trim()).filter(Boolean)\n        : updated.additional_certs || [],
      preferred_categories: updated.preferred_categories
        ? updated.preferred_categories.split(",").map((value: string) => value.trim()).filter(Boolean)
        : [],
      preferred_states: updated.preferred_states
        ? updated.preferred_states.split(",").map((value: string) => value.trim()).filter(Boolean)
        : [],
    };
  },
};
