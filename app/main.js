document.getElementById("btnCache").addEventListener("click", async() => {
    await window.pywebview.api.cache();
});
