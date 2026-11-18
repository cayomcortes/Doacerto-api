const API_URL = "http://localhost:8000";

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function clearToken() {
  localStorage.removeItem("token");
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "index.html";
  }
}

async function apiFetch(path, options = {}) {
  const headers = options.headers || {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (options.body && !(options.body instanceof URLSearchParams)) {
    headers["Content-Type"] = "application/json";
  }

  let res;
  try {
    res = await fetch(`${API_URL}${path}`, { ...options, headers });
  } catch (e) {
    throw new Error(
      "Não foi possível conectar à API. Verifique se o backend está rodando em " +
        API_URL
    );
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Erro na requisição");
  }
  if (res.status === 204) return null;
  return res.json();
}
