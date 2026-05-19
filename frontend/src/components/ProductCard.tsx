import type { Product } from "../types";

interface ProductCardProps {
  product: Product;
}

function ProductCard({ product }: ProductCardProps) {
  const formattedPrice = new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(product.price);

  const rating = Math.max(0, Math.min(5, product.rating));
  const fullStars = Math.round(rating);
  const hasImage = Boolean(product.image_url);

  return (
    <article className="group overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-soft transition duration-300 hover:-translate-y-1 hover:border-brand-200 hover:shadow-xl sm:grid sm:grid-cols-[11rem_1fr] lg:block">
      <div className="relative flex min-h-52 items-center justify-center overflow-hidden bg-gradient-to-br from-slate-100 via-white to-brand-50 sm:min-h-full lg:h-56">
        {hasImage ? (
          <img
            src={product.image_url}
            alt={product.title}
            className="h-full w-full object-cover transition duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center gap-3 p-6 text-center">
            <div className="grid h-20 w-20 place-items-center rounded-2xl border border-slate-200 bg-white shadow-sm">
              <span className="text-3xl font-semibold text-brand-500">{product.brand.slice(0, 1).toUpperCase()}</span>
            </div>
            <span className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">Image coming soon</span>
          </div>
        )}

        <span className="absolute left-4 top-4 rounded-full bg-white/90 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-slate-600 shadow-sm backdrop-blur">
          {product.category}
        </span>
      </div>

      <div className="flex h-full flex-col gap-5 p-5 sm:p-6">
        <div className="space-y-3">
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand-600">{product.brand}</p>
              <h3 className="mt-2 line-clamp-2 text-lg font-semibold leading-6 text-slate-950">{product.title}</h3>
            </div>
            <span className="shrink-0 rounded-xl bg-slate-950 px-3 py-2 text-sm font-semibold text-white shadow-sm">
              {formattedPrice}
            </span>
          </div>

          <p className="line-clamp-2 text-sm leading-6 text-slate-600">{product.description}</p>
        </div>

        <div className="mt-auto space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4 text-sm">
            <div className="flex items-center gap-2" aria-label={`Rating ${rating.toFixed(1)} out of 5`}>
              <span className="tracking-wide text-amber-400" aria-hidden="true">
                {"★".repeat(fullStars)}
                <span className="text-slate-200">{"★".repeat(5 - fullStars)}</span>
              </span>
              <span className="font-semibold text-slate-700">{rating.toFixed(1)}</span>
            </div>
            <span className="text-slate-500">{product.reviews.length} reviews</span>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              className="rounded-xl bg-brand-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
            >
              View details
            </button>
            <button
              type="button"
              className="rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-brand-200 hover:bg-brand-50 hover:text-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
            >
              Compare
            </button>
            <button
              type="button"
              className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm font-semibold text-slate-700 transition hover:border-slate-300 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2"
            >
              Ask AI
            </button>
          </div>
        </div>
      </div>
    </article>
  );
}

export default ProductCard;
