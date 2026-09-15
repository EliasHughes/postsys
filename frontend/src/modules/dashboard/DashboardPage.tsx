import { useEffect, useState } from "react";
import { api, fmt } from "../../services/api";
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

type Dash = {
  sales_today: number;
  sales_today_count: number;
  sales_week: number;
  sales_month: number;
  sales_year: number;
  avg_ticket: number;
  inventory_value: number;
  product_count: number;
  cash_open: boolean;
  customers: number;
  suppliers: number;
  ar: number;
  ap: number;
  sales_7d: { date: string; total: number }[];
  top_products: { name: string; total: number }[];
  audit: { module: string; action: string; message: string; created_at: string }[];
};

function Card({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800 shadow-sm">
      <p className="text-xs font-semibold tracking-wider text-slate-400 uppercase">{label}</p>
      <h3 className="text-2xl font-bold mt-1">{value}</h3>
      {sub && <p className="text-xs text-slate-500 mt-1">{sub}</p>}
    </div>
  );
}

export default function DashboardPage() {
  const [d, setD] = useState<Dash | null>(null);
  useEffect(() => {
    api<Dash>("/dashboard").then(setD).catch(console.error);
  }, []);
  if (!d) return <p className="text-slate-400 text-sm">Cargando dashboard…</p>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card label="Ventas Hoy" value={fmt(d.sales_today)} sub={`${d.sales_today_count} transacciones`} />
        <Card label="Esta Semana" value={fmt(d.sales_week)} />
        <Card label="Este Mes" value={fmt(d.sales_month)} />
        <Card label="Este Año" value={fmt(d.sales_year)} />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card label="Ticket Promedio" value={fmt(d.avg_ticket)} />
        <Card label="Valor Inventario" value={fmt(d.inventory_value)} sub={`${d.product_count} productos`} />
        <Card label="Estado de Caja" value={d.cash_open ? "Abierta" : "Cerrada"} />
        <Card label="Cuentas x Cobrar" value={fmt(d.ar)} />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800">
          <h4 className="font-bold mb-4">Ventas últimos 7 días</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={d.sales_7d}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="total" stroke="#f9572a" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800">
          <h4 className="font-bold mb-4">Más vendidos</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={d.top_products} layout="vertical">
                <XAxis type="number" hide />
                <YAxis type="category" dataKey="name" width={110} tick={{ fontSize: 10 }} />
                <Tooltip />
                <Bar dataKey="total" fill="#f9572a" radius={6} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card label="Clientes" value={String(d.customers)} />
        <Card label="Proveedores" value={String(d.suppliers)} />
        <Card label="CxC" value={fmt(d.ar)} />
        <Card label="CxP" value={fmt(d.ap)} />
      </div>
      <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800">
        <h4 className="font-bold mb-3">Actividad reciente</h4>
        <table className="w-full text-xs">
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {d.audit.map((a, i) => (
              <tr key={i}>
                <td className="py-2 font-semibold uppercase text-slate-400 w-28">{a.module}</td>
                <td className="py-2">{a.message || a.action}</td>
                <td className="py-2 text-right text-slate-400">{a.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
