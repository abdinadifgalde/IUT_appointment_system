# IUT Appointment Management System - Database Schema Upgrades

This document outlines the database schema changes and SQL migration queries required to implement the advanced features for the IUT Appointment Management System.

## 1. New Tables and Columns

### `User` Table
- No direct changes to the `User` table, but the `role` column will be utilized for Role-Based Access Control.

### `Officer` Table
- Added `avg_appointment_duration` (INT, default 15): Stores the average duration of appointments for an officer, used in waiting time prediction.

### `Appointment` Table
- Added `priority` (VARCHAR(20), default 'Normal'): Stores the priority level of an appointment (Emergency, High, Normal, Low).
- Added `queue_number` (INT, nullable): Stores the queue number for an appointment.
- Added `estimated_wait_time` (INT, nullable): Stores the estimated waiting time in minutes for an appointment.
- Added `qr_code_data` (VARCHAR(255), nullable): Stores the data to be encoded in the QR code for the appointment slip.
- Added `status_updated_at` (DATETIME, default CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP): Tracks the last time the appointment status was updated for live status tracking.

### `NotificationLog` Table (New)
This table stores a log of all notifications sent by the system.
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `user_id` (INT, FOREIGN KEY to `user.id`)
- `type` (VARCHAR(50)): Type of notification (e.g., 'email', 'sms', 'whatsapp').
- `subject` (VARCHAR(255), nullable): Subject of the notification (for emails).
- `message` (TEXT): The content of the notification.
- `status` (VARCHAR(20), default 'pending'): Status of the notification (e.g., 'pending', 'sent', 'failed').
- `created_at` (DATETIME, default CURRENT_TIMESTAMP)
- `sent_at` (DATETIME, nullable): Timestamp when the notification was sent.

### `Feedback` Table (New)
This table stores student feedback for officers after appointments.
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `appointment_id` (INT, FOREIGN KEY to `appointment.id`, UNIQUE): Ensures one feedback per appointment.
- `student_id` (INT, FOREIGN KEY to `user.id`)
- `officer_id` (INT, FOREIGN KEY to `officer.id`)
- `rating` (INT, CHECK (rating >= 1 AND rating <= 5)): Star rating.
- `comments` (TEXT, nullable): Student's comments.
- `created_at` (DATETIME, default CURRENT_TIMESTAMP)

### `AppointmentTimeline` Table (New)
This table tracks the history of status changes for each appointment.
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `appointment_id` (INT, FOREIGN KEY to `appointment.id`)
- `status` (VARCHAR(50)): The status at that point in time.
- `note` (TEXT, nullable): Any additional notes for the status change.
- `created_at` (DATETIME, default CURRENT_TIMESTAMP)

## 2. SQL Migration Queries

The following SQL queries can be used to update your existing database schema. It is recommended to back up your database before running these queries.

```sql
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

-- 15. Live Status Tracking
ALTER TABLE appointment ADD COLUMN status_updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- 19. Appointment History Timeline
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
```

## 3. Database Normalization Improvements

- The existing database schema is generally well-normalized. The additions for `NotificationLog`, `Feedback`, and `AppointmentTimeline` are new entities that further improve the normalization by separating concerns and avoiding redundant data in the `Appointment` table.
- The `User` and `Officer` tables are appropriately structured.

## 4. Next Steps

After applying these schema changes, the next phase will involve implementing the backend and frontend logic to support these new features.
