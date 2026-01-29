/**
 * Main dashboard JavaScript - Handles user info, 2FA, and data management
 */

let currentUser = null;

document.addEventListener('DOMContentLoaded', async () => {
    // Load user information
    await loadUserInfo();
    
    // Load dashboard by role
    await loadDashboardByRole();
    
    // Set up event listeners
    setupEventListeners();
});

// Load user information
async function loadUserInfo() {
    try {
        currentUser = await apiClient.request('/api/auth/me');
        
        // Display user info in nav
        const userInfoElement = document.getElementById('user-info');
        const roleName = getRoleName(currentUser.role);
        userInfoElement.textContent = `Welcome, ${currentUser.username} (${roleName})`;
        
        // Display user details
        const userDetailsElement = document.getElementById('user-details');
        userDetailsElement.innerHTML = `
            <p><strong>Username:</strong> ${currentUser.username}</p>
            <p><strong>Email:</strong> ${currentUser.email}</p>
            <p><strong>Role:</strong> ${roleName}</p>
            <p><strong>Member since:</strong> ${new Date(currentUser.created_at).toLocaleDateString()}</p>
            <p><strong>Last login:</strong> ${currentUser.last_login ? new Date(currentUser.last_login).toLocaleString() : 'N/A'}</p>
        `;
        
        // Update 2FA section
        if (currentUser.is_2fa_enabled) {
            document.getElementById('2fa-disabled').style.display = 'none';
            document.getElementById('2fa-enabled').style.display = 'block';
        } else {
            document.getElementById('2fa-disabled').style.display = 'block';
            document.getElementById('2fa-enabled').style.display = 'none';
        }
    } catch (error) {
        console.error('Failed to load user info:', error);
        // If unauthorized, redirect to login
        if (error.message.includes('401')) {
            TokenManager.clearTokens();
            window.location.href = 'login.html';
        }
    }
}

// Get role name from role number
function getRoleName(role) {
    const roles = {
        1: 'Pending',
        2: 'Admin',
        3: 'Region Admin',
        4: 'Hospital User'
    };
    return roles[role] || 'Unknown';
}

// Load dashboard by role
async function loadDashboardByRole() {
    if (!currentUser) return;
    
    // Hide all role-specific sections first
    hideAllRoleSections();
    
    switch(currentUser.role) {
        case 1:
            showPendingUserView();
            break;
        case 2:
            await showAdminDashboard();
            break;
        case 3:
            await showRegionAdminDashboard();
            break;
        case 4:
            await showHospitalDashboard();
            break;
    }
}

// Hide all role-specific sections
function hideAllRoleSections() {
    const sections = [
        'pending-user-section',
        'admin-section',
        'region-admin-section',
        'hospital-user-section',
        'data-management'
    ];
    
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = 'none';
        }
    });
}

// Show pending user view
function showPendingUserView() {
    const section = document.getElementById('pending-user-section');
    if (section) {
        section.style.display = 'block';
    }
}

// Show admin dashboard
async function showAdminDashboard() {
    const section = document.getElementById('admin-section');
    if (section) {
        section.style.display = 'block';
        await loadAdminStats();
        await loadSensorStats();
        await loadSensorsOverview();
        await loadAdminUsers();
        await loadRegions();
        await loadHospitals();
        await loadAPIKeys();
        await loadAllowedEmails();
        await loadAuditStats();
        await loadAuditLogs();
        setupAdminEventListeners();
    }
}

// Show region admin dashboard
async function showRegionAdminDashboard() {
    const section = document.getElementById('region-admin-section');
    if (section) {
        section.style.display = 'block';
        await loadRegionAdminStats();
        await loadRegionUsers();
        await loadRegionHospitals();
        await loadRegionSensorData();
    }
}

// Show hospital user dashboard
async function showHospitalDashboard() {
    const section = document.getElementById('hospital-user-section');
    if (section) {
        section.style.display = 'block';
        await loadHospitalStats();
        await loadHospitalSensorData();
    }
}

// Load admin stats
async function loadAdminStats() {
    try {
        const stats = await apiClient.request('/api/dashboard/stats');
        document.getElementById('admin-stats').innerHTML = `
            <div class="stat-item">
                <h4>Total Users</h4>
                <p class="stat-number">${stats.total_users || 0}</p>
            </div>
            <div class="stat-item">
                <h4>Pending Users</h4>
                <p class="stat-number">${stats.pending_users || 0}</p>
            </div>
            <div class="stat-item">
                <h4>Total Regions</h4>
                <p class="stat-number">${stats.total_regions || 0}</p>
            </div>
            <div class="stat-item">
                <h4>Total Hospitals</h4>
                <p class="stat-number">${stats.total_hospitals || 0}</p>
            </div>
            <div class="stat-item">
                <h4>Sensor Readings</h4>
                <p class="stat-number">${stats.total_sensor_readings || 0}</p>
            </div>
        `;
    } catch (error) {
        console.error('Failed to load admin stats:', error);
    }
}

// Load admin users list
async function loadAdminUsers() {
    try {
        const users = await apiClient.request('/api/admin/users');
        const usersList = document.getElementById('admin-users-list');
        
        if (users.length === 0) {
            usersList.innerHTML = '<p>No users found.</p>';
            return;
        }
        
        usersList.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Region</th>
                        <th>Hospital</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${users.map(user => `
                        <tr>
                            <td>${escapeHtml(user.username)}</td>
                            <td>${escapeHtml(user.email)}</td>
                            <td>${getRoleName(user.role)}</td>
                            <td>${user.region_id || 'N/A'}</td>
                            <td>${user.hospital_id || 'N/A'}</td>
                            <td>
                                <button class="btn btn-small btn-primary" onclick="editUserRole(${user.id})">Edit Role</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Failed to load users:', error);
    }
}

// Load regions
async function loadRegions() {
    try {
        const regions = await apiClient.request('/api/admin/regions');
        const regionsList = document.getElementById('regions-list');
        
        if (!regions || regions.length === 0) {
            regionsList.innerHTML = '<p>No regions found.</p>';
            return;
        }
        
        regionsList.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Code</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${regions.map(region => `
                        <tr>
                            <td>${region.id}</td>
                            <td><strong>${escapeHtml(region.name)}</strong></td>
                            <td><code>${escapeHtml(region.code)}</code></td>
                            <td>${new Date(region.created_at).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-small btn-primary" onclick="editRegion(${region.id})">Edit</button>
                                <button class="btn btn-small btn-danger" onclick="deleteRegion(${region.id})">Delete</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
        
        // Populate dropdowns after loading regions
        await populateRegionDropdowns();
    } catch (error) {
        console.error('Failed to load regions:', error);
    }
}

// Edit region - global function for onclick
async function editRegion(regionId) {
    try {
        const regions = await apiClient.request('/api/admin/regions');
        const region = regions.find(r => r.id === regionId);
        
        if (!region) {
            showError('Region not found');
            return;
        }
        
        document.getElementById('edit-region-id').value = regionId;
        document.getElementById('edit-region-name').value = region.name;
        document.getElementById('edit-region-code').value = region.code;
        document.getElementById('edit-region-form').style.display = 'block';
    } catch (error) {
        showError('Failed to load region: ' + error.message);
    }
}

// Delete region - global function for onclick
async function deleteRegion(regionId) {
    if (!confirm('Are you sure you want to delete this region? This will fail if there are hospitals or users assigned to it.')) {
        return;
    }
    
    try {
        await apiClient.request(`/api/admin/regions/${regionId}`, { method: 'DELETE' });
        showSuccess('Region deleted successfully');
        await loadRegions();
    } catch (error) {
        showError('Failed to delete region: ' + error.message);
    }
}

// Load hospitals
async function loadHospitals() {
    try {
        const hospitals = await apiClient.request('/api/admin/hospitals');
        const regions = await apiClient.request('/api/admin/regions');
        const hospitalsList = document.getElementById('hospitals-list');
        
        if (!hospitals || hospitals.length === 0) {
            hospitalsList.innerHTML = '<p>No hospitals found.</p>';
            return;
        }
        
        hospitalsList.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Code</th>
                        <th>Region</th>
                        <th>Address</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${hospitals.map(hospital => {
                        const region = regions.find(r => r.id === hospital.region_id);
                        return `
                            <tr>
                                <td>${hospital.id}</td>
                                <td><strong>${escapeHtml(hospital.name)}</strong></td>
                                <td><code>${escapeHtml(hospital.code)}</code></td>
                                <td>${region ? escapeHtml(region.name) : 'N/A'}</td>
                                <td>${escapeHtml(hospital.address || 'N/A')}</td>
                                <td>${new Date(hospital.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button class="btn btn-small btn-primary" onclick="editHospital(${hospital.id})">Edit</button>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        `;
        
        // Populate dropdowns after loading hospitals
        await populateHospitalDropdowns();
    } catch (error) {
        console.error('Failed to load hospitals:', error);
    }
}

// Edit hospital - global function for onclick
async function editHospital(hospitalId) {
    try {
        const hospitals = await apiClient.request('/api/admin/hospitals');
        const hospital = hospitals.find(h => h.id === hospitalId);
        
        if (!hospital) {
            showError('Hospital not found');
            return;
        }
        
        document.getElementById('edit-hospital-id').value = hospitalId;
        document.getElementById('edit-hospital-name').value = hospital.name;
        document.getElementById('edit-hospital-code').value = hospital.code;
        document.getElementById('edit-hospital-region').value = hospital.region_id;
        document.getElementById('edit-hospital-address').value = hospital.address || '';
        document.getElementById('edit-hospital-form').style.display = 'block';
    } catch (error) {
        showError('Failed to load hospital: ' + error.message);
    }
}

// Load region admin stats
async function loadRegionAdminStats() {
    try {
        const stats = await apiClient.request('/api/dashboard/stats');
        document.getElementById('region-admin-stats').innerHTML = `
            <div class="stat-item">
                <h4>Hospitals in Region</h4>
                <p class="stat-number">${stats.total_hospitals || 0}</p>
            </div>
            <div class="stat-item">
                <h4>Users in Region</h4>
                <p class="stat-number">${stats.total_users_in_region || 0}</p>
            </div>
            <div class="stat-item">
                <h4>Sensor Readings</h4>
                <p class="stat-number">${stats.total_sensor_readings || 0}</p>
            </div>
        `;
    } catch (error) {
        console.error('Failed to load region admin stats:', error);
    }
}

// Load region users
async function loadRegionUsers() {
    try {
        const users = await apiClient.request('/api/region/users');
        document.getElementById('region-users-list').innerHTML = users.map(user => `
            <div class="list-item">
                ${escapeHtml(user.username)} - ${getRoleName(user.role)}
            </div>
        `).join('') || '<p>No users in your region.</p>';
    } catch (error) {
        console.error('Failed to load region users:', error);
    }
}

// Load region hospitals
async function loadRegionHospitals() {
    try {
        const hospitals = await apiClient.request('/api/region/hospitals');
        document.getElementById('region-hospitals-list').innerHTML = hospitals.map(hospital => `
            <div class="list-item">
                <strong>${escapeHtml(hospital.name)}</strong> (${escapeHtml(hospital.code)})
            </div>
        `).join('') || '<p>No hospitals in your region.</p>';
    } catch (error) {
        console.error('Failed to load region hospitals:', error);
    }
}

// Load region sensor data
async function loadRegionSensorData() {
    try {
        const sensorData = await apiClient.request('/api/dashboard/sensor-data?limit=10');
        displaySensorData('region-sensor-data', sensorData);
    } catch (error) {
        console.error('Failed to load region sensor data:', error);
    }
}

// Load hospital stats
async function loadHospitalStats() {
    try {
        const stats = await apiClient.request('/api/dashboard/stats');
        document.getElementById('hospital-stats').innerHTML = `
            <div class="stat-item">
                <h4>Total Sensor Readings</h4>
                <p class="stat-number">${stats.total_sensor_readings || 0}</p>
            </div>
            <div class="stat-item">
                <h4>Unique Sensors</h4>
                <p class="stat-number">${stats.unique_sensors || 0}</p>
            </div>
        `;
    } catch (error) {
        console.error('Failed to load hospital stats:', error);
    }
}

// Load hospital sensor data
async function loadHospitalSensorData() {
    try {
        const sensorData = await apiClient.request('/api/dashboard/sensor-data?limit=20');
        displaySensorData('hospital-sensor-data', sensorData);
    } catch (error) {
        console.error('Failed to load hospital sensor data:', error);
    }
}

// Display sensor data in table
// Display sensor data in table
async function displaySensorData(elementId, sensorData) {
    const element = document.getElementById(elementId);
    
    if (!sensorData || sensorData.length === 0) {
        element.innerHTML = '<p>No sensor data available.</p>';
        return;
    }
    
    // Fetch hospitals to get names
    try {
        const hospitals = await apiClient.request('/api/admin/hospitals');
        const hospitalMap = {};
        hospitals.forEach(h => {
            hospitalMap[h.id] = h.name;
        });
        
        element.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Sensor ID</th>
                        <th>Hospital</th>
                        <th>Temperature</th>
                        <th>Humidity</th>
                        <th>Air Quality</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    ${sensorData.map(data => `
                        <tr>
                            <td><strong>${escapeHtml(data.sensor_id)}</strong></td>
                            <td>${hospitalMap[data.hospital_id] || `ID: ${data.hospital_id}`}</td>
                            <td>${data.temperature !== null ? data.temperature.toFixed(1) + '°C' : 'N/A'}</td>
                            <td>${data.humidity !== null ? data.humidity.toFixed(1) + '%' : 'N/A'}</td>
                            <td>${data.air_quality !== null ? data.air_quality.toFixed(0) : 'N/A'}</td>
                            <td>${new Date(data.timestamp).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Failed to fetch hospital names:', error);
        // Fallback to showing hospital IDs
        element.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Sensor ID</th>
                        <th>Hospital ID</th>
                        <th>Temperature</th>
                        <th>Humidity</th>
                        <th>Air Quality</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    ${sensorData.map(data => `
                        <tr>
                            <td><strong>${escapeHtml(data.sensor_id)}</strong></td>
                            <td>${data.hospital_id}</td>
                            <td>${data.temperature !== null ? data.temperature.toFixed(1) + '°C' : 'N/A'}</td>
                            <td>${data.humidity !== null ? data.humidity.toFixed(1) + '%' : 'N/A'}</td>
                            <td>${data.air_quality !== null ? data.air_quality.toFixed(0) : 'N/A'}</td>
                            <td>${new Date(data.timestamp).toLocaleString()}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
}

// Set up event listeners
function setupEventListeners() {
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', async () => {
        try {
            await apiClient.request('/api/auth/logout', { method: 'POST' });
        } catch (error) {
            console.error('Logout request failed:', error);
        } finally {
            TokenManager.clearTokens();
            window.location.href = 'login.html';
        }
    });
    
    // Enable 2FA button
    document.getElementById('enable-2fa-btn').addEventListener('click', async () => {
        try {
            const response = await apiClient.request('/api/auth/enable-2fa', { method: 'POST' });
            
            // Display QR code
            const qrContainer = document.getElementById('qr-code-container');
            qrContainer.innerHTML = `<img src="${response.qr_code}" alt="2FA QR Code">`;
            
            // Display secret
            document.getElementById('totp-secret').textContent = response.secret;
            
            // Show setup section
            document.getElementById('2fa-disabled').style.display = 'none';
            document.getElementById('2fa-setup').style.display = 'block';
        } catch (error) {
            showError(error.message);
        }
    });
    
    // Close 2FA setup
    document.getElementById('close-2fa-setup').addEventListener('click', () => {
        document.getElementById('2fa-setup').style.display = 'none';
        loadUserInfo(); // Reload to update 2FA status
    });
    
    // Disable 2FA button
    document.getElementById('disable-2fa-btn').addEventListener('click', async () => {
        if (!confirm('Are you sure you want to disable 2FA?')) {
            return;
        }
        
        try {
            await apiClient.request('/api/auth/disable-2fa', { method: 'POST' });
            await loadUserInfo(); // Reload to update 2FA status
        } catch (error) {
            showError(error.message);
        }
    });
    
    // Add data button
    document.getElementById('add-data-btn').addEventListener('click', () => {
        document.getElementById('add-data-form').style.display = 'block';
        document.getElementById('add-data-btn').style.display = 'none';
    });
    
    // Cancel add data
    document.getElementById('cancel-data-btn').addEventListener('click', () => {
        document.getElementById('add-data-form').style.display = 'none';
        document.getElementById('add-data-btn').style.display = 'block';
        document.getElementById('data-title').value = '';
        document.getElementById('data-content').value = '';
    });
    
    // Save data
    document.getElementById('save-data-btn').addEventListener('click', async () => {
        const title = document.getElementById('data-title').value;
        const content = document.getElementById('data-content').value;
        
        if (!title || !content) {
            showError('Please fill in all fields');
            return;
        }
        
        try {
            await apiClient.request('/api/data/', {
                method: 'POST',
                body: JSON.stringify({ title, content })
            });
            
            // Clear form
            document.getElementById('data-title').value = '';
            document.getElementById('data-content').value = '';
            document.getElementById('add-data-form').style.display = 'none';
            document.getElementById('add-data-btn').style.display = 'block';
            
            // Reload data
            await loadUserData();
        } catch (error) {
            showError(error.message);
        }
    });
}

// Load user data
async function loadUserData() {
    try {
        const data = await apiClient.request('/api/data/');
        
        const dataListElement = document.getElementById('data-list');
        
        if (data.length === 0) {
            dataListElement.innerHTML = '<p style="color: #888; text-align: center; padding: 2rem;">No data items yet. Click "Add New Item" to create one.</p>';
            return;
        }
        
        dataListElement.innerHTML = data.map(item => `
            <div class="data-item" data-item-id="${item.id}">
                <h3>${escapeHtml(item.title)}</h3>
                <p>${escapeHtml(item.content)}</p>
                <small>Created: ${new Date(item.created_at).toLocaleString()}</small>
                <br>
                <button class="btn btn-danger delete-item-btn">Delete</button>
            </div>
        `).join('');
        
        // Add event listeners for delete buttons
        document.querySelectorAll('.delete-item-btn').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const itemId = e.target.closest('.data-item').dataset.itemId;
                await deleteDataItem(parseInt(itemId));
            });
        });
    } catch (error) {
        showError('Failed to load data: ' + error.message);
    }
}

// Delete data item
async function deleteDataItem(itemId) {
    if (!confirm('Are you sure you want to delete this item?')) {
        return;
    }
    
    try {
        await apiClient.request(`/api/data/${itemId}`, { method: 'DELETE' });
        await loadUserData();
    } catch (error) {
        showError('Failed to delete item: ' + error.message);
    }
}

// Show error message
function showError(message) {
    const errorElement = document.getElementById('error-message');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}

// Show success message
function showSuccess(message) {
    // Create success element if it doesn't exist
    let successElement = document.getElementById('success-message');
    if (!successElement) {
        successElement = document.createElement('div');
        successElement.id = 'success-message';
        successElement.className = 'success-message';
        successElement.style.position = 'fixed';
        successElement.style.top = '20px';
        successElement.style.right = '20px';
        successElement.style.zIndex = '9999';
        successElement.style.maxWidth = '400px';
        document.body.appendChild(successElement);
    }
    
    successElement.textContent = message;
    successElement.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        successElement.style.display = 'none';
    }, 5000);
}

// Load sensor stats
async function loadSensorStats() {
    try {
        const stats = await apiClient.request('/api/admin/sensors/stats');
        document.getElementById('sensor-stats').innerHTML = `
            <div class="stat-item">
                <h4>Total Sensors</h4>
                <p class="stat-number">${stats.total_sensors || 0}</p>
            </div>
            <div class="stat-item">
                <h4>Active Sensors</h4>
                <p class="stat-number" style="color: #4CAF50;">${stats.active_sensors || 0}</p>
            </div>
            <div class="stat-item">
                <h4>Inactive Sensors</h4>
                <p class="stat-number" style="color: #f44336;">${stats.inactive_sensors || 0}</p>
            </div>
            <div class="stat-item">
                <h4>Readings (24h)</h4>
                <p class="stat-number">${stats.readings_last_24h || 0}</p>
            </div>
        `;
    } catch (error) {
        console.error('Failed to load sensor stats:', error);
    }
}

// Load sensors overview
async function loadSensorsOverview() {
    try {
        const hospitalFilter = document.getElementById('sensor-hospital-filter')?.value || '';
        const regionFilter = document.getElementById('sensor-region-filter')?.value || '';
        const searchFilter = document.getElementById('sensor-search')?.value || '';
        
        let url = '/api/admin/sensors/overview?';
        if (hospitalFilter) url += `hospital_id=${hospitalFilter}&`;
        if (regionFilter) url += `region_id=${regionFilter}&`;
        if (searchFilter) url += `sensor_id=${searchFilter}&`;
        
        const sensors = await apiClient.request(url);
        const overviewElement = document.getElementById('sensors-overview');
        
        if (!sensors || sensors.length === 0) {
            overviewElement.innerHTML = '<p>No sensors found.</p>';
            return;
        }
        
        overviewElement.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Sensor ID</th>
                        <th>Hospital</th>
                        <th>Region</th>
                        <th>Last Reading</th>
                        <th>Temp</th>
                        <th>Humidity</th>
                        <th>Air Quality</th>
                        <th>Status</th>
                        <th>Total Readings</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${sensors.map(sensor => `
                        <tr class="sensor-row">
                            <td><strong>${escapeHtml(sensor.sensor_id)}</strong></td>
                            <td>${escapeHtml(sensor.hospital_name)}</td>
                            <td>${escapeHtml(sensor.region_name)}</td>
                            <td>${new Date(sensor.last_reading_timestamp).toLocaleString()}</td>
                            <td>${sensor.temperature !== null ? sensor.temperature.toFixed(1) + '°C' : 'N/A'}</td>
                            <td>${sensor.humidity !== null ? sensor.humidity.toFixed(1) + '%' : 'N/A'}</td>
                            <td>${sensor.air_quality !== null ? sensor.air_quality.toFixed(0) : 'N/A'}</td>
                            <td>
                                <span class="status-badge ${sensor.is_active ? 'status-active' : 'status-inactive'}">
                                    ${sensor.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </td>
                            <td>${sensor.total_readings}</td>
                            <td>
                                <button class="btn btn-small btn-primary" onclick="viewSensorDetails('${escapeHtml(sensor.sensor_id)}', ${sensor.hospital_id})">
                                    View Details
                                </button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Failed to load sensors overview:', error);
        document.getElementById('sensors-overview').innerHTML = '<p>Failed to load sensors</p>';
    }
}

// View sensor details - global function for onclick
async function viewSensorDetails(sensorId, hospitalId) {
    try {
        const history = await apiClient.request(`/api/admin/sensors/${sensorId}/history?hospital_id=${hospitalId}&limit=50`);
        
        const modal = document.getElementById('sensor-modal');
        const content = document.getElementById('sensor-modal-content');
        
        if (history.length === 0) {
            content.innerHTML = `<p>No history found for sensor ${escapeHtml(sensorId)}</p>`;
        } else {
            content.innerHTML = `
                <h3>Sensor: ${escapeHtml(sensorId)}</h3>
                <p><strong>Hospital ID:</strong> ${hospitalId}</p>
                <p><strong>Total Records:</strong> ${history.length}</p>
                
                <h4>Recent Readings</h4>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Temperature</th>
                            <th>Humidity</th>
                            <th>Air Quality</th>
                            <th>Custom Data</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${history.map(record => `
                            <tr>
                                <td>${new Date(record.timestamp).toLocaleString()}</td>
                                <td>${record.temperature !== null ? record.temperature.toFixed(1) + '°C' : 'N/A'}</td>
                                <td>${record.humidity !== null ? record.humidity.toFixed(1) + '%' : 'N/A'}</td>
                                <td>${record.air_quality !== null ? record.air_quality.toFixed(0) : 'N/A'}</td>
                                <td><pre style="font-size: 0.8rem; max-width: 200px; overflow-x: auto;">${JSON.stringify(record.data_json, null, 2)}</pre></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
        
        modal.style.display = 'block';
    } catch (error) {
        showError('Failed to load sensor details: ' + error.message);
    }
}

// Load API keys
async function loadAPIKeys() {
    try {
        const apiKeys = await apiClient.request('/api/admin/api-keys');
        const hospitals = await apiClient.request('/api/admin/hospitals');
        const listElement = document.getElementById('api-keys-list');
        
        // Create hospital ID to name mapping
        const hospitalMap = {};
        hospitals.forEach(h => {
            hospitalMap[h.id] = h.name;
        });
        
        if (!apiKeys || apiKeys.length === 0) {
            listElement.innerHTML = '<p>No API keys found. Generate one to get started.</p>';
            return;
        }
        
        listElement.innerHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Sensor ID</th>
                        <th>Key (truncated)</th>
                        <th>Hospital</th>
                        <th>Description</th>
                        <th>Status</th>
                        <th>Validated</th>
                        <th>Created</th>
                        <th>Last Used</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${apiKeys.map(key => `
                        <tr>
                            <td><strong>${escapeHtml(key.sensor_id)}</strong></td>
                            <td><code>${escapeHtml(key.key.substring(0, 12))}...</code></td>
                            <td>${hospitalMap[key.hospital_id] || `ID: ${key.hospital_id}`}</td>
                            <td>${escapeHtml(key.description || 'N/A')}</td>
                            <td>
                                <span class="status-badge ${key.is_active ? 'status-active' : 'status-inactive'}">
                                    ${key.is_active ? 'Active' : 'Revoked'}
                                </span>
                            </td>
                            <td>
                                ${key.is_validated 
                                    ? '<span class="status-badge status-active">✓ Validated</span>' 
                                    : `<button class="btn btn-small btn-primary" onclick="validateAPIKey(${key.id})">Validate</button>`
                                }
                            </td>
                            <td>${new Date(key.created_at).toLocaleDateString()}</td>
                            <td>${key.last_used ? new Date(key.last_used).toLocaleString() : 'Never'}</td>
                            <td>
                                ${key.is_active ? `<button class="btn btn-small btn-danger" onclick="revokeAPIKey(${key.id})">Revoke</button>` : ''}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Failed to load API keys:', error);
    }
}

// Validate API key - global function for onclick
async function validateAPIKey(keyId) {
    try {
        await apiClient.request(`/api/admin/api-keys/${keyId}/validate`, { method: 'PUT' });
        showSuccess('API key validated successfully');
        await loadAPIKeys();
    } catch (error) {
        showError('Failed to validate API key: ' + error.message);
    }
}

// Revoke API key - global function for onclick
async function revokeAPIKey(keyId) {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
        return;
    }
    
    try {
        await apiClient.request(`/api/admin/api-keys/${keyId}`, { method: 'DELETE' });
        showSuccess('API key revoked successfully');
        await loadAPIKeys();
    } catch (error) {
        showError('Failed to revoke API key: ' + error.message);
    }
}

// Load allowed emails
async function loadAllowedEmails() {
    try {
        const emails = await apiClient.request('/api/admin/allowed-emails');
        const listElement = document.getElementById('allowed-emails-list');
        
        if (!emails || emails.length === 0) {
            listElement.innerHTML = '<p>No whitelisted emails found. Add one to allow registrations.</p>';
            return;
        }
        
        listElement.innerHTML = `
            <p style="margin-bottom: 1rem; color: #666;">
                <strong>Note:</strong> You can whitelist specific emails (e.g., user@example.com) or entire domains (e.g., @example.com)
            </p>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Email/Domain</th>
                        <th>Added</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${emails.map(email => `
                        <tr>
                            <td><strong>${escapeHtml(email.email)}</strong>${email.email.startsWith('@') ? ' <span style="color: #4CAF50;">(Domain)</span>' : ''}</td>
                            <td>${new Date(email.created_at).toLocaleDateString()}</td>
                            <td>
                                <button class="btn btn-small btn-danger" onclick="deleteAllowedEmail(${email.id})">Remove</button>
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } catch (error) {
        console.error('Failed to load allowed emails:', error);
    }
}

// Delete allowed email - global function for onclick
async function deleteAllowedEmail(emailId) {
    if (!confirm('Are you sure you want to remove this email from the whitelist?')) {
        return;
    }
    
    try {
        await apiClient.request(`/api/admin/allowed-emails/${emailId}`, { method: 'DELETE' });
        showSuccess('Email removed from whitelist successfully');
        await loadAllowedEmails();
    } catch (error) {
        showError('Failed to remove email: ' + error.message);
    }
}

// Setup admin event listeners
function setupAdminEventListeners() {
    // Modal close buttons
    document.querySelectorAll('.modal-close').forEach(closeBtn => {
        closeBtn.onclick = function() {
            this.closest('.modal').style.display = 'none';
        };
    });
    
    // Close modals when clicking outside
    window.onclick = function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    };
    
    // Refresh all button
    document.getElementById('refresh-all-btn')?.addEventListener('click', async () => {
        await loadDashboardByRole();
        showSuccess('Data refreshed');
    });
    
    // Sensor filter button
    document.getElementById('sensor-filter-btn')?.addEventListener('click', async () => {
        await loadSensorsOverview();
    });
    
    // Region management buttons
    document.getElementById('add-region-btn')?.addEventListener('click', () => {
        document.getElementById('add-region-form').style.display = 'block';
        document.getElementById('add-region-btn').style.display = 'none';
    });
    
    document.getElementById('cancel-region-btn')?.addEventListener('click', () => {
        document.getElementById('add-region-form').style.display = 'none';
        document.getElementById('add-region-btn').style.display = 'block';
        document.getElementById('region-name').value = '';
        document.getElementById('region-code').value = '';
    });
    
    document.getElementById('cancel-edit-region-btn')?.addEventListener('click', () => {
        document.getElementById('edit-region-form').style.display = 'none';
    });
    
    document.getElementById('update-region-btn')?.addEventListener('click', async () => {
        const regionId = document.getElementById('edit-region-id').value;
        const name = document.getElementById('edit-region-name').value;
        const code = document.getElementById('edit-region-code').value;
        
        if (!name || !code) {
            showError('Please fill in all required fields');
            return;
        }
        
        try {
            await apiClient.request(`/api/admin/regions/${regionId}`, {
                method: 'PUT',
                body: JSON.stringify({ name, code })
            });
            
            showSuccess('Region updated successfully');
            document.getElementById('edit-region-form').style.display = 'none';
            await loadRegions();
        } catch (error) {
            showError('Failed to update region: ' + error.message);
        }
    });
    
    document.getElementById('save-region-btn')?.addEventListener('click', async () => {
        const name = document.getElementById('region-name').value;
        const code = document.getElementById('region-code').value;
        
        if (!name || !code) {
            showError('Please fill in all required fields');
            return;
        }
        
        try {
            await apiClient.request('/api/admin/regions', {
                method: 'POST',
                body: JSON.stringify({ name, code })
            });
            
            showSuccess('Region created successfully');
            document.getElementById('add-region-form').style.display = 'none';
            document.getElementById('add-region-btn').style.display = 'block';
            document.getElementById('region-name').value = '';
            document.getElementById('region-code').value = '';
            
            await loadRegions();
            await populateRegionDropdowns();
        } catch (error) {
            showError('Failed to create region: ' + error.message);
        }
    });
    
    // Hospital management buttons
    document.getElementById('add-hospital-btn')?.addEventListener('click', () => {
        document.getElementById('add-hospital-form').style.display = 'block';
        document.getElementById('add-hospital-btn').style.display = 'none';
    });
    
    document.getElementById('cancel-hospital-btn')?.addEventListener('click', () => {
        document.getElementById('add-hospital-form').style.display = 'none';
        document.getElementById('add-hospital-btn').style.display = 'block';
        clearHospitalForm();
    });
    
    document.getElementById('cancel-edit-hospital-btn')?.addEventListener('click', () => {
        document.getElementById('edit-hospital-form').style.display = 'none';
    });
    
    document.getElementById('update-hospital-btn')?.addEventListener('click', async () => {
        const hospitalId = document.getElementById('edit-hospital-id').value;
        const name = document.getElementById('edit-hospital-name').value;
        const code = document.getElementById('edit-hospital-code').value;
        const region_id = parseInt(document.getElementById('edit-hospital-region').value);
        const address = document.getElementById('edit-hospital-address').value;
        
        if (!name || !code || !region_id) {
            showError('Please fill in all required fields');
            return;
        }
        
        try {
            await apiClient.request(`/api/admin/hospitals/${hospitalId}`, {
                method: 'PUT',
                body: JSON.stringify({ name, code, region_id, address: address || null })
            });
            
            showSuccess('Hospital updated successfully');
            document.getElementById('edit-hospital-form').style.display = 'none';
            await loadHospitals();
        } catch (error) {
            showError('Failed to update hospital: ' + error.message);
        }
    });
    
    document.getElementById('save-hospital-btn')?.addEventListener('click', async () => {
        const name = document.getElementById('hospital-name').value;
        const code = document.getElementById('hospital-code').value;
        const region_id = parseInt(document.getElementById('hospital-region').value);
        const address = document.getElementById('hospital-address').value;
        
        if (!name || !code || !region_id) {
            showError('Please fill in all required fields');
            return;
        }
        
        try {
            await apiClient.request('/api/admin/hospitals', {
                method: 'POST',
                body: JSON.stringify({ name, code, region_id, address: address || null })
            });
            
            showSuccess('Hospital created successfully');
            document.getElementById('add-hospital-form').style.display = 'none';
            document.getElementById('add-hospital-btn').style.display = 'block';
            clearHospitalForm();
            
            await loadHospitals();
            await populateHospitalDropdowns();
        } catch (error) {
            showError('Failed to create hospital: ' + error.message);
        }
    });
    
    // API Key management buttons
    document.getElementById('add-api-key-btn')?.addEventListener('click', () => {
        document.getElementById('add-api-key-form').style.display = 'block';
        document.getElementById('add-api-key-btn').style.display = 'none';
    });
    
    document.getElementById('cancel-api-key-btn')?.addEventListener('click', () => {
        document.getElementById('add-api-key-form').style.display = 'none';
        document.getElementById('add-api-key-btn').style.display = 'block';
        document.getElementById('api-key-hospital').value = '';
        document.getElementById('api-key-sensor-id').value = '';
        document.getElementById('api-key-description').value = '';
    });
    
    document.getElementById('save-api-key-btn')?.addEventListener('click', async () => {
        const hospital_id = parseInt(document.getElementById('api-key-hospital').value);
        const sensor_id = document.getElementById('api-key-sensor-id').value.trim();
        const description = document.getElementById('api-key-description').value;
        
        if (!hospital_id) {
            showError('Please select a hospital');
            return;
        }
        
        if (!sensor_id) {
            showError('Please enter a sensor ID');
            return;
        }
        
        try {
            const result = await apiClient.request('/api/admin/api-keys', {
                method: 'POST',
                body: JSON.stringify({ sensor_id, hospital_id, description: description || null })
            });
            
            // Show the generated key in a modal with copy functionality
            const modal = document.getElementById('sensor-modal');
            const content = document.getElementById('sensor-modal-content');
            content.innerHTML = `
                <h3 style="color: #4CAF50;">✓ API Key Generated Successfully</h3>
                <div style="background: #fff3cd; border: 1px solid #ffc107; padding: 1rem; border-radius: 4px; margin: 1rem 0;">
                    <p style="margin: 0; font-weight: bold;">⚠️ IMPORTANT: Save this key securely!</p>
                    <p style="margin: 0.5rem 0 0 0;">This key will only be shown once and cannot be retrieved later.</p>
                    <p style="margin: 0.5rem 0 0 0; color: #856404;">⚠️ Key requires admin validation before it can be used.</p>
                </div>
                <div class="form-group">
                    <label><strong>Sensor ID:</strong></label>
                    <input type="text" value="${escapeHtml(result.sensor_id)}" readonly style="font-family: monospace;">
                </div>
                <div class="form-group">
                    <label><strong>API Key:</strong></label>
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="text" id="generated-api-key" value="${escapeHtml(result.key)}" readonly style="flex: 1; font-family: monospace;">
                        <button id="copy-api-key-btn" class="btn btn-primary">Copy</button>
                    </div>
                </div>
                <p style="margin-top: 1rem;">Use this key in the <code>X-API-Key</code> header when sending sensor data.</p>
                <p>The sensor_id in your data must match: <code>${escapeHtml(result.sensor_id)}</code></p>
            `;
            modal.style.display = 'block';
            
            // Add copy functionality
            document.getElementById('copy-api-key-btn').addEventListener('click', () => {
                const keyInput = document.getElementById('generated-api-key');
                keyInput.select();
                document.execCommand('copy');
                showSuccess('API key copied to clipboard!');
            });
            
            showSuccess('API key generated successfully');
            document.getElementById('add-api-key-form').style.display = 'none';
            document.getElementById('add-api-key-btn').style.display = 'block';
            document.getElementById('api-key-hospital').value = '';
            document.getElementById('api-key-sensor-id').value = '';
            document.getElementById('api-key-description').value = '';
            
            await loadAPIKeys();
        } catch (error) {
            showError('Failed to generate API key: ' + error.message);
        }
    });
    
    // Email whitelist management buttons
    document.getElementById('add-email-btn')?.addEventListener('click', () => {
        document.getElementById('add-email-form').style.display = 'block';
        document.getElementById('add-email-btn').style.display = 'none';
    });
    
    document.getElementById('cancel-email-btn')?.addEventListener('click', () => {
        document.getElementById('add-email-form').style.display = 'none';
        document.getElementById('add-email-btn').style.display = 'block';
        document.getElementById('whitelist-email').value = '';
    });
    
    document.getElementById('save-email-btn')?.addEventListener('click', async () => {
        const email = document.getElementById('whitelist-email').value.trim();
        
        if (!email) {
            showError('Please enter an email address or domain');
            return;
        }
        
        // Validate format - allow email or @domain.com format
        if (!email.includes('@')) {
            showError('Please enter a valid email address or domain (e.g., @domain.com)');
            return;
        }
        
        // More robust validation
        const emailParts = email.split('@');
        if (emailParts.length !== 2 || !emailParts[1]) {
            showError('Invalid format. Use email@domain.com or @domain.com');
            return;
        }
        
        // For domain format, ensure there's content after @
        if (emailParts[0] === '' && !emailParts[1].includes('.')) {
            showError('Domain must include a TLD (e.g., @domain.com)');
            return;
        }
        
        try {
            await apiClient.request('/api/admin/allowed-emails', {
                method: 'POST',
                body: JSON.stringify({ email })
            });
            
            showSuccess('Email/domain added to whitelist successfully');
            document.getElementById('add-email-form').style.display = 'none';
            document.getElementById('add-email-btn').style.display = 'block';
            document.getElementById('whitelist-email').value = '';
            
            await loadAllowedEmails();
        } catch (error) {
            showError('Failed to add email/domain to whitelist: ' + error.message);
        }
    });
    
    // Setup audit log event listeners
    setupAuditLogEventListeners();
    
    // Initialize hospital location pickers if available
    initializeCreateHospitalLocationPicker();
    initializeEditHospitalLocationPicker();
}

// Helper to clear hospital form
function clearHospitalForm() {
    document.getElementById('hospital-name').value = '';
    document.getElementById('hospital-code').value = '';
    document.getElementById('hospital-region').value = '';
    document.getElementById('hospital-address').value = '';
}

// Populate region dropdowns
async function populateRegionDropdowns() {
    try {
        const regions = await apiClient.request('/api/admin/regions');
        
        // Populate hospital form region dropdown
        const hospitalRegionSelect = document.getElementById('hospital-region');
        if (hospitalRegionSelect) {
            hospitalRegionSelect.innerHTML = '<option value="">Select a region...</option>' +
                regions.map(r => `<option value="${r.id}">${escapeHtml(r.name)}</option>`).join('');
        }
        
        // Populate edit hospital form region dropdown
        const editHospitalRegionSelect = document.getElementById('edit-hospital-region');
        if (editHospitalRegionSelect) {
            editHospitalRegionSelect.innerHTML = '<option value="">Select a region...</option>' +
                regions.map(r => `<option value="${r.id}">${escapeHtml(r.name)}</option>`).join('');
        }
        
        // Populate sensor filter region dropdown
        const sensorRegionFilter = document.getElementById('sensor-region-filter');
        if (sensorRegionFilter) {
            sensorRegionFilter.innerHTML = '<option value="">All Regions</option>' +
                regions.map(r => `<option value="${r.id}">${escapeHtml(r.name)}</option>`).join('');
        }
    } catch (error) {
        console.error('Failed to populate region dropdowns:', error);
    }
}

// Populate hospital dropdowns
async function populateHospitalDropdowns() {
    try {
        const hospitals = await apiClient.request('/api/admin/hospitals');
        
        // Populate API key hospital dropdown
        const apiKeyHospitalSelect = document.getElementById('api-key-hospital');
        if (apiKeyHospitalSelect) {
            apiKeyHospitalSelect.innerHTML = '<option value="">Select a hospital...</option>' +
                hospitals.map(h => `<option value="${h.id}">${escapeHtml(h.name)}</option>`).join('');
        }
        
        // Populate sensor filter hospital dropdown
        const sensorHospitalFilter = document.getElementById('sensor-hospital-filter');
        if (sensorHospitalFilter) {
            sensorHospitalFilter.innerHTML = '<option value="">All Hospitals</option>' +
                hospitals.map(h => `<option value="${h.id}">${escapeHtml(h.name)}</option>`).join('');
        }
    } catch (error) {
        console.error('Failed to populate hospital dropdowns:', error);
    }
}

// Show error message
function showError(message) {
    const errorElement = document.getElementById('error-message');
    errorElement.textContent = message;
    errorElement.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        errorElement.style.display = 'none';
    }, 5000);
}

// Edit user role - global function for onclick
async function editUserRole(userId) {
    try {
        // Get user details
        const users = await apiClient.request('/api/admin/users');
        const user = users.find(u => u.id === userId);
        
        if (!user) {
            showError('User not found');
            return;
        }

        // Get regions and hospitals for dropdowns
        const regions = await apiClient.request('/api/admin/regions');
        const hospitals = await apiClient.request('/api/admin/hospitals');

        // Show modal with edit form
        const modal = document.getElementById('user-role-modal');
        const content = document.getElementById('user-role-modal-content');
        
        content.innerHTML = `
            <div class="form-group">
                <label><strong>User:</strong> ${escapeHtml(user.username)} (${escapeHtml(user.email)})</label>
            </div>
            <div class="form-group">
                <label for="edit-user-role">Role *</label>
                <select id="edit-user-role" required>
                    <option value="1" ${user.role === 1 ? 'selected' : ''}>Pending</option>
                    <option value="2" ${user.role === 2 ? 'selected' : ''}>Admin</option>
                    <option value="3" ${user.role === 3 ? 'selected' : ''}>Region Admin</option>
                    <option value="4" ${user.role === 4 ? 'selected' : ''}>Hospital User</option>
                </select>
            </div>
            <div class="form-group">
                <label for="edit-user-region">Region</label>
                <select id="edit-user-region">
                    <option value="">None</option>
                    ${regions.map(r => `<option value="${r.id}" ${user.region_id === r.id ? 'selected' : ''}>${escapeHtml(r.name)}</option>`).join('')}
                </select>
            </div>
            <div class="form-group">
                <label for="edit-user-hospital">Hospital</label>
                <select id="edit-user-hospital">
                    <option value="">None</option>
                    ${hospitals.map(h => `<option value="${h.id}" ${user.hospital_id === h.id ? 'selected' : ''}>${escapeHtml(h.name)}</option>`).join('')}
                </select>
            </div>
            <button id="save-user-role-btn" class="btn btn-success">Save Changes</button>
        `;

        modal.style.display = 'block';

        // Function to update hospital dropdown based on selected region
        function updateHospitalDropdown(selectedRegionId, currentHospitalId) {
            const hospitalSelect = document.getElementById('edit-user-hospital');
            
            // Filter hospitals by region
            let filteredHospitals = hospitals;
            if (selectedRegionId) {
                filteredHospitals = hospitals.filter(h => h.region_id === parseInt(selectedRegionId));
            }
            
            // Ensure currentHospitalId is a number for comparison
            const hospitalIdNum = currentHospitalId ? parseInt(currentHospitalId) : null;
            
            // Update hospital dropdown
            hospitalSelect.innerHTML = `
                <option value="">None</option>
                ${filteredHospitals.map(h => `<option value="${h.id}" ${hospitalIdNum === h.id ? 'selected' : ''}>${escapeHtml(h.name)}</option>`).join('')}
            `;
            
            // If current hospital is not in filtered list, it will be automatically reset to "None"
        }
        
        // Apply initial filter - always call to ensure consistent behavior
        updateHospitalDropdown(user.region_id, user.hospital_id);
        
        // Add event listener for region dropdown changes
        document.getElementById('edit-user-region').addEventListener('change', (e) => {
            const selectedRegionId = e.target.value;
            const currentHospitalSelection = document.getElementById('edit-user-hospital').value;
            updateHospitalDropdown(selectedRegionId, currentHospitalSelection);
        });

        // Save button handler
        document.getElementById('save-user-role-btn').addEventListener('click', async () => {
            const newRole = parseInt(document.getElementById('edit-user-role').value);
            const newRegionId = document.getElementById('edit-user-region').value;
            const newHospitalId = document.getElementById('edit-user-hospital').value;

            try {
                // Update role
                await apiClient.request(`/api/admin/users/${userId}/role`, {
                    method: 'POST',
                    body: JSON.stringify({ role: newRole })
                });

                // Update assignment
                await apiClient.request(`/api/admin/users/${userId}/assign`, {
                    method: 'POST',
                    body: JSON.stringify({
                        region_id: newRegionId ? parseInt(newRegionId) : null,
                        hospital_id: newHospitalId ? parseInt(newHospitalId) : null
                    })
                });

                showSuccess('User updated successfully');
                modal.style.display = 'none';
                await loadAdminUsers();
            } catch (error) {
                showError('Failed to update user: ' + error.message);
            }
        });
    } catch (error) {
        showError('Failed to load user data: ' + error.message);
    }
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ================== Audit Log Functions ==================

// Load and display audit logs with current filters
async function loadAuditLogs() {
    try {
        // Get filter values from form inputs
        const startDate = document.getElementById('audit-start-date')?.value || '';
        const endDate = document.getElementById('audit-end-date')?.value || '';
        const userId = document.getElementById('audit-user-filter')?.value || '';
        const action = document.getElementById('audit-action-filter')?.value || '';
        const resourceType = document.getElementById('audit-resource-filter')?.value || '';
        const status = document.getElementById('audit-status-filter')?.value || '';
        const limit = parseInt(document.getElementById('audit-limit')?.value) || 50;
        const offset = parseInt(document.getElementById('audit-offset')?.value) || 0;
        
        // Build query parameters
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        if (userId) params.append('user_id', userId);
        if (action) params.append('action', action);
        if (resourceType) params.append('resource_type', resourceType);
        if (status) params.append('status', status);
        params.append('limit', limit.toString());
        params.append('offset', offset.toString());
        
        // Make API call
        const response = await apiClient.request(`/api/admin/audit-logs?${params.toString()}`);
        
        const auditLogsTable = document.getElementById('audit-logs-table');
        if (!auditLogsTable) return;
        
        const logs = response.logs || [];
        const total = response.total || 0;
        
        if (logs.length === 0) {
            auditLogsTable.innerHTML = '<p style="text-align: center; padding: 2rem; color: #888;">No audit logs found.</p>';
        } else {
            // Populate the audit logs table
            auditLogsTable.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>User</th>
                            <th>Action</th>
                            <th>Resource</th>
                            <th>Status</th>
                            <th>IP Address</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${logs.map(log => `
                            <tr>
                                <td>${new Date(log.timestamp).toLocaleString()}</td>
                                <td>${escapeHtml(log.username || 'N/A')}</td>
                                <td><strong>${formatActionName(log.action)}</strong></td>
                                <td>${escapeHtml(log.resource_type || 'N/A')}</td>
                                <td><span class="status-badge status-${log.status}">${log.status}</span></td>
                                <td>${escapeHtml(log.ip_address || 'N/A')}</td>
                                <td>${formatAuditDetails(log.details)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
        
        // Update pagination info
        const currentPage = Math.floor(offset / limit) + 1;
        const totalPages = Math.ceil(total / limit);
        const paginationInfo = document.getElementById('audit-pagination-info');
        if (paginationInfo) {
            paginationInfo.textContent = `Page ${currentPage} of ${totalPages} (${total} total records)`;
        }
        
        // Update pagination buttons
        const prevBtn = document.getElementById('audit-prev-btn');
        const nextBtn = document.getElementById('audit-next-btn');
        if (prevBtn) prevBtn.disabled = offset === 0;
        if (nextBtn) nextBtn.disabled = offset + limit >= total;
        
    } catch (error) {
        console.error('Failed to load audit logs:', error);
        showError('Failed to load audit logs: ' + error.message);
    }
}

// Filter audit logs - reset to first page and reload
async function filterAuditLogs() {
    const offsetInput = document.getElementById('audit-offset');
    if (offsetInput) offsetInput.value = '0';
    await loadAuditLogs();
}

// Clear all audit log filters
async function clearAuditFilters() {
    const filterInputs = [
        'audit-start-date',
        'audit-end-date',
        'audit-user-filter',
        'audit-action-filter',
        'audit-resource-filter',
        'audit-status-filter'
    ];
    
    filterInputs.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.value = '';
    });
    
    const limitInput = document.getElementById('audit-limit');
    if (limitInput) limitInput.value = '50';
    
    await filterAuditLogs();
}

// Load and display audit log statistics
async function loadAuditStats() {
    try {
        const stats = await apiClient.request('/api/admin/audit-logs/stats');
        
        // Update stat cards
        const actionsToday = document.getElementById('audit-actions-today');
        if (actionsToday) actionsToday.textContent = stats.actions_today || 0;
        
        const actionsWeek = document.getElementById('audit-actions-week');
        if (actionsWeek) actionsWeek.textContent = stats.actions_this_week || 0;
        
        const actionsMonth = document.getElementById('audit-actions-month');
        if (actionsMonth) actionsMonth.textContent = stats.actions_this_month || 0;
        
        const failedLogins = document.getElementById('audit-failed-logins');
        if (failedLogins) failedLogins.textContent = stats.failed_logins || 0;
        
        // Populate top users table
        const topUsersTable = document.getElementById('audit-top-users');
        if (topUsersTable && stats.top_users) {
            if (stats.top_users.length === 0) {
                topUsersTable.innerHTML = '<p style="text-align: center; color: #888;">No data available.</p>';
            } else {
                topUsersTable.innerHTML = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Action Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${stats.top_users.map(user => `
                                <tr>
                                    <td>${escapeHtml(user.username)}</td>
                                    <td><strong>${user.action_count}</strong></td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            }
        }
        
        // Populate recent critical actions table
        const criticalActionsTable = document.getElementById('audit-critical-actions');
        if (criticalActionsTable && stats.recent_critical) {
            if (stats.recent_critical.length === 0) {
                criticalActionsTable.innerHTML = '<p style="text-align: center; color: #888;">No critical actions recorded.</p>';
            } else {
                criticalActionsTable.innerHTML = `
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>User</th>
                                <th>Action</th>
                                <th>Resource</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${stats.recent_critical.map(action => `
                                <tr>
                                    <td>${new Date(action.timestamp).toLocaleString()}</td>
                                    <td>${escapeHtml(action.username || 'N/A')}</td>
                                    <td><strong>${formatActionName(action.action)}</strong></td>
                                    <td>${escapeHtml(action.resource_type || 'N/A')}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;
            }
        }
        
    } catch (error) {
        console.error('Failed to load audit stats:', error);
        showError('Failed to load audit statistics: ' + error.message);
    }
}

// ================== Helper Functions ==================

// Format action name from snake_case to Title Case
function formatActionName(action) {
    if (!action) return 'N/A';
    return action
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
}

// Format audit details object into readable text
function formatAuditDetails(details) {
    if (!details) return 'N/A';
    
    try {
        // If details is a string, try to parse it as JSON
        const detailsObj = typeof details === 'string' ? JSON.parse(details) : details;
        
        if (typeof detailsObj === 'object' && detailsObj !== null) {
            // Convert object to readable key-value pairs
            const entries = Object.entries(detailsObj)
                .filter(([key, value]) => value !== null && value !== undefined)
                .map(([key, value]) => {
                    const formattedKey = formatActionName(key);
                    const formattedValue = typeof value === 'object' ? JSON.stringify(value) : value;
                    return `${formattedKey}: ${formattedValue}`;
                })
                .join(', ');
            
            return truncateString(entries, 100) || 'N/A';
        }
        
        return truncateString(String(detailsObj), 100);
    } catch (error) {
        // If parsing fails, return the string as-is
        return truncateString(String(details), 100);
    }
}

// Truncate long strings with ellipsis
function truncateString(str, length) {
    if (!str) return '';
    if (str.length <= length) return escapeHtml(str);
    return escapeHtml(str.substring(0, length)) + '...';
}

// ================== Audit Log Event Listeners ==================

// Setup audit log event listeners (should be called from setupAdminEventListeners)
function setupAuditLogEventListeners() {
    // Filter button
    const filterBtn = document.getElementById('audit-apply-filters-btn');
    if (filterBtn) {
        filterBtn.addEventListener('click', async () => {
            await filterAuditLogs();
        });
    }
    
    // Clear filters button
    const clearBtn = document.getElementById('audit-clear-filters-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', async () => {
            await clearAuditFilters();
        });
    }
    
    // Pagination - Previous button
    const prevBtn = document.getElementById('audit-prev-btn');
    if (prevBtn) {
        prevBtn.addEventListener('click', async () => {
            const offsetInput = document.getElementById('audit-offset');
            const limitInput = document.getElementById('audit-limit');
            if (offsetInput && limitInput) {
                const limit = parseInt(limitInput.value) || 50;
                const currentOffset = parseInt(offsetInput.value) || 0;
                const newOffset = Math.max(0, currentOffset - limit);
                offsetInput.value = newOffset.toString();
                await loadAuditLogs();
            }
        });
    }
    
    // Pagination - Next button
    const nextBtn = document.getElementById('audit-next-btn');
    if (nextBtn) {
        nextBtn.addEventListener('click', async () => {
            const offsetInput = document.getElementById('audit-offset');
            const limitInput = document.getElementById('audit-limit');
            if (offsetInput && limitInput) {
                const limit = parseInt(limitInput.value) || 50;
                const currentOffset = parseInt(offsetInput.value) || 0;
                offsetInput.value = (currentOffset + limit).toString();
                await loadAuditLogs();
            }
        });
    }
}

// ================== Hospital Location Picker Functions ==================

// Initialize location picker for create hospital form
function initializeCreateHospitalLocationPicker() {
    const pickOnMapBtn = document.getElementById('pick-location-btn');
    const mapContainer = document.getElementById('location-picker-map');
    const latInput = document.getElementById('hospital-latitude');
    const lonInput = document.getElementById('hospital-longitude');
    
    if (!pickOnMapBtn || !mapContainer) return;
    
    let pickerInstance = null;
    
    // Toggle map visibility
    pickOnMapBtn.addEventListener('click', () => {
        const isVisible = mapContainer.style.display === 'block';
        mapContainer.style.display = isVisible ? 'none' : 'block';
        pickOnMapBtn.textContent = isVisible ? '📍 Pick on Map' : 'Hide Map';
        
        // Initialize map if showing
        if (!isVisible && typeof initializeLocationPicker === 'function') {
            const defaultLat = parseFloat(latInput?.value) || 50.8503;
            const defaultLon = parseFloat(lonInput?.value) || 4.3517;
            pickerInstance = initializeLocationPicker(
                'location-picker-map',
                defaultLat,
                defaultLon,
                (lat, lon) => {
                    if (latInput) latInput.value = lat.toFixed(6);
                    if (lonInput) lonInput.value = lon.toFixed(6);
                }
            );
        }
    });
}

// Initialize location picker for edit hospital form
function initializeEditHospitalLocationPicker() {
    const pickOnMapBtn = document.getElementById('edit-pick-location-btn');
    const mapContainer = document.getElementById('edit-location-picker-map');
    const latInput = document.getElementById('edit-hospital-latitude');
    const lonInput = document.getElementById('edit-hospital-longitude');
    
    if (!pickOnMapBtn || !mapContainer) return;
    
    let pickerInstance = null;
    
    // Toggle map visibility
    pickOnMapBtn.addEventListener('click', () => {
        const isVisible = mapContainer.style.display === 'block';
        mapContainer.style.display = isVisible ? 'none' : 'block';
        pickOnMapBtn.textContent = isVisible ? '📍 Pick on Map' : 'Hide Map';
        
        // Initialize map if showing
        if (!isVisible && typeof initializeLocationPicker === 'function') {
            const currentLat = parseFloat(latInput?.value) || 50.8503;
            const currentLon = parseFloat(lonInput?.value) || 4.3517;
            pickerInstance = initializeLocationPicker(
                'edit-location-picker-map',
                currentLat,
                currentLon,
                (lat, lon) => {
                    if (latInput) latInput.value = lat.toFixed(6);
                    if (lonInput) lonInput.value = lon.toFixed(6);
                }
            );
        }
    });
}

