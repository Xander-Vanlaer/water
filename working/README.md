# Secure Full-Stack Application with RBAC

A production-ready, secure web application featuring Docker containerization, FastAPI backend, PostgreSQL database, Redis session management, comprehensive 2FA authentication, and role-based access control (RBAC) for hospital/region management with IoT sensor data ingestion.

## 🌟 Features

### Security Features
- ✅ **Bcrypt Password Hashing** - All passwords securely hashed with bcrypt
- ✅ **JWT Authentication** - Secure token-based authentication with refresh tokens
- ✅ **2FA/TOTP** - Time-based One-Time Password (compatible with Google Authenticator, Authy)
- ✅ **Rate Limiting** - Protection against brute-force attacks
- ✅ **SQL Injection Prevention** - Using SQLAlchemy ORM with parameterized queries
- ✅ **XSS Protection** - Input sanitization and output escaping
- ✅ **CSRF Protection** - Secure state-changing operations
- ✅ **Security Headers** - X-Frame-Options, X-Content-Type-Options, etc.
- ✅ **Account Lockout** - Temporary lockout after failed login attempts
- ✅ **Password Complexity** - Enforced password requirements
- ✅ **Environment-based Secrets** - No hardcoded credentials
- ✅ **API Key Authentication** - Secure sensor data ingestion with API keys
- ✅ **Audit Logging** - Comprehensive action tracking for security and compliance

### RBAC Features
- 🔐 **Role-Based Access Control** - 4 user roles with different permissions
- 🏥 **Hospital Management** - Manage hospitals and assign users
- 🌍 **Region Management** - Regional organization with region admins
- 📊 **IoT Sensor Integration** - Secure API for Orange Pi sensor data ingestion
- 📈 **Dashboard Analytics** - Role-filtered statistics and visualizations
- 🗺️ **Hospital Location Map** - Interactive map showing hospital locations with sensor status
- 📋 **Audit Logs** - Track all user actions, failed logins, and system changes

### Technical Features
- 🐳 **Docker Containerization** - Complete multi-container setup
- 🔄 **Database Migrations** - Alembic for version-controlled schema changes
- 📊 **PostgreSQL Database** - Reliable, production-ready data storage
- 🚀 **Redis Caching** - Fast session management and rate limiting
- 📝 **API Documentation** - Auto-generated Swagger UI
- 🔍 **Health Checks** - Service monitoring and orchestration
- 📱 **Responsive Design** - Mobile-friendly frontend
- ⚡ **Async/Await** - High-performance async operations
- 🗺️ **Leaflet Maps** - Interactive maps with marker clustering

## 👥 User Roles

The application supports 4 user roles with hierarchical permissions:

| Role | Level | Description | Permissions |
|------|-------|-------------|-------------|
| **Pending** | 1 | New registered users | Read-only access to profile, pending admin approval |
| **Admin** | 2 | System administrators | Full access to all features, user/region/hospital management |
| **Region Admin** | 3 | Regional managers | Manage users and hospitals within assigned region, view regional sensor data |
| **Hospital User** | 4 | Hospital staff | View sensor data only for assigned hospital, read-only access |

### Permissions Matrix

| Feature | Pending | Admin | Region Admin | Hospital User |
|---------|---------|-------|--------------|---------------|
| View own profile | ✅ | ✅ | ✅ | ✅ |
| Enable 2FA | ✅ | ✅ | ✅ | ✅ |
| Create regions | ❌ | ✅ | ❌ | ❌ |
| Create hospitals | ❌ | ✅ | ❌ | ❌ |
| Set hospital locations | ❌ | ✅ | ❌ | ❌ |
| Manage API keys | ❌ | ✅ | ❌ | ❌ |
| Update user roles | ❌ | ✅ | ❌ | ❌ |
| Assign users to regions | ❌ | ✅ | ❌ | ❌ |
| Assign users to hospitals | ❌ | ✅ | ✅ (in region) | ❌ |
| View all sensor data | ❌ | ✅ | ✅ (in region) | ✅ (own hospital) |
| Ingest sensor data (API) | ❌ | ✅ (via API key) | ✅ (via API key) | ✅ (via API key) |
| View audit logs | ❌ | ✅ | ❌ | ❌ |
| View hospital map | ❌ | ✅ | ✅ (region only) | ❌ |

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (v20.10 or higher)
  - Download from: https://www.docker.com/products/docker-desktop
- **Docker Compose** (v2.0 or higher, usually included with Docker Desktop)
- **PowerShell** (for Windows) or **Bash** (for Linux/Mac)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**Windows (PowerShell):**
```powershell
.\setup.ps1
```

**Linux/Mac (if you create a bash version):**
```bash
chmod +x setup.sh
./setup.sh
```

The setup script will:
1. Check for prerequisites (Docker, Docker Compose)
2. Generate secure random secrets
3. Create `.env` configuration file
4. Build Docker images
5. Start all containers
6. Run database migrations
7. Display access URLs

### Option 2: Manual Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd secure-app
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and replace all placeholder values with secure random strings:
   ```
   DB_PASSWORD=<your-secure-password>
   REDIS_PASSWORD=<your-secure-password>
   SECRET_KEY=<your-secret-key-min-32-chars>
   JWT_SECRET_KEY=<your-jwt-secret-key-min-32-chars>
   ```

3. **Build and start containers**
   ```bash
   docker compose build
   docker compose up -d
   ```

4. **Run database migrations**
   ```bash
   docker compose exec backend alembic upgrade head
   ```

5. **Create admin account and setup domain whitelist (Required for first-time setup)**
   ```bash
   # Create admin account
   docker compose exec backend python create_admin.py
   
   # Add domain whitelist (optional but recommended)
   docker compose exec backend python add_domain_whitelist.py
   ```
   
   This will create:
   - Admin user (username: `admin`, password: `Admin123!`)
   - Whitelisted email domains: `@outlook.be` and `@gmail.com`
   
   **Note:** Users can only register with whitelisted email domains or specific whitelisted emails.

## 🌐 Access the Application

After successful setup:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Alternative API Docs**: http://localhost:8000/api/redoc

## 📖 Usage Guide

### Email Whitelist System

For enhanced security, the system now requires email addresses to be whitelisted before users can register.

**Adding Emails to Whitelist (Admin Only):**

1. Login as **Admin**
2. Navigate to admin dashboard
3. Go to **Email Whitelist Management** section
4. Click **"Add Email to Whitelist"**
5. Enter the email address
6. Click **"Add Email"**

**Via API:**

```bash
# Add email to whitelist (replace {access_token})
curl -X POST http://localhost:8000/api/admin/allowed-emails \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{"email": "newuser@example.com"}'

# List whitelisted emails
curl -X GET http://localhost:8000/api/admin/allowed-emails \
  -H "Authorization: Bearer {access_token}"

# Remove email from whitelist (replace {email_id})
curl -X DELETE http://localhost:8000/api/admin/allowed-emails/{email_id} \
  -H "Authorization: Bearer {access_token}"
```

**Important:**
- Only whitelisted emails can register new accounts
- Users attempting to register with non-whitelisted emails will receive an error
- Contact an administrator to add your email to the whitelist

### Creating an Account

**Prerequisites:** Your email must be whitelisted by an administrator.

1. Navigate to http://localhost:3000
2. Click **"Register"**
3. Fill in:
   - Username (min 3 characters)
   - **Email address** (must be whitelisted)
   - Password (min 8 characters, must include uppercase, lowercase, and numbers)
4. Click **"Register"**
5. If your email is not whitelisted, you'll receive an error - contact an administrator
6. You'll see a message about pending approval
7. **New users start as "Pending" (role 1)** - Contact admin to get role assigned

### Default Admin Account (after running create_admin.py)

| Username | Password | Role |
|----------|----------|------|
| admin | Admin123! | Admin |

**Important:** Change the default password immediately after first login!

To create additional users:
1. Login as admin
2. Add their email addresses to the whitelist (via Admin Dashboard → Email Whitelist Management)
3. Users can then register with their whitelisted email addresses
4. Admin assigns roles and region/hospital access as needed

### Logging In

1. Enter your username and password
2. Click **"Login"**
3. If 2FA is enabled, enter your 6-digit code
4. You'll be redirected to the dashboard
5. Dashboard content varies by role (Pending, Admin, Region Admin, Hospital User)

### Enabling 2FA

1. Login to your account
2. Navigate to the dashboard
3. In the "Two-Factor Authentication" section, click **"Enable 2FA"**
4. Scan the QR code with your authenticator app (Google Authenticator, Authy, Microsoft Authenticator, etc.)
5. The 2FA will be active immediately
6. Next time you login, you'll need to provide the 6-digit code

### Managing Data

1. On the dashboard, click **"Add New Item"**
2. Enter a title and content
3. Click **"Save"**
4. Your data items will be displayed below
5. Click **"Delete"** to remove an item

## 🔧 API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login with credentials | No |
| POST | `/api/auth/verify-2fa` | Verify 2FA code | No |
| POST | `/api/auth/enable-2fa` | Enable 2FA | Yes |
| POST | `/api/auth/disable-2fa` | Disable 2FA | Yes |
| GET | `/api/auth/me` | Get current user info | Yes |
| POST | `/api/auth/refresh` | Refresh access token | No |
| POST | `/api/auth/logout` | Logout | Yes |

### Admin Endpoints (Admin role only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/users/{user_id}/role` | Update user role |
| POST | `/api/admin/users/{user_id}/assign` | Assign user to region/hospital |
| GET | `/api/admin/users` | List all users (with filters) |
| GET | `/api/admin/regions` | List all regions |
| POST | `/api/admin/regions` | Create new region |
| GET | `/api/admin/hospitals` | List all hospitals |
| POST | `/api/admin/hospitals` | Create new hospital |
| POST | `/api/admin/api-keys` | Generate API key for sensor |
| PUT | `/api/admin/api-keys/{key_id}/validate` | Validate/approve API key |
| DELETE | `/api/admin/api-keys/{key_id}` | Revoke API key |
| GET | `/api/admin/api-keys` | List all API keys |
| POST | `/api/admin/allowed-emails` | Add email to whitelist |
| GET | `/api/admin/allowed-emails` | List whitelisted emails |
| DELETE | `/api/admin/allowed-emails/{email_id}` | Remove email from whitelist |

### Region Admin Endpoints (Region Admin or Admin roles)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/region/users` | List users in my region |
| POST | `/api/region/users/{user_id}/assign-hospital` | Assign user to hospital in region |
| GET | `/api/region/hospitals` | List hospitals in my region |
| GET | `/api/region/sensor-data` | Get sensor data for my region |

### Sensor Data Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| POST | `/api/sensors/data` | Ingest sensor data | API Key (X-API-Key header) |
| GET | `/api/sensors/data` | Get sensor data (role-filtered) | JWT Bearer Token |
| GET | `/api/sensors/data/{hospital_id}` | Get sensor data for specific hospital | JWT Bearer Token |
| GET | `/api/sensors/latest` | Get latest sensor readings | JWT Bearer Token |

### Dashboard Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/stats` | Get dashboard statistics (role-filtered) |
| GET | `/api/dashboard/sensor-data` | Get sensor data for dashboard |

### Data Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| GET | `/api/data/` | Get all user data items | Yes |
| POST | `/api/data/` | Create new data item | Yes |
| GET | `/api/data/{id}` | Get specific data item | Yes |
| DELETE | `/api/data/{id}` | Delete data item | Yes |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/` | API information |

### Audit Log Endpoints (Admin only)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/admin/audit-logs` | List audit logs with filtering | Yes (Admin) |
| GET | `/api/admin/audit-logs/stats` | Get audit log statistics | Yes (Admin) |

**Audit Log Query Parameters:**
- `user_id`: Filter by user ID
- `action`: Filter by action type (e.g., "user_login", "role_update")
- `resource_type`: Filter by resource type (e.g., "user", "region", "hospital")
- `start_date`: Start date for filtering (ISO 8601 format)
- `end_date`: End date for filtering (ISO 8601 format)
- `status`: Filter by status ("success" or "failure")
- `limit`: Number of results per page (max 1000, default 100)
- `offset`: Pagination offset (default 0)

### Hospital Map Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/admin/hospitals/map` | Get all hospitals with location data | Yes (Admin) |
| GET | `/api/region/hospitals/map` | Get region hospitals with location data | Yes (Region Admin) |

**Hospital Map Response:**
```json
{
  "id": 1,
  "name": "General Hospital",
  "code": "GH001",
  "latitude": 50.8503,
  "longitude": 4.3517,
  "sensor_count": 5,
  "last_reading_time": "2026-01-29T10:30:00",
  "region_id": 1,
  "region_name": "Brussels"
}
```

## 📋 Audit Logging System

The application includes comprehensive audit logging to track all user actions for security, compliance, and debugging purposes.

### What Gets Logged

**Authentication Events:**
- User registration
- Successful and failed login attempts
- Logout events
- 2FA enable/disable actions

**Administrative Actions:**
- User role changes
- User assignments to regions/hospitals
- Region create/update/delete operations
- Hospital create/update/delete operations
- API key create/validate/revoke operations
- Email whitelist modifications

**Sensor Data:**
- Sensor data ingestion (sampled at 1% to avoid log spam)

### Viewing Audit Logs

**Admin Dashboard:**
1. Navigate to Admin section
2. Click on "Audit Logs" tab
3. Use filters to search:
   - Date range
   - User
   - Action type
   - Resource type
   - Status (success/failure)
4. View statistics:
   - Total actions today/week/month
   - Top active users
   - Recent critical actions
   - Failed login attempts

**API Access:**
```bash
# Get recent audit logs
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/api/admin/audit-logs?limit=50"

# Get failed login attempts
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/api/admin/audit-logs?action=user_login&status=failure"

# Get audit statistics
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/api/admin/audit-logs/stats"
```

### Log Retention

**Recommendation:** Implement a log retention policy to archive or delete audit logs older than 90 days to maintain database performance. See comments in `app/models.py` for the AuditLog model.

## 🗺️ Hospital Location Map

The application includes an interactive map to visualize hospital locations and sensor deployment.

### Features

**Interactive Map:**
- View all hospitals on an interactive Leaflet map
- Color-coded markers based on sensor activity:
  - 🟢 Green: Active sensors (data within last hour)
  - 🔵 Blue: Has sensors (inactive)
  - ⚫ Gray: No sensors
- Marker clustering for better performance with many hospitals
- Click markers to view hospital details
- Auto-zoom to fit all hospital markers

**Hospital Details:**
- Hospital name and code
- Region
- Number of sensors
- Last sensor reading timestamp
- Link to detailed hospital view

**Filters:**
- Filter by region
- Show only hospitals with active sensors
- Search functionality in sidebar

### Adding Hospital Locations

**Admin Dashboard:**
1. Navigate to Admin section
2. Go to "Hospitals" tab
3. Create new hospital or edit existing:
   - Enter latitude (-90 to 90)
   - Enter longitude (-180 to 180)
   - Or click "Pick on Map" button to select location interactively
4. Save hospital

**Valid Coordinate Ranges:**
- Latitude: -90° to 90° (North/South)
- Longitude: -180° to 180° (East/West)

### Accessing the Map

**Web Interface:**
- Click "Hospital Map" link in Admin or Region Admin dashboard
- Opens full-screen interactive map
- Sidebar shows hospital list and filters

**API Access:**
```bash
# Get all hospitals with map data
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/api/admin/hospitals/map"

# Get hospitals for specific region
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost/api/admin/hospitals/map?region_id=1"
```

## 🌡️ IoT Sensor Integration (Orange Pi)

### Sensor-Based API Key System

The system now uses **sensor-based API keys** instead of hospital-based keys. Each sensor has its own unique identifier and dedicated API key.

**Benefits:**
- Better tracking of individual sensors
- Enhanced security through sensor-ID validation
- Admin validation required before sensors can submit data
- Prevents API key sharing between sensors

### Generating API Keys

1. Login as **Admin**
2. Navigate to admin dashboard
3. Create a hospital (if not exists)
4. Generate API key with a unique **Sensor ID**
   - Example Sensor ID: `HOSP001-TEMP-001` (Hospital Code - Sensor Type - Number)
5. **Validate** the API key to enable it
6. Save the API key securely (shown only once)

Alternatively, using the API:

```bash
# Login and get access token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Admin123!"}'

# Create API key (replace {sensor_id}, {hospital_id} and {access_token})
curl -X POST http://localhost:8000/api/admin/api-keys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {access_token}" \
  -d '{"sensor_id": "HOSP001-TEMP-001", "hospital_id": 1, "description": "Temperature sensor in Ward A"}'

# Validate the API key (replace {key_id} and {access_token})
curl -X PUT http://localhost:8000/api/admin/api-keys/{key_id}/validate \
  -H "Authorization: Bearer {access_token}"
```

### Sending Sensor Data from Orange Pi

**Important:** The `sensor_id` in your data must exactly match the sensor ID registered with the API key.

**Python Example:**

```python
import requests
import json
from datetime import datetime

API_URL = "http://your-server:8000/api/sensors/data"
API_KEY = "sk_your_generated_api_key_here"
SENSOR_ID = "HOSP001-TEMP-001"  # Must match the sensor_id registered with the API key

# Sample sensor reading
sensor_data = {
    "sensor_id": SENSOR_ID,  # Required: Must match API key's sensor_id
    "timestamp": datetime.utcnow().isoformat() + "Z",  # Optional
    "temperature": 22.5,
    "humidity": 45.2,
    "air_quality": 85,
    "custom_data": {  # Optional, max 1MB
        "co2": 400,
        "pressure": 1013,
        "location": "Ward A"
    }
}

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(API_URL, json=sensor_data, headers=headers)

if response.status_code == 201:
    print("Sensor data uploaded successfully!")
    print(response.json())
elif response.status_code == 403:
    if "pending admin validation" in response.text.lower():
        print("Error: API key not yet validated by admin")
    elif "sensor id mismatch" in response.text.lower():
        print(f"Error: Sensor ID mismatch. Check that sensor_id matches: {SENSOR_ID}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

**cURL Example:**

```bash
curl -X POST http://localhost:8000/api/sensors/data \
  -H "X-API-Key: sk_your_generated_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "HOSP001-TEMP-001",
    "timestamp": "2026-01-28T10:30:00Z",
    "temperature": 22.5,
    "humidity": 45.2,
    "air_quality": 85,
    "custom_data": {
      "co2": 400,
      "pressure": 1013
    }
  }'
```

### Sensor Data Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sensor_id` | string | Yes | Unique identifier for the sensor (must match API key's sensor_id) |
| `timestamp` | datetime | No | Timestamp of reading (UTC, defaults to now) |
| `temperature` | float | No | Temperature in Celsius |
| `humidity` | float | No | Humidity percentage |
| `air_quality` | float | No | Air quality index |
| `custom_data` | object | No | Additional sensor data as JSON (max 1MB) |

**Note:** 
- The `sensor_id` must exactly match the sensor ID registered with your API key
- All sensor data is stored in `data_json` field
- Standard fields (temperature, humidity, air_quality) are also available as separate columns for easier querying
- API keys require admin validation before they can be used

### Rate Limiting

- **Sensor API**: 100 requests per minute per API key
- Exceeding rate limits returns HTTP 429 (Too Many Requests)

### Retrieving Sensor Data

```bash
# Get latest sensor data for your hospital (as hospital user)
curl -X GET http://localhost:8000/api/sensors/latest \
  -H "Authorization: Bearer {your_jwt_token}"

# Get sensor data with filters (as admin/region admin)
curl -X GET "http://localhost:8000/api/sensors/data?hospital_id=1&limit=50" \
  -H "Authorization: Bearer {your_jwt_token}"
```

## 🔐 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_USER` | PostgreSQL username | `secureapp` |
| `DB_PASSWORD` | PostgreSQL password | `random_secure_password` |
| `DB_NAME` | PostgreSQL database name | `secureappdb` |
| `REDIS_PASSWORD` | Redis password | `random_secure_password` |
| `SECRET_KEY` | Application secret key | `random_string_min_32_chars` |
| `JWT_SECRET_KEY` | JWT signing key | `random_string_min_32_chars` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://localhost` |
| `DEBUG` | Debug mode | `false` |

## 🐳 Docker Commands

```bash
# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db

# Stop all services
docker compose down

# Stop and remove volumes (WARNING: deletes all data)
docker compose down -v

# Restart services
docker compose restart

# Rebuild and restart
docker compose up -d --build

# Execute command in container
docker compose exec backend bash
docker compose exec db psql -U secureapp -d secureappdb
```

## 🗄️ Database Schema

### Users Table
- `id` - Primary key (integer)
- `username` - Unique username (string)
- `email` - Unique email address (string)
- `hashed_password` - Bcrypt hashed password (string)
- `totp_secret` - TOTP secret for 2FA (string, nullable)
- `is_2fa_enabled` - 2FA enabled flag (boolean)
- `created_at` - Account creation timestamp
- `updated_at` - Last update timestamp
- `last_login` - Last login timestamp (nullable)
- `failed_login_attempts` - Failed login counter (integer)
- `locked_until` - Account lock timestamp (nullable)

### Data Items Table
- `id` - Primary key (integer)
- `user_id` - Foreign key to users (integer)
- `title` - Item title (string)
- `content` - Item content (text)
- `created_at` - Creation timestamp

## 🛠️ Development

### Running Backend Tests
```bash
docker compose exec backend pytest
```

### Running Database Migrations

Create a new migration:
```bash
docker compose exec backend alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
docker compose exec backend alembic upgrade head
```

Rollback migration:
```bash
docker compose exec backend alembic downgrade -1
```

### Accessing Database
```bash
docker compose exec db psql -U secureapp -d secureappdb
```

## 🔒 Security Best Practices

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Use strong passwords** - Generate random strings for all secrets
3. **Enable 2FA** - Always use two-factor authentication
4. **Regular updates** - Keep dependencies up to date
5. **HTTPS in production** - Always use SSL/TLS in production
6. **Review logs** - Monitor for suspicious activity
7. **Backup database** - Regular backups of PostgreSQL data
8. **Rotate secrets** - Periodically change passwords and secret keys

## 🐛 Troubleshooting

### Services won't start
```bash
# Check if ports are already in use
docker compose down
docker compose up -d

# Check service status
docker compose ps

# View detailed logs
docker compose logs
```

### Database connection errors
```bash
# Restart database service
docker compose restart db

# Check database health
docker compose exec db pg_isready -U secureapp
```

### Frontend can't connect to backend
- Verify CORS_ORIGINS in `.env` includes your frontend URL
- Check that backend is running: http://localhost:8000/health
- Clear browser cache and cookies

### Migration errors
```bash
# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d
docker compose exec backend alembic upgrade head
```

## 📁 Project Structure

```
secure-app/
├── docker-compose.yml          # Docker orchestration
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── README.md                   # This file
├── setup.ps1                   # Automated setup script
├── backend/                    # Backend API
│   ├── Dockerfile              # Backend container definition
│   ├── requirements.txt        # Python dependencies
│   ├── alembic.ini             # Alembic configuration
│   ├── app/                    # Application code
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app
│   │   ├── config.py           # Configuration
│   │   ├── database.py         # Database connection
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── schemas.py          # Pydantic schemas
│   │   ├── auth.py             # Authentication utilities
│   │   ├── dependencies.py     # FastAPI dependencies
│   │   └── routers/            # API routers
│   │       ├── __init__.py
│   │       ├── auth.py         # Auth endpoints
│   │       └── data.py         # Data endpoints
│   └── alembic/                # Database migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
└── frontend/                   # Frontend web app
    ├── Dockerfile              # Frontend container definition
    ├── nginx.conf              # Nginx configuration
    ├── index.html              # Dashboard page
    ├── login.html              # Login/register page
    ├── css/
    │   └── style.css           # Styling
    └── js/
        ├── auth.js             # Authentication logic
        └── main.js             # Dashboard logic
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI, PostgreSQL, Redis, and Docker**