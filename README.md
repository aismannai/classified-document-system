# Classified Documents Management System

A Flask-based web application for managing classified documents with security clearance levels and access control.

## Features

- **Classification Levels**: UNCLASSIFIED, CONFIDENTIAL, SECRET, TOP SECRET
- **Document Types**: Report, Memo, Intelligence Brief, Policy, Operation Plan, and more
- **Access Control**: Users can only view documents at or below their clearance level
- **File Attachments**: Upload and download files with documents
- **Audit Logging**: All actions are logged (view, download, access denied, login/logout)
- **User Management**: Admins can manage user clearance levels

## Requirements

- Python 3.8+
- Flask

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

## Default Credentials

| Username | Password | Clearance Level |
|----------|----------|-----------------|
| admin    | admin123 | TOP SECRET      |

## User Roles

- **New users** register with UNCLASSIFIED clearance
- **TOP SECRET** users can:
  - Access all documents
  - View audit logs
  - Manage user clearances

## Document Types

| Type | Description |
|------|-------------|
| Report | General reports |
| Memorandum | Internal memos |
| Intelligence Brief | Intel summaries |
| Policy Document | Policies and procedures |
| Operation Plan | Operational plans |
| Correspondence | Letters and communications |
| Technical Manual | Technical documentation |
| Personnel File | HR/personnel records |
| Financial Record | Financial documents |
| Other | Miscellaneous |

## Project Structure

```
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── templates/          # HTML templates
    ├── base.html       # Base template
    ├── login.html      # Login page
    ├── register.html   # Registration page
    ├── index.html      # Document list
    ├── upload.html     # Upload document
    ├── document.html   # View document
    ├── audit.html      # Audit log
    └── users.html      # User management
```

## License

MIT License
