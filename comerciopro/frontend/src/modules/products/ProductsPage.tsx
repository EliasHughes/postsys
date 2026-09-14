import { useEffect, useState } from "react";
import { api, fmt } from "../../services/api";

export default function ProductsPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ sku: "", name: "", price: 0, cost: 0 });

  const load = () => api<any[]>("/products").then(setRows);
  useEffect(() => {
    load();
  }, []);

  async function save() {
    await api("/products", { method: "POST", body: JSON.stringify(form) });
    setOpen(false);
    load();
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h3 className="font-bold text-lg">Gestión de productos</h3>
        <button onClick={() => setOpen(true)} className="px-4 py-2 bg-brand-500 text-white text-xs font-bold rounded-xl">
          Nuevo producto
        </button>
      </div>
      <div className="bg-white dark:bg-slate-900 rounded-2xl border overflow-hidden">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-slate-50 dark:bg-slate-800 text-slate-400">
              <th className="py-3 px-4 text-left">Producto</th>
              <th className="text-left">SKU</th>
              <th className="text-left">Categoría</th>
              <th className="text-right">Precio</th>
              <th className="text-right">Stock</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {rows.map((p) => (
              <tr key={p.id}>
                <td className="py-3 px-4 font-bold">{p.name}</td>
                <td>{p.sku}</td>
                <td>{p.category}</td>
                <td className="text-right text-brand-500 font-semibold">{fmt(p.price)}</td>
                <td className={`text-right font-bold ${p.stock < 10 ? "text-rose-500" : ""}`}>{p.stock}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {open && (
        <div className="fixed inset-0 bg-slate-900/60 grid place-items-center p-4">
          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl w-full max-w-md space-y-3">
            <h4 className="font-bold">Nuevo producto</h4>
            {["sku", "name"].map((k) => (
              <input
                key={k}
                placeholder={k}
                className="w-full border rounded-xl px-3 py-2 text-sm"
                onChange={(e) => setForm({ ...form, [k]: e.target.value })}
              />
            ))}
            <input type="number" placeholder="precio" className="w-full border rounded-xl px-3 py-2 text-sm" onChange={(e) => setForm({ ...form, price: Number(e.target.value) })} />
            <input type="number" placeholder="costo" className="w-full border rounded-xl px-3 py-2 text-sm" onChange={(e) => setForm({ ...form, cost: Number(e.target.value) })} />
            <div className="flex gap-2">
              <button onClick={() => setOpen(false)} className="flex-1 border rounded-xl py-2 text-sm">Cancelar</button>
              <button onClick={save} className="flex-1 bg-brand-500 text-white rounded-xl py-2 text-sm font-bold">Guardar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
