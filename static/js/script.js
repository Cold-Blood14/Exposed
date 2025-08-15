// static/js/script.js
const getInfoBtn = document.getElementById('getInfoBtn');
const loadingContainer = document.getElementById('loadingContainer');
const loadingBar = document.getElementById('loadingBar');
const loadingPercent = document.getElementById('loadingPercent');
const resultContainer = document.getElementById('resultContainer');
const errorContainer = document.getElementById('error');
const mapBtn = document.getElementById('mapBtn');

getInfoBtn.addEventListener('click', async () => {
    // Reset UI
    getInfoBtn.disabled = true;
    loadingContainer.style.display = 'flex';
    loadingBar.style.width = '0%';
    loadingPercent.textContent = '0% Getting your IP...';
    resultContainer.style.display = 'none';
    errorContainer.style.display = 'none';
    errorContainer.textContent = '';
    mapBtn.disabled = true;

    // Loading messages and progress
    let percent = 0;
    const messages = ["Getting your IP...", "Searching your network provider...", "Looking out the window..."];
    let messageIndex = 0;

    // Auto-progress but cap at 95% — final 5% reserved for backend completion
    const progressInterval = setInterval(() => {
        // increment slowly and a bit randomly for organic feel
        percent += Math.floor(Math.random() * 4) + 1; // +1..4
        if (percent >= 95) {
            percent = 95;
        }

        // update message index at thresholds
        if (percent >= 70) messageIndex = 2;
        else if (percent >= 35) messageIndex = 1;
        else messageIndex = 0;

        loadingBar.style.width = percent + '%';
        loadingPercent.textContent = `${percent}% ${messages[messageIndex]}`;
    }, 120); // tick every 120ms

    try {
        const res = await fetch('/get_info');
        const data = await res.json();

        if (data.error) throw new Error(data.error);

        // Now finish progress to 100%
        clearInterval(progressInterval);
        loadingBar.style.width = '100%';
        loadingPercent.textContent = `100% ${messages[2]}`;

        // Small delay so user sees 100%
        await new Promise(r => setTimeout(r, 300));

        // IP info
        document.getElementById('ipInfo').innerHTML =
            Object.entries(data.ip_info).map(([k, v]) => `<div><strong>${k}:</strong> ${v}</div>`).join('');

        // ISP info
        document.getElementById('ispInfo').innerHTML =
            Object.entries(data.isp_info).map(([k, v]) => `<div><strong>${k}:</strong> ${v}</div>`).join('');

        // Weather info
        const weather = data.weather_info;
        document.getElementById('weatherInfo').innerHTML = weather.Error || weather.error
            ? `<div>${weather.Error || weather.error}</div>`
            : Object.entries(weather).map(([k, v]) => `<div><strong>${k}:</strong> ${v}</div>`).join('');

        // Map button
        const lat = data.ip_info.Latitude || data.ip_info.latitude;
        const lon = data.ip_info.Longitude || data.ip_info.longitude;
        if (lat && lon && lat !== 'N/A' && lon !== 'N/A') {
            mapBtn.disabled = false;
            mapBtn.onclick = () => window.open(`https://www.google.com/maps?q=${lat},${lon}`, '_blank');
        } else {
            mapBtn.disabled = true;
        }

        // show results
        loadingContainer.style.display = 'none';
        resultContainer.style.display = 'block';
    } catch (err) {
        clearInterval(progressInterval);
        loadingContainer.style.display = 'none';
        errorContainer.textContent = `Error: ${err.message}`;
        errorContainer.style.display = 'block';
    } finally {
        getInfoBtn.disabled = false;
    }
});
