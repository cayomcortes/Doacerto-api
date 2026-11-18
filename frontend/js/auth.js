function toggleForms() {
  const login = document.getElementById("loginCard");
  const register = document.getElementById("registerCard");
  login.style.display = login.style.display === "none" ? "block" : "none";
  register.style.display = register.style.display === "none" ? "block" : "none";
}

async function doLogin() {
  const email = document.getElementById("loginEmail").value.trim();
  const password = document.getElementById("loginPassword").value;
  const errEl = document.getElementById("loginError");
  errEl.textContent = "";

  if (!email || !password) {
    errEl.textContent = "Preencha e-mail e senha.";
    return;
  }

  try {
    const body = new URLSearchParams();
    body.append("username", email);
    body.append("password", password);

    const data = await apiFetch("/auth/login", { method: "POST", body });
    setToken(data.access_token);

    const me = await apiFetch("/auth/me");
    if (me.role === "admin") {
      window.location.href = "admin.html";
    } else {
      window.location.href = "dashboard.html";
    }
  } catch (e) {
    errEl.textContent = e.message;
  }
}

async function doRegister() {
  const full_name = document.getElementById("regName").value.trim();
  const email = document.getElementById("regEmail").value.trim();
  const password = document.getElementById("regPassword").value;
  const phone = document.getElementById("regPhone").value.trim();
  const blood_type = document.getElementById("regBloodType").value || null;

  const errEl = document.getElementById("registerError");
  const okEl = document.getElementById("registerSuccess");
  errEl.textContent = "";
  okEl.textContent = "";

  if (!full_name || !email || !password) {
    errEl.textContent = "Nome, e-mail e senha são obrigatórios.";
    return;
  }

  try {
    await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ full_name, email, password, phone, blood_type }),
    });
    okEl.textContent = "Cadastro realizado! Faça login para continuar.";
    setTimeout(toggleForms, 1200);
  } catch (e) {
    errEl.textContent = e.message;
  }
}
