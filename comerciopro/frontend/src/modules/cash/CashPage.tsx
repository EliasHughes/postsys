import { useEffect, useState } from "react";
import { api, fmt } from "../../services/api";

export default function CashPage() {
  const [registers, setRegisters] = useState<any[]>([]);
  const [current, setCurrent] = useState<any>(null);
  const [floatAmt, setFloatAmt] = useState(1000);
  const [counted, setCounted] = useState(0);
  const [result, setResult] = useState<any>(null);

  const load = async () => {
    setRegisters(await api("/cash/registers"));
    setCurrent(await api("/cash/sessions/current"));
  };
  useEffect(() => { load(); }, []);

  async function openCash() {
    if (!registers[0]) return;
    await api("/cash/open", { method: "POST", body: JSON.stringify({ register_id: registers[0].id, opening_float: floatAmt }) });
    load();
  }
  async function closeCash() {
    if (!current) return;
    const r = await api("/cash/close", { method: "POST", body: JSON.stringify({ session_id: current.id, counted_cash: counted }) });
    setResult(r);
    load();
  }

  return (
    <div className="max-w-md bg-white dark:bg-slate-900 p-6 rounded-2xl border space-y-4">
      <h3 className="font-bold text-lg">Control de caja / cuadre</h3>
      <div className="flex justify-between text-sm">
        <span className="text-slate-400">Estado actual</span>
        <span className={current ? "text-emerald-500 font-bold" : "text-rose-500 font-bold"}>
          {current ? "Abierta" : "Cerrada"}
        </span>
      </div>
      {!current ? (
        <>
          <label className="text-xs text-slate-400">Fondo inicial
            <input type="number" value={floatAmt} onChange={(e) => setFloatAmt(Number(e.target.value))} className="mt-1 w-full border rounded-xl px-3 py-2" />
          </label>
          <button onClick={openCash} className="w-full py-3 bg-brand-500 text-white font-bold rounded-xl">Abrir caja</button>
        </>
      ) : (
        <>
          <p className="text-xs text-slate-500">Fondo inicial: {fmt(current.opening_float)}</p>
          <label className="text-xs text-slate-400">Efectivo contado
            <input type="number" value={counted} onChange={(e) => setCounted(Number(e.target.value))} className="mt-1 w-full border rounded-xl px-3 py-2" />
          </label>
          <button onClick={closeCash} className="w-full py-3 bg-rose-500 text-white font-bold rounded-xl">Cerrar y cuadrar</button>
        </>
      )}
      {result && (
        <div className="text-xs bg-slate-50 dark:bg-slate-800 p-3 rounded-xl space-y-1">
          <div>Esperado: {fmt(result.expected_cash)}</div>
          <div>Contado: {fmt(result.counted_cash)}</div>
          <div className="font-bold">Diferencia: {fmt(result.difference)}</div>
        </div>
      )}
    </div>
  );
}
