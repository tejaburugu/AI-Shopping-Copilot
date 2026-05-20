import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import AuthPage from "./components/AuthPage";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import type { AuthUser } from "./types";
import { getCurrentUser, setAuthToken } from "./services/api";

const TOKEN_STORAGE_KEY = "ai-shopping-token";

function App() {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_STORAGE_KEY));
  const [user, setUser] = useState<AuthUser | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(Boolean(token));

  useEffect(() => {
    setAuthToken(token);
    if (!token) {
      setCheckingAuth(false);
      return;
    }

    getCurrentUser()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem(TOKEN_STORAGE_KEY);
        setToken(null);
        setAuthToken(null);
      })
      .finally(() => setCheckingAuth(false));
  }, [token]);

  const handleLogout = () => {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    setAuthToken(null);
    setToken(null);
    setUser(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar user={user} onLogout={handleLogout} />
      {checkingAuth ? (
        <div className="mx-auto max-w-7xl px-4 py-16 text-sm text-slate-500 sm:px-6 lg:px-8">
          Checking your session...
        </div>
      ) : user ? (
        <Routes>
          <Route path="/*" element={<Home />} />
        </Routes>
      ) : (
        <AuthPage
          onAuthenticated={(auth) => {
            localStorage.setItem(TOKEN_STORAGE_KEY, auth.access_token);
            setAuthToken(auth.access_token);
            setToken(auth.access_token);
            setUser(auth.user);
          }}
        />
      )}
    </div>
  );
}

export default App;
