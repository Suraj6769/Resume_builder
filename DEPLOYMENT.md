# DeepSeek Resume Tailor & PDF Generator — Deployment Guide

This guide explains how to deploy your FastAPI + DeepSeek AI Resume Tailor application to the cloud.

---

## 🧹 Automatic PDF Disk Cleanup

The backend ([app.py](file:///c:/Users/Suraj/Downloads/New%20folder/app.py)) includes an **automatic PDF purger** (`cleanup_old_pdfs`).
- Automatically deletes temporary PDF/TEX files older than 5 minutes.
- Keeps a maximum of 3 recent PDFs in `generated_pdfs/` to ensure disk usage remains near zero.

---

## 🚀 Option 1: Deploy with Render (Free / Recommended)

Render supports Docker deployments out of the box:

1. Push your repository to GitHub.
2. Go to **[Render.com](https://render.com)** and create a new **Web Service**.
3. Connect your GitHub repository.
4. Select **Docker** as the Environment.
5. Set the Port to `8050`.
6. Add Environment Variable:
   - `OPENROUTER_API_KEY`: `<YOUR_OPENROUTER_API_KEY>`
7. Click **Create Web Service**. Render will build the Docker container and provide a public HTTPS URL (e.g., `https://resume-tailor.onrender.com`).

---

## 🚂 Option 2: Deploy with Railway

1. Install Railway CLI or connect GitHub on **[Railway.app](https://railway.app)**.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Railway automatically detects `Dockerfile`.
4. Under Project Settings → Variables, add:
   - `PORT`: `8050`
   - `OPENROUTER_API_KEY`: `<YOUR_OPENROUTER_API_KEY>`
5. Click **Deploy**.

---

## 🐳 Option 3: Deploy on any Linux VPS / DigitalOcean / AWS (Using Docker Compose)

1. SSH into your VPS:
   ```bash
   ssh user@your-vps-ip
   ```
2. Clone your code repository:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```
3. Create `.env` file on your server:
   ```bash
   echo "OPENROUTER_API_KEY=<YOUR_OPENROUTER_API_KEY>" > .env
   ```
4. Run with Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
5. Your application will be live at `http://your-vps-ip:8050`.
