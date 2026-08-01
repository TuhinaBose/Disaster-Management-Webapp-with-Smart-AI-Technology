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
    district VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    total_capacity INT NOT NULL,
    available_beds INT NOT NULL,
    has_food BOOLEAN DEFAULT TRUE,
    has_water BOOLEAN DEFAULT TRUE,
    has_medical BOOLEAN DEFAULT TRUE,
    contact_number VARCHAR(20) NOT NULL,
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

-- Sample Emergency Shelters
INSERT IGNORE INTO shelters (id, name, address, district, latitude, longitude, total_capacity, available_beds, has_food, has_water, has_medical, contact_number) VALUES
(1, 'Central Relief & Rescue Community Hall', '124 Station Road, Central District', 'Central', 28.6139, 77.2090, 500, 320, 1, 1, 1, '+91-9876543210'),
(2, 'St. Mary High School Emergency Complex', '88 Riverside Drive, North Haven', 'North Haven', 28.7041, 77.1025, 300, 145, 1, 1, 1, '+91-9876543211'),
(3, 'Metro Indoor Stadium Shelter', '45 Sports City Boulevard, East Zone', 'East Zone', 28.5355, 77.3910, 1200, 890, 1, 1, 1, '+91-9876543212'),
(4, 'Coastal High Ground Refuge Camp', '12 Beach Safety Highway, South Shore', 'South Shore', 28.4595, 77.0266, 400, 50, 1, 1, 0, '+91-9876543213');

-- Sample Active Disaster Alerts
INSERT IGNORE INTO disaster_alerts (id, title, disaster_type, severity, location, description, is_active) VALUES
(1, 'Heavy Rainfall & Flash Flood Warning', 'Flood', 'Critical', 'Riverside & North Haven', 'Severe precipitation exceeded 180mm. Water levels in local rivers approaching critical marks. Citizens advised to move to higher ground.', 1),
(2, 'Cyclone Alert - Strong Gusts Expected', 'Cyclone', 'Warning', 'South Shore Coastal Belt', 'Wind speeds recorded up to 95 km/h. Coastal communities urged to remain indoors and secure emergency supplies.', 1),
(3, 'Heatwave Advisory - Extreme Temperatures', 'Heatwave', 'Advisory', 'Central Plains', 'Temperatures reaching 44°C. Stay hydrated and avoid outdoor exposure during mid-day hours.', 1);
