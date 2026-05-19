interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

function SearchBar({ value, onChange, onSubmit, loading }: SearchBarProps) {
  return (
    <form
      className="grid gap-3 rounded-3xl border border-slate-200 bg-slate-50 p-4 shadow-sm sm:grid-cols-[1fr_auto]"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <label className="sr-only" htmlFor="search-input">
        Ask the shopping assistant
      </label>
      <input
        id="search-input"
        className="min-h-[56px] rounded-3xl border border-slate-200 bg-white px-4 text-slate-900 shadow-sm outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
        placeholder="Ask anything..."
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
      <button
        type="submit"
        className="inline-flex min-h-[56px] items-center justify-center rounded-3xl bg-brand-600 px-6 text-sm font-semibold text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        disabled={loading}
      >
        {loading ? "Searching..." : "Ask Copilot"}
      </button>
    </form>
  );
}

export default SearchBar;
