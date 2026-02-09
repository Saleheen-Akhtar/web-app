# Chemical Equipment Parameter Visualizer

This is a hybrid application that runs both as a Web Application and a Desktop Application for visualizing chemical equipment data.

## Project Structure

- `backend/`: Django + Django REST Framework API.
- `frontend-web/`: React.js + Chart.js Web Application.
- `frontend-desktop/`: PyQt5 + Matplotlib Desktop Application.
- `sample_equipment_data.csv`: Sample data for testing.

## Prerequisites

- Python 3.8+
- Node.js & npm (for Web Frontend)

## Setup Instructions

### 1. Backend Setup

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser (for login):
   ```bash
   python manage.py createsuperuser
   ```
5. Start the server:
   ```bash
   python manage.py runserver
   ```
   The API will be available at `http://localhost:8000/api/`.

### 2. Web Frontend Setup

1. Navigate to the `frontend-web` directory:
   ```bash
   cd frontend-web
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The web app will be available at `http://localhost:5173` (or similar).

### 3. Desktop Frontend Setup

1. Navigate to the `frontend-desktop` directory:
   ```bash
   cd frontend-desktop
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Features

- **Upload CSV:** Upload equipment data CSV files.
- **Dashboard:** View summary statistics and charts (Type Distribution, Parameters Overview).
- **History:** Access the last 5 uploaded datasets.
- **PDF Report:** Generate and download a PDF report of the analysis.
- **Authentication:** Basic login system.

## Usage

1. Start the Backend server.
2. Open either the Web App or run the Desktop App.
3. Login using the superuser credentials created in the Backend Setup.
4. Upload `sample_equipment_data.csv`.
5. View the dashboard and charts.
6. Download the PDF report.
