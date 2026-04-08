# Phisher: Advanced Phishing Detection System

A comprehensive phishing detection application featuring a rule-based engine and a machine learning ensemble model.

## Features

- **Rule-Based Engine**: Instant domain and text analysis using curated keywords and patterns.
- **ML Ensemble Model**: Advanced classification using Logistic Regression, Random Forest, and Gradient Boosting.
- **Unified Dataset**: Trained on 160k+ samples aggregated from multiple industry sources.

## Dataset Architecture

The system now utilizes a unified training pipeline that aggregates several phishing datasets:

- `backend/dataset/`: Directory containing source CSV files (Nazario, Enron, SpamAssasin, etc.).
- `backend/process_datasets.py`: Normalization script to combine diverse schemas into a standard format.
- `backend/mega_dataset.csv`: The aggregated dataset (over 165,000 samples).

## Getting Started

### Backend Setup

1. **Install Dependencies**:
   ```bash
   pip install flask flask-cors pandas scikit-learn numpy
   ```

2. **Process Datasets**:
   If you have new data in `backend/dataset/`, run the normalization script:
   ```bash
   python backend/process_datasets.py
   ```

3. **Train Model**:
   Retrain the ensemble model using the aggregated data:
   ```bash
   python backend/train_model.py
   ```

4. **Run Backend**:
   ```bash
   python backend/app.py
   ```

### Frontend Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Run Dev Server**:
   ```bash
   npm run dev
   ```

## Configuration

The rule-based detection is controlled via `backend/config_data.csv`. You can add trusted domains, typo keywords, and suspicious patterns directly to this file.
