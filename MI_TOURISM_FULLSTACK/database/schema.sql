-- =============================================================================
-- MI TOURISM DEVELOPMENT - FULL STACK DATABASE
-- MySQL schema: users, places, packages, bookings, payments, reviews, etc.
-- =============================================================================

CREATE DATABASE IF NOT EXISTS mi_tourism_db;
USE mi_tourism_db;

-- ---------------------------------------------------------------------------
-- USERS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    full_name       VARCHAR(120) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    phone           VARCHAR(15),
    password_hash   VARCHAR(255) NOT NULL,
    role            ENUM('user', 'admin') DEFAULT 'user',
    profile_picture VARCHAR(255) DEFAULT 'assets/img/user1.jpg',
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Password reset / "forgot password" one-time codes
CREATE TABLE IF NOT EXISTS password_resets (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    otp_code    VARCHAR(10) NOT NULL,
    expires_at  DATETIME NOT NULL,
    used        TINYINT(1) DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Login sessions (simple token based, dummy auth for academic project)
CREATE TABLE IF NOT EXISTS sessions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    token       VARCHAR(64) NOT NULL UNIQUE,
    user_id     INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at  DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- TOURIST PLACES
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS places (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150) NOT NULL,
    district    VARCHAR(80) NOT NULL,
    category    ENUM('Hill Station', 'Spiritual', 'Beach', 'Heritage', 'Wildlife', 'Regular') DEFAULT 'Regular',
    description TEXT,
    image_url   VARCHAR(255),
    rating      DECIMAL(2,1) DEFAULT 0.0,
    is_trending TINYINT(1) DEFAULT 0,
    is_featured TINYINT(1) DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- TOUR PACKAGES
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS packages (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    place_id        INT,
    title           VARCHAR(150) NOT NULL,
    description     TEXT,
    duration_days   INT DEFAULT 1,
    price           DECIMAL(10,2) NOT NULL,
    image_url       VARCHAR(255),
    is_trending     TINYINT(1) DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- BOOKINGS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bookings (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    package_id      INT NOT NULL,
    travel_date     DATE NOT NULL,
    members         INT NOT NULL DEFAULT 1,
    vehicle_type    ENUM('Bus', 'Car', 'Van', 'None') DEFAULT 'None',
    hotel_type      ENUM('Budget', 'Standard', 'Luxury') DEFAULT 'Standard',
    total_amount    DECIMAL(10,2) NOT NULL,
    status          ENUM('Pending', 'Confirmed', 'Cancelled') DEFAULT 'Pending',
    booking_code    VARCHAR(20) UNIQUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- PAYMENTS (dummy gateway - no real transactions)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    booking_id      INT NOT NULL,
    method          ENUM('UPI', 'Card', 'Net Banking') NOT NULL,
    amount          DECIMAL(10,2) NOT NULL,
    status          ENUM('Success', 'Failed') DEFAULT 'Success',
    transaction_ref VARCHAR(40) UNIQUE,
    paid_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- FAVOURITES / RECENT SEARCHES (for user dashboard)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS favourites (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    place_id    INT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    UNIQUE KEY unique_favourite (user_id, place_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS recent_searches (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    search_term VARCHAR(150),
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- CONTACT MESSAGES
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS contact_messages (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(120) NOT NULL,
    email       VARCHAR(150) NOT NULL,
    phone       VARCHAR(15),
    message     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- FEEDBACK / REVIEWS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reviews (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    place_id    INT,
    rating      INT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- NEWS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS news (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    content     TEXT NOT NULL,
    image_url   VARCHAR(255),
    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- GALLERY
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gallery (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    title       VARCHAR(150),
    category    VARCHAR(80),
    image_url   VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- BLOG
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS blogs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    author_id   INT,
    title       VARCHAR(200) NOT NULL,
    content     TEXT NOT NULL,
    image_url   VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- NOTIFICATIONS (dummy)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    title       VARCHAR(150),
    message     VARCHAR(255),
    is_read     TINYINT(1) DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------------
-- SITE STATISTICS (for homepage animated counters)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS site_stats (
    stat_key    VARCHAR(50) PRIMARY KEY,
    stat_value  INT NOT NULL
) ENGINE=InnoDB;

-- =============================================================================
-- SEED / DEMO DATA
-- =============================================================================

INSERT INTO users (full_name, email, phone, password_hash, role) VALUES
-- password for admin = Admin@123  (hash format: salt$sha256(salt+password))
('Site Admin', 'admin@mitourism.com', '9999999999',
 'a1b2c3d4e5f60718$8f0a2f2d1e7a0c2b9e1e2f2a3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d',
 'admin');

INSERT INTO places (name, district, category, description, image_url, rating, is_trending, is_featured) VALUES
('Ooty Hill Station', 'Nilgiris', 'Hill Station', 'Queen of hill stations with tea gardens and cool climate.', 'assets/img/hill-station.jpg', 4.5, 1, 1),
('Rameswaram Temple', 'Ramanathapuram', 'Spiritual', 'Sacred pilgrimage site and one of the Char Dham.', 'assets/img/spiritual.jpg', 4.8, 1, 1),
('Marina Beach', 'Chennai', 'Beach', 'One of the longest urban beaches in the world.', 'assets/img/picture1.jpg', 4.2, 0, 1),
('Mahabalipuram Shore Temple', 'Chengalpattu', 'Heritage', 'UNESCO World Heritage rock-cut temple complex.', 'assets/img/PIC.jpeg', 4.6, 1, 0),
('Kodaikanal', 'Dindigul', 'Hill Station', 'Princess of hill stations with a scenic lake.', 'assets/img/regular.jpg', 4.4, 0, 1);

INSERT INTO packages (place_id, title, description, duration_days, price, image_url, is_trending) VALUES
(1, 'Ooty Tea Trail - 3 Days', 'Tea estates, botanical gardens and toy train ride.', 3, 8999.00, 'assets/img/hill-station.jpg', 1),
(2, 'Rameswaram Pilgrimage - 2 Days', 'Temple darshan with Dhanushkodi excursion.', 2, 5499.00, 'assets/img/spiritual.jpg', 1),
(3, 'Chennai City Tour - 1 Day', 'Marina Beach, Kapaleeshwarar Temple and Fort St. George.', 1, 1999.00, 'assets/img/picture1.jpg', 0),
(4, 'Heritage Mahabalipuram - 1 Day', 'Guided heritage walk through the shore temple complex.', 1, 2499.00, 'assets/img/PIC.jpeg', 1);

INSERT INTO news (title, content, image_url) VALUES
('Tamil Nadu Tourism sees record footfall this season', 'The state recorded a sharp rise in domestic tourist arrivals this quarter, driven by hill station and temple circuits.', 'assets/img/hill-station.jpg'),
('New coach services launched for hill station routes', 'MI Tourism Development has added new coach services connecting major cities to popular hill stations.', 'assets/img/BUS1.jpeg');

INSERT INTO site_stats (stat_key, stat_value) VALUES
('happy_travellers', 125000),
('destinations_covered', 53),
('tour_packages', 40),
('years_of_service', 54);
