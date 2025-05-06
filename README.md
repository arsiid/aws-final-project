# AWS S3 Web Application with EC2 and RDS

This project demonstrates a web application hosted on AWS S3 with a Flask backend on EC2 and PostgreSQL RDS database.

## How This Was Created

### 1. Infrastructure Setup
- **EC2 Instance**:
  - Ubuntu 22.04 LTS
  - Python 3.10
  - Flask application serving API endpoints

- **RDS Database**:
  - PostgreSQL instance
  - Table: `synthetic_data` with columns:
    - category (varchar)
    - price (numeric)
    - rating (numeric)
    - stock (varchar)
    - discount (numeric)

- **S3 Bucket**:
  - Static website hosting enabled
  - Bucket policy for public read access
  - `index_diana.html` as the entry point

### 2. Application Components
- **Backend (EC2)**:
  - Flask app (`app.py`) with these endpoints:
    - `GET /api/data` - Fetch all data
    - `GET /api/data/category/<category>` - Filter by category
    - `POST /api/data` - Add new record
    - `DELETE /api/data` - Remove record

- **Frontend (S3)**:
  - Single HTML page (`index_diana.html`) with:
    - Data display table
    - Add new record form
    - Category filter
    - Delete functionality

### 3. Deployment Steps

#### Backend Setup (EC2):
```bash
# On your EC2 instance:
git clone https://github.com/arsiid/aws-final-project.git
cd aws-final-project
python3 -m venv venv
source venv/bin/activate
pip install flask flask-cors psycopg2-binary
python app.py
