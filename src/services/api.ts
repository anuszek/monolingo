// API service for communicating with the backend
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  imageUrl?: string;
}

export interface ChatResponse {
  reply: string;
  error?: string;
}

/**
 * Send a message to the AI chat endpoint
 */
export async function sendMessage(message: string): Promise<ChatResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ prompt: message }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to get response from server");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error sending message:", error);
    throw error;
  }
}

/**
 * Request TTS for a text message. Returns a Blob (audio/mpeg).
 */
export async function agentTts(message: string, lang = "en-US"): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/agent-tts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, lang }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "TTS request failed");
  }
  return await response.blob();
}

/**
 * Send image + optional message to combined OCR+chat+TTS endpoint.
 * Expects FormData with field 'file', optional 'message' and 'lang'.
 * Returns JSON { reply, audio_b64, ocr_text }.
 */
export async function agentOcrTts(form: FormData): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/agent-ocr-tts`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "OCR+TTS request failed");
  }
  return await response.json();
}

/**
 * OCR-only endpoint: expects FormData with 'file' field.
 */
export async function ocr(form: FormData): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/ocr`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || "OCR request failed");
  }
  return await response.json();
}
