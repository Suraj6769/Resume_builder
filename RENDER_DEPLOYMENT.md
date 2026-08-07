# 🚀 Deploying Underleaf Resume Studio to Render / Docker

This guide walks you through deploying your **Underleaf Resume Studio** app to **Render.com** (Free Tier with Docker) or any cloud provider.

---

## 🔒 Security: API Key Handling
- Your secret OpenRouter API Key is stored safely in `.env` locally (which is `.gitignore`'d).
- On Render, your API Key is stored as a secure **Environment Variable** named `OPENROUTER_API_KEY`.
- The Web UI automatically detects when your API key is loaded from the environment and displays a green **`[ API Key Active ✓ ]`** badge in the navbar without exposing any plain text key!

---

## 🛠️ Step 1: Ensure Repository is Up-to-Date on GitHub
Make sure all your latest code is pushed to your GitHub repo:
```bash
git add .
git commit -m "Prepare for Render Docker deployment"
git push origin main
```
Your repo URL: **`https://github.com/Suraj6769/Resume_builder.git`**

---

## 🌐 Step 2: Deploy on Render (Free Docker Web Service)

1. Go to **[https://dashboard.render.com](https://dashboard.render.com)** and sign in with your GitHub account.
2. Click **New +** -> **Web Service**.
3. Select **Build and deploy from a Git repository** and connect your repo: `Suraj6769/Resume_builder`.
4. Configure the Web Service settings:
   - **Name**: `underleaf-resume-studio`
   - **Region**: Oregon (US West) or closest region
   - **Language / Environment**: **`Docker`** *(Render automatically reads your `Dockerfile` with TeX Live LaTeX compiler)*
   - **Instance Type**: **Free**
5. Scroll down to **Environment Variables**:
   - Add Key: `OPENROUTER_API_KEY`
   - Add Value: `sk-or-v1-61984c9...` *(Your OpenRouter API Key)*
6. Click **Create Web Service**!

Render will build the Docker container (installing Python + TeX Live LaTeX) and deploy your live URL (e.g., `https://underleaf-resume-studio.onrender.com`).

---

## 🧪 Step 3: Verify Your Live Deployment
Once Render finishes deploying (usually takes 2-3 minutes):
1. Open your live Render URL.
2. Check the top navbar: you will see **`[ API Key Active ✓ ]`**.
3. Select any of the 5 templates (Jake Ryan, Deedy Resume, Modern Classic, Academic CV, Executive Charter).
4. Enter a target Job Description and click **Generate & Compile PDF**!
