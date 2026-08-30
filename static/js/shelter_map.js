/**
 * LEAFLET INTERACTIVE MAP FOR EMERGENCY SHELTERS & LIVE OPENSTREETMAP FACILITIES
 * WITH REAL-TIME GPS LIVE LOCATION & DISTANCE CALCULATOR
 */

document.addEventListener('DOMContentLoaded', () => {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    // Default map center (India coordinates)
    const map = L.map('map').setView([20.5937, 78.9629], 5);
    let userLocationMarker = null;
    let facilityMarkersGroup = L.featureGroup().addTo(map);

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
        return (R * c).toFixed(1);
    }

    // Extract current URL search params
    const urlParams = new URLSearchParams(window.location.search);
    const searchApiUrl = `/api/search_facilities?${urlParams.toString()}`;

    let allFacilitiesData = [];

    // Fetch combined shelters & live OpenStreetMap facilities
    fetch(searchApiUrl)
        .then(response => response.json())
        .then(data => {
            if (data.shelters && data.shelters.length > 0) {
                allFacilitiesData = data.shelters;
                renderMarkers(data.shelters);
            } else {
                // Fallback to basic shelters API
                fetch('/api/shelters')
                    .then(r => r.json())
                    .then(shs => {
                        allFacilitiesData = shs;
                        renderMarkers(shs);
                    });
            }

            // Automatically attempt GPS live location lookup
            locateUserPosition();
        })
        .catch(err => console.error("Error loading shelter markers on map:", err));

    function renderMarkers(shelters, userLat = null, userLng = null) {
        facilityMarkersGroup.clearLayers();
        const bounds = [];

        // Add User Location Marker if available
        if (userLat && userLng) {
            bounds.push([userLat, userLng]);
            if (userLocationMarker) map.removeLayer(userLocationMarker);

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

                const cardBadge = document.getElementById(`shelter-dist-${shelter.id}`);
                if (cardBadge) {
                    cardBadge.innerHTML = `<i class="fa-solid fa-location-arrow text-cyan me-1"></i> <strong>${dist} km</strong> from your live position`;
                    cardBadge.classList.remove('d-none');
                }
            }

            const isOsmLive = shelter.is_osm_live;
            const facilityBadge = shelter.facility_type === 'School' ? '🏫 School' :
                                  shelter.facility_type === 'College' ? '🎓 College' :
                                  shelter.facility_type === 'Hospital' ? '🏥 Hospital' : '🏢 Relief Building';

            const popupContent = `
                <div style="color: #0f172a; min-width: 220px;">
                    <div style="margin-bottom: 4px;">
                        <span style="background: #0284c7; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">${facilityBadge}</span>
                        ${isOsmLive ? '<span style="background: #eab308; color: black; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: 700;">🌐 Live OSM</span>' : ''}
                    </div>
                    <h6 style="font-weight: 700; margin-bottom: 4px;">${shelter.name}</h6>
                    <p style="font-size: 0.85rem; margin-bottom: 6px; color: #475569;">${shelter.address}</p>
                    ${distanceHtml}
                    <div style="font-size: 0.85rem; margin-bottom: 8px;">
                        <strong>District:</strong> ${shelter.district}<br>
                        <strong>Status:</strong> <span style="color: #16a34a; font-weight: 700;">Available Emergency Center</span>
                    </div>
                    <a href="https://maps.google.com/?q=${shelter.latitude},${shelter.longitude}" target="_blank" class="btn btn-sm btn-primary w-100" style="font-size: 0.8rem; padding: 4px 8px;">
                        <i class="fa-solid fa-map-location-dot me-1"></i> Navigate via Google Maps
                    </a>
                </div>
            `;

            // Custom Marker Colors: Gold for OSM live schools/colleges, Cyan for DB shelters
            const markerColor = isOsmLive ? '#eab308' : '#06b6d4';
            const customIcon = L.divIcon({
                className: 'custom-facility-pin',
                html: `<div style="background-color: ${markerColor}; width: 16px; height: 16px; border-radius: 50%; border: 2px solid white; box-shadow: 0 0 10px ${markerColor};"></div>`,
                iconSize: [18, 18]
            });

            const marker = L.marker(latLng, { icon: customIcon }).addTo(facilityMarkersGroup);
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

                renderMarkers(allFacilitiesData, uLat, uLng);
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
