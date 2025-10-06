document.getElementById("btnCache").addEventListener("click", async() => {
    await window.pywebview.api.clearPath("cache");
});

document.getElementById("btnLogs").addEventListener("click", async() => {
    await window.pywebview.api.clearPath("logs");
});
