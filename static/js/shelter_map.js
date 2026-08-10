/**
 * LEAFLET INTERACTIVE MAP FOR EMERGENCY SHELTERS LOCATOR
 * WITH REAL-TIME GPS LIVE LOCATION & DISTANCE CALCULATOR
 */

document.addEventListener('DOMContentLoaded', () => {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    // Default map center (New Delhi / India coordinates default, adjustable dynamically)
    const map = L.map('map').setView([28.6139, 77.2090], 10);
    let userLocationMarker = null;

    // Dark styled OpenStreetMap tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    // Haversine formula to compute distance between 2 GPS points in km
    function calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371; // Radius of Earth in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon / 2) * Math.sin(dLon / 2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return (R * c).toFixed(1); // distance in km rounded to 1 decimal
    }

    // Fetch shelter JSON data from backend API
    let allSheltersData = [];

    fetch('/api/shelters')
        .then(response => response.json())
        .then(shelters => {
            allSheltersData = shelters;
            renderMarkers(shelters);

            // Automatically attempt GPS live location lookup
            locateUserPosition();
        })
        .catch(err => console.error("Error loading shelter markers on map:", err));

    function renderMarkers(shelters, userLat = null, userLng = null) {
        const bounds = [];

        // Add User Location Marker if available
        if (userLat && userLng) {
            bounds.push([userLat, userLng]);
            if (userLocationMarker) map.removeLayer(userLocationMarker);

            // Custom glowing blue icon for user live position
            const userIcon = L.divIcon({
                className: 'user-live-pin',
                html: '<div style="background-color: #06b6d4; width: 18px; height: 18px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 15px #06b6d4;"></div>',
                iconSize: [20, 20]
            });

            userLocationMarker = L.marker([userLat, userLng], { icon: userIcon }).addTo(map);
            userLocationMarker.bindPopup(`
                <div style="color: #0f172a; font-weight: 700;">
                    📍 YOUR LIVE LOCATION
                </div>
            `).openPopup();
        }

        shelters.forEach(shelter => {
            const latLng = [shelter.latitude, shelter.longitude];
            bounds.push(latLng);

            let distanceHtml = '';
            if (userLat && userLng) {
                const dist = calculateDistance(userLat, userLng, shelter.latitude, shelter.longitude);
                distanceHtml = `<div style="font-weight: 700; color: #0284c7; margin-bottom: 4px;">📍 ${dist} km away from you</div>`;

                // Update DOM distance badge on corresponding card
                const cardBadge = document.getElementById(`shelter-dist-${shelter.id}`);
                if (cardBadge) {
                    cardBadge.innerHTML = `<i class="fa-solid fa-location-arrow text-cyan me-1"></i> <strong>${dist} km</strong> from your live position`;
                    cardBadge.classList.remove('d-none');
                }
            }

            const bedStatusClass = shelter.available_beds > 50 ? 'text-success' : 'text-danger';
            const popupContent = `
                <div style="color: #0f172a; min-width: 210px;">
                    <h6 style="font-weight: 700; margin-bottom: 4px;">${shelter.name}</h6>
                    <p style="font-size: 0.85rem; margin-bottom: 6px; color: #475569;">${shelter.address}</p>
                    ${distanceHtml}
                    <div style="font-size: 0.85rem; margin-bottom: 8px;">
                        <strong>District:</strong> ${shelter.district}<br>
                        <strong>Beds Free:</strong> <span class="${bedStatusClass}" style="font-weight: 700;">${shelter.available_beds} / ${shelter.total_capacity}</span>
                    </div>
                    <div style="margin-bottom: 8px; font-size: 0.8rem;">
                        ${shelter.has_food ? '🍱 Food ' : ''}
                        ${shelter.has_water ? '💧 Water ' : ''}
                        ${shelter.has_medical ? '🚑 Medical' : ''}
                    </div>
                    <a href="tel:${shelter.contact_number}" class="btn btn-sm btn-primary w-100" style="font-size: 0.8rem; padding: 4px 8px;">
                        <i class="fa-solid fa-phone me-1"></i> Call ${shelter.contact_number}
                    </a>
                </div>
            `;

            const marker = L.marker(latLng).addTo(map);
            marker.bindPopup(popupContent);
        });

        if (bounds.length > 0) {
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }

    function locateUserPosition() {
        if (!navigator.geolocation) return;

        const locateBtn = document.getElementById('locate-me-btn');
        const statusText = document.getElementById('gps-status-text');

        if (statusText) statusText.textContent = "Locating your live GPS position...";
        if (locateBtn) locateBtn.disabled = true;

        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const uLat = pos.coords.latitude;
                const uLng = pos.coords.longitude;

                if (statusText) statusText.textContent = `📍 Live Location Detected (${uLat.toFixed(4)}, ${uLng.toFixed(4)})`;
                if (locateBtn) locateBtn.disabled = false;

                renderMarkers(allSheltersData, uLat, uLng);
            },
            (err) => {
                console.warn("GPS lookup denied or unavailable:", err);
                if (statusText) statusText.textContent = "GPS access disabled. Showing default map view.";
                if (locateBtn) locateBtn.disabled = false;
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    }

    const locateBtn = document.getElementById('locate-me-btn');
    if (locateBtn) {
        locateBtn.addEventListener('click', locateUserPosition);
    }
});
