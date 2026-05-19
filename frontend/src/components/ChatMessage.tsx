interface ChatMessageProps {
  role: "user" | "assistant";
  message: string;
}

function ChatMessage({ role, message }: ChatMessageProps) {
  const isUser = role === "user";
  return (
    <div className={`rounded-3xl p-5 shadow-soft ${isUser ? "bg-slate-50 text-slate-900" : "bg-brand-600 text-white"}`}>
      <div className="text-xs uppercase tracking-[0.24em] opacity-80">{isUser ? "You" : "Copilot"}</div>
      <p className="mt-3 whitespace-pre-line text-sm leading-6">{message}</p>
    </div>
  );
}

export default ChatMessage;
