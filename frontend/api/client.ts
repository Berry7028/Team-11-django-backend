// Simple API client for React Native frontend.
//
// 想定利用例:
// const client = new ApiClient(process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8000");
// const quests = await client.get("/api/quests/quests/");

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export interface ApiClientOptions {
  baseUrl: string;
  getAuthToken?: () => Promise<string | null> | string | null;
}

export class ApiClient {
  private baseUrl: string;
  private getAuthToken?: ApiClientOptions["getAuthToken"];

  constructor(options: ApiClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/+$/, "");
    const parsedUrl = new URL(this.baseUrl);
    const isLocalhost = ["localhost", "127.0.0.1", "::1"].includes(
      parsedUrl.hostname
    );
    if (!isLocalhost && parsedUrl.protocol !== "https:") {
      throw new Error("ApiClient baseUrl must use HTTPS outside localhost");
    }
    this.getAuthToken = options.getAuthToken;
  }

  private async request<T>(
    method: HttpMethod,
    path: string,
    body?: unknown
  ): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (this.getAuthToken) {
      const token = await this.getAuthToken();
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
    }

    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(
        `Request failed with status ${response.status}: ${text || response.statusText}`
      );
    }

    if (response.status === 204) {
      // No Content
      return undefined as T;
    }

    return (await response.json()) as T;
  }

  get<T>(path: string): Promise<T> {
    return this.request<T>("GET", path);
  }

  post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("POST", path, body);
  }

  put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("PUT", path, body);
  }

  patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>("PATCH", path, body);
  }

  delete<T>(path: string): Promise<T> {
    return this.request<T>("DELETE", path);
  }
}
