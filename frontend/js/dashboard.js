requireAuth();

const statusLabels = {
  scheduled: "Agendado",
  completed: "Concluído",
  canceled: "Cancelado",
};

function logout() {
  clearToken();
  window.location.href = "index.html";
}

function fmtDate(iso) {
  const d = new Date(iso);
  return d.toLocaleString("pt-BR");
}

async function loadProfile() {
  try {
    const me = await apiFetch("/auth/me");
    document.getElementById("profileInfo").innerHTML = `
      <strong>${me.full_name}</strong> — ${me.email}<br/>
      Tipo sanguíneo: <strong>${me.blood_type || "não informado"}</strong><br/>
      Última doação: ${me.last_donation_date || "nenhuma registrada ainda"}
    `;
  } catch (e) {
    document.getElementById("profileInfo").textContent = e.message;
  }
}

async function loadAppointments() {
  const tbody = document.getElementById("apptTableBody");
  try {
    const appts = await apiFetch("/appointments/me");
    if (appts.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4">Você ainda não tem agendamentos.</td></tr>';
      return;
    }
    tbody.innerHTML = appts
      .map(
        (a) => `
      <tr>
        <td>${fmtDate(a.scheduled_datetime)}</td>
        <td>${a.location}</td>
        <td><span class="badge ${a.status}">${statusLabels[a.status]}</span></td>
        <td>${a.notes || "-"}</td>
      </tr>`
      )
      .join("");
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4">${e.message}</td></tr>`;
  }
}

async function loadInventory() {
  const tbody = document.getElementById("inventoryTableBody");
  try {
    const items = await apiFetch("/inventory");
    tbody.innerHTML = items
      .map((i) => {
        const low = i.units_available < i.min_threshold;
        return `<tr>
          <td>${i.blood_type}</td>
          <td>${i.units_available}</td>
          <td><span class="badge ${low ? "low" : "ok"}">${low ? "Estoque baixo" : "Normal"}</span></td>
        </tr>`;
      })
      .join("");
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="3">${e.message}</td></tr>`;
  }
}

async function scheduleAppointment() {
  const dt = document.getElementById("apptDatetime").value;
  const location = document.getElementById("apptLocation").value.trim();
  const notes = document.getElementById("apptNotes").value.trim();
  const errEl = document.getElementById("apptError");
  const okEl = document.getElementById("apptSuccess");
  errEl.textContent = "";
  okEl.textContent = "";

  if (!dt || !location) {
    errEl.textContent = "Informe data/horário e local.";
    return;
  }

  try {
    await apiFetch("/appointments", {
      method: "POST",
      body: JSON.stringify({
        scheduled_datetime: new Date(dt).toISOString(),
        location,
        notes,
      }),
    });
    okEl.textContent = "Agendamento realizado com sucesso!";
    document.getElementById("apptDatetime").value = "";
    document.getElementById("apptLocation").value = "";
    document.getElementById("apptNotes").value = "";
    loadAppointments();
  } catch (e) {
    errEl.textContent = e.message;
  }
}

loadProfile();
loadAppointments();
loadInventory();
