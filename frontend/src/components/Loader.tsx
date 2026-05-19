function Loader() {
  return (
    <div className="rounded-3xl border border-slate-200 bg-slate-50 p-6 shadow-soft">
      <div className="flex items-center gap-4 text-slate-700">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-brand-600 border-t-transparent" />
        <div>
          <p className="font-semibold">AI is thinking...</p>
          <p className="text-sm text-slate-500">Crafting the perfect product recommendations for you.</p>
        </div>
      </div>
    </div>
  );
}

export default Loader;
