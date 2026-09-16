-- Smart Student Reminder System Schema & Sample Data DDL
-- Database Name: smart_student_reminder

CREATE DATABASE IF NOT EXISTS smart_student_reminder DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_student_reminder;

-- --------------------------------------------------------
-- Table structure for `users`
-- Roles: admin, professor, student
-- Password for all sample users: admin123 / prof123 / student123 (werkzeug pbkdf2:sha256 hash)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) UNIQUE NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `role` ENUM('admin', 'professor', 'student') NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for `tasks`
-- Created by professors
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `tasks` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `title` VARCHAR(200) NOT NULL,
  `description` TEXT,
  `deadline` DATE NOT NULL,
  `professor_id` INT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`professor_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for `task_status`
-- Tracks individual student completion status for each assigned task
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `task_status` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `task_id` INT NOT NULL,
  `student_id` INT NOT NULL,
  `status` ENUM('Pending', 'Completed') NOT NULL DEFAULT 'Pending',
  `completed_at` TIMESTAMP NULL DEFAULT NULL,
  UNIQUE KEY `unique_task_student` (`task_id`, `student_id`),
  FOREIGN KEY (`task_id`) REFERENCES `tasks`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`student_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Table structure for `notifications`
-- In-app notifications & automated task reminders
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `notifications` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `student_id` INT NOT NULL,
  `task_id` INT NOT NULL,
  `message` TEXT NOT NULL,
  `is_read` TINYINT(1) DEFAULT 0,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`student_id`) REFERENCES `users`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`task_id`) REFERENCES `tasks`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------
-- Insert Sample Data
-- --------------------------------------------------------
INSERT IGNORE INTO `users` (`id`, `name`, `email`, `password`, `role`) VALUES
(1, 'System Administrator', 'admin@college.edu', 'scrypt:32768:8:1$hU837D9s02s9$d45c829074d0811e5ce04958f2efc405a7664878a2f4cfc58c27e48b1111667e2311fbbd5a7d79b9a6ffaa9e1c7f4803a6a9b47e24681604a4bc317d75b06f52', 'admin'),
(2, 'Dr. Robert Smith', 'prof.smith@college.edu', 'scrypt:32768:8:1$hU837D9s02s9$680210214a19eaec0efceca1621379c9339e80c35faea9e9cf2efb1bf80153f3e9c5dbd1b2ea13ceb5f2dbef996f04c63282b013b0c609c13bcfb79bc8f4a132', 'professor'),
(3, 'Prof. Sarah Davis', 'prof.davis@college.edu', 'scrypt:32768:8:1$hU837D9s02s9$680210214a19eaec0efceca1621379c9339e80c35faea9e9cf2efb1bf80153f3e9c5dbd1b2ea13ceb5f2dbef996f04c63282b013b0c609c13bcfb79bc8f4a132', 'professor'),
(4, 'Student A (Arun)', 'student.john@college.edu', 'scrypt:32768:8:1$hU837D9s02s9$78fca6d3cb997096d274bf07a0c8b6b177265d3ec62bfa128d57fa2ebfe5e786b66efbf37c6ae07c11eb4c29cf46cf110a12e84177b949ab3d168515c1e9ed71', 'student'),
(5, 'Student B (Ravi)', 'student.jane@college.edu', 'scrypt:32768:8:1$hU837D9s02s9$78fca6d3cb997096d274bf07a0c8b6b177265d3ec62bfa128d57fa2ebfe5e786b66efbf37c6ae07c11eb4c29cf46cf110a12e84177b949ab3d168515c1e9ed71', 'student'),
(6, 'Student C (Kumar)', 'student.alex@college.edu', 'scrypt:32768:8:1$hU837D9s02s9$78fca6d3cb997096d274bf07a0c8b6b177265d3ec62bfa128d57fa2ebfe5e786b66efbf37c6ae07c11eb4c29cf46cf110a12e84177b949ab3d168515c1e9ed71', 'student');

INSERT IGNORE INTO `tasks` (`id`, `title`, `description`, `deadline`, `professor_id`) VALUES
(1, 'Submit Internship Form', 'Complete and submit the internship form before the deadline.', '2026-10-09', 2);

INSERT IGNORE INTO `task_status` (`id`, `task_id`, `student_id`, `status`) VALUES
(1, 1, 4, 'Pending'),
(2, 1, 5, 'Pending'),
(3, 1, 6, 'Pending');

INSERT IGNORE INTO `notifications` (`id`, `student_id`, `task_id`, `message`, `is_read`) VALUES
(1, 4, 1, '🔔 New Task Assigned: "Submit Internship Form". Deadline: 2026-10-09.', 0),
(2, 5, 1, '🔔 New Task Assigned: "Submit Internship Form". Deadline: 2026-10-09.', 0),
(3, 6, 1, '🔔 New Task Assigned: "Submit Internship Form". Deadline: 2026-10-09.', 0);
