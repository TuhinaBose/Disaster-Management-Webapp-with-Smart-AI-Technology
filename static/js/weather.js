/**
 * REAL-TIME WEATHER MODULE (RADAR DISASTER MANAGEMENT)
 * Fetches live meteorological telemetry from /api/weather based on user GPS or location query.
 */

document.addEventListener('DOMContentLoaded', () => {
    const weatherContainer = document.getElementById('weather-widget');
    if (!weatherContainer) return;

    const tempEl = document.getElementById('weather-temp');
    const condEl = document.getElementById('weather-condition');
    const iconEl = document.getElementById('weather-icon');
    const locationEl = document.getElementById('weather-location');
    const rainEl = document.getElementById('weather-rain');
    const windEl = document.getElementById('weather-wind');
    const humidityEl = document.getElementById('weather-humidity');
    const timestampEl = document.getElementById('weather-timestamp');
    const providerEl = document.getElementById('weather-provider');
    const statusText = document.getElementById('weather-status-text');

    const searchForm = document.getElementById('weather-search-form');
    const searchInput = document.getElementById('weather-search-input');
    const gpsBtn = document.getElementById('weather-gps-btn');

    // Default load: Delhi NCR weather or user GPS
    loadWeather();

    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const loc = searchInput.value.trim();
            if (loc) {
                loadWeather({ location: loc });
            }
        });
    }

    if (gpsBtn) {
        gpsBtn.addEventListener('click', () => {
            if (!navigator.geolocation) {
                showStatus("Geolocation is not supported by your browser.", "danger");
                return;
            }
            showStatus("Locating your live GPS coordinates...", "info");
            gpsBtn.disabled = true;

            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    gpsBtn.disabled = false;
                    loadWeather({ lat: pos.coords.latitude, lng: pos.coords.longitude });
                },
                (err) => {
                    gpsBtn.disabled = false;
                    let msg = "GPS access denied or unavailable.";
                    if (err.code === err.PERMISSION_DENIED) msg = "Location permission denied. Please allow location access.";
                    else if (err.code === err.TIMEOUT) msg = "GPS lookup timed out. Please try searching by city name.";
                    showStatus(msg, "warning");
                },
                { enableHighAccuracy: true, timeout: 8000 }
            );
        });
    }

    function loadWeather(params = {}) {
        let url = '/api/weather';
        const queryParts = [];

        if (params.lat && params.lng) {
            queryParts.push(`lat=${params.lat}&lng=${params.lng}`);
        } else if (params.location) {
            queryParts.push(`location=${encodeURIComponent(params.location)}`);
        }

        if (queryParts.length > 0) {
            url += '?' + queryParts.join('&');
        }

        showStatus("Fetching real-time weather telemetry...", "info");

        fetch(url)
            .then(resp => {
                if (!resp.ok) throw new Error("Weather service returned error response.");
                return resp.json();
            })
            .then(data => {
                if (data.success || data.temperature !== undefined) {
                    if (tempEl) tempEl.textContent = `${data.temperature}°C`;
                    if (condEl) condEl.textContent = data.weather_condition || "Clear";
                    if (locationEl) locationEl.textContent = data.location || "Selected Location";
                    if (rainEl) rainEl.textContent = `${data.rainfall} mm`;
                    if (windEl) windEl.textContent = `${data.wind_speed} km/h`;
                    if (humidityEl) humidityEl.textContent = `${data.humidity} %`;
                    if (timestampEl) timestampEl.textContent = `Updated: ${data.timestamp}`;
                    if (providerEl) providerEl.textContent = `Data Source: ${data.provider || 'Live Telemetry'}`;

                    // Update weather icon based on condition
                    if (iconEl) {
                        const cond = (data.weather_condition || '').toLowerCase();
                        if (cond.includes('rain') || cond.includes('drizzle')) iconEl.className = 'fa-solid fa-cloud-showers-heavy text-cyan';
                        elif (cond.includes('thunder') || cond.includes('storm')) iconEl.className = 'fa-solid fa-cloud-bolt text-warning';
                        elif (cond.includes('cloud') || cond.includes('overcast')) iconEl.className = 'fa-solid fa-cloud-sun text-info';
                        elif (cond.includes('fog')) iconEl.className = 'fa-solid fa-smog text-secondary';
                        else iconEl.className = 'fa-solid fa-sun text-warning';
                    }

                    showStatus(`Weather updated for ${data.location}`, "success", 3000);
                } else {
                    showStatus(data.error || "Could not retrieve weather for specified location.", "danger");
                }
            })
            .catch(err => {
                console.error("Weather error:", err);
                showStatus("Failed to load real-time weather telemetry. Please try again.", "danger");
            });
    }

    function showStatus(text, type = "info", autoDismissMs = 0) {
        if (!statusText) return;
        statusText.innerHTML = `<span class="badge bg-${type}">${text}</span>`;
        if (autoDismissMs > 0) {
            setTimeout(() => {
                statusText.innerHTML = '';
            }, autoDismissMs);
        }
    }
});
