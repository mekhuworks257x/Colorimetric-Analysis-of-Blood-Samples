# 🌐 Remote Access Setup for Color Analyzer

Your friend cannot access the app because the backend is on your **private local IP** (10.1.21.126). When they connect via Expo tunnel, they need a **public URL**.

## Option 1: Use ngrok (Easiest) ⭐

### Step 1: Get ngrok

1. Go to https://ngrok.com/download
2. Download ngrok for Windows
3. Extract it and add to PATH, or run from the extracted folder

### Step 2: Start your backend

```powershell
cd d:\CALOBLOOD\Backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### Step 3: Start ngrok tunnel

```powershell
ngrok http 8001
```

### Step 4: Get the public URL

ngrok will show output like:

```
Forwarding    https://abc123def456.ngrok.io -> http://localhost:8001
```

Copy that `https://abc123def456.ngrok.io` URL

### Step 5: Update the app configuration

Create a `.env` file in `ColorAnalyzerApp/` with:

```
EXPO_PUBLIC_BACKEND_URL=https://abc123def456.ngrok.io
```

### Step 6: Restart the frontend

In a new terminal (keep ngrok running):

```powershell
cd d:\CALOBLOOD\ColorAnalyzerApp
npx expo start --tunnel
```

#### Your friend should now be able to access the app via the Expo tunnel QR code!

---

## Option 2: Use Cloudflare Tunnel (Free, No Account Needed)

### Step 1: Install Cloudflare Warp

Download from: https://1.1.1.1/

### Step 2: Start your backend

```powershell
cd d:\CALOBLOOD\Backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### Step 3: Install Cloudflare Tunnel CLI

```powershell
# Try using cloudflared if installed, or download from:
# https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
```

### Step 4a: OR Use localhost.run (Simplest!)

```powershell
# Install SSH (usually available on Windows 10+)
# Run this to create a tunnel:
ssh -R 80:localhost:8001 ssh.localhost.run
```

This gives you an instant public URL!

---

## Option 3: Router Port Forwarding (Advanced)

If you want permanent access without services:

1. Log into your router settings
2. Forward external port 8001 → internal IP 10.1.21.126:8001
3. Get your public IP from https://whatismyip.com
4. Use `http://YOUR_PUBLIC_IP:8001` as the backend URL
5. **Warning**: This is less secure, only do this temporarily

---

## Quick Test

After setting up the tunnel, test it works:

### Locally:

```powershell
curl http://localhost:8001/docs
```

### Remotely (via tunnel URL):

```powershell
curl https://YOUR_TUNNEL_URL/docs
```

Both should return HTTP 200!

---

## Troubleshooting

**Q: My friend still gets "Network Error"**

- ✅ Verify ngrok is running (check terminal)
- ✅ Verify backend is running on port 8001
- ✅ Check that `.env` file has the correct tunnel URL
- ✅ Restart the frontend after changing `.env`

**Q: "Host does not match ngrok subdomain"**

- Add this header to your requests:
  ```javascript
  // The backend should accept requests from the ngrok URL
  // This is handled automatically, but check CORS settings
  ```

---

## Quick Commands

```powershell
# Check if backend is running
Test-NetConnection -ComputerName localhost -Port 8001

# Kill all processes and start fresh
Get-Process python, node -ErrorAction SilentlyContinue | Stop-Process -Force

# Start backend
cd d:\CALOBLOOD\Backend ; python -m uvicorn main:app --host 0.0.0.0 --port 8001

# Start Expo tunnel
cd d:\CALOBLOOD\ColorAnalyzerApp ; npx expo start --tunnel

# Keep ngrok running in another terminal
ngrok http 8001
```

---

Once your friend can access the backend, they'll see successful responses like:

```
✅ Backend response received: {"b_channel": {...}, "color_values": [...]}
```

Good luck! 🎉
