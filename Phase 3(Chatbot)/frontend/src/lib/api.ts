import { useNotification } from '@/contexts/NotificationContext';

// Define API response types
interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

class ApiClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://adeelahmed01-fullstack-todo-app.hf.space/api/v1';
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  // Set auth token
  setAuthToken(token: string | null) {
    if (token) {
      this.defaultHeaders = {
        ...this.defaultHeaders,
        'Authorization': `Bearer ${token}`,
      };
    } else {
      delete this.defaultHeaders['Authorization'];
    }
  }

  // Generic request method
  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const config: RequestInit = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `API request failed: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  // GET request
  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  // POST request
  async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // PUT request
  async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // PATCH request
  async patch<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

// Create singleton instance
export const apiClient = new ApiClient();

// Hook for using API with notifications
export const useApi = () => {
  const { showNotification } = useNotification();

  const handleApiCall = async <T,>(
    apiCall: () => Promise<T>,
    successMessage?: string,
    errorMessage?: string
  ): Promise<T | null> => {
    try {
      const result = await apiCall();
      if (successMessage) {
        showNotification(successMessage, 'success');
      }
      return result;
    } catch (error) {
      const message = errorMessage || (error instanceof Error ? error.message : 'An error occurred');
      showNotification(message, 'error');
      console.error('API call error:', error);
      return null;
    }
  };

  return { handleApiCall };
};