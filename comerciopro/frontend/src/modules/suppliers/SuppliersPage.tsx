import { useEffect, useState } from "react";
import { api, fmt } from "../../services/api";

export default function SuppliersPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [name, setName] = useState("");
  const load = () => api<any[]>("/suppliers").then(setRows);
  useEffect(() => { load(); }, []);
  return (
    <div className="space-y-4">
      <h3 className="font-bold text-lg">Proveedores</h3>
      <div className="flex gap-2">
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Nombre" className="border rounded-xl px-3 py-2 text-sm" />
        <button
          className="px-4 py-2 bg-brand-500 text-white text-xs font-bold rounded-xl"
          onClick={async () => { await api("/suppliers", { method: "POST", body: JSON.stringify({ name }) }); setName(""); load(); }}
        >Agregar</button>
      </div>
      <div className="bg-white dark:bg-slate-900 rounded-2xl border p-4">
        <table className="w-full text-xs">
          <tbody>
            {rows.map((s) => (
              <tr key={s.id} className="border-b">
                <td className="py-2 font-semibold">{s.name}</td>
                <td>{s.rnc}</td>
                <td className="text-right">{fmt(s.balance)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
