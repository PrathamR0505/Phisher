# Deployment Guide: Phishing Detector

Follow these steps to deploy your full-stack application.

## Prerequisites
1. Push your latest code changes to your GitHub repository.
2. Create a [Render](https://render.com/) account.
3. Create a [Vercel](https://vercel.com/) account.

---

## Step 1: Deploy Backend (Render)

1. **New Web Service**: In Render dashboard, click **New** > **Web Service**.
2. **Connect Repo**: Select your `Phisher` repository.
3. **Configure Service**:
   - **Name**: `phisher-backend` (or any name).
   - **Region**: Select the one closest to you.
   - **Language**: `Python` (Render will detect `nixpacks.toml` automatically).
   - **Branch**: `main`.
4. **Environment Variables**: Click **Advanced** > **Add Environment Variable**:
   - `PYTHON_VERSION`: `3.11.0`
   - `CORS_ORIGINS`: `https://your-vercel-domain.vercel.app,http://localhost:5173` (You can update this after Step 2).
5. **Deploy**: Click **Create Web Service**.
6. **Note your URL**: Once deployed, Render will provide a URL like `https://phisher-backend.onrender.com`. **Copy this URL**.

---

## Step 2: Deploy Frontend (Vercel)

1. **New Project**: In Vercel dashboard, click **Add New** > **Project**.
2. **Import Repo**: Import your `Phisher` repository.
3. **Configure Project**:
   - **Framework Preset**: `Vite`.
   - **Root Directory**: `./` (Root).
4. **Environment Variables**: Add the following variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://phisher-backend.onrender.com` (The URL you copied from Render).
5. **Deploy**: Click **Deploy**.
6. **Final Link**: Vercel will give you a production URL (e.g., `https://phisher-detector.vercel.app`).

---

## Step 3: Final Connectivity Check

1. Go back to your **Render** dashboard for the backend service.
2. Update the `CORS_ORIGINS` environment variable to include your real Vercel URL:
   - `CORS_ORIGINS`: `https://phisher-detector.vercel.app`
3. Restart the Render service.
4. Open your Vercel site and try scanning a URL/File!

### Troubleshooting
- **Tesseract Error**: If the backend says Tesseract is missing, ensure the `nixpacks.toml` file is in the root of your repo when you deploy to Render.
- **CORS Error**: Ensure the Vercel URL in `CORS_ORIGINS` on Render matches exactly (no trailing slash).
