import { useEffect, useState } from "react";
import { api, fmt } from "../../services/api";

export default function CustomersPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [name, setName] = useState("");
  const load = () => api<any[]>("/customers").then(setRows);
  useEffect(() => { load(); }, []);
  return (
    <div className="space-y-4">
      <h3 className="font-bold text-lg">Clientes</h3>
      <div className="flex gap-2">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nombre" className="border rounded-xl px-3 py-2 text-sm" />
        <button
          className="px-4 py-2 bg-brand-500 text-white text-xs font-bold rounded-xl"
          onClick={async () => { await api("/customers", { method: "POST", body: JSON.stringify({ name }) }); setName(""); load(); }}
        >Agregar</button>
      </div>
      <div className="bg-white dark:bg-slate-900 rounded-2xl border p-4">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-slate-400">
              <th className="text-left py-2">Nombre</th>
              <th>Documento</th>
              <th className="text-right">Límite</th>
              <th className="text-right">Balance</th>
              <th className="text-right">Puntos</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.id} className="border-t">
                <td className="py-2 font-semibold">{c.name}</td>
                <td>{c.document}</td>
                <td className="text-right">{fmt(c.credit_limit)}</td>
                <td className="text-right">{fmt(c.balance)}</td>
                <td className="text-right">{c.loyalty_points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
