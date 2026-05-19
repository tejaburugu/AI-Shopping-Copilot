function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center rounded-3xl border border-slate-200 bg-slate-100 p-6 text-slate-600">
      <div className="flex items-center gap-3">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-brand-500 border-t-transparent"></div>
        <span>Thinking through the best recommendations...</span>
      </div>
    </div>
  );
}

export default LoadingSpinner;
