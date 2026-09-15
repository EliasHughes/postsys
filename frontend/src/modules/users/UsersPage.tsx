import { useEffect, useState } from "react";
import { api } from "../../services/api";

export default function UsersPage() {
  const [users, setUsers] = useState<any[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [audit, setAudit] = useState<any[]>([]);
  const [form, setForm] = useState({ username: "", full_name: "", password: "Cambio123!", role_slug: "cashier" });

  useEffect(() => {
    api<any[]>("/users").then(setUsers).catch(() => setUsers([]));
    api<any[]>("/roles").then(setRoles);
    api<any[]>("/audit").then(setAudit);
  }, []);

  return (
    <div className="grid lg:grid-cols-2 gap-6">
      <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border space-y-3">
        <h3 className="font-bold">Usuarios y roles</h3>
        <div className="grid grid-cols-2 gap-2 text-xs">
          <input placeholder="usuario" className="border rounded-xl px-3 py-2" onChange={(e) => setForm({ ...form, username: e.target.value })} />
          <input placeholder="nombre" className="border rounded-xl px-3 py-2" onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
          <select className="border rounded-xl px-3 py-2" onChange={(e) => setForm({ ...form, role_slug: e.target.value })}>
            {roles.map((r) => <option key={r.id} value={r.slug}>{r.name}</option>)}
          </select>
          <button
            className="bg-brand-500 text-white rounded-xl font-bold"
            onClick={async () => { await api("/users", { method: "POST", body: JSON.stringify(form) }); setUsers(await api("/users")); }}
          >Crear</button>
        </div>
        <table className="w-full text-xs">
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-t">
                <td className="py-2 font-semibold">{u.full_name}</td>
                <td>{u.username}</td>
                <td>{(u.roles || []).join(", ")}</td>
                <td>{u.is_active ? "Activo" : "Inactivo"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border">
        <h3 className="font-bold mb-3">Auditoría</h3>
        <div className="max-h-[480px] overflow-y-auto text-xs space-y-2">
          {audit.map((a) => (
            <div key={a.id} className="border-b pb-2">
              <div className="font-semibold">{a.module}.{a.action} · {a.entity_id}</div>
              <div className="text-slate-400">{a.created_at} · {a.ip}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
