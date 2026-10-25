const API_BASE = '/api';

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  created_at: string;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  role: 'owner' | 'reviewer' | 'viewer';
  created_at: string;
}

export interface Member {
  user_id: string;
  email: string;
  full_name: string | null;
  role: 'owner' | 'reviewer' | 'viewer';
  created_at: string;
}

export interface RfError {
  type: string;
  title: string;
  status: number;
  detail: string;
  code: string;
  request_id: string;
}

class ApiClient {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('rf_session_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('rf_session_token', token);
    } else {
      localStorage.removeItem('rf_session_token');
    }
  }

  getToken() {
    return this.token;
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!res.ok) {
      const error: RfError = await res.json().catch(() => ({
        type: 'about:blank',
        title: 'Error',
        status: res.status,
        detail: res.statusText,
        code: 'NETWORK_ERROR',
        request_id: res.headers.get('X-Request-ID') || 'unknown',
      }));
      throw error;
    }

    return res.json();
  }

  // Health
  getHealth() {
    return this.request<{ status: string; service: string; env: string }>('/healthz');
  }

  // Auth
  requestMagicLink(email: string) {
    return this.request<{ message: string; token?: string }>('/auth/magic-link', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  }

  async verifySession(token: string) {
    const res = await this.request<{ user: User; session_token: string }>('/auth/session', {
      method: 'POST',
      body: JSON.stringify({ token }),
    });
    this.setToken(res.session_token);
    return res;
  }

  getMe() {
    return this.request<User>('/me');
  }

  logout() {
    this.setToken(null);
  }

  // Projects
  getProjects() {
    return this.request<Project[]>('/projects');
  }

  createProject(name: string, description?: string) {
    return this.request<Project>('/projects', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    });
  }

  getProject(id: string) {
    return this.request<Project>(`/projects/${id}`);
  }

  getProjectMembers(projectId: string) {
    return this.request<Member[]>(`/projects/${projectId}/members`);
  }

  addProjectMember(projectId: string, email: string, role: string) {
    return this.request<Member>(`/projects/${projectId}/members`, {
      method: 'POST',
      body: JSON.stringify({ email, role }),
    });
  }

  // Works & Federated Search
  searchWorks(query: string, yearFrom?: number, yearTo?: number, oaOnly: boolean = false) {
    const params = new URLSearchParams({ q: query });
    if (yearFrom) params.append('year_from', yearFrom.toString());
    if (yearTo) params.append('year_to', yearTo.toString());
    if (oaOnly) params.append('oa_only', 'true');
    return this.request<{
      items: any[];
      source_status: { source: string; status: string; latency_ms: number; items_count: number }[];
      total_results: number;
    }>(`/works/search?${params.toString()}`);
  }

  // Library Management
  getLibraryItems(projectId: string, limit: number = 50, offset: number = 0) {
    return this.request<{
      items: any[];
      total: number;
      limit: number;
      offset: number;
    }>(`/projects/${projectId}/library/items?limit=${limit}&offset=${offset}`);
  }

  addToLibrary(projectId: string, workId: string, userNotes?: string) {
    return this.request(`/projects/${projectId}/library/items`, {
      method: 'POST',
      body: JSON.stringify({ work_id: workId, user_notes: userNotes }),
    });
  }

  importReferences(projectId: string, format: 'ris' | 'bibtex' | 'csv', content: string) {
    return this.request<{
      batch_id: string;
      source: string;
      total_count: number;
      imported_count: number;
      skipped_count: number;
      report: any;
    }>(`/projects/${projectId}/imports`, {
      method: 'POST',
      body: JSON.stringify({ format, content }),
    });
  }

  getExportUrl(projectId: string, format: 'bibtex' | 'ris' | 'csv') {
    return `${API_BASE}/projects/${projectId}/exports?format=${format}`;
  }
}

export const api = new ApiClient();
