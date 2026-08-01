/**
 * EMERGENCY SOS LOCATION CAPTURE SCRIPT
 */

document.addEventListener('DOMContentLoaded', () => {
    const locateBtn = document.getElementById('get-location-btn');
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    const locationInput = document.getElementById('location');
    const statusText = document.getElementById('location-status');

    if (locateBtn) {
        locateBtn.addEventListener('click', () => {
            if (!navigator.geolocation) {
                alert("Geolocation is not supported by your browser.");
                return;
            }

            statusText.textContent = "Acquiring GPS coordinates...";
            locateBtn.disabled = true;

            navigator.geolocation.getCurrentPosition(
                async (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;

                    if (latInput) latInput.value = lat;
                    if (lngInput) lngInput.value = lng;

                    statusText.textContent = `GPS Captured: (${lat.toFixed(4)}, ${lng.toFixed(4)})`;

                    // Reverse geocode via OpenStreetMap Nominatim
                    try {
                        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`);
                        const data = await response.json();
                        if (data && data.display_name && locationInput) {
                            locationInput.value = data.display_name;
                        }
                    } catch (e) {
                        if (locationInput && !locationInput.value) {
                            locationInput.value = `Latitude: ${lat.toFixed(4)}, Longitude: ${lng.toFixed(4)}`;
                        }
                    } finally {
                        locateBtn.disabled = false;
                    }
                },
                (error) => {
                    console.error("GPS Error:", error);
                    statusText.textContent = "Could not fetch GPS automatically. Please type your location below.";
                    locateBtn.disabled = false;
                },
                { enableHighAccuracy: true, timeout: 10000 }
            );
        });
    }
});
