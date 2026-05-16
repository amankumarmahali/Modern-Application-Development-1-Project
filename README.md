# Placement-Portal-Application

The institutes need efficient systems to manage campus recruitment activities involving companies, students, and placement drives. Currently, many institutes rely on spreadsheets, emails, or manual processes, which makes it difficult to manage company approvals, track student applications, avoid duplicate registrations, and maintain placement records.

## 📖 Overview

**Placement Portal** is a structured and user-friendly placement portal app developed using **Html, CSS, Flask, Flask-SQLAlchemy, etc.**.

---

## 🚀 Key Features

### 🛠 Institute Panel
- Full **CRUD operations** :
  - Blacklist/Whitelist Student
  - Blacklist/Whitelist Company
  - placement drives operations
  - Company Request
  - Student Applications
 
- Dynamic dashboard with :
  - Placement statistics
  - Complete Status of App  

### 🏢 Company dashboard
- Secure **Registration/Login**
- Create placement drives
- Shortlist student
- Select student
- View **historical data** and applications


### 👨‍🎓 Student dashboard
- Secure **Registration/Login**
- Explore Drives and Applications
- Apply for placement drive
- Check Status of Application
- View **historical performance** and applied drives

---

## 🧰 Tech Stack

| Layer           | Technologies Used |
|----------------|-------------------|
| 🖥️ Frontend    | HTML5, CSS3, Bootstrap, Jinja2 |
| ⚙️ Backend     | Flask, Flask-SQLAlchemy |
| 💾 Database    | SQLite |
| 🛡️ Security    | Role-Based Access |
| 🔐 Session     | Flask Sessions |

---
## 🏗️ Architecture

```text
📦 placement-portal-application/
 ┣ 📂 application/           
   ┣ 📂 controllers.py            # Routes & logic
   ┣ 📂 database.py               # SQLAlchemy
   ┗ 📂 models.py                 # Models
┣ 📂 instance/                    # SQLite database
┣ 📂 static/                      # CSS, images
┣ 📂 templates/                   # All templates
┣ 📜 app.py                       # Core app file
┣ 📜 README.md                    # Project documentation

```
---
## 🧬 Database Schema Overview

- **User**
  - `id`, `username`, `email`, `password`, `role`, etc.
- **PlacementDrive**
  - `company_id`, `name`, `job_title`, `job_description`, `eligibility_criteria`, etc.
- **Application**
  - `student_id`, `drive_id`, `status`, `remarks`, etc.

> Relationships use SQLAlchemy backrefs with cascade deletes for integrity.

---
