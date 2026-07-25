const API_BASE = 'http://localhost:3000';

export interface PromptRequest {
  question: string;
  companyName?: string;
  companyAbout?: string;
}

export interface PromptSource {
  source: string;
  section: string;
}

export interface PromptResponse {
  prompt: string;
  sources: PromptSource[];
}

export async function fetchPrompt(payload: PromptRequest): Promise<PromptResponse> {
  const response = await fetch(`${API_BASE}/prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    const message =
      body && typeof body === 'object' && 'message' in body
        ? String((body as { message: unknown }).message)
        : `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return response.json() as Promise<PromptResponse>;
}
