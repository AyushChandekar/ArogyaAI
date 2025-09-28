import { QueryRequest, QueryResponse, DiseasesResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async fetchWithTimeout(url: string, options: RequestInit = {}, timeout: number = 30000): Promise<Response> {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });
      clearTimeout(id);
      return response;
    } catch (error) {
      clearTimeout(id);
      throw error;
    }
  }

  async query(request: QueryRequest): Promise<QueryResponse> {
    try {
      const response = await this.fetchWithTimeout(`${this.baseUrl}/api/query`, {
        method: 'POST',
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to send query: ${error.message}`);
      }
      throw new Error('Failed to send query: Unknown error');
    }
  }

  async getDiseases(): Promise<DiseasesResponse> {
    try {
      const response = await this.fetchWithTimeout(`${this.baseUrl}/api/diseases`);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to fetch diseases: ${error.message}`);
      }
      throw new Error('Failed to fetch diseases: Unknown error');
    }
  }

  async healthCheck(): Promise<{ status: string; rasa_available: boolean; diseases_loaded: number }> {
    try {
      const response = await this.fetchWithTimeout(`${this.baseUrl}/health`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Health check failed: ${error.message}`);
      }
      throw new Error('Health check failed: Unknown error');
    }
  }
}

export const apiClient = new ApiClient();
export default ApiClient;