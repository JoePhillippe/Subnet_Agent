# 🚀 Render Deployment Instructions

## 📦 Files in This Folder

Upload ALL these files to your GitHub repository:

```
render_deploy/
├── app.py                     # Main Flask app (authentication & routing)
├── agent1_blueprint.py        # Basic Subnetting agent
├── agent2_blueprint.py        # Custom Subnet Masks agent  
├── agent3_blueprint.py        # Subnet Ranges agent
├── agent4_blueprint.py        # VLSM agent
├── requirements.txt           # Python dependencies
└── README_DEPLOYMENT.md       # This file
```

## 🎯 Step-by-Step Render Deployment

### Step 1: Upload to GitHub

1. Copy ALL files from `render_deploy/` to your repository: `JoePhillippe/Subnet_Agent`
2. Commit and push:
   ```bash
   git add .
   git commit -m "Add Render-ready Blueprint structure"
   git push origin main
   ```

### Step 2: Create Render Web Service

1. Go to https://render.com/dashboard
2. Click **"New +"** → **"Web Service"**
3. Connect to your GitHub repository: `JoePhillippe/Subnet_Agent`
4. Click **"Connect"**

### Step 3: Configure Service

| Setting | Value |
|---------|-------|
| **Name** | `networking-tutor-suite` (or your choice) |
| **Region** | Oregon (US West) or closest to you |
| **Branch** | `main` |
| **Root Directory** | (leave blank) |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |

### Step 4: Set Environment Variable

In the **"Environment Variables"** section:

1. Click **"Add Environment Variable"**
2. Enter:
   - **Key:** `ANTHROPIC_API_KEY`
   - **Value:** `sk-ant-your-actual-key-here`
3. Click **"Add"**

### Step 5: Deploy!

1. Click **"Create Web Service"** (blue button at bottom)
2. Wait 3-5 minutes while Render builds and deploys
3. Watch the logs for any errors
4. Once deployed, your URL will be: `https://networking-tutor-suite.onrender.com`

## 🔐 Login Credentials

Give these to your students:

- **URL:** `https://networking-tutor-suite.onrender.com` (or your custom domain)
- **Username:** `Student12345`
- **Password:** `12345FTCC!@#$%`

## 📍 Routes Structure

After login, students access:

- `/` → Login page
- `/menu` → Agent selection (redirected from `/`)
- `/agent1/` → Basic Subnetting
- `/agent2/` → Custom Subnet Masks
- `/agent3/` → Subnet Ranges
- `/agent4/` → VLSM

## ⚙️ How It Works

This uses Flask **Blueprints** - a modular architecture where:

1. **app.py** handles authentication and routing
2. Each agent is a separate Blueprint module
3. All Blueprints are registered with URL prefixes (`/agent1`, `/agent2`, etc.)
4. Everything runs on ONE port (Render requirement)

## 💰 Render Pricing

- **Free Tier:** App sleeps after 15 min (takes ~30 sec to wake up)
- **Paid Tier ($7/month):** Always awake, faster

Since you have a paid account, your app will be always-on! 🎉

## 🐛 Troubleshooting

**Problem:** "No module named 'agent1_blueprint'"
**Solution:** Make sure ALL 6 files are in your GitHub repo

**Problem:** "ANTHROPIC_API_KEY not found"
**Solution:** Check environment variables in Render dashboard

**Problem:** "Login not working"
**Solution:** Check credentials: `Student12345` / `12345FTCC!@#$%`

**Problem:** Agents not loading
**Solution:** Check Render logs for specific error messages

## ✅ Testing Locally (Optional)

Before deploying, test locally:

```bash
export ANTHROPIC_API_KEY="your-key-here"
python app.py
```

Visit: `http://localhost:5000`

## 📝 Next Steps After Deployment

1. ✅ Test all 4 agents
2. ✅ Verify authentication works
3. ✅ Share URL with students
4. ✅ Monitor Render logs for any issues

## 🎓 For Your Students

Once deployed, students just need:
1. The URL
2. The login credentials
3. No installation required - works in any browser!

---

**Need Help?** Check Render logs or contact support at https://render.com/docs
