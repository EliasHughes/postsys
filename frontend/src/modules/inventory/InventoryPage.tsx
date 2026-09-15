import { useEffect, useState } from "react";
import { api, fmt } from "../../services/api";

export default function InventoryPage() {
  const [rows, setRows] = useState<any[]>([]);
  const [kardex, setKardex] = useState<any[] | null>(null);
  useEffect(() => {
    api<any[]>("/inventory").then(setRows);
  }, []);

  async function adjust(p: any) {
    const raw = prompt(`Nuevo movimiento para ${p.name} (cantidad +entrada / -salida)`, "0");
    if (!raw) return;
    const qty = Number(raw);
    const reason = prompt("Motivo", "Ajuste") || "Ajuste";
    await api("/inventory/adjust", {
      method: "POST",
      body: JSON.stringify({ product_id: p.product_id, qty, reason, movement_type: qty >= 0 ? "IN" : "OUT" }),
    });
    setRows(await api("/inventory"));
  }

  return (
    <div className="space-y-4">
      <h3 className="font-bold text-lg">Inventario / Kardex</h3>
      <div className="bg-white dark:bg-slate-900 rounded-2xl border overflow-hidden">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-slate-50 text-slate-400">
              <th className="py-3 px-4 text-left">Producto</th>
              <th className="text-right">Existencia</th>
              <th className="text-right">Costo prom.</th>
              <th className="text-right">Valor</th>
              <th></th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {rows.map((r) => (
              <tr key={r.product_id}>
                <td className="py-2 px-4 font-semibold">{r.name}</td>
                <td className="text-right">{r.qty_on_hand}</td>
                <td className="text-right">{fmt(r.avg_cost)}</td>
                <td className="text-right">{fmt(r.value)}</td>
                <td className="text-right pr-4 space-x-2">
                  <button className="text-brand-500 font-semibold" onClick={() => adjust(r)}>Ajustar</button>
                  <button className="text-slate-500" onClick={() => api<any[]>(`/inventory/kardex/${r.product_id}`).then(setKardex)}>Kardex</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {kardex && (
        <div className="bg-white dark:bg-slate-900 rounded-2xl border p-4">
          <div className="flex justify-between mb-2">
            <h4 className="font-bold text-sm">Kardex</h4>
            <button onClick={() => setKardex(null)} className="text-xs">Cerrar</button>
          </div>
          <table className="w-full text-xs">
            <tbody>
              {kardex.map((m) => (
                <tr key={m.id} className="border-t">
                  <td className="py-1">{m.moved_at}</td>
                  <td>{m.type}</td>
                  <td>{m.qty}</td>
                  <td>{m.qty_before} → {m.qty_after}</td>
                  <td>{m.source_doc}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
