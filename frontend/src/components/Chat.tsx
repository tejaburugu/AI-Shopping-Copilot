import ChatMessage from "./ChatMessage";
import Loader from "./Loader";

interface ChatProps {
  history: { role: "user" | "assistant"; text: string }[];
  loading: boolean;
  error: string | null;
}

function Chat({ history, loading, error }: ChatProps) {
  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 shadow-soft">
        <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.25em] text-brand-600">AI Chat Assistant</p>
            <h2 className="mt-2 text-2xl font-semibold text-slate-900">Ask anything and get intelligent shopping guidance.</h2>
          </div>
          <p className="rounded-full bg-white px-4 py-2 text-sm text-slate-600 ring-1 ring-slate-200">
            Friendly suggestions, product summaries, and comparison help.
          </p>
        </div>

        <div className="space-y-4">
          {history.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-slate-200 bg-white/80 p-6 text-sm text-slate-600">
              Start by asking the copilot a question. It will answer and surface product recommendations in real time.
            </div>
          ) : (
            history.map((message, index) => (
              <ChatMessage key={`${message.role}-${index}`} role={message.role} message={message.text} />
            ))
          )}

          {loading && <Loader />}

          {error ? (
            <div className="rounded-3xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">{error}</div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export default Chat;
