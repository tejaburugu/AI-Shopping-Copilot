function Header() {
  return (
    <header className="rounded-3xl bg-gradient-to-r from-brand-500 to-slate-700 p-6 text-white shadow-soft">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.25em] text-slate-200">AI Shopping Copilot</p>
          <h2 className="mt-2 text-2xl font-semibold sm:text-3xl">Your AI-driven e-commerce search assistant.</h2>
        </div>
        <div className="rounded-3xl bg-white/10 px-4 py-3 text-sm text-slate-100 ring-1 ring-white/10">
          Powered by FastAPI, LangChain, Gemini, FAISS & PostgreSQL
        </div>
      </div>
    </header>
  );
}

export default Header;
