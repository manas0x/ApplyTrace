-- ApplyTrace MySQL schema. Matches the SQLAlchemy models in backend/app/models.py.
-- Create the database first: CREATE DATABASE applytrace CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS applications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company VARCHAR(200) NOT NULL,
    role VARCHAR(200) NOT NULL,
    location VARCHAR(200) DEFAULT '',
    status VARCHAR(50) DEFAULT 'wishlist',
    applied_date DATE DEFAULT (CURRENT_DATE),
    jd_text TEXT DEFAULT '',
    resume_text TEXT DEFAULT '',
    link VARCHAR(500) DEFAULT '',
    notes TEXT DEFAULT '',
    match_score FLOAT DEFAULT NULL,
    INDEX idx_applications_status (status),
    INDEX idx_applications_company (company)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS resume_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL UNIQUE,
    weight FLOAT DEFAULT 1.0,
    INDEX idx_resume_keywords_keyword (keyword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Demo seed: realistic Indian-fresher (2027 batch) applications. Idempotent-ish:
-- re-running inserts duplicates, so run once or DELETE first.
INSERT INTO applications (company, role, location, status, applied_date, jd_text, link, notes) VALUES
('Heizen', 'Software Engineer (Fullstack + React Native)', 'Remote', 'applied', '2026-09-26', '',
 'https://example.com/apply/heizen', 'Top of the shortlist. Tailor resume around React Native.'),
('HARMAN', 'Associate Engineer AI/ML', 'Bengaluru', 'interviewing', '2026-09-24',
 'We are hiring Associate Engineer AI/ML. Skills: Python, FastAPI, MySQL, JWT auth, REST APIs, machine learning fundamentals, data pipelines.', '',
 'JD names FastAPI, JWT, MySQL — strong match.'),
('Vidyalai', 'Full Stack Developer Intern', 'Kochi', 'applied', '2026-09-27', '',
 'https://example.com/apply/vidyalai', '2027 batch eligible.'),
('MantraCare', 'Full Stack Developer Intern', 'Delhi', 'wishlist', '2026-09-29', '', '',
 'Check stipend details before applying.');
