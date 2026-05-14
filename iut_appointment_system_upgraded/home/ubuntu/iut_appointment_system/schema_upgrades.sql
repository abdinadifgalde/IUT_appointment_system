-- Schema Upgrades for IUT Appointment System

-- 1. Real-time Notifications (Notification Logs)
CREATE TABLE IF NOT EXISTS notification_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type VARCHAR(50) NOT NULL, -- email, sms, whatsapp
    subject VARCHAR(255),
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, failed
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- 3. Queue & Priority System
ALTER TABLE appointment ADD COLUMN priority VARCHAR(20) DEFAULT 'Normal'; -- Emergency, High, Normal, Low
ALTER TABLE appointment ADD COLUMN queue_number INT NULL;
ALTER TABLE appointment ADD COLUMN estimated_wait_time INT NULL; -- in minutes

-- 6. Student Feedback System
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    student_id INT NOT NULL,
    officer_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointment(id),
    FOREIGN KEY (student_id) REFERENCES user(id),
    FOREIGN KEY (officer_id) REFERENCES officer(id),
    UNIQUE (appointment_id) -- Prevent duplicate feedback
);

-- 7. QR Code Appointment Slip
ALTER TABLE appointment ADD COLUMN qr_code_data VARCHAR(255) NULL;

-- 12. Role-Based Access Control
-- The user table already has a 'role' column. We will ensure it supports: Super Admin, Admin, Officer, Receptionist, Student.
-- We can add a permissions table if fine-grained control is needed, but role-based is usually sufficient for this scope.

-- 15. Live Status Tracking
-- The appointment table already has a 'status' column. We will update the application logic to support:
-- Pending, Approved, Student Arrived, In Progress, Completed, Cancelled.
ALTER TABLE appointment ADD COLUMN status_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 19. Appointment History Timeline
-- We can track status changes in a separate table for a detailed timeline.
CREATE TABLE IF NOT EXISTS appointment_timeline (
    id INT AUTO_INCREMENT PRIMARY KEY,
    appointment_id INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointment(id)
);

-- Officer Settings (for average duration, etc.)
ALTER TABLE officer ADD COLUMN avg_appointment_duration INT DEFAULT 15; -- in minutes
