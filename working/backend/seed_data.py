"""
Seed script to populate database with sample data
"""
import sys
import os
from datetime import datetime, timedelta
import secrets
import random
import math

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import User, Region, Hospital, APIKey, SensorData
from app.auth import get_password_hash


def seed_data():
    """Populate database with sample data"""
    db = SessionLocal()
    
    try:
        print("Starting database seeding...")
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("Admin123!"),
            role=2,  # Admin
            is_2fa_enabled=False
        )
        db.add(admin)
        db.commit()
        print(f"✓ Admin user created: username=admin, password=Admin123!")
        
        # Create regions
        print("\nCreating regions...")
        regions_data = [
            {"name": "North Region", "code": "NORTH"},
            {"name": "South Region", "code": "SOUTH"},
            {"name": "East Region", "code": "EAST"}
        ]
        
        regions = []
        for region_data in regions_data:
            region = Region(**region_data)
            db.add(region)
            regions.append(region)
        db.commit()
        print(f"✓ Created {len(regions)} regions")
        
        # Create hospitals
        print("\nCreating hospitals...")
        hospitals_data = [
            {"name": "North General Hospital", "code": "NGH-001", "region_id": regions[0].id, "address": "123 North St"},
            {"name": "North Medical Center", "code": "NMC-001", "region_id": regions[0].id, "address": "456 Medical Ave"},
            {"name": "South Regional Hospital", "code": "SRH-001", "region_id": regions[1].id, "address": "789 South Blvd"},
            {"name": "South Community Hospital", "code": "SCH-001", "region_id": regions[1].id, "address": "321 Community Dr"},
            {"name": "East City Hospital", "code": "ECH-001", "region_id": regions[2].id, "address": "654 East Road"},
            {"name": "East Medical Institute", "code": "EMI-001", "region_id": regions[2].id, "address": "987 Institute Lane"}
        ]
        
        hospitals = []
        for hospital_data in hospitals_data:
            hospital = Hospital(**hospital_data)
            db.add(hospital)
            hospitals.append(hospital)
        db.commit()
        print(f"✓ Created {len(hospitals)} hospitals")
        
        # Create API keys for each hospital
        print("\nCreating API keys...")
        api_keys = []
        for hospital in hospitals:
            api_key_value = f"sk_{secrets.token_urlsafe(32)}"
            api_key = APIKey(
                key=api_key_value,
                hospital_id=hospital.id,
                description=f"API key for {hospital.name}",
                is_active=True
            )
            db.add(api_key)
            api_keys.append(api_key)
            print(f"  ✓ {hospital.code}: {api_key_value}")
        db.commit()
        print(f"✓ Created {len(api_keys)} API keys")
        
        # Create sample users
        print("\nCreating sample users...")
        
        # Region admin for North Region
        region_admin_north = User(
            username="region_admin_north",
            email="region.north@example.com",
            hashed_password=get_password_hash("RegionAdmin123!"),
            role=3,  # Region Admin
            region_id=regions[0].id,
            is_2fa_enabled=False
        )
        db.add(region_admin_north)
        
        # Region admin for South Region
        region_admin_south = User(
            username="region_admin_south",
            email="region.south@example.com",
            hashed_password=get_password_hash("RegionAdmin123!"),
            role=3,  # Region Admin
            region_id=regions[1].id,
            is_2fa_enabled=False
        )
        db.add(region_admin_south)
        
        # Hospital users
        hospital_user_1 = User(
            username="hospital_user_ngh",
            email="user.ngh@example.com",
            hashed_password=get_password_hash("Hospital123!"),
            role=4,  # Hospital User
            region_id=regions[0].id,
            hospital_id=hospitals[0].id,
            is_2fa_enabled=False
        )
        db.add(hospital_user_1)
        
        hospital_user_2 = User(
            username="hospital_user_srh",
            email="user.srh@example.com",
            hashed_password=get_password_hash("Hospital123!"),
            role=4,  # Hospital User
            region_id=regions[1].id,
            hospital_id=hospitals[2].id,
            is_2fa_enabled=False
        )
        db.add(hospital_user_2)
        
        # Pending user
        pending_user = User(
            username="pending_user",
            email="pending@example.com",
            hashed_password=get_password_hash("Pending123!"),
            role=1,  # Pending
            is_2fa_enabled=False
        )
        db.add(pending_user)
        
        db.commit()
        print("✓ Created 5 sample users")
        
        # Create sample sensor data
        print("\nCreating sample sensor data...")
        sensor_count = 0
        
        # Generate realistic sensor data for the last 7 days
        for hospital in hospitals:
            # Create 2-3 sensors per hospital
            num_sensors = random.randint(2, 3)
            for sensor_num in range(1, num_sensors + 1):
                sensor_id = f"OPI-{hospital.code}-{sensor_num:03d}"
                
                # Generate 20-30 readings per sensor over the last 7 days
                num_readings = random.randint(20, 30)
                for i in range(num_readings):
                    # Spread readings over last 7 days
                    hours_ago = random.uniform(0, 168)  # 7 days = 168 hours
                    timestamp = datetime.utcnow() - timedelta(hours=hours_ago)
                    
                    # Generate realistic temperature (15-30°C) with daily cycle
                    base_temp = 22.0
                    daily_variation = 4.0 * math.sin((hours_ago / 24.0) * 2 * math.pi)
                    random_variation = random.uniform(-2.0, 2.0)
                    temperature = base_temp + daily_variation + random_variation
                    
                    # Generate realistic humidity (30-70%)
                    base_humidity = 50.0
                    humidity_variation = random.uniform(-20.0, 20.0)
                    humidity = max(30.0, min(70.0, base_humidity + humidity_variation))
                    
                    # Generate realistic air quality (50-100)
                    base_air_quality = 75.0
                    air_quality_variation = random.uniform(-25.0, 25.0)
                    air_quality = max(50.0, min(100.0, base_air_quality + air_quality_variation))
                    
                    # Additional sensor data
                    co2 = random.randint(400, 800)
                    pressure = random.uniform(1010, 1020)
                    
                    sensor_data = SensorData(
                        hospital_id=hospital.id,
                        sensor_id=sensor_id,
                        timestamp=timestamp,
                        temperature=round(temperature, 2),
                        humidity=round(humidity, 2),
                        air_quality=round(air_quality, 2),
                        data_json={
                            "temperature": round(temperature, 2),
                            "humidity": round(humidity, 2),
                            "air_quality": round(air_quality, 2),
                            "co2": co2,
                            "pressure": round(pressure, 2),
                            "sensor_type": "environmental",
                            "firmware_version": "1.2.3"
                        }
                    )
                    db.add(sensor_data)
                    sensor_count += 1
        
        db.commit()
        print(f"✓ Created {sensor_count} sensor data readings across multiple sensors over the last 7 days")
        
        print("\n" + "="*60)
        print("Database seeding completed successfully!")
        print("="*60)
        print("\nSample Credentials:")
        print("-" * 60)
        print("Admin:              username=admin, password=Admin123!")
        print("Region Admin North: username=region_admin_north, password=RegionAdmin123!")
        print("Region Admin South: username=region_admin_south, password=RegionAdmin123!")
        print("Hospital User NGH:  username=hospital_user_ngh, password=Hospital123!")
        print("Hospital User SRH:  username=hospital_user_srh, password=Hospital123!")
        print("Pending User:       username=pending_user, password=Pending123!")
        print("-" * 60)
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
