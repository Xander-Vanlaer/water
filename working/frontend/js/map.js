/**
 * Hospital Map Visualization
 * Uses Leaflet.js for interactive map with hospital markers
 */

let hospitalMap = null;
let markersLayer = null;
let markerClusterGroup = null;

/**
 * Initialize the hospital map
 * @param {string} containerId - ID of the map container element
 * @param {number} defaultLat - Default latitude for map center
 * @param {number} defaultLng - Default longitude for map center
 * @param {number} defaultZoom - Default zoom level
 */
function initializeMap(containerId, defaultLat = 50.8503, defaultLng = 4.3517, defaultZoom = 7) {
    // Create map centered on Belgium (default location)
    hospitalMap = L.map(containerId).setView([defaultLat, defaultLng], defaultZoom);
    
    // Add OpenStreetMap tiles (no API key required)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(hospitalMap);
    
    // Initialize marker cluster group if library is available
    if (typeof L.markerClusterGroup !== 'undefined') {
        markerClusterGroup = L.markerClusterGroup({
            maxClusterRadius: 50,
            spiderfyOnMaxZoom: true,
            showCoverageOnHover: false,
            zoomToBoundsOnClick: true
        });
        hospitalMap.addLayer(markerClusterGroup);
    } else {
        // Fallback to regular layer group
        markersLayer = L.layerGroup().addTo(hospitalMap);
    }
    
    return hospitalMap;
}

/**
 * Load hospital markers from API and add to map
 * @param {string} apiUrl - URL to fetch hospital map data
 */
async function loadHospitalMarkers(apiUrl = '/api/admin/hospitals/map') {
    try {
        const response = await fetch(apiUrl, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load hospital data');
        }
        
        const hospitals = await response.json();
        
        // Clear existing markers
        if (markerClusterGroup) {
            markerClusterGroup.clearLayers();
        } else if (markersLayer) {
            markersLayer.clearLayers();
        }
        
        if (hospitals.length === 0) {
            showNotification('No hospitals found', 'info');
            return;
        }
        
        const bounds = [];
        
        hospitals.forEach(hospital => {
            // Skip hospitals without coordinates
            if (!hospital.latitude || !hospital.longitude) {
                return;
            }
            
            // Determine marker color based on sensor activity
            let markerColor = 'gray'; // No sensors
            if (hospital.sensor_count > 0) {
                // Check if last reading is recent (within 1 hour)
                if (hospital.last_reading_time) {
                    const lastReading = new Date(hospital.last_reading_time);
                    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
                    markerColor = lastReading > oneHourAgo ? 'green' : 'blue';
                }
            }
            
            // Create custom marker icon
            const markerIcon = L.divIcon({
                className: 'custom-marker',
                html: `<div style="background-color: ${markerColor}; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>`,
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            });
            
            // Create marker
            const marker = L.marker([hospital.latitude, hospital.longitude], {
                icon: markerIcon
            });
            
            // Create popup content
            const lastReadingText = hospital.last_reading_time 
                ? formatDateTime(hospital.last_reading_time)
                : 'No data';
            
            const popupContent = `
                <div class="hospital-popup">
                    <h3>${escapeHtml(hospital.name)}</h3>
                    <p><strong>Code:</strong> ${escapeHtml(hospital.code)}</p>
                    <p><strong>Region:</strong> ${escapeHtml(hospital.region_name)}</p>
                    <p><strong>Sensors:</strong> ${hospital.sensor_count}</p>
                    <p><strong>Last Reading:</strong> ${lastReadingText}</p>
                    <a href="#" onclick="viewHospitalDetails(${hospital.id}); return false;" class="btn-small">View Details</a>
                </div>
            `;
            
            marker.bindPopup(popupContent);
            
            // Add marker to cluster group or layer
            if (markerClusterGroup) {
                markerClusterGroup.addLayer(marker);
            } else if (markersLayer) {
                markersLayer.addLayer(marker);
            }
            
            // Add to bounds for auto-zoom
            bounds.push([hospital.latitude, hospital.longitude]);
        });
        
        // Auto-zoom to fit all markers
        if (bounds.length > 0) {
            hospitalMap.fitBounds(bounds, { padding: [50, 50] });
        }
        
        return hospitals;
    } catch (error) {
        console.error('Error loading hospital markers:', error);
        showNotification('Failed to load hospital map data', 'error');
    }
}

/**
 * Filter hospitals on map
 * @param {string} regionId - Filter by region ID (null for all)
 * @param {boolean} withSensorsOnly - Show only hospitals with sensors
 */
async function filterHospitalsOnMap(regionId = null, withSensorsOnly = false) {
    let apiUrl = '/api/admin/hospitals/map';
    if (regionId) {
        apiUrl += `?region_id=${regionId}`;
    }
    
    const hospitals = await loadHospitalMarkers(apiUrl);
    
    // Client-side filtering for sensors (if needed)
    // This is already handled by marker color, but we could hide markers here
}

/**
 * Create a location picker map for hospital forms
 * @param {string} containerId - Container ID for the map
 * @param {number} initialLat - Initial latitude
 * @param {number} initialLng - Initial longitude
 * @param {function} onLocationSelected - Callback when location is selected
 */
function initializeLocationPicker(containerId, initialLat = 50.8503, initialLng = 4.3517, onLocationSelected) {
    const pickerMap = L.map(containerId).setView([initialLat, initialLng], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(pickerMap);
    
    let marker = L.marker([initialLat, initialLng], { draggable: true }).addTo(pickerMap);
    
    // Update coordinates when marker is dragged
    marker.on('dragend', function(e) {
        const position = marker.getLatLng();
        if (onLocationSelected) {
            onLocationSelected(position.lat, position.lng);
        }
    });
    
    // Allow clicking on map to set location
    pickerMap.on('click', function(e) {
        marker.setLatLng(e.latlng);
        if (onLocationSelected) {
            onLocationSelected(e.latlng.lat, e.latlng.lng);
        }
    });
    
    return { map: pickerMap, marker: marker };
}

/**
 * Update location picker marker position
 * @param {object} pickerInstance - Object returned from initializeLocationPicker containing {map, marker}
 * @param {number} lat - Latitude
 * @param {number} lng - Longitude
 */
function updatePickerLocation(pickerInstance, lat, lng) {
    if (pickerInstance && pickerInstance.marker && lat && lng) {
        pickerInstance.marker.setLatLng([lat, lng]);
        if (pickerInstance.map) {
            pickerInstance.map.setView([lat, lng], 13);
        }
    }
}

/**
 * View hospital details (redirect to hospital section)
 * @param {number} hospitalId - Hospital ID
 */
function viewHospitalDetails(hospitalId) {
    // This would navigate to the hospital details view
    // Implementation depends on your navigation system
    console.log('View hospital details:', hospitalId);
    // Example: window.location.hash = `#hospital-${hospitalId}`;
}

/**
 * Helper function to format date/time
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

/**
 * Helper function to escape HTML
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
