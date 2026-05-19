function Navbar() {
  return (
    <nav className="sticky top-0 z-30 border-b border-slate-200/80 bg-white/95 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-600 to-slate-900 text-xl font-bold text-white shadow-lg shadow-brand-500/20">
            AI
          </div>
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-900">AI Shopping Copilot</p>
            <p className="text-xs text-slate-500">Smart shopping with AI recommendations</p>
          </div>
        </div>

        <div className="hidden items-center gap-6 sm:flex">
          <a href="#chat" className="text-sm font-medium text-slate-600 transition hover:text-slate-900">Chat</a>
          <a href="#products" className="text-sm font-medium text-slate-600 transition hover:text-slate-900">Products</a>
          <a href="#suggestions" className="text-sm font-medium text-slate-600 transition hover:text-slate-900">Questions</a>
        </div>

        <button className="hidden rounded-full bg-slate-900 px-5 py-2 text-sm font-semibold text-white transition hover:bg-slate-800 sm:inline-flex">
          Start shopping
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
