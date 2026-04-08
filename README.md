# Phisher: Advanced Phishing Detection System

A comprehensive phishing detection application featuring a rule-based engine, a machine learning ensemble model, and support for PDF/Image scanning.

## 🚀 New Features

- **Document Scanning**: Upload PDF files to analyze email content directly.
- **Image OCR**: Upload screenshots of suspicious emails; the system "reads" the text using OCR (Optical Character Recognition) to perform analysis.
- **Improved UI**: Modern glassmorphic interface with dedicated file upload capabilities and real-time risk scoring.
- **Ensemble ML Model**: Advanced classification using Logistic Regression, Random Forest, and Gradient Boosting.

## 📂 Project Structure

- `backend/app.py`: Main Flask API with unified threat detection logic.
- `backend/config_data.csv`: Curated rule-based indicators (trusted domains, suspicious words, etc.).
- `src/pages/Scan.tsx`: React scanner interface with file processing integration.
- `.venv/`: Dedicated Python virtual environment for backend dependencies.

## 🛠️ Setup Instructions

### Prerequisites
- **Node.js** (for frontend)
- **Python 3.9+** (for backend)
- **Tesseract-OCR Engine**: Required for image scanning.
    - [Download for Windows](https://github.com/UB-Mannheim/tesseract/wiki)
    - After installing, the backend is configured to find it at `C:\Program Files\Tesseract-OCR\tesseract.exe`.

### Backend Setup
1. **Navigate to the root directory**.
2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run Backend**:
   ```bash
   python backend/app.py
   ```
   *The backend runs on `http://127.0.0.1:5000`.*

### Frontend Setup
1. **Install Dependencies**:
   ```bash
   npm install
   ```
2. **Set the API URL**:
   ```bash
   # .env.local
   VITE_API_URL=http://127.0.0.1:5000
   ```
2. **Run Dev Server**:
   ```bash
   npm run dev
   ```
   *The frontend runs on `http://localhost:5173`.*

## Deployment Notes
- For **Vercel**, set `VITE_API_URL` to your Render backend URL, for example:
  ```bash
  VITE_API_URL=https://your-backend-name.onrender.com
  ```
- For **Render**, optionally set `CORS_ORIGINS` to your Vercel site URL for stricter CORS:
  ```bash
  CORS_ORIGINS=https://your-frontend-name.vercel.app
  ```
- For **Render image uploads**, Render must also install `tesseract` during build. This repo now configures that in [nixpacks.toml](/d:/VS%20Code%20/Phishing%20Detector%20(Hackaholics)/nixpacks.toml), so redeploy the backend after pushing.
- If Render still cannot find OCR after redeploy, set:
  ```bash
  TESSERACT_CMD=/usr/bin/tesseract
  ```
- The frontend now refuses to use `127.0.0.1` in production, so if `VITE_API_URL` is missing you will see a clear error instead of silent upload failures.

## ⚙️ Configuration
The rule-based detection is controlled via `backend/config_data.csv`. You can add trusted domains, typo keywords, and suspicious patterns directly to this file to tune the accuracy.

## 📄 License
This project is developed for cybersecurity research and educational purposes.
