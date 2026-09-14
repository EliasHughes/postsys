import { useEffect, useState } from "react";
import { api, fmt } from "../../services/api";

const TABS = [
  ["diario", "Libro Diario"],
  ["catalogo", "Catálogo"],
  ["comprobacion", "Comprobación"],
  ["resultados", "Resultados"],
  ["general", "Balance General"],
] as const;

export default function AccountingPage() {
  const [tab, setTab] = useState("diario");
  const [journal, setJournal] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [trial, setTrial] = useState<any>(null);
  const [pl, setPl] = useState<any>(null);
  const [bs, setBs] = useState<any>(null);
  const [manual, setManual] = useState({ concept: "", debit_code: "1101", credit_code: "4101", amount: 0 });

  useEffect(() => {
    api<any[]>("/accounting/journal").then(setJournal);
    api<any[]>("/accounting/accounts").then(setAccounts);
    api("/accounting/trial-balance").then(setTrial);
    api("/accounting/income-statement").then(setPl);
    api("/accounting/balance-sheet").then(setBs);
  }, []);

  async function saveManual() {
    await api("/accounting/manual", { method: "POST", body: JSON.stringify(manual) });
    setJournal(await api("/accounting/journal"));
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="flex gap-2 overflow-x-auto">
          {TABS.map(([id, label]) => (
            <button key={id} onClick={() => setTab(id)} className={`px-4 py-2 rounded-full text-xs font-semibold ${tab === id ? "bg-brand-500 text-white" : "bg-slate-100"}`}>
              {label}
            </button>
          ))}
        </div>
      </div>

      {tab === "diario" && (
        <div className="space-y-3">
          <div className="bg-white dark:bg-slate-900 p-4 rounded-2xl border grid md:grid-cols-4 gap-2 text-xs">
            <input placeholder="Concepto" className="border rounded-xl px-3 py-2" onChange={(e) => setManual({ ...manual, concept: e.target.value })} />
            <input placeholder="Cuenta débito" className="border rounded-xl px-3 py-2" defaultValue="1101" onChange={(e) => setManual({ ...manual, debit_code: e.target.value })} />
            <input placeholder="Cuenta crédito" className="border rounded-xl px-3 py-2" defaultValue="4101" onChange={(e) => setManual({ ...manual, credit_code: e.target.value })} />
            <div className="flex gap-2">
              <input type="number" placeholder="Monto" className="border rounded-xl px-3 py-2 flex-1" onChange={(e) => setManual({ ...manual, amount: Number(e.target.value) })} />
              <button onClick={saveManual} className="px-3 bg-brand-500 text-white rounded-xl font-bold">OK</button>
            </div>
          </div>
          {journal.map((e) => (
            <div key={e.id} className="bg-white dark:bg-slate-900 p-5 rounded-2xl border">
              <div className="flex justify-between mb-2">
                <div>
                  <h5 className="font-bold text-sm">{e.concept}</h5>
                  <p className="text-[11px] text-slate-400 font-mono">{e.number} · {e.posted_at}</p>
                </div>
                <span className="text-[10px] font-bold uppercase px-2 py-1 bg-slate-100 rounded">{e.source}</span>
              </div>
              <table className="w-full text-xs font-mono">
                <tbody>
                  {e.lines.map((l: any, i: number) => (
                    <tr key={i}>
                      <td className="py-1 w-16 text-slate-400">{l.code}</td>
                      <td>{l.name}</td>
                      <td className="text-right">{l.debit ? fmt(l.debit) : ""}</td>
                      <td className="text-right">{l.credit ? fmt(l.credit) : ""}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}

      {tab === "catalogo" && (
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border">
          <table className="w-full text-xs">
            <thead><tr className="text-slate-400 border-b"><th className="text-left py-2">Código</th><th className="text-left">Nombre</th><th>Tipo</th><th className="text-right">Saldo</th></tr></thead>
            <tbody>
              {accounts.map((a) => (
                <tr key={a.id} className="border-t">
                  <td className="py-2 font-mono text-brand-500 font-bold">{a.code}</td>
                  <td>{a.name}</td>
                  <td>{a.type}</td>
                  <td className="text-right">{fmt(a.balance)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "comprobacion" && trial && (
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border text-sm space-y-2">
          <p>Total débitos (naturaleza): {fmt(trial.total_debit)}</p>
          <p>Total créditos (naturaleza): {fmt(trial.total_credit)}</p>
        </div>
      )}

      {tab === "resultados" && pl && (
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border space-y-2 text-sm">
          <div className="flex justify-between"><span>Ventas</span><span>{fmt(pl.sales)}</span></div>
          <div className="flex justify-between"><span>Costo de ventas</span><span>{fmt(pl.cogs)}</span></div>
          <div className="flex justify-between font-semibold"><span>Utilidad bruta</span><span>{fmt(pl.gross_profit)}</span></div>
          <div className="flex justify-between"><span>Gastos</span><span>{fmt(pl.expenses)}</span></div>
          <div className="flex justify-between font-bold text-lg border-t pt-2"><span>Utilidad neta</span><span>{fmt(pl.net_income)}</span></div>
        </div>
      )}

      {tab === "general" && bs && (
        <div className="grid md:grid-cols-3 gap-4">
          {[["Activos", bs.assets, bs.total_assets], ["Pasivos", bs.liabilities, bs.total_liabilities], ["Capital", bs.equity, bs.total_equity]].map(([title, rows, total]: any) => (
            <div key={title} className="bg-white dark:bg-slate-900 p-5 rounded-2xl border">
              <h4 className="font-bold mb-2">{title}</h4>
              {(rows || []).map((a: any) => (
                <div key={a.id} className="flex justify-between text-xs py-1"><span>{a.name}</span><span>{fmt(a.balance)}</span></div>
              ))}
              <div className="flex justify-between font-bold text-sm border-t pt-2 mt-2"><span>Total</span><span>{fmt(total)}</span></div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
