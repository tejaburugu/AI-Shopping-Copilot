interface SuggestionsProps {
  options: string[];
  onSelect: (value: string) => void;
  loading: boolean;
}

function Suggestions({ options, onSelect, loading }: SuggestionsProps) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <div className="mb-5">
        <p className="text-sm uppercase tracking-[0.25em] text-brand-600">Suggested questions</p>
        <h3 className="mt-3 text-xl font-semibold text-slate-900">Need inspiration? Start with one of these prompts.</h3>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            className="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-4 text-left text-sm font-medium text-slate-800 transition hover:border-brand-500 hover:bg-brand-50 disabled:cursor-not-allowed disabled:opacity-60"
            onClick={() => onSelect(option)}
            disabled={loading}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}

export default Suggestions;
