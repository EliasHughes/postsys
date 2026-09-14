import { useEffect, useMemo, useState } from "react";
import { api, fmt } from "../../services/api";

type Product = {
  id: number;
  name: string;
  sku: string;
  barcode: string | null;
  price: number;
  stock: number;
  category: string | null;
};
type Customer = { id: number; name: string; is_final_consumer: boolean };
type CartItem = { product: Product; qty: number; discount: number };
type Session = { id: number; status: string } | null;

export default function PosPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [q, setQ] = useState("");
  const [cat, setCat] = useState("Todos");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [discount, setDiscount] = useState(0);
  const [customerId, setCustomerId] = useState<number | "">("");
  const [session, setSession] = useState<Session>(null);
  const [checkout, setCheckout] = useState(false);
  const [payments, setPayments] = useState([{ method: "CASH", amount: 0 }]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api<Product[]>("/products").then(setProducts);
    api<Customer[]>("/customers").then((rows) => {
      setCustomers(rows);
      const cf = rows.find((c) => c.is_final_consumer);
      if (cf) setCustomerId(cf.id);
    });
    api<Session>("/cash/sessions/current").then(setSession);
  }, []);

  const categories = useMemo(
    () => ["Todos", ...Array.from(new Set(products.map((p) => p.category).filter(Boolean) as string[]))],
    [products]
  );

  const visible = products.filter((p) => {
    const okCat = cat === "Todos" || p.category === cat;
    const okQ =
      !q ||
      p.name.toLowerCase().includes(q.toLowerCase()) ||
      (p.sku || "").includes(q) ||
      (p.barcode || "").includes(q);
    return okCat && okQ;
  });

  function add(p: Product) {
    if ((p.stock || 0) <= 0) return setMsg("Sin stock");
    setCart((c) => {
      const i = c.find((x) => x.product.id === p.id);
      if (i) return c.map((x) => (x.product.id === p.id ? { ...x, qty: x.qty + 1 } : x));
      return [...c, { product: p, qty: 1, discount: 0 }];
    });
  }

  const subtotal = cart.reduce((a, i) => a + i.product.price * i.qty - i.discount, 0);
  const tax = Math.max(0, subtotal - discount) * 0.18;
  const total = Math.max(0, subtotal - discount) + tax;

  async function complete() {
    try {
      const sale = await api<any>("/sales", {
        method: "POST",
        body: JSON.stringify({
          customer_id: customerId || null,
          cash_session_id: session?.id || null,
          discount_global: discount,
          items: cart.map((i) => ({
            product_id: i.product.id,
            qty: i.qty,
            unit_price: i.product.price,
            discount: i.discount,
          })),
          payments: payments.filter((p) => p.amount > 0),
        }),
      });
      setMsg(`Venta ${sale.number} registrada · ${fmt(sale.total)}`);
      setCart([]);
      setDiscount(0);
      setCheckout(false);
      setProducts(await api<Product[]>("/products"));
    } catch (e: any) {
      setMsg(e.message);
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
      <div className="lg:col-span-8 space-y-4">
        {!session && (
          <div className="text-xs bg-amber-50 text-amber-700 px-3 py-2 rounded-xl">
            No hay caja abierta. La venta se registra, pero no se asocia a una sesión.
          </div>
        )}
        {msg && <div className="text-xs bg-slate-900 text-white px-3 py-2 rounded-xl">{msg}</div>}
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Escanear código o buscar producto…"
          className="w-full px-4 py-3 bg-white dark:bg-slate-900 border border-brand-500 rounded-xl text-sm"
        />
        <div className="flex space-x-2 overflow-x-auto">
          {categories.map((c) => (
            <button
              key={c}
              onClick={() => setCat(c)}
              className={`px-4 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap ${
                cat === c ? "bg-brand-500 text-white" : "bg-white dark:bg-slate-900 border"
              }`}
            >
              {c}
            </button>
          ))}
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 max-h-[calc(100vh-270px)] overflow-y-auto">
          {visible.map((p) => (
            <button
              key={p.id}
              onClick={() => add(p)}
              className="bg-white dark:bg-slate-900 p-3.5 rounded-2xl border text-left h-32 flex flex-col justify-between hover:border-brand-500"
            >
              <h5 className="font-bold text-xs line-clamp-2">{p.name}</h5>
              <div>
                <div className="text-brand-500 font-extrabold text-sm">{fmt(p.price)}</div>
                <div className="text-[10px] text-slate-400">Stock: {p.stock}</div>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="lg:col-span-4 bg-white dark:bg-slate-900 rounded-2xl border flex flex-col h-[calc(100vh-140px)]">
        <div className="p-4 border-b flex justify-between">
          <h3 className="font-bold">Carrito ({cart.reduce((a, i) => a + i.qty, 0)})</h3>
          {cart.length > 0 && (
            <button className="text-xs text-rose-500 font-semibold" onClick={() => setCart([])}>
              Vaciar
            </button>
          )}
        </div>
        <div className="p-4">
          <select
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value ? Number(e.target.value) : "")}
            className="w-full text-xs border rounded-xl px-3 py-2 bg-slate-50 dark:bg-slate-800"
          >
            <option value="">Cliente…</option>
            {customers.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {cart.length === 0 && <p className="text-xs text-slate-400 text-center py-10">Agrega productos para comenzar.</p>}
          {cart.map((i) => (
            <div key={i.product.id} className="flex items-center justify-between p-2.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl text-xs">
              <div>
                <p className="font-bold">{i.product.name}</p>
                <p className="text-slate-400">{fmt(i.product.price)}</p>
              </div>
              <div className="flex items-center space-x-1">
                <button
                  className="w-6 h-6 rounded bg-slate-200"
                  onClick={() =>
                    setCart((c) =>
                      c.map((x) => (x.product.id === i.product.id ? { ...x, qty: x.qty - 1 } : x)).filter((x) => x.qty > 0)
                    )
                  }
                >
                  -
                </button>
                <span className="w-6 text-center font-bold">{i.qty}</span>
                <button
                  className="w-6 h-6 rounded bg-slate-200"
                  onClick={() => setCart((c) => c.map((x) => (x.product.id === i.product.id ? { ...x, qty: x.qty + 1 } : x)))}
                >
                  +
                </button>
              </div>
            </div>
          ))}
        </div>
        <div className="p-4 border-t space-y-2 text-xs">
          <div className="flex justify-between">
            <span>Subtotal</span>
            <span>{fmt(subtotal)}</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Descuento</span>
            <input
              type="number"
              value={discount}
              onChange={(e) => setDiscount(Number(e.target.value) || 0)}
              className="w-20 px-2 py-0.5 border rounded text-right"
            />
          </div>
          <div className="flex justify-between">
            <span>ITBIS (18%)</span>
            <span>{fmt(tax)}</span>
          </div>
          <div className="flex justify-between items-baseline pt-2 border-t">
            <span className="font-bold uppercase">Total</span>
            <span className="text-2xl font-extrabold text-brand-500">{fmt(total)}</span>
          </div>
          <button
            onClick={() => {
              setPayments([{ method: "CASH", amount: Number(total.toFixed(2)) }]);
              setCheckout(true);
            }}
            className="w-full py-2.5 bg-emerald-500 text-white font-bold rounded-xl"
          >
            Cobrar
          </button>
        </div>
      </div>

      {checkout && (
        <div className="fixed inset-0 bg-slate-900/60 z-50 grid place-items-center p-4">
          <div className="bg-white dark:bg-slate-900 rounded-3xl w-full max-w-md p-6 space-y-4">
            <div className="flex justify-between">
              <h3 className="font-bold text-lg">Procesar pago</h3>
              <button onClick={() => setCheckout(false)}>✕</button>
            </div>
            <div className="text-3xl font-extrabold text-brand-500">{fmt(total)}</div>
            {payments.map((p, idx) => (
              <div key={idx} className="grid grid-cols-2 gap-2">
                <select
                  value={p.method}
                  onChange={(e) =>
                    setPayments((arr) => arr.map((x, i) => (i === idx ? { ...x, method: e.target.value } : x)))
                  }
                  className="px-3 py-2 rounded-xl border text-sm"
                >
                  {["CASH", "CARD", "TRANSFER", "CHECK", "CREDIT", "OTHER"].map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  value={p.amount}
                  onChange={(e) =>
                    setPayments((arr) => arr.map((x, i) => (i === idx ? { ...x, amount: Number(e.target.value) } : x)))
                  }
                  className="px-3 py-2 rounded-xl border text-sm"
                />
              </div>
            ))}
            <button
              className="text-xs text-brand-500 font-semibold"
              onClick={() => setPayments((p) => [...p, { method: "CARD", amount: 0 }])}
            >
              + Pago mixto
            </button>
            <button onClick={complete} className="w-full py-3 bg-emerald-500 text-white font-bold rounded-xl">
              Completar venta
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
