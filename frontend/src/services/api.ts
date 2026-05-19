import axios from "axios";
import type { AskResponse } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export async function askAssistant(query: string, sessionId?: string): Promise<AskResponse> {
  const response = await api.post<AskResponse>("/ask", { query, session_id: sessionId });
  return response.data;
}
