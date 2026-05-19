import { useMemo } from "react";
import SearchBar from "../components/SearchBar";
import Chat from "../components/Chat";
import ProductCard from "../components/ProductCard";
import Suggestions from "../components/Suggestions";
import { useChat } from "../hooks/useChat";

const promptExamples = [
  "Best laptop under ₹70000",
  "Compare iPhone and Samsung",
  "Smart watches for gym",
];

function Home() {
  const { query, setQuery, history, products, loading, error, sendQuery } = useChat();

  const featuredPrompt = useMemo(
    () => promptExamples[Math.floor(Math.random() * promptExamples.length)],
    []
  );

  const handleSuggestion = (prompt: string) => {
    setQuery(prompt);
    sendQuery(prompt);
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <section className="grid gap-8 lg:grid-cols-[1.35fr_0.75fr]">
        <div className="rounded-[2rem] bg-white p-8 shadow-soft">
          <div className="space-y-6">
            <div className="max-w-2xl space-y-4">
              <p className="text-sm uppercase tracking-[0.3em] text-brand-600">AI Shopping Copilot</p>
              <h1 className="text-4xl font-semibold tracking-tight text-slate-900 sm:text-5xl">
                Modern AI shopping for confident buys.
              </h1>
              <p className="text-lg leading-8 text-slate-600">
                Ask the copilot anything about products, comparisons, or review summaries and discover recommendations instantly.
              </p>
            </div>

            <div className="grid gap-4 rounded-[2rem] bg-slate-50 p-6 sm:grid-cols-[1fr_auto]">
              <div>
                <p className="text-sm text-slate-500">Featured prompt</p>
                <p className="mt-3 text-lg font-semibold text-slate-900">{featuredPrompt}</p>
              </div>
            </div>

            <SearchBar
              value={query}
              onChange={(value) => setQuery(value)}
              onSubmit={() => sendQuery(query)}
              loading={loading}
            />
          </div>
        </div>

        <div id="suggestions">
          <Suggestions options={promptExamples} onSelect={handleSuggestion} loading={loading} />
        </div>
      </section>

      <section className="mt-10 grid gap-8 lg:grid-cols-[1.45fr_0.85fr]">
        <div id="chat">
          <Chat history={history} loading={loading} error={error} />
        </div>

        <aside id="products" className="space-y-6">
          <div className="rounded-[2rem] bg-slate-900 p-6 text-white shadow-soft">
            <div className="space-y-3">
              <p className="text-sm uppercase tracking-[0.25em] text-brand-300">Recommended products</p>
              <h2 className="text-2xl font-semibold text-white">Products the AI thinks you'll love.</h2>
              <p className="text-sm text-slate-300">
                These cards update automatically based on your latest query.
              </p>
            </div>
          </div>

          <div className="grid gap-4">
            {products.length > 0 ? (
              products.map((product) => <ProductCard key={product.id} product={product} />)
            ) : (
              <div className="rounded-[2rem] border border-slate-700 bg-slate-950/80 p-6 text-sm text-slate-300">
                Ask the assistant a shopping query to see matched products.
              </div>
            )}
          </div>
        </aside>
      </section>
    </div>
  );
}

export default Home;
