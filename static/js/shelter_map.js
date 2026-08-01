/**
 * LEAFLET INTERACTIVE MAP FOR EMERGENCY SHELTERS LOCATOR
 */

document.addEventListener('DOMContentLoaded', () => {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    // Default map center (New Delhi / India coordinates default, adjustable dynamically)
    const map = L.map('map').setView([28.6139, 77.2090], 10);

    // Dark styled OpenStreetMap tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    // Fetch shelter JSON data from backend API
    fetch('/api/shelters')
        .then(response => response.json())
        .then(shelters => {
            if (shelters.length === 0) return;

            const bounds = [];
            shelters.forEach(shelter => {
                const latLng = [shelter.latitude, shelter.longitude];
                bounds.push(latLng);

                const bedStatusClass = shelter.available_beds > 50 ? 'text-success' : 'text-danger';
                const popupContent = `
                    <div style="color: #0f172a; min-width: 200px;">
                        <h6 style="font-weight: 700; margin-bottom: 4px;">${shelter.name}</h6>
                        <p style="font-size: 0.85rem; margin-bottom: 6px; color: #475569;">${shelter.address}</p>
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
        })
        .catch(err => console.error("Error loading shelter markers on map:", err));
});
