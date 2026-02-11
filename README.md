# Classified Documents Management System

A Flask-based web application for managing classified documents with security clearance levels, document categorization, and comprehensive access control.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [How It Works](#how-it-works)
  - [Classification Levels](#classification-levels)
  - [Document Types](#document-types)
  - [User Clearance System](#user-clearance-system)
  - [Document Management](#document-management)
  - [Access Control](#access-control)
  - [Audit Logging](#audit-logging)
- [User Guide](#user-guide)
- [Admin Guide](#admin-guide)
- [Project Structure](#project-structure)

## Features

- User authentication (login/register)
- 4-tier security classification system
- 10 document type categories
- Clearance-based access control
- File upload and download
- Document filtering by type
- Complete audit trail
- Admin user management panel

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aismannai/Classified-document-system.git
cd Classified-document-system
```

2. Create a virtual environment (optional but recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python3 app.py
```

The application will start at: **http://127.0.0.1:5000**

### Default Admin Credentials

| Username | Password | Clearance Level |
|----------|----------|-----------------|
| admin    | admin123 | TOP SECRET      |

---

## How It Works

### Classification Levels

The system uses a hierarchical security classification system with 4 levels. Each level has a numeric value that determines access permissions:

| Level | Value | Color | Description |
|-------|-------|-------|-------------|
| **UNCLASSIFIED** | 0 | Green | Public information, no restrictions |
| **CONFIDENTIAL** | 1 | Blue | Sensitive information, limited distribution |
| **SECRET** | 2 | Yellow | Serious damage if disclosed |
| **TOP SECRET** | 3 | Red | Exceptionally grave damage if disclosed |

**How classification works:**
- Documents are assigned a classification level when uploaded
- Users can only create documents at or below their clearance level
- Higher classification = more restricted access

### Document Types

Documents are categorized into 10 types for better organization:

| Type | Color | Use Case |
|------|-------|----------|
| **Report** | Blue | General reports, analysis documents |
| **Memorandum** | Purple | Internal memos, communications between departments |
| **Intelligence Brief** | Red | Intelligence summaries, threat assessments |
| **Policy Document** | Green | Policies, procedures, guidelines |
| **Operation Plan** | Orange | Mission plans, operational procedures |
| **Correspondence** | Teal | Letters, external communications |
| **Technical Manual** | Dark Gray | Technical documentation, system guides |
| **Personnel File** | Yellow | HR records, employee information |
| **Financial Record** | Green | Budget reports, financial statements |
| **Other** | Gray | Documents that don't fit other categories |

**How document types work:**
- Select a type when uploading a document
- Filter documents by type on the main page
- Each type has a color-coded badge for quick identification

### User Clearance System

Every user has a clearance level that determines what they can access:

| Clearance | Can Access | Can Create |
|-----------|------------|------------|
| UNCLASSIFIED | UNCLASSIFIED only | UNCLASSIFIED only |
| CONFIDENTIAL | UNCLASSIFIED, CONFIDENTIAL | UNCLASSIFIED, CONFIDENTIAL |
| SECRET | UNCLASSIFIED, CONFIDENTIAL, SECRET | UNCLASSIFIED, CONFIDENTIAL, SECRET |
| TOP SECRET | All documents | All documents |

**Key points:**
- New users start with UNCLASSIFIED clearance
- Only TOP SECRET users can upgrade other users' clearance
- Your clearance badge is displayed in the navigation bar

### Document Management

#### Uploading Documents

1. Click **"+ Upload Document"** from the main page
2. Fill in the required fields:
   - **Title**: Document name (required)
   - **Document Type**: Select category (required)
   - **Description**: Detailed description (optional)
   - **Classification Level**: Security level (required)
   - **File**: Attach a file (optional)
3. Click **"Upload Document"**

**Rules:**
- You can only select classification levels at or below your clearance
- Documents without file attachments are still valid (metadata only)
- All uploads are logged in the audit trail

#### Viewing Documents

- The main page shows all documents you have clearance to view
- Documents are sorted by upload date (newest first)
- Each document shows: Title, Type, Classification, Uploader, Date
- Click **"View"** to see full document details
- Click **"Download"** to download attached files

#### Filtering Documents

- Use the type filter bar at the top of the document list
- Click on a document type to show only that type
- Click **"All"** to show all documents
- Filters respect your clearance level (hidden documents stay hidden)

#### Deleting Documents

1. Open the document you want to delete
2. Click **"Delete Document"**
3. Confirm the deletion
4. The action is logged in the audit trail

### Access Control

The system enforces strict access control:

| Action | Requirement |
|--------|-------------|
| View document | Clearance >= Document classification |
| Download file | Clearance >= Document classification |
| Upload document | Clearance >= Selected classification |
| Delete document | Clearance >= Document classification |
| View audit logs | TOP SECRET clearance only |
| Manage users | TOP SECRET clearance only |

**What happens when access is denied:**
- User sees "Access denied. Insufficient clearance level." message
- The attempt is logged in the audit trail
- User is redirected to the document list

### Audit Logging

Every action in the system is logged for security purposes:

| Action | What's Logged |
|--------|---------------|
| LOGIN | User logged in |
| LOGOUT | User logged out |
| VIEW | Document viewed |
| UPLOAD | Document uploaded |
| DOWNLOAD | File downloaded |
| DELETE | Document deleted |
| ACCESS_DENIED | Unauthorized view attempt |
| DOWNLOAD_DENIED | Unauthorized download attempt |
| CLEARANCE_CHANGE | User clearance modified |

**Audit log access:**
- Only TOP SECRET users can view audit logs
- Logs show: Timestamp, User, Action, Details
- Last 100 actions are displayed

---

## User Guide

### Registering an Account

1. Go to the login page
2. Click **"Register"**
3. Enter username and password
4. You'll start with UNCLASSIFIED clearance
5. Contact an admin to upgrade your clearance

### Logging In

1. Enter your username and password
2. Click **"Login"**
3. You'll be redirected to the document list

### Navigating the System

- **Documents**: Main document list (home page)
- **Upload**: Create new documents
- **Users**: Manage user clearances (admin only)
- **Audit Log**: View system activity (admin only)
- **Logout**: End your session

---

## Admin Guide

### Managing User Clearances

1. Click **"Users"** in the navigation bar
2. Find the user you want to modify
3. Select their new clearance level from the dropdown
4. Click **"Update"**
5. The change is logged in the audit trail

### Viewing Audit Logs

1. Click **"Audit Log"** in the navigation bar
2. Review recent system activity
3. Look for:
   - Suspicious access attempts (ACCESS_DENIED)
   - Unusual login patterns
   - Document deletions

### Security Best Practices

- Regularly review audit logs
- Only grant clearances as needed
- Change the default admin password
- Monitor for ACCESS_DENIED events

---

## Project Structure

```
Classified-document-system/
├── app.py              # Main Flask application
│                       # - Routes and views
│                       # - Database models (User, Document, AuditLog)
│                       # - Access control logic
│                       # - Classification/type definitions
│
├── requirements.txt    # Python dependencies
│                       # - Flask
│                       # - Flask-Login
│                       # - Flask-SQLAlchemy
│                       # - Werkzeug
│
├── README.md           # This documentation
│
├── .gitignore          # Git ignore rules
│
└── templates/          # HTML templates (Jinja2)
    ├── base.html       # Base template with navigation and styling
    ├── login.html      # User login form
    ├── register.html   # User registration form
    ├── index.html      # Document list with type filters
    ├── upload.html     # Document upload form
    ├── document.html   # Single document view
    ├── audit.html      # Audit log table
    └── users.html      # User management table
```

### Database

The system uses SQLite with 3 tables:

**User Table:**
- id, username, password_hash, clearance_level, created_at

**Document Table:**
- id, title, description, classification, doc_type, content, filename, uploaded_by, created_at, updated_at

**AuditLog Table:**
- id, user_id, action, document_id, details, timestamp

---

## License

MIT License
