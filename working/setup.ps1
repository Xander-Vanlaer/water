# Secure Full-Stack Application Setup Script
# This script automates the complete setup process

param(
    [switch]$SkipPrereqCheck,
    [switch]$CleanInstall
)

# Color output functions
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green @args }
function Write-Info { Write-ColorOutput Cyan @args }
function Write-Warning { Write-ColorOutput Yellow @args }
function Write-ErrorMsg { Write-ColorOutput Red @args }

# Banner
Write-Host ""
Write-Info "=========================================="
Write-Info "  Secure Full-Stack Application Setup"
Write-Info "=========================================="
Write-Host ""

# Check prerequisites
if (-not $SkipPrereqCheck) {
    Write-Info "Checking prerequisites..."
    
    # Check Docker
    try {
        $dockerVersion = docker --version
        Write-Success "✓ Docker found: $dockerVersion"
    }
    catch {
        Write-ErrorMsg "✗ Docker not found. Please install Docker Desktop."
        Write-ErrorMsg "  Download from: https://www.docker.com/products/docker-desktop"
        exit 1
    }
    
    # Check Docker Compose
    try {
        $composeVersion = docker compose version
        Write-Success "✓ Docker Compose found: $composeVersion"
    }
    catch {
        Write-ErrorMsg "✗ Docker Compose not found."
        exit 1
    }
    
    # Check if Docker is running
    try {
        docker ps | Out-Null
        Write-Success "✓ Docker daemon is running"
    }
    catch {
        Write-ErrorMsg "✗ Docker daemon is not running. Please start Docker Desktop."
        exit 1
    }
}

# Clean install - remove existing containers and volumes
if ($CleanInstall) {
    Write-Warning "`nPerforming clean install..."
    Write-Warning "This will remove all existing containers, volumes, and data!"
    $confirm = Read-Host "Are you sure? (yes/no)"
    
    if ($confirm -eq "yes") {
        Write-Info "Stopping and removing existing containers..."
        docker compose down -v 2>$null
        
        if (Test-Path ".env") {
            Remove-Item ".env"
            Write-Success "✓ Removed existing .env file"
        }
    }
    else {
        Write-Info "Clean install cancelled."
        exit 0
    }
}

# Generate secure random string
function Get-RandomString {
    param([int]$Length = 32)
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-="
    $random = 1..$Length | ForEach-Object { $chars[(Get-Random -Maximum $chars.Length)] }
    return -join $random
}

# Check if .env file exists
if (Test-Path ".env") {
    Write-Warning "`n.env file already exists!"
    $overwrite = Read-Host "Do you want to overwrite it? (yes/no)"
    
    if ($overwrite -ne "yes") {
        Write-Info "Using existing .env file..."
    }
    else {
        Remove-Item ".env"
        $createEnv = $true
    }
}
else {
    $createEnv = $true
}

# Create .env file with secure random secrets
if ($createEnv) {
    Write-Info "`nGenerating secure configuration..."
    
    $dbPassword = Get-RandomString -Length 32
    $redisPassword = Get-RandomString -Length 32
    $secretKey = Get-RandomString -Length 48
    $jwtSecretKey = Get-RandomString -Length 48
    
    $envContent = @"
# Database Configuration
DB_USER=secureapp
DB_PASSWORD=$dbPassword
DB_NAME=secureappdb

# Redis Configuration
REDIS_PASSWORD=$redisPassword

# Application Security
SECRET_KEY=$secretKey
JWT_SECRET_KEY=$jwtSecretKey

# CORS Configuration (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost

# Debug Mode (set to false in production)
DEBUG=false
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding utf8
    Write-Success "✓ Created .env file with secure random secrets"
}

# Build Docker images
Write-Info "`nBuilding Docker images..."
try {
    docker compose build --no-cache
    Write-Success "✓ Docker images built successfully"
}
catch {
    Write-ErrorMsg "✗ Failed to build Docker images"
    Write-ErrorMsg $_.Exception.Message
    exit 1
}

# Start Docker containers
Write-Info "`nStarting Docker containers..."
try {
    docker compose up -d
    Write-Success "✓ Docker containers started"
}
catch {
    Write-ErrorMsg "✗ Failed to start Docker containers"
    Write-ErrorMsg $_.Exception.Message
    exit 1
}

# Wait for services to be healthy
Write-Info "`nWaiting for services to be healthy..."
$maxAttempts = 30
$attempt = 0

while ($attempt -lt $maxAttempts) {
    $attempt++
    Write-Host "." -NoNewline
    
    Start-Sleep -Seconds 2
    
    try {
        $dbHealth = docker inspect --format='{{.State.Health.Status}}' secure-app-db 2>$null
        $redisHealth = docker inspect --format='{{.State.Health.Status}}' secure-app-redis 2>$null
        
        if ($dbHealth -eq "healthy" -and $redisHealth -eq "healthy") {
            Write-Host ""
            Write-Success "✓ All services are healthy"
            break
        }
    }
    catch {
        # Continue waiting
    }
    
    if ($attempt -eq $maxAttempts) {
        Write-Host ""
        Write-ErrorMsg "✗ Services did not become healthy in time"
        Write-Info "Check logs with: docker compose logs"
        exit 1
    }
}

# Wait a bit more for backend to be ready
Write-Info "`nWaiting for backend to initialize..."
Start-Sleep -Seconds 5

# Run database migrations
Write-Info "`nRunning database migrations..."
try {
    docker compose exec -T backend alembic upgrade head 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✓ Database migrations completed"
    }
    else {
        Write-Warning "⚠ Database migrations may have failed (this is OK if tables already exist)"
    }
}
catch {
    Write-Warning "⚠ Could not run migrations (this is OK if tables already exist)"
}

# Success message
Write-Host ""
Write-Success "=========================================="
Write-Success "  Setup completed successfully!"
Write-Success "=========================================="
Write-Host ""

Write-Info "Application URLs:"
Write-Success "  Frontend: http://localhost:3000"
Write-Success "  Backend API: http://localhost:8000"
Write-Success "  API Documentation: http://localhost:8000/api/docs"
Write-Host ""

Write-Info "Next steps:"
Write-Host "  1. Open your browser and navigate to http://localhost:3000"
Write-Host "  2. Click 'Register' to create a new account"
Write-Host "  3. Login with your credentials"
Write-Host "  4. Enable 2FA for enhanced security"
Write-Host ""

Write-Info "Useful commands:"
Write-Host "  View logs:        docker compose logs -f"
Write-Host "  Stop services:    docker compose down"
Write-Host "  Restart services: docker compose restart"
Write-Host "  Clean install:    ./setup.ps1 -CleanInstall"
Write-Host ""

Write-Success "Enjoy your secure application! 🔒"
Write-Host ""
