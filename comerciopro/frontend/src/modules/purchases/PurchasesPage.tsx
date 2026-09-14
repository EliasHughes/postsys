import { useEffect, useState } from "react";
import { api, fmt } from "../../services/api";

export default function PurchasesPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [supplierId, setSupplierId] = useState<number | "">("");
  const [items, setItems] = useState([{ product_id: 0, qty: 1, unit_cost: 0 }]);

  const load = () => api<any[]>("/purchases").then(setRows);
  useEffect(() => {
    load();
    api<any[]>("/suppliers").then(setSuppliers);
    api<any[]>("/products").then(setProducts);
  }, []);

  async function create() {
    await api("/purchases", {
      method: "POST",
      body: JSON.stringify({
        supplier_id: supplierId,
        items: items.filter((i) => i.product_id),
      }),
    });
    setOpen(false);
    load();
  }

  async function receive(id: number) {
    await api(`/purchases/${id}/receive`, { method: "POST" });
    load();
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h3 className="font-bold text-lg">Órdenes de compra</h3>
        <button onClick={() => setOpen(true)} className="px-4 py-2 bg-brand-500 text-white text-xs font-bold rounded-xl">
          Nueva OC
        </button>
      </div>
      <div className="bg-white dark:bg-slate-900 rounded-2xl border p-4">
        <table className="w-full text-xs">
          <thead>
            <tr className="text-slate-400 border-b">
              <th className="text-left py-2">Número</th>
              <th>Estado</th>
              <th className="text-right">Total</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map((p) => (
              <tr key={p.id} className="border-t">
                <td className="py-2 font-semibold">{p.number}</td>
                <td>{p.status}</td>
                <td className="text-right">{fmt(p.total)}</td>
                <td className="text-right">
                  {p.status !== "RECEIVED" && (
                    <button className="text-brand-500 font-semibold" onClick={() => receive(p.id)}>
                      Recibir
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {open && (
        <div className="fixed inset-0 bg-slate-900/60 grid place-items-center p-4">
          <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl w-full max-w-lg space-y-3">
            <h4 className="font-bold">Nueva orden</h4>
            <select className="w-full border rounded-xl px-3 py-2 text-sm" onChange={(e) => setSupplierId(Number(e.target.value))}>
              <option value="">Proveedor</option>
              {suppliers.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            {items.map((it, idx) => (
              <div key={idx} className="grid grid-cols-3 gap-2">
                <select className="border rounded-xl px-2 py-2 text-xs" onChange={(e) => setItems((arr) => arr.map((x, i) => i === idx ? { ...x, product_id: Number(e.target.value) } : x))}>
                  <option value="0">Producto</option>
                  {products.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
                <input type="number" placeholder="qty" className="border rounded-xl px-2 text-xs" onChange={(e) => setItems((arr) => arr.map((x, i) => i === idx ? { ...x, qty: Number(e.target.value) } : x))} />
                <input type="number" placeholder="costo" className="border rounded-xl px-2 text-xs" onChange={(e) => setItems((arr) => arr.map((x, i) => i === idx ? { ...x, unit_cost: Number(e.target.value) } : x))} />
              </div>
            ))}
            <button className="text-xs text-brand-500" onClick={() => setItems((i) => [...i, { product_id: 0, qty: 1, unit_cost: 0 }])}>+ línea</button>
            <div className="flex gap-2">
              <button className="flex-1 border rounded-xl py-2" onClick={() => setOpen(false)}>Cancelar</button>
              <button className="flex-1 bg-brand-500 text-white rounded-xl py-2 font-bold" onClick={create}>Crear</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
