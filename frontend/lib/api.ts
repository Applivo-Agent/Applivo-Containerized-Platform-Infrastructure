import axios from "axios";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ||
  (process.env.NODE_ENV === "production" ? "" : "http://localhost:8000");

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
  // Signup
  registerInitiate: (data: { email: string; password: string; full_name: string }) =>
    api.post("/auth/register/initiate", data),
  registerVerify: (data: { email: string; otp: string; purpose: "register"; password?: string; full_name?: string }, userData: Record<string, unknown>) =>
    api.post("/auth/register/verify", { ...data, ...userData }),
  
  // Login
  loginInitiate: (data: { email: string; password: string }) =>
    api.post("/auth/login/initiate", data),
  loginVerify: (data: { email: string; otp: string; purpose: "login" }) =>
    api.post("/auth/login/verify", data),
  
  // Shared
  resendOtp: (email: string, purpose: "register" | "login") =>
    api.post("/auth/otp/resend", null, { params: { email, purpose } }),

  googleLogin: (id_token: string) =>
    api.post("/auth/google", { id_token }),
  me: () => api.get("/auth/me"),
  status: () => api.get("/auth/status"),
  forgotPassword: (email: string) => api.post("/auth/forgot-password", { email }),
  resetPassword: (data: { token: string; new_password: string }) => api.post("/auth/reset-password", data),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post("/auth/change-password", data),
  logout: () => api.post("/auth/logout"),

  // Legacy (can be removed once forms are updated)
  register: (data: { email: string; password: string; full_name: string }) =>
    api.post("/auth/register/initiate", data),
  login: (data: { email: string; password: string }) =>
    api.post("/auth/login/initiate", data),
};

// ─── Profile ──────────────────────────────────────────────────────────────
export const profileApi = {
  get: () => api.get("/profile"),
  update: (data: Record<string, unknown>) => api.patch("/profile", data),
  listSkills: () => api.get("/profile/skills"),
  addSkill: (data: Record<string, unknown>) => api.post("/profile/skills", data),
  deleteSkill: (id: string) => api.delete(`/profile/skills/${id}`),
};

// ─── Onboarding ───────────────────────────────────────────────────────────
export const onboardingApi = {
  status: () => api.get("/v1/onboarding/status"),
  complete: (step: string, data: Record<string, unknown>) =>
    api.post(`/v1/onboarding/${step}`, data),
  parseResume: (formData: FormData) =>
    api.post("/v1/onboarding/resume/parse", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  parseResumeAndFill: (formData: FormData) =>
    api.post("/v1/onboarding/resume/parse-and-fill", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};

// ─── Jobs ─────────────────────────────────────────────────────────────────
export const jobsApi = {
  list: (params?: Record<string, unknown>) => api.get("/jobs", { params }),
  get: (id: string) => api.get(`/jobs/${id}`),
  analyze: (id: string) => api.post(`/jobs/${id}/analyze`),
  skip: (id: string) => api.post(`/jobs/${id}/skip`),
  scrape: () => api.post("/jobs/scrape"),
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
  download: (id: string) => api.get(`/resumes/${id}/file`),
  getLatex: () => api.get("/resumes/latex"),
  getLatexTemplates: () => api.get("/resumes/latex/templates"),
  selectLatexTemplate: (name: string) =>
    api.post("/resumes/latex/template/select", { template_name: name }),
  analyze: () => api.get("/resumes/analyze"),
  delete: (id: string) => api.delete(`/resumes/${id}`),
};

// ─── Cover Letters ────────────────────────────────────────────────────────
export const coverLettersApi = {
  list: () => api.get("/cover-letters"),
  generate: (data: { job_id: string; tone?: string; additional_context?: string }) =>
    api.post("/cover-letters/generate", data),
  get: (id: string) => api.get(`/cover-letters/${id}`),
  delete: (id: string) => api.delete(`/cover-letters/${id}`),
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

// ─── Workflow Pipeline ────────────────────────────────────────────────────
export const workflowsApi = {
  run: () => api.post("/workflows/run"),
  latest: () => api.get("/workflows/latest"),
  get: (id: string) => api.get(`/workflows/${id}`),
  cancel: (id: string) => api.post(`/workflows/${id}/cancel`),
};

// ─── Analytics ────────────────────────────────────────────────────────────
export const analyticsApi = {
  dashboard: () => api.get("/analytics/dashboard"),
  skillGaps: () => api.get("/analytics/skill-gaps"),
  market: () => api.get("/analytics/market"),
  resumePerformance: () => api.get("/analytics/resume-performance"),
  velocity: (days?: number) => api.get("/analytics/velocity", { params: { days } }),
  funnel: () => api.get("/analytics/funnel"),
};

// ─── Chat ─────────────────────────────────────────────────────────────────
export const chatApi = {
  send: (data: { message: string; history: { role: string; content: string }[]; persona?: string }) =>
    api.post("/chat", data),
  credits: () => api.get("/chat/credits"),
  history: (limit = 50) => api.get(`/chat/history?limit=${limit}`),
  clearHistory: () => api.delete("/chat/history"),
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
  startTrialWithAutopay: (data: { plan: string }) =>
    api.post("/payments/start-trial-with-autopay", data),
  getAutopayManageUrl: () => api.get("/payments/autopay-manage-url"),
  cancelAutopay: () => api.post("/payments/cancel-autopay"),
};

// ─── Quotas ───────────────────────────────────────────────────────────────
export const quotasApi = {
  status: () => api.get("/quota/"),
  analyzeBudget: () => api.get("/quota/analyze-budget"),
};

// ─── Platform ─────────────────────────────────────────────────────────────
export const platformApi = {
  status: () => api.get("/platform/status"),
  connect: (data: { platform: string; cookies: string | Record<string, unknown> | unknown[] }) =>
    api.post("/platform/connect", data),
  uploadCookies: (data: { platform: string; cookies: string | Record<string, unknown> | unknown[] }) =>
    api.post("/platform/upload-cookies", data),
  login: (platform: string, data: { email: string; password: string }) =>
    api.post(`/platform/login/${platform}`, data),
  validate: (data: Record<string, unknown>) => api.post("/platform/validate", data),
  disconnect: (platform: string) => api.delete(`/platform/disconnect/${platform}`),
  invalidate: (platform: string) => api.post(`/platform/invalidate/${platform}`),
  messages: (platform: string = "internshala", limit: number = 50) =>
    api.get(`/platform/messages?platform=${platform}&limit=${limit}`),
  scanMessages: (platform: string = "internshala") =>
    api.post(`/platform/scan/messages/${platform}`),
};

// ─── Settings ─────────────────────────────────────────────────────────────
export const settingsApi = {
  get: () => api.get("/settings"),
  update: (data: Record<string, unknown>) => api.patch("/settings", data),
};

// ─── Settings V2 (full persistence) ──────────────────────────────────────
export const settingsV2Api = {
  getAll: () => api.get("/settings/v2"),
  updateGeneral: (data: Record<string, unknown>) => api.put("/settings/v2/general", data),
  updateNotifications: (data: Record<string, unknown>) => api.put("/settings/v2/notifications", data),
  testNotification: (channel: string) => api.post("/settings/v2/notifications/test", { channel }),
  updateAutomation: (data: Record<string, unknown>) => api.put("/settings/v2/automation", data),
  updateStrategy: (data: Record<string, unknown>) => api.put("/settings/v2/strategy", data),
  updateAI: (data: Record<string, unknown>) => api.put("/settings/v2/ai", data),
  getPlatformStatus: () => api.get("/settings/v2/platforms/status"),
  updatePlatforms: (data: Record<string, unknown>) => api.put("/settings/v2/platforms", data),
  updateSecurity: (data: Record<string, unknown>) => api.put("/settings/v2/security", data),
  getSessions: () => api.get("/settings/v2/security/sessions"),
  terminateSession: (sessionId: string) => api.post(`/settings/v2/security/sessions/${sessionId}/terminate`),
  terminateAllSessions: () => api.post("/settings/v2/security/sessions/terminate-all"),
  updateAdvanced: (data: Record<string, unknown>) => api.put("/settings/v2/advanced", data),
  exportData: (types: string[], format: string) => api.post("/settings/v2/advanced/export", { types, format }),
  resetSystem: (confirmation: string) => api.post("/settings/v2/advanced/reset", { confirmation }),
  getAuditLogs: (limit?: number, offset?: number) => api.get("/settings/v2/audit", { params: { limit, offset } }),
};

// ─── Security ─────────────────────────────────────────────────────────────
export const securityApi = {
  credentials: () => api.get("/security/credentials"),
  addCredential: (data: Record<string, unknown>) => api.post("/security/credentials", data),
  deleteCredential: (id: string) => api.delete(`/security/credentials/${id}`),
  consents: () => api.get("/security/consents"),
  updateConsent: (data: Record<string, unknown>) => api.post("/security/consents", data),
  audit: () => api.get("/security/data/audit"),
  exportData: () => api.post("/security/data/export"),
  deleteData: () => api.post("/security/data/delete"),
};

// ─── Admin ────────────────────────────────────────────────────────────────
export const adminApi = {
  stats: () => api.get("/admin/stats"),
  llmUsage: () => api.get("/admin/llm-usage"),
  health: () => api.get("/admin/system/health"),
  users: (params?: Record<string, unknown>) => api.get("/admin/users", { params }),
  getUser: (id: string) => api.get(`/admin/users/${id}`),
  updateUser: (id: string, data: Record<string, unknown>) =>
    api.patch(`/admin/users/${id}`, data),
  suspendUser: (id: string) => api.patch(`/admin/users/${id}`, { is_active: false }),
  reactivateUser: (id: string) => api.patch(`/admin/users/${id}`, { is_active: true }),
  auditLogs: (params?: Record<string, unknown>) =>
    api.get("/admin/audit-logs", { params }),
};

// ─── Scheduler ───────────────────────────────────────────────────────────
export const schedulerApi = {
  listJobs: () => api.get("/scheduler/jobs"),
  addJob: (data: Record<string, unknown>) => api.post("/scheduler/jobs", data),
  removeJob: (jobId: string) => api.delete(`/scheduler/jobs/${jobId}`),
  runJobNow: (jobId: string) => api.post(`/scheduler/jobs/${jobId}/run`),
  pauseJob: (jobId: string) => api.post(`/scheduler/jobs/${jobId}/pause`),
  resumeJob: (jobId: string) => api.post(`/scheduler/jobs/${jobId}/resume`),
  triggerTask: (taskName: string) => api.post(`/scheduler/trigger/${taskName}`),
  toggleJob: async (jobId: string, enabled: boolean) => {
    if (enabled) {
      return api.post(`/scheduler/jobs/${jobId}/resume`);
    } else {
      return api.post(`/scheduler/jobs/${jobId}/pause`);
    }
  },
};
