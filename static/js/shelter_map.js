/**
 * LEAFLET INTERACTIVE MAP FOR VERIFIED EMERGENCY SHELTERS & GENERAL POI FACILITIES
 * WITH REAL-TIME GPS LIVE LOCATION & GEODESIC DISTANCE CALCULATOR
 */

document.addEventListener('DOMContentLoaded', () => {
    const mapElement = document.getElementById('map');
    if (!mapElement) return;

    // Default map center - India
    const map = L.map('map').setView([20.5937, 78.9629], 5);

    let userLocationMarker = null;
    let facilityMarkersGroup = L.featureGroup().addTo(map);
    let allFacilitiesData = [];

    // ---------------------------------------------------------
    // MAP TILE LAYER
    // ---------------------------------------------------------

    L.tileLayer(
        'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        {
            attribution:
                '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 19
        }
    ).addTo(map);

    // ---------------------------------------------------------
    // HAVERSINE DISTANCE CALCULATOR
    // ---------------------------------------------------------

    function calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371;

        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;

        const a =
            Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * Math.PI / 180) *
            Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLon / 2) *
            Math.sin(dLon / 2);

        const c = 2 * Math.atan2(
            Math.sqrt(a),
            Math.sqrt(1 - a)
        );

        return (R * c).toFixed(1);
    }

    // ---------------------------------------------------------
    // URL SEARCH PARAMETERS
    // ---------------------------------------------------------

    const urlParams = new URLSearchParams(window.location.search);

    const queryString = urlParams.toString();

    const searchApiUrl = queryString
        ? `/api/search_facilities?${queryString}`
        : `/api/search_facilities`;

    // ---------------------------------------------------------
    // LOAD FACILITIES
    // ---------------------------------------------------------

    loadFacilities();

    function loadFacilities() {

        fetch(searchApiUrl)
            .then(response => {

                if (!response.ok) {
                    throw new Error(
                        `Facility API returned ${response.status}`
                    );
                }

                return response.json();
            })

            .then(data => {

                if (
                    data &&
                    Array.isArray(data.shelters) &&
                    data.shelters.length > 0
                ) {

                    allFacilitiesData = data.shelters;

                    renderMarkers(allFacilitiesData);

                } else {

                    // Fallback API
                    return fetch('/api/shelters')
                        .then(response => {

                            if (!response.ok) {
                                throw new Error(
                                    `Shelter API returned ${response.status}`
                                );
                            }

                            return response.json();
                        })

                        .then(shelters => {

                            allFacilitiesData =
                                Array.isArray(shelters)
                                    ? shelters
                                    : [];

                            renderMarkers(allFacilitiesData);
                        });
                }
            })

            .catch(error => {

                console.error(
                    "Error loading shelter markers:",
                    error
                );

                updateGpsStatus(
                    "⚠️ Unable to load facility data.",
                    "warning"
                );
            })

            .finally(() => {

                // Attempt GPS after facility data is loaded
                locateUserPosition();
            });
    }

    // ---------------------------------------------------------
    // RENDER MAP MARKERS
    // ---------------------------------------------------------

    function renderMarkers(
        shelters,
        userLat = null,
        userLng = null
    ) {

        facilityMarkersGroup.clearLayers();

        const bounds = [];

        // -----------------------------------------------------
        // USER LOCATION MARKER
        // -----------------------------------------------------

        if (
            userLat !== null &&
            userLng !== null &&
            Number.isFinite(userLat) &&
            Number.isFinite(userLng)
        ) {

            bounds.push([userLat, userLng]);

            if (userLocationMarker) {
                map.removeLayer(userLocationMarker);
            }

            const userIcon = L.divIcon({
                className: 'user-live-pin',

                html: `
                    <div style="
                        background-color: #06b6d4;
                        width: 18px;
                        height: 18px;
                        border-radius: 50%;
                        border: 3px solid white;
                        box-shadow: 0 0 15px #06b6d4;
                    "></div>
                `,

                iconSize: [20, 20],
                iconAnchor: [10, 10]
            });

            userLocationMarker = L.marker(
                [userLat, userLng],
                {
                    icon: userIcon
                }
            )
                .addTo(map)
                .bindPopup(`
                    <div style="
                        color: #0f172a;
                        font-weight: 700;
                    ">
                        📍 YOUR LIVE LOCATION
                    </div>
                `);

            userLocationMarker.openPopup();
        }

        // -----------------------------------------------------
        // FACILITY MARKERS
        // -----------------------------------------------------

        if (!Array.isArray(shelters)) {
            return;
        }

        shelters.forEach(shelter => {

            const latitude = Number(shelter.latitude);
            const longitude = Number(shelter.longitude);

            // Ignore invalid coordinates
            if (
                !Number.isFinite(latitude) ||
                !Number.isFinite(longitude)
            ) {
                console.warn(
                    "Skipping facility with invalid coordinates:",
                    shelter
                );

                return;
            }

            const latLng = [latitude, longitude];

            bounds.push(latLng);

            // -------------------------------------------------
            // DISTANCE
            // -------------------------------------------------

            let distanceHtml = '';

            if (
                userLat !== null &&
                userLng !== null
            ) {

                const dist = calculateDistance(
                    userLat,
                    userLng,
                    latitude,
                    longitude
                );

                distanceHtml = `
                    <div style="
                        font-weight: 700;
                        color: #0284c7;
                        margin-bottom: 4px;
                    ">
                        📍 ${dist} km away from you
                    </div>
                `;

                // Update corresponding shelter card
                if (shelter.id !== undefined) {

                    const cardBadge =
                        document.getElementById(
                            `shelter-dist-${shelter.id}`
                        );

                    if (cardBadge) {

                        cardBadge.innerHTML = `
                            <i class="fa-solid fa-location-arrow text-cyan me-1"></i>
                            <strong>${dist} km</strong>
                            from your live position
                        `;

                        cardBadge.classList.remove('d-none');
                    }
                }
            }

            // -------------------------------------------------
            // FACILITY TYPE
            // -------------------------------------------------

            const isVerified =
                shelter.verification_status === 'Verified' ||
                shelter.is_verified_shelter === true;

            const facilityType =
                shelter.facility_type ||
                'Emergency Facility';

            const facilityBadge =
                isVerified
                    ? '✅ Verified Disaster Shelter'
                    : `🏢 General Facility (${facilityType})`;

            // -------------------------------------------------
            // CAPACITY
            // -------------------------------------------------

            let capacityText = 'N/A';

            if (
                Number(shelter.total_capacity) > 0
            ) {

                const available =
                    shelter.available_capacity ??
                    shelter.available_beds ??
                    0;

                capacityText =
                    `${available} free / ${shelter.total_capacity} total`;
            }

            // -------------------------------------------------
            // POPUP
            // -------------------------------------------------

            const popupContent = `
                <div style="
                    color: #0f172a;
                    min-width: 230px;
                ">

                    <div style="margin-bottom: 6px;">

                        <span style="
                            background: ${isVerified ? '#10b981' : '#f59e0b'};
                            color: white;
                            padding: 3px 8px;
                            border-radius: 4px;
                            font-size: 0.75rem;
                            font-weight: 700;
                        ">
                            ${facilityBadge}
                        </span>

                    </div>

                    <h6 style="
                        font-weight: 700;
                        margin-bottom: 4px;
                    ">
                        ${shelter.name || 'Unnamed Facility'}
                    </h6>

                    <p style="
                        font-size: 0.85rem;
                        margin-bottom: 6px;
                        color: #475569;
                    ">
                        ${shelter.address || 'Address unavailable'}
                    </p>

                    ${distanceHtml}

                    <div style="
                        font-size: 0.85rem;
                        margin-bottom: 8px;
                    ">

                        <strong>District:</strong>
                        ${shelter.district || 'N/A'}
                        <br>

                        <strong>
                            Capacity / Occupancy:
                        </strong>
                        ${capacityText}
                        <br>

                        <strong>Contact:</strong>
                        ${shelter.contact || shelter.contact_number || 'N/A'}

                    </div>

                    <a
                        href="https://maps.google.com/?q=${latitude},${longitude}"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="btn btn-sm btn-primary w-100"
                        style="
                            font-size: 0.8rem;
                            padding: 4px 8px;
                        "
                    >
                        <i class="fa-solid fa-map-location-dot me-1"></i>
                        Navigate via Google Maps
                    </a>

                </div>
            `;

            // -------------------------------------------------
            // MARKER
            // -------------------------------------------------

            const markerColor =
                isVerified
                    ? '#10b981'
                    : '#f59e0b';

            const customIcon = L.divIcon({

                className:
                    'custom-facility-pin',

                html: `
                    <div style="
                        background-color: ${markerColor};
                        width: 16px;
                        height: 16px;
                        border-radius: 50%;
                        border: 2px solid white;
                        box-shadow: 0 0 10px ${markerColor};
                    "></div>
                `,

                iconSize: [18, 18],
                iconAnchor: [9, 9]
            });

            const marker = L.marker(
                latLng,
                {
                    icon: customIcon
                }
            ).addTo(facilityMarkersGroup);

            marker.bindPopup(popupContent);
        });

        // -----------------------------------------------------
        // FIT MAP TO MARKERS
        // -----------------------------------------------------

        if (bounds.length > 0) {

            map.fitBounds(
                bounds,
                {
                    padding: [50, 50],
                    maxZoom: 15
                }
            );
        }
    }

    // ---------------------------------------------------------
    // GPS LOCATION
    // ---------------------------------------------------------

    function locateUserPosition() {

        if (!navigator.geolocation) {

            updateGpsStatus(
                "⚠️ Geolocation is not supported by your browser.",
                "warning"
            );

            return;
        }

        const locateBtn =
            document.getElementById('locate-me-btn');

        updateGpsStatus(
            "📍 Locating your live GPS coordinates...",
            "info"
        );

        if (locateBtn) {
            locateBtn.disabled = true;
        }

        navigator.geolocation.getCurrentPosition(

            // =================================================
            // SUCCESS
            // =================================================

            (pos) => {

                const uLat =
                    pos.coords.latitude;

                const uLng =
                    pos.coords.longitude;

                const accuracy =
                    pos.coords.accuracy;

                console.log(
                    "GPS location detected:",
                    {
                        latitude: uLat,
                        longitude: uLng,
                        accuracy: accuracy
                    }
                );

                updateGpsStatus(
                    `📍 Live GPS Detected: (${uLat.toFixed(4)}, ${uLng.toFixed(4)})`,
                    "success"
                );

                if (locateBtn) {
                    locateBtn.disabled = false;
                }

                // Render facilities with distance
                renderMarkers(
                    allFacilitiesData,
                    uLat,
                    uLng
                );

                // Center map around user
                map.setView(
                    [uLat, uLng],
                    13
                );
            },

            // =================================================
            // ERROR
            // =================================================

            (err) => {

                let msg =
                    "GPS lookup denied or unavailable. Showing default map.";

                if (
                    err.code ===
                    GeolocationPositionError.PERMISSION_DENIED
                ) {

                    msg =
                        "⚠️ GPS location permission denied. Please allow location access.";
                }

                else if (
                    err.code ===
                    GeolocationPositionError.POSITION_UNAVAILABLE
                ) {

                    msg =
                        "⚠️ Your location is currently unavailable.";
                }

                else if (
                    err.code ===
                    GeolocationPositionError.TIMEOUT
                ) {

                    msg =
                        "⚠️ GPS position lookup timed out. Please try again.";
                }

                console.warn(
                    "Geolocation error:",
                    err
                );

                updateGpsStatus(
                    msg,
                    "warning"
                );

                if (locateBtn) {
                    locateBtn.disabled = false;
                }

                // Keep existing facility markers
                renderMarkers(
                    allFacilitiesData
                );
            },

            // =================================================
            // GPS OPTIONS
            // =================================================

            {
                enableHighAccuracy: true,
                timeout: 15000,
                maximumAge: 30000
            }
        );
    }

    // ---------------------------------------------------------
    // GPS STATUS
    // ---------------------------------------------------------

    function updateGpsStatus(
        text,
        type = "cyan"
    ) {

        const statusText =
            document.getElementById(
                'gps-status-text'
            );

        if (statusText) {

            statusText.textContent = text;

            // Optional status styling
            statusText.classList.remove(
                'text-success',
                'text-warning',
                'text-danger',
                'text-info'
            );

            if (type === 'success') {
                statusText.classList.add(
                    'text-success'
                );
            }

            else if (type === 'warning') {
                statusText.classList.add(
                    'text-warning'
                );
            }

            else if (type === 'danger') {
                statusText.classList.add(
                    'text-danger'
                );
            }

            else {
                statusText.classList.add(
                    'text-info'
                );
            }
        }
    }

    // ---------------------------------------------------------
    // LOCATE ME BUTTON
    // ---------------------------------------------------------

    const locateBtn =
        document.getElementById(
            'locate-me-btn'
        );

    if (locateBtn) {

        locateBtn.addEventListener(
            'click',
            locateUserPosition
        );
    }
})