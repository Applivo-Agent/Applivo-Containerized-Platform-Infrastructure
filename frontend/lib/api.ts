import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: `${API_BASE}/api`,
  headers: { "Content-Type": "application/json" },
  timeout: 30000,
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("applivo_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("applivo_token");
        localStorage.removeItem("applivo_user");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// ─── Auth ─────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login", data),
  me: () => api.get("/auth/me"),
  status: () => api.get("/auth/status"),
};

// ─── Profile ──────────────────────────────────────────────────────────────
export const profileApi = {
  get: () => api.get("/profile"),
  update: (data: Record<string, unknown>) => api.patch("/profile", data),
  addSkill: (data: Record<string, unknown>) => api.post("/profile/skills", data),
  deleteSkill: (id: string) => api.delete(`/profile/skills/${id}`),
};

// ─── Onboarding ───────────────────────────────────────────────────────────
export const onboardingApi = {
  status: () => api.get("/onboarding/status"),
  complete: (step: string, data: Record<string, unknown>) =>
    api.post(`/onboarding/${step}`, data),
};

// ─── Jobs ─────────────────────────────────────────────────────────────────
export const jobsApi = {
  list: (params?: Record<string, unknown>) => api.get("/jobs", { params }),
  get: (id: string) => api.get(`/jobs/${id}`),
  analyze: (id: string) => api.post(`/jobs/${id}/analyze`),
  skip: (id: string) => api.post(`/jobs/${id}/skip`),
  scrape: () => api.get("/jobs/scrape"),
};

// ─── Applications ─────────────────────────────────────────────────────────
export const applicationsApi = {
  list: (params?: Record<string, unknown>) => api.get("/applications", { params }),
  create: (data: Record<string, unknown>) => api.post("/applications", data),
  get: (id: string) => api.get(`/applications/${id}`),
  updateStatus: (id: string, data: Record<string, unknown>) =>
    api.patch(`/applications/${id}/status`, data),
  approve: (id: string) => api.post(`/applications/${id}/approve`),
  star: (id: string) => api.patch(`/applications/${id}/star`),
  stats: () => api.get("/applications/stats"),
  queueStatus: () => api.get("/applications/queue-status"),
};

// ─── Resumes ──────────────────────────────────────────────────────────────
export const resumesApi = {
  list: () => api.get("/resumes"),
  upload: (formData: FormData) =>
    api.post("/resumes/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  generate: (data: { job_id: string; base_resume_id?: string }) =>
    api.post("/resumes/generate", data),
  setDefault: (id: string) => api.patch(`/resumes/${id}/set-default`),
  getLatex: () => api.get("/resumes/latex"),
  getLatexTemplates: () => api.get("/resumes/latex/templates"),
  selectLatexTemplate: (name: string) =>
    api.post("/resumes/latex/template/select", { template_name: name }),
  analyze: () => api.get("/resumes/analyze"),
};

// ─── Cover Letters ────────────────────────────────────────────────────────
export const coverLettersApi = {
  list: () => api.get("/cover-letters"),
  generate: (data: { job_id: string; tone?: string; additional_context?: string }) =>
    api.post("/cover-letters/generate", data),
};

// ─── Agent ────────────────────────────────────────────────────────────────
export const agentApi = {
  status: () => api.get("/agent/status"),
  tasks: (params?: Record<string, unknown>) => api.get("/agent/tasks", { params }),
  run: (data: { task_type: string; payload?: Record<string, unknown> }) =>
    api.post("/agent/run", data),
  pause: () => api.post("/agent/pause"),
  resume: () => api.post("/agent/resume"),
  applyOne: (applicationId: string) => api.post(`/agent/apply/${applicationId}`),
};

// ─── Analytics ────────────────────────────────────────────────────────────
export const analyticsApi = {
  dashboard: () => api.get("/analytics/dashboard"),
  skillGaps: () => api.get("/analytics/skill-gaps"),
  market: () => api.get("/analytics/market"),
  resumePerformance: () => api.get("/analytics/resume-performance"),
};

// ─── Chat ─────────────────────────────────────────────────────────────────
export const chatApi = {
  send: (data: { message: string; history: { role: string; content: string }[] }) =>
    api.post("/chat", data),
  credits: () => api.get("/chat/credits"),
};

// ─── Subscriptions ────────────────────────────────────────────────────────
export const subscriptionsApi = {
  plans: () => api.get("/subscriptions/plans"),
  current: () => api.get("/subscriptions/current"),
  cancel: () => api.post("/subscriptions/cancel"),
};

// ─── Payments ─────────────────────────────────────────────────────────────
export const paymentsApi = {
  createOrder: (data: { plan: string }) => api.post("/payments/create-order", data),
  verify: (data: Record<string, string>) => api.post("/payments/verify", data),
  history: () => api.get("/payments/history"),
};

// ─── Quotas ───────────────────────────────────────────────────────────────
export const quotasApi = {
  status: () => api.get("/quota/"),
};

// ─── Platform ─────────────────────────────────────────────────────────────
export const platformApi = {
  status: () => api.get("/platform/status"),
  connect: (data: Record<string, unknown>) => api.post("/platform/connect", data),
  login: (platform: string, data: { email: string; password: string }) =>
    api.post(`/platform/login/${platform}`, data),
  validate: (data: Record<string, unknown>) => api.post("/platform/validate", data),
  invalidate: (platform: string) => api.post(`/platform/invalidate/${platform}`),
};

// ─── Settings ─────────────────────────────────────────────────────────────
export const settingsApi = {
  get: () => api.get("/settings"),
  update: (data: Record<string, unknown>) => api.patch("/settings", data),
};

// ─── Security ─────────────────────────────────────────────────────────────
export const securityApi = {
  credentials: () => api.get("/security/credentials"),
  addCredential: (data: Record<string, unknown>) => api.post("/security/credentials", data),
  deleteCredential: (id: string) => api.delete(`/security/credentials/${id}`),
  consents: () => api.get("/security/consents"),
  updateConsent: (data: Record<string, unknown>) => api.post("/security/consents", data),
  audit: () => api.get("/security/audit"),
  exportData: () => api.post("/security/data/export"),
  deleteData: () => api.post("/security/data/delete"),
};

// ─── Admin ────────────────────────────────────────────────────────────────
export const adminApi = {
  stats: () => api.get("/admin/stats"),
  health: () => api.get("/admin/health"),
  users: (params?: Record<string, unknown>) => api.get("/admin/users", { params }),
  getUser: (id: string) => api.get(`/admin/users/${id}`),
  updateUserPlan: (id: string, data: Record<string, unknown>) =>
    api.post(`/admin/users/${id}/plan`, data),
  suspendUser: (id: string) => api.post(`/admin/users/${id}/suspend`),
  reactivateUser: (id: string) => api.post(`/admin/users/${id}/reactivate`),
  auditLogs: (params?: Record<string, unknown>) =>
    api.get("/admin/audit-logs", { params }),
};
