import { FormEvent, useState } from "react";
import type { AuthResponse } from "../types";
import { loginUser, registerUser } from "../services/api";

interface AuthPageProps {
  onAuthenticated: (auth: AuthResponse) => void;
}

function AuthPage({ onAuthenticated }: AuthPageProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isRegistering = mode === "register";

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const auth = isRegistering
        ? await registerUser({ email, password, full_name: fullName })
        : await loginUser({ email, password });
      onAuthenticated(auth);
    } catch {
      setError(isRegistering ? "Unable to create account." : "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto grid min-h-[calc(100vh-88px)] max-w-6xl items-center gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1fr_28rem] lg:px-8">
      <section className="space-y-6">
        <p className="text-sm font-semibold uppercase tracking-[0.25em] text-brand-600">Secure AI Shopping</p>
        <div className="max-w-2xl space-y-4">
          <h1 className="text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
            Sign in to keep your shopping context private.
          </h1>
          <p className="text-lg leading-8 text-slate-600">
            JWT authentication protects the assistant endpoint while preserving multi-turn memory for each signed-in shopper.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
        <div className="mb-6 grid grid-cols-2 rounded-xl bg-slate-100 p-1">
          <button
            type="button"
            onClick={() => setMode("login")}
            className={`rounded-lg px-4 py-2 text-sm font-semibold transition ${
              mode === "login" ? "bg-white text-slate-950 shadow-sm" : "text-slate-500"
            }`}
          >
            Login
          </button>
          <button
            type="button"
            onClick={() => setMode("register")}
            className={`rounded-lg px-4 py-2 text-sm font-semibold transition ${
              mode === "register" ? "bg-white text-slate-950 shadow-sm" : "text-slate-500"
            }`}
          >
            Register
          </button>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          {isRegistering && (
            <label className="block">
              <span className="text-sm font-medium text-slate-700">Full name</span>
              <input
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
                placeholder="Your name"
              />
            </label>
          )}

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Email</span>
            <input
              type="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
              placeholder="you@example.com"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Password</span>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="mt-2 w-full rounded-xl border border-slate-200 px-4 py-3 outline-none transition focus:border-brand-500 focus:ring-2 focus:ring-brand-100"
              placeholder="At least 8 characters"
            />
          </label>

          {error && <p className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Please wait..." : isRegistering ? "Create account" : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}

export default AuthPage;
