/**
 * EMERGENCY SOS LOCATION CAPTURE SCRIPT
 * AUTOMATICALLY CAPTURES USER GPS & REVERSE GEOCODES ADDRESS
 */

document.addEventListener('DOMContentLoaded', () => {
    const locateBtn = document.getElementById('get-location-btn');
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    const locationInput = document.getElementById('location');
    const statusText = document.getElementById('location-status');

    function captureLiveGPS() {
        if (!navigator.geolocation) {
            if (statusText) statusText.textContent = "Geolocation is not supported by your browser.";
            return;
        }

        if (statusText) statusText.textContent = "📍 Acquiring your live GPS coordinates...";
        if (locateBtn) locateBtn.disabled = true;

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;

                if (latInput) latInput.value = lat;
                if (lngInput) lngInput.value = lng;

                if (statusText) statusText.textContent = `📍 GPS Live Coordinates Captured: (${lat.toFixed(4)}, ${lng.toFixed(4)})`;

                // Reverse geocode via OpenStreetMap Nominatim
                try {
                    const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
                    const data = await response.json();
                    if (data && data.display_name && locationInput) {
                        locationInput.value = data.display_name;
                    } else if (locationInput && !locationInput.value) {
                        locationInput.value = `Latitude: ${lat.toFixed(4)}, Longitude: ${lng.toFixed(4)}`;
                    }
                } catch (e) {
                    if (locationInput && !locationInput.value) {
                        locationInput.value = `Latitude: ${lat.toFixed(4)}, Longitude: ${lng.toFixed(4)}`;
                    }
                } finally {
                    if (locateBtn) locateBtn.disabled = false;
                }
            },
            (error) => {
                console.error("GPS Error:", error);
                if (statusText) statusText.textContent = "GPS access permission needed. Please click 'Auto-Detect GPS' or type your address manually.";
                if (locateBtn) locateBtn.disabled = false;
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    }

    if (locateBtn) {
        locateBtn.addEventListener('click', captureLiveGPS);
    }

    // Auto-trigger GPS detection when opening SOS page
    captureLiveGPS();
});
