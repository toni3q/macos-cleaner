document.getElementById("btnCache").addEventListener("click", async() => {
    await window.pywebview.api.clearPath("cache");
});

document.getElementById("btnLogs").addEventListener("click", async() => {
    await window.pywebview.api.clearPath("logs");
});

document.getElementById("btnDonwload").addEventListener("click", async() => {
    await window.pywebview.api.clearPath("downloads");
});

function updateVitals(data) {
    document.getElementById("cpu").textContent = data.cpu.toFixed(1);
    document.getElementById("ram").textContent = data.memory.toFixed(1);
    document.getElementById("disk").textContent = data.disk.toFixed(1);
    document.getElementById("temp").textContent = data.temperature === "N/A" ? "N/A" : data.temperature.toFixed(1);
}