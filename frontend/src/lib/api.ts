import { QueryRequest, QueryResponse, DiseasesResponse } from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async fetchWithTimeout(url: string, options: RequestInit = {}, timeout: number = 60000): Promise<Response> {
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
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          throw new Error('Request timed out. Please refresh the page and try again.');
        }
        if (error.message.includes('fetch')) {
          throw new Error('Connection failed. Please check your internet and refresh the page.');
        }
      }
      throw error;
    }
  }

  async query(request: QueryRequest): Promise<QueryResponse> {
    // Try up to 2 times with increasing timeout
    const maxRetries = 2;
    let lastError: Error = new Error('Unknown error');
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        const timeoutMs = attempt === 1 ? 30000 : 60000; // First try: 30s, Second try: 60s
        const response = await this.fetchWithTimeout(`${this.baseUrl}/api/query`, {
          method: 'POST',
          body: JSON.stringify(request),
        }, timeoutMs);

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }

        return await response.json();
      } catch (error) {
        lastError = error instanceof Error ? error : new Error('Unknown error');
        
        // If it's the last attempt, throw the error
        if (attempt === maxRetries) {
          break;
        }
        
        // Wait 2 seconds before retry
        await new Promise(resolve => setTimeout(resolve, 2000));
      }
    }
    
    // Provide user-friendly error messages
    if (lastError.message.includes('timed out') || lastError.message.includes('AbortError')) {
      throw new Error('The server is taking longer than expected to respond. Please refresh the page and try again. This often happens when the server is starting up.');
    }
    if (lastError.message.includes('Connection failed') || lastError.message.includes('fetch')) {
      throw new Error('Unable to connect to the server. Please check your internet connection and refresh the page.');
    }
    
    throw new Error(`Failed to send query: ${lastError.message}`);
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