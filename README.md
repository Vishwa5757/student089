# Student Smart Reminder System 🎓🔔

A modern full-stack web application built with **Python Flask**, **SQLAlchemy (MySQL / SQLite)**, **HTML5/CSS3**, and **Bootstrap 5**. Designed to streamline academic task assignments, deadline tracking, and student completion monitoring across three dedicated user roles: **Admin**, **Faculty**, and **Student**.

---

## 🌟 Key Features

### 🏛️ Admin Role
- **Dashboard Metrics**: Overview of total students, faculty, departments, classes, and system reminders.
- **Student Management**: Add, view, filter, and remove student accounts.
- **Faculty Management**: Add, view, filter, and remove faculty profiles.
- **Academic Structure**: Create and manage Departments (e.g., `CS`, `EE`) and Classes (e.g., `CS-101`).

### 👨‍🏫 Faculty Role
- **Task Creation**: Create tasks/reminders with title, instructions, class assignment, deadline timestamp, and priority level (`Urgent`, `High`, `Medium`, `Low`).
- **Student Submission Tracking**: Real-time status matrix showing student submission rates, timestamps, and optional student remarks.
- **Task Management**: Edit or remove created reminders.

### 🎓 Student Role
- **Reminder Dashboard**: View active pending tasks organized by priority and deadline.
- **Task Completion Toggle**: Mark tasks as completed with submission notes/links.
- **In-App Notifications**: Receive alerts whenever a faculty member assigns a new reminder.
- **Task History**: Review past completed and submitted assignments.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.13, Flask 3.0, Flask-SQLAlchemy 3.1, Werkzeug
- **Database**: MySQL (PyMySQL) with automatic SQLite local fallback
- **Frontend**: HTML5, Vanilla JavaScript, Bootstrap 5, FontAwesome 6, Custom CSS with Glassmorphism styling

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/Vishwa5757/Smart-Student-Remainder-System.git
cd Smart-Student-Remainder-System

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
```bash
python seed.py
```

### 4. Run Development Server
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 🔑 Pre-seeded Demo Accounts

| Role | Email | Password |
| :--- | :--- | :--- |
| **Admin** | `admin@system.com` | `admin123` |
| **Faculty** | `prof.smith@univ.edu` | `faculty123` |
| **Student** | `student.john@univ.edu` | `student123` |

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
