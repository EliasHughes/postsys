import { useEffect, useState } from "react";
import { api, fmt } from "../../services/api";

export default function SalesPage() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => {
    api<any[]>("/sales").then(setRows);
  }, []);
  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border p-6">
      <h3 className="font-bold mb-4">Historial de ventas</h3>
      <table className="w-full text-xs">
        <thead>
          <tr className="text-slate-400 border-b">
            <th className="py-2 text-left">Factura</th>
            <th className="text-left">Estado</th>
            <th className="text-left">Fecha</th>
            <th className="text-right">Total</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((s) => (
            <tr key={s.id}>
              <td className="py-2 font-semibold">{s.number}</td>
              <td>{s.status}</td>
              <td>{s.sold_at}</td>
              <td className="text-right font-bold text-brand-500">{fmt(s.total)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
