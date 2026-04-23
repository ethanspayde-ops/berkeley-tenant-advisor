# Berkeley Tenant Rights Advisor
## AI-powered chatbot for Berkeley tenant rights — deployable on Render (free)
## Uses Google Gemini 2.0 Flash — no credit card required

---

## Project Structure

```
berkeley-tenant-advisor/
├── app.py              ← Flask backend (holds API key securely)
├── requirements.txt    ← Python dependencies
├── render.yaml         ← Render deployment config
├── static/
│   └── index.html      ← Frontend chatbot UI
└── README.md
```

---

## Deploy to Render (Free Tier) — Step by Step

### 1. Create a GitHub repository

1. Go to https://github.com and sign in (create a free account if needed)
2. Click **New repository**
3. Name it `berkeley-tenant-advisor`
4. Set it to **Public**, click **Create repository**

### 2. Upload the files

Option A — GitHub website (easiest):
1. In your new repo, click **Add file → Upload files**
2. Upload: `app.py`, `requirements.txt`, `render.yaml`, `README.md`
3. Create a folder called `static` and upload `index.html` inside it
4. Click **Commit changes**

Option B — Git command line:
```bash
git clone https://github.com/YOUR_USERNAME/berkeley-tenant-advisor
cd berkeley-tenant-advisor
# copy all files here, then:
git add .
git commit -m "Initial commit"
git push
```

### 3. Deploy on Render

1. Go to https://render.com and sign up for a free account
2. Click **New → Web Service**
3. Connect your GitHub account and select your `berkeley-tenant-advisor` repo
4. Render will auto-detect the `render.yaml` config
5. Fill in:
   - **Name**: berkeley-tenant-advisor
   - **Region**: Oregon (US West) — closest to Berkeley
   - **Instance Type**: Free
6. Click **Create Web Service**

### 4. Get your FREE Gemini API key (no credit card needed)

1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click **Get API Key** in the left sidebar
4. Click **Create API key**
5. Copy the key — it starts with `AIza...`

### 5. Add your Gemini API key to Render

1. In Render, go to your service → **Environment** tab
2. Click **Add Environment Variable**
3. Key: `GEMINI_API_KEY`
4. Value: your API key (`AIza...`)
5. Click **Save Changes** — Render will redeploy automatically

### 6. Get your live URL

After ~2 minutes, Render gives you a URL like:
`https://berkeley-tenant-advisor.onrender.com`

Your chatbot is now live! No API key needed from users.

---

## Embed in Google Sites

1. Copy your Render URL
2. Open Google Sites → edit your page
3. Click **Insert → Embed → Embed code**
4. Paste this (replace with your actual URL):
   ```html
   <iframe src="https://berkeley-tenant-advisor.onrender.com"
           width="100%" height="700"
           frameborder="0" allowfullscreen></iframe>
   ```
5. Click **Insert** and publish your site

> **Note**: Render's free tier spins down after 15 minutes of inactivity.
> The first load after inactivity takes ~30 seconds to wake up.
> Upgrade to Render's $7/month plan to avoid this.

---

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set your API key
export GEMINI_API_KEY="AIza..."

# Run locally
python app.py

# Open http://localhost:5000
```

---

## Security Notes

- Your Gemini API key is stored as an environment variable on Render — never in code
- The backend validates all incoming messages before sending to Gemini
- No user data is stored or logged
- The free Gemini tier allows 1,500 requests per day — more than enough for a student chatbot

---

## Resources Referenced in the Chatbot

| Organization | Phone | Website |
|---|---|---|
| Berkeley Rent Board | (510) 981-7368 | cityofberkeley.info/rent |
| East Bay Community Law Center | (510) 548-4040 | ebclc.org |
| Bay Area Legal Aid | (415) 982-1300 | baylegal.org |
| Centro Legal de la Raza | (510) 437-1554 | centrolegal.org |
| Tenants Together | (415) 703-8634 | tenantstogether.org |
