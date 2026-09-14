import { api } from "../../services/api";

const ITEMS = [
  { key: "ventas", title: "Reporte de Ventas", desc: "Facturas con subtotal, ITBIS y total.", path: "/reports/sales.csv" },
];

export default function ReportsPage() {
  async function download(path: string) {
    const csv = await api<string>(path);
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "reporte.csv";
    a.click();
  }
  return (
    <div className="space-y-4">
      <p className="text-xs text-slate-500">Los reportes salen de datos reales. PDF/Excel se conectan al mismo endpoint.</p>
      <div className="grid md:grid-cols-2 gap-4">
        {ITEMS.map((r) => (
          <div key={r.key} className="bg-white dark:bg-slate-900 p-6 rounded-2xl border space-y-3">
            <h4 className="font-bold">{r.title}</h4>
            <p className="text-xs text-slate-500">{r.desc}</p>
            <button onClick={() => download(r.path)} className="px-3 py-1.5 bg-slate-100 rounded-lg text-xs font-semibold">CSV</button>
          </div>
        ))}
      </div>
    </div>
  );
}
