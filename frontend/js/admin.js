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
  return new Date(iso).toLocaleString("pt-BR");
}

function showTab(tab) {
  document.getElementById("tabAppointments").style.display = tab === "appointments" ? "block" : "none";
  document.getElementById("tabInventory").style.display = tab === "inventory" ? "block" : "none";
  document.querySelectorAll(".tabs a").forEach((a) => a.classList.remove("active"));
  event.target.classList.add("active");
}

async function loadAppointments() {
  const tbody = document.getElementById("apptTableBody");
  const filter = document.getElementById("statusFilter").value;
  const query = filter ? `?status_filter=${filter}` : "";
  try {
    const appts = await apiFetch(`/appointments${query}`);
    if (appts.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5">Nenhum agendamento encontrado.</td></tr>';
      return;
    }
    tbody.innerHTML = appts
      .map((a) => {
        const actions =
          a.status === "scheduled"
            ? `<button class="small-btn ok" onclick="updateStatus(${a.id}, 'completed')">Concluir</button>
               <button class="small-btn danger" onclick="updateStatus(${a.id}, 'canceled')">Cancelar</button>`
            : "-";
        return `<tr>
          <td>#${a.donor_id}</td>
          <td>${fmtDate(a.scheduled_datetime)}</td>
          <td>${a.location}</td>
          <td><span class="badge ${a.status}">${statusLabels[a.status]}</span></td>
          <td>${actions}</td>
        </tr>`;
      })
      .join("");
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5">${e.message}</td></tr>`;
  }
}

async function updateStatus(id, status) {
  try {
    await apiFetch(`/appointments/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    });
    loadAppointments();
    loadInventory();
  } catch (e) {
    alert(e.message);
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
          <td>
            <input type="number" min="0" value="${i.units_available}" id="units_${i.blood_type}" style="width:80px" />
          </td>
          <td>${i.min_threshold}</td>
          <td><span class="badge ${low ? "low" : "ok"}">${low ? "Estoque baixo" : "Normal"}</span></td>
          <td><button class="small-btn ok" onclick="saveInventory('${i.blood_type}')">Salvar</button></td>
        </tr>`;
      })
      .join("");
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="5">${e.message}</td></tr>`;
  }
}

async function saveInventory(bloodType) {
  const value = parseInt(document.getElementById(`units_${bloodType}`).value, 10);
  try {
    await apiFetch(`/inventory/${encodeURIComponent(bloodType)}`, {
      method: "PATCH",
      body: JSON.stringify({ units_available: value }),
    });
    loadInventory();
  } catch (e) {
    alert(e.message);
  }
}

loadAppointments();
loadInventory();
