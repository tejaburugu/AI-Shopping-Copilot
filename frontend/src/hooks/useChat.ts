import { useMemo, useState } from "react";
import type { AskResponse } from "../types";
import { askAssistant } from "../services/api";

export function useChat() {
  const sessionId = useMemo(() => {
    if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
      return crypto.randomUUID();
    }
    return `session-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  }, []);
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState<{ role: "user" | "assistant"; text: string }[]>([]);
  const [products, setProducts] = useState<AskResponse["products"]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendQuery = async (message: string) => {
    if (!message.trim()) {
      return;
    }

    setError(null);
    setLoading(true);
    setHistory((prev) => [...prev, { role: "user", text: message }]);

    try {
      const data = await askAssistant(message, sessionId);
      setHistory((prev) => [...prev, { role: "assistant", text: data.answer }]);
      setProducts(data.products);
    } catch (err) {
      setError("Unable to reach the AI assistant. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return {
    query,
    setQuery,
    history,
    products,
    loading,
    error,
    sendQuery,
  };
}
