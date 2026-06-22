# 🤖 HireBot AI Assistant Pro

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-GUI-green)
![SQLite](https://img.shields.io/badge/Database-SQLite-orange)
![License](https://img.shields.io/badge/License-MIT-red)

### 🚀 Modern AI Assistant Desktop Application

A powerful AI-powered desktop assistant built with Python, CustomTkinter, and SQLite featuring user management, admin portal, productivity tools, and a modern glassmorphism UI.

</div>

---

# 📌 Project Overview

**HireBot AI Assistant Pro** is a modern desktop application designed to provide AI-powered assistance along with productivity tools and user management features.

The application includes:

- AI Chat Assistant
- User Authentication System
- Admin Dashboard
- Notes Manager
- To-Do Manager
- QR Code Generator
- Password Generator
- User Profile Management
- Activity Tracking
- Analytics Dashboard

---

# ✨ Key Features

## 👤 User Features

### Authentication System
- User Registration
- Secure Login
- Remember Me
- Logout System
- Password Encryption (bcrypt)

### Profile Management
- Upload Profile Picture
- Change Profile Picture
- Remove Profile Picture
- Edit User Information
- Change Password

### AI Chat Assistant
- Interactive Chat Interface
- Chat History
- Message Storage
- Search Conversations
- Export Chat History

### Notes Manager
- Create Notes
- Edit Notes
- Delete Notes
- Search Notes

### To-Do Manager
- Create Tasks
- Edit Tasks
- Delete Tasks
- Task Tracking

### Productivity Tools
- QR Code Generator
- Password Generator
- Settings Management

---

# 🛡️ Admin Portal

### Admin Dashboard

Default Credentials:

```text
Username: admin
Password: admin123
```

### Admin Capabilities

#### User Management
- View All Users
- Search Users
- Edit User Details
- Delete Users
- Ban / Unban Users
- Reset User Passwords

#### Activity Monitoring
- View User Activity
- Track Login History
- Monitor Notes
- Monitor Tasks
- Monitor Chat Usage

#### Analytics
- Total Users
- Active Users
- Total Notes
- Total Tasks
- Total Chats

---

# 🏗️ Technology Stack

| Technology | Purpose |
|------------|----------|
| Python | Backend Logic |
| CustomTkinter | Desktop GUI |
| SQLite | Database |
| bcrypt | Password Security |
| Pillow | Image Handling |
| OpenAI / Gemini API | AI Features |
| FPDF | PDF Export |
| QRCode | QR Generation |

---

# 📂 Project Structure

```text
HireBot AI Assistant/
│
├── main.py
├── auth.py
├── database.py
├── admin_login.py
├── admin_dashboard.py
├── chatbot.py
├── notes.py
├── todo.py
├── qr_generator.py
├── password_generator.py
├── settings.py
├── about.py
├── notifications.py
│
├── assets/
│   ├── icons/
│   ├── images/
│   └── profile_pictures/
│
├── database/
│   └── hirebot.db
│
└── exports/
```

---

# ⚙️ Installation

### Clone Repository

```bash
git clone YOUR_REPOSITORY_URL
cd HireBot-AI-Assistant
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=YOUR_API_KEY
```

or

```env
GEMINI_API_KEY=YOUR_API_KEY
```

---

# ▶️ Run Application

```bash
python main.py
```

---

# 📊 Database

The application automatically creates:

```text
hirebot.db
```

Tables:

- Users
- Admins
- ChatHistory
- Notes
- Tasks
- UserActivity
- Settings

No manual database setup required.

---

# 🎨 UI Features

- Dark Theme
- Glassmorphism Design
- Modern Sidebar
- Professional Dashboard
- Animated Components
- Responsive Layout
- Smooth Navigation

---

# 🔒 Security Features

- bcrypt Password Hashing
- Secure Authentication
- Session Handling
- Input Validation
- Error Handling

---

# 🚀 Future Enhancements

- Voice Assistant
- Gemini AI Integration
- Real-Time Notifications
- Cloud Database
- Email Verification
- Analytics Charts
- Multi-Language Support

---

# 📸 Screenshots

Add screenshots here:

- Login Page
- Dashboard
- Chat Interface
- Admin Panel
- Notes Manager
- To-Do Manager

---

# 👩‍💻 Developer

**Rimsha Riaz**

Python Developer | Desktop Application Developer | AI Enthusiast

---

# ⭐ Support

If you like this project, please give it a ⭐ on GitHub.

---

# 📄 License

This project is licensed under the MIT License.

© 2026 HireBot AI Assistant Pro
