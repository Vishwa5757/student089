# Smart Student Reminder System

A web-based college task management and automated reminder system developed for an MCA mini project using **Python Flask**, **MySQL**, **APScheduler**, and **Bootstrap 5**.

---

## 📋 1. Project Title
**Smart Student Reminder System**

---

## 📝 2. Project Description
The **Smart Student Reminder System** is a web application designed for academic institutions to streamline task distribution, deadline tracking, and automated reminder notifications. It empowers professors to assign tasks to specific students, provides students with an interactive dashboard to complete assigned tasks, and runs a background automated reminder engine that periodically prompts students with pending tasks until submission.

---

## ❓ 3. Problem Statement
In traditional academic management, professors frequently assign assignments, internship forms, project reports, and administrative tasks manually or via unstructured group chats. Consequently:
* Students frequently miss deadline dates due to a lack of timely reminders.
* Professors lack real-time visibility into individual student completion progress.
* Manual follow-ups create unnecessary administrative overhead.

---

## 🎯 4. Objectives
1. Build a secure, role-based academic portal for **Admins**, **Professors**, and **Students**.
2. Automate task distribution and student assignment with deadline tracking.
3. Implement an in-app notification center to alert students of new task assignments.
4. Engine a background automated reminder system using **APScheduler** that runs at configurable intervals.
5. Automatically suppress automated reminders as soon as a student marks a task as **Completed**.
6. Deliver real-time status reports and progress tracking for professors.

---

## ⭐ 5. Key Features
* **Admin Module**: Account management (View, Add, Edit, Delete students/professors), role filtering, text search, system overview metrics.
* **Professor Module**: Task creation with title, description, deadline date picker, student selection, task status reports (`% Completion`), student-wise completion tracking, and interactive status filters (`All`, `🔴 Pending`, `🟢 Completed`).
* **Student Module**: Dashboard displaying assigned tasks separated into **🔴 Pending** and **🟢 Completed** cards, task detail modals, and a one-click `[Complete Task]` button.
* **In-App Notification Center**: Top navbar bell 🔔 with live unread count badge, task assignment alerts, and automated reminder logs.
* **Automated Background Reminder Engine**: Periodically checks pending task assignments and generates reminders until completion.
* **Security & Input Protection**: `Werkzeug` PBKDF2/scrypt password hashing, session RBAC guards, ORM SQL injection prevention, and `.env.example` configuration template.

---

## 💻 6. Technologies Used
* **Backend Framework**: Python Flask (v3.1)
* **ORM & Database**: Flask-SQLAlchemy (v3.1), PyMySQL (v1.2) / SQLite (Fallback)
* **Background Scheduler**: APScheduler (v3.11)
* **Security & Auth**: Werkzeug (v3.1) Security Hashing, Flask Sessions
* **Frontend UI**: HTML5, Vanilla CSS3, JavaScript (ES6), Bootstrap 5.3, Bootstrap Icons

---

## ⚙️ 7. System Requirements

### Hardware Requirements
* **Processor**: Dual Core 2.0 GHz or higher
* **RAM**: 4 GB minimum (8 GB recommended)
* **Disk Space**: 500 MB available space

### Software Requirements
* **Operating System**: Windows 10/11, Linux, or macOS
* **Python**: Python 3.10+ (Tested on Python 3.13)
* **Database**: MySQL Server 8.0+ (or SQLite 3)
* **Web Browser**: Chrome, Firefox, Edge, or Safari

---

## 🗄️ 8. Database Structure

The database consists of 4 main relational tables:

```text
smart_student_reminder
├── users (id, name, email, password, role, created_at)
├── tasks (id, title, description, deadline, professor_id, created_at)
├── task_status (id, task_id, student_id, status ['Pending','Completed'], completed_at)
└── notifications (id, student_id, task_id, message, is_read, created_at)
```

1. **`users`**: Stores user credentials, roles (`admin`, `professor`, `student`), and password hashes.
2. **`tasks`**: Stores task title, description, deadline, and assigned professor ID.
3. **`task_status`**: Tracks per-student task completion status (`Pending` vs `Completed`) and completion timestamp. Unique key on `(task_id, student_id)`.
4. **`notifications`**: Stores in-app alerts and automated reminder logs per student.

---

## 📥 9. Installation Steps

1. **Clone or Extract Project Workspace**:
   Ensure you are in the project root directory: `Smart student Remainders System/`.

2. **Configure Environment Variables**:
   Copy `.env.example` to `.env` if you wish to override default database settings:
   ```bash
   cp .env.example .env
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Import Database Schema (Optional for MySQL)**:
   If using MySQL Server, create the database and import `database/schema.sql` or `database/sample_data.sql`:
   ```bash
   mysql -u root -p < database/sample_data.sql
   ```

---

## 🚀 10. How to Run the Application

1. **Seed Initial Database Accounts**:
   ```bash
   python seed.py
   ```
2. **Launch Web Application & Reminder Scheduler**:
   ```bash
   python app.py
   ```
3. **Access Web Application**:
   Open browser at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

4. **Run Automated System Test Suite**:
   ```bash
   python test_system.py
   ```

---

## 🔑 11. Default Test Accounts

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@college.edu` | `admin123` |
| **Professor** | `prof.smith@college.edu` | `prof123` |
| **Student A (Arun)** | `student.john@college.edu` | `student123` |
| **Student B (Ravi)** | `student.jane@college.edu` | `student123` |
| **Student C (Kumar)** | `student.alex@college.edu` | `student123` |

---

## 🔄 12. Main Project Workflow

```text
               Professor Creates Task & Assigns Students
                                  │
                                  ▼
                Student Receives In-App Notification 🔔
                                  │
                                  ▼
                Student Views Task on Dashboard
                                  │
                                  ▼
                     Is Task Status Completed?
                    /                         \
             YES   /                           \   NO
                  /                             \
                 ▼                               ▼
    Stop Automated Reminders           APScheduler Sends Reminder ⏰
                 │                               │
                 │                               │
                 └───────────────┬───────────────┘
                                 │
                                 ▼
                    Update Completion Timestamp
                                 │
                                 ▼
                 Professor Tracks Real-Time Status
```

---

## 🚀 13. Future Enhancements

The following features are outlined for future enterprise releases:
* **Firebase Cloud Messaging (FCM)**: Native Android & iOS push notification alerts.
* **Email Notifications**: Integration with SMTP / SendGrid API for automated email reminders.
* **WhatsApp Messaging**: Twilio WhatsApp API integration for direct instant messaging.
* **Native Mobile Application**: Cross-platform mobile client built with React Native / Flutter.
* **AI-Based Task Priority**: Machine learning model to analyze task descriptions and deadlines to auto-assign urgency scores.
* **AI Message Summarization**: LLM summarization of long assignment instructions into quick bullet points.
* **Calendar Integration**: iCal / Google Calendar synchronization for academic deadlines.
