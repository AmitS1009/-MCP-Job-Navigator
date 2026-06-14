const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ResearchResult {
  session_id: string;
  company_name: string;
  validation_passed: boolean;
  total_results: number;
  elapsed_seconds: number;
  synthesis: string;
  retry_count: number;
}

export interface HistoryItem {
  session_id: string;
  query: string;
  validation_passed: boolean;
  created_at: string;
  synthesis: string;
}

// Import axios here to avoid circular import issues
import axios from 'axios';

async function axiosWithRetry<T>(axiosFunc: () => Promise<T>): Promise<T> {
  const maxRetries = 3;
  const delayMs = 2000;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await axiosFunc();
    } catch (error) {
      // Check if it's a network error (no response)
      if (axios.isAxiosError(error) && !error.response) {
        if (attempt < maxRetries) {
          console.log(`Retrying... attempt ${attempt} of ${maxRetries}`);
          await new Promise(resolve => setTimeout(resolve, delayMs));
          continue;
        }
      }
      // If not a network error or last attempt, rethrow
      throw error;
    }
  }
  // Should never reach here
  throw new Error('Unexpected retry exhaustion');
}

export async function runResearch(query: string): Promise<ResearchResult> {
  console.log(`[API] Starting research for query: ${query}`);
  return axiosWithRetry(() =>
    axios.post(`${API_BASE}/research`, { query }).then(res => res.data)
  );
}

export async function getHistory(): Promise<HistoryItem[]> {
  console.log('[API] Fetching research history');
  return axiosWithRetry(() =>
    axios.get(`${API_BASE}/history`).then(res => res.data)
  );
}