export interface Job {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  operation: string;
  filenames?: string[];
  expires: number;
  result?: Record<string, unknown>;
  error?: string;
  download_available?: boolean;
}

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/v1${path}`, { ...init, credentials: 'same-origin' });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(
      typeof data.detail === 'string' ? data.detail : `Request failed (${response.status})`,
    );
  }
  return response.status === 204 ? (undefined as T) : response.json();
}
