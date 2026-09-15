const API = "/api/v1";

function token(): string | null {
  return localStorage.getItem("cp_access");
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    ...(init.headers as Record<string, string>),
  };
  const t = token();
  if (t) headers.Authorization = `Bearer ${t}`;
  if (init.body && !(init.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const res = await fetch(`${API}${path}`, { ...init, headers });
  if (res.status === 401) {
    localStorage.removeItem("cp_access");
    if (!path.startsWith("/auth")) window.location.href = "/login";
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = j.detail || JSON.stringify(j);
    } catch {
      /* ignore */
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  if (res.headers.get("content-type")?.includes("text/csv")) {
    return (await res.text()) as T;
  }
  return res.json();
}

export async function login(username: string, password: string) {
  const body = new URLSearchParams({ username, password });
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new Error("Credenciales inválidas");
  const data = await res.json();
  localStorage.setItem("cp_access", data.access_token);
  localStorage.setItem("cp_refresh", data.refresh_token);
  return data;
}

export const fmt = (n: number) =>
  `RD$ ${Number(n || 0).toLocaleString("es-DO", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
