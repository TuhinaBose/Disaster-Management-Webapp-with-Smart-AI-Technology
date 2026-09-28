-- =========================================================
-- DISASTER MANAGEMENT WEB APPLICATION - MYSQL DATABASE SCHEMA
-- Project Title: Disaster Management Web Application with Smart AI Technology
-- =========================================================

CREATE DATABASE IF NOT EXISTS disaster_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE disaster_db;

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user', -- 'admin' or 'user'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. SHELTERS TABLE
CREATE TABLE IF NOT EXISTS shelters (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    address TEXT NOT NULL,
    state VARCHAR(100) NOT NULL DEFAULT 'Delhi NCR',
    district VARCHAR(100) NOT NULL,
    city_village VARCHAR(100) NOT NULL DEFAULT 'Central City',
    facility_type VARCHAR(50) NOT NULL DEFAULT 'Shelter',
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    total_capacity INT NOT NULL,
    current_occupancy INT NOT NULL DEFAULT 0,
    available_capacity INT NOT NULL DEFAULT 0,
    contact VARCHAR(50) NOT NULL DEFAULT '+91-108',
    verification_status VARCHAR(20) NOT NULL DEFAULT 'Verified',
    has_food BOOLEAN DEFAULT TRUE,
    has_water BOOLEAN DEFAULT TRUE,
    has_medical BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. DISASTER ALERTS TABLE
CREATE TABLE IF NOT EXISTS disaster_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    disaster_type VARCHAR(50) NOT NULL, -- 'Flood', 'Cyclone', 'Earthquake', 'Heavy Rain', 'Fire'
    severity VARCHAR(20) NOT NULL,       -- 'Critical', 'Warning', 'Advisory'
    location VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. EMERGENCY REQUESTS TABLE
CREATE TABLE IF NOT EXISTS emergency_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_name VARCHAR(100) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    location VARCHAR(150) NOT NULL,
    latitude FLOAT NULL,
    longitude FLOAT NULL,
    urgency_level VARCHAR(20) NOT NULL, -- 'Critical', 'High', 'Medium'
    situation_description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending', -- 'Pending', 'In Progress', 'Resolved'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. PREDICTIONS TABLE
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rainfall FLOAT NOT NULL,
    river_level FLOAT NOT NULL,
    wind_speed FLOAT NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    earthquake_mag FLOAT NOT NULL,
    predicted_risk VARCHAR(20) NOT NULL, -- 'Low', 'Medium', 'High'
    risk_score FLOAT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =========================================================
-- INITIAL SEED DATA
-- Default Admin Account: Username: admin, Password: pbkdf2 hash for 'admin123'
-- =========================================================

INSERT IGNORE INTO users (id, username, email, password_hash, role) VALUES
(1, 'admin', 'admin@disasterapp.org', 'scrypt:32768:8:1$7fM3zQ4s1L!pbkdf2:sha256:600000$default_admin_hash_placeholder', 'admin');

-- Sample Verified Emergency Shelters
INSERT IGNORE INTO shelters (id, name, address, state, district, city_village, facility_type, latitude, longitude, total_capacity, current_occupancy, available_capacity, contact, verification_status, has_food, has_water, has_medical) VALUES
(1, 'Central Disaster Relief & Rescue Complex', 'Sector 14, Connaught Place Avenue, Central District', 'Delhi NCR', 'Central Delhi', 'Connaught Place', 'Community Center', 28.6139, 77.2090, 800, 320, 480, '+91-9876543210', 'Verified', 1, 1, 1),
(2, 'St. Mary Emergency Shelter Hub', '88 Riverside Boulevard, Civil Lines', 'Delhi NCR', 'North Delhi', 'Civil Lines', 'School', 28.7041, 77.1025, 450, 255, 195, '+91-9876543211', 'Verified', 1, 1, 1),
(3, 'Metro Indoor Sports Stadium Relief Camp', '45 Sports City Boulevard, Laxmi Nagar', 'Delhi NCR', 'East Delhi', 'Laxmi Nagar', 'Stadium', 28.5355, 77.3910, 1500, 380, 1120, '+91-9876543212', 'Verified', 1, 1, 1),
(4, 'Apex Medical Relief Facility Annex', '10 District Hospital Road, Saket', 'Delhi NCR', 'South Delhi', 'Saket', 'Hospital', 28.5244, 77.2100, 500, 190, 310, '+91-9876543213', 'Verified', 1, 1, 1);

-- Sample Active Disaster Alerts
INSERT IGNORE INTO disaster_alerts (id, title, disaster_type, severity, location, description, is_active) VALUES
(1, 'Heavy Rainfall & Flash Flood Warning', 'Flood', 'Critical', 'Riverside & North Haven', 'Severe precipitation exceeded 180mm. Water levels in local rivers approaching critical marks. Citizens advised to move to higher ground.', 1),
(2, 'Cyclone Alert - Strong Gusts Expected', 'Cyclone', 'Warning', 'South Shore Coastal Belt', 'Wind speeds recorded up to 95 km/h. Coastal communities urged to remain indoors and secure emergency supplies.', 1),
(3, 'Heatwave Advisory - Extreme Temperatures', 'Heatwave', 'Advisory', 'Central Plains', 'Temperatures reaching 44°C. Stay hydrated and avoid outdoor exposure during mid-day hours.', 1);
