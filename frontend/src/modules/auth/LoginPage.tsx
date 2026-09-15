import { FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { ShoppingCart } from "lucide-react";

export default function LoginPage() {
  const { user, login } = useAuth();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("Admin123!");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(username, password);
    } catch (err: any) {
      setError(err.message || "Error de autenticación");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="h-full grid place-items-center bg-slate-50 dark:bg-slate-950">
      <form onSubmit={onSubmit} className="w-full max-w-sm bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-200 dark:border-slate-800 shadow-xl space-y-5">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-brand-500 rounded-xl grid place-items-center text-white">
            <ShoppingCart className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Comercio<span className="text-brand-500">Pro</span></h1>
            <p className="text-xs text-slate-400">POS + ERP · República Dominicana</p>
          </div>
        </div>
        {error && <div className="text-xs bg-rose-50 text-rose-600 px-3 py-2 rounded-xl">{error}</div>}
        <label className="block text-xs font-semibold text-slate-400 uppercase">Usuario
          <input value={username} onChange={(e) => setUsername(e.target.value)} className="mt-1 w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm" />
        </label>
        <label className="block text-xs font-semibold text-slate-400 uppercase">Contraseña
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="mt-1 w-full px-3 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-sm" />
        </label>
        <button disabled={busy} className="w-full py-3 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-xl">
          {busy ? "Entrando…" : "Iniciar sesión"}
        </button>
      </form>
    </div>
  );
}
