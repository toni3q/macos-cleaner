document.getElementById("btnCache").addEventListener("click", async() => {
    await window.pywebview.api.cache();
});

document.getElementById("btnLogs").addEventListener("click", async() => {
    await window.pywebview.api.logs();
});
