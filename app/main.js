// --- Wait until pywebview API is available before binding events ---
function waitForAPI(callback) {
    if (window.pywebview && window.pywebview.api) {
        callback();
    } else {
        setTimeout(() => waitForAPI(callback), 100);
    }
}

waitForAPI(() => {
    // Safe DOM binding
    const bindSafe = () => {
        const $ = id => document.getElementById(id);

        const btnCache = $("btnCache");
        const btnLogs = $("btnLogs");
        const btnDownload = $("btnDownload"); // fixed typo (was btnDonwload)
        const btnScan = $("btnScan");

        if (btnCache) {
            btnCache.addEventListener("click", async () => {
            console.log("Clear cache clicked");
                try {
                    await window.pywebview.api.clearPath("cache");
                } catch (e) {
                    console.error("clearPath(cache) failed:", e);
                }
            });
        }

        if (btnLogs) {
            btnLogs.addEventListener("click", async () => {
                console.log("Clear logs clicked");
                try {
                    await window.pywebview.api.clearPath("logs");
                } catch (e) {
                    console.error("clearPath(logs) failed:", e);
                }
            });
        }

        if (btnDownload) {
            btnDownload.addEventListener("click", async () => {
                console.log("Clear downloads clicked");
                    try {
                        await window.pywebview.api.clearPath("downloads");
                    } catch (e) {
                        console.error("clearPath(downloads) failed:", e);
                    }
            });
        }

        if (btnScan) {
            btnScan.addEventListener("click", async () => {
            console.log("Antivirus scan clicked");
                try {
                    await window.pywebview.api.start_scan();
                } catch (e) {
                    console.error("start_scan failed:", e);
                }
            });
        }
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindSafe);
    } else {
        bindSafe();
    }
});

    // --- Vitals / progress update functions used by Python ---
function updateVitals(data) {
    const cpuEl = document.getElementById("cpu");
    const ramEl = document.getElementById("ram");
    const diskEl = document.getElementById("disk");
    const tempEl = document.getElementById("temp");

    try {
        if (cpuEl) cpuEl.textContent = (data.cpu || 0).toFixed(1);
        if (ramEl) ramEl.textContent = (data.memory || 0).toFixed(1);
        if (diskEl) diskEl.textContent = (data.disk || 0).toFixed(1);
        if (tempEl)
        tempEl.textContent =
            data.temperature === "N/A" || data.temperature == null
            ? "N/A"
            : Number(data.temperature).toFixed(1);
    } catch (e) {
        console.warn("updateVitals error:", e);
    }
}



let total = 0;
let current = 0;

function startScanUI() {
    total = 0;
    current = 0;
    const statusEl = document.getElementById("status");
    const bar = document.getElementById("progress-bar");

    if (!statusEl || !bar) {
        console.warn("UI not ready yet");
        return;
    }

    statusEl.textContent = "Scanning...";
    bar.style.width = "0%";
}

function updateTotal(t) {
    total = parseInt(t) || 0;
}

function updateProgress(count, filePath) {
    current = parseInt(count) || current;
    const statusEl = document.getElementById("status");
    const bar = document.getElementById("progress-bar");
    if (!bar || !statusEl) return;

    if (total > 0) {
        const percent = Math.min(100, (current / total) * 100);
        bar.style.width = percent.toFixed(1) + "%";
        statusEl.textContent = `Scanning ${filePath} (${percent.toFixed(1)}%)`;
    } else {
        statusEl.textContent = `Scanning ${filePath}`;
    }
}

function finishScanUI() {
    const statusEl = document.getElementById("status");
    const bar = document.getElementById("progress-bar");
    if (bar) bar.style.width = "100%";
    if (statusEl) statusEl.textContent = "Scan complete!";
}