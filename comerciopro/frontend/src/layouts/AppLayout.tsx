import { NavLink, Outlet, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  ShoppingCart,
  Receipt,
  Package,
  Boxes,
  FileText,
  Truck,
  Users,
  Wallet,
  BookOpen,
  BarChart3,
  UserCog,
  Settings,
  LogOut,
  Moon,
  Sun,
  Menu,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useAuth } from "../hooks/useAuth";

const NAV = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/pos", label: "Punto de Venta", icon: ShoppingCart },
  { to: "/ventas", label: "Ventas", icon: Receipt },
  { to: "/productos", label: "Productos", icon: Package },
  { to: "/inventario", label: "Inventario", icon: Boxes },
  { to: "/compras", label: "Compras", icon: FileText },
  { to: "/proveedores", label: "Proveedores", icon: Truck },
  { to: "/clientes", label: "Clientes", icon: Users },
  { to: "/caja", label: "Caja", icon: Wallet },
  { to: "/contabilidad", label: "Contabilidad", icon: BookOpen },
  { to: "/reportes", label: "Reportes", icon: BarChart3 },
  { to: "/usuarios", label: "Usuarios", icon: UserCog },
  { to: "/configuracion", label: "Configuración", icon: Settings },
];

const TITLES: Record<string, string> = Object.fromEntries(NAV.map((n) => [n.to, n.label]));

export default function AppLayout() {
  const { user, logout } = useAuth();
  const loc = useLocation();
  const [dark, setDark] = useState(() => document.documentElement.classList.contains("dark"));
  const [open, setOpen] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
  }, [dark]);

  const initials = (user?.full_name || "U")
    .split(" ")
    .slice(0, 2)
    .map((s) => s[0])
    .join("")
    .toUpperCase();

  return (
    <div className="h-full bg-slate-50 text-slate-800 dark:bg-slate-950 dark:text-slate-100 flex overflow-hidden">
      <aside
        className={`${open ? "fixed inset-y-0 left-0 z-30" : "hidden"} md:flex w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 flex-col justify-between shrink-0`}
      >
        <div>
          <div className="p-5 flex items-center space-x-3 border-b border-slate-100 dark:border-slate-800/60">
            <div className="w-9 h-9 bg-brand-500 rounded-xl flex items-center justify-center text-white shadow-md shadow-brand-500/20">
              <ShoppingCart className="w-5 h-5" />
            </div>
            <span className="text-xl font-bold tracking-tight">
              Comercio<span className="text-brand-500">Pro</span>
            </span>
          </div>
          <nav className="p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
            {NAV.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-colors ${
                      isActive
                        ? "text-white bg-brand-500 shadow-sm"
                        : "text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800/60"
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
        <div className="p-4 border-t border-slate-100 dark:border-slate-800/60 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-full bg-indigo-100 dark:bg-indigo-950 text-indigo-600 font-semibold flex items-center justify-center text-sm">
              {initials}
            </div>
            <div>
              <p className="text-sm font-semibold leading-none">{user?.full_name}</p>
              <p className="text-xs text-slate-500 mt-0.5">{user?.roles[0] || "Usuario"}</p>
            </div>
          </div>
          <button onClick={logout} className="text-slate-400 hover:text-slate-600" title="Cerrar sesión">
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col h-full overflow-hidden">
        <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 px-6 flex items-center justify-between shrink-0">
          <div className="flex items-center space-x-4">
            <button className="md:hidden" onClick={() => setOpen((v) => !v)}>
              <Menu className="w-6 h-6" />
            </button>
            <h1 className="text-xl font-bold">{TITLES[loc.pathname] || "ComercioPro"}</h1>
          </div>
          <button
            onClick={() => setDark((d) => !d)}
            className="p-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-500"
          >
            {dark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
        </header>
        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
