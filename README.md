# 📸 TimeCaps- Your Day, Wrapped Automatically  
*A personal AI-powered daily memory journal.*

TimeCapsis a complete **mobile + backend** system that automatically captures your day, stores photos/videos, and generates a beautiful “Day Wrap-Up” video — similar to Reels auto-edits.
It turns your small daily moments into cinematic memories.

---

## 🌟 Features

### 📱 Flutter App
-  modern gradient UI  
- Automatic **7-second video recording limit**  
- Live daily counter (photos + videos captured)  
- “Today’s Captures” slide-up sheet  
- Tap media → **full-screen viewer**  
- Delete photos/videos  
- Generate daily wrap-up  
- View previous wrap-ups  
- ExoPlayer for smooth playback  
- Auto-refresh after camera screen  

---

### 🧠 AI Story Engine (Backend)
- Auto-generates:
  - Title card  
  - **3–4 sentence inspirational quote**  
  - Poetic daily summary  
- Chooses best shot order  
- Writes a short cinematic sequence script  
- Produces polished 9:16 vertical videos  
- Smooth transitions & crossfades  
- All rendering done with Python (MoviePy + Pillow)

---

### 🎥 Wrap-Up Renderer
- Supports mixed media (photos + videos)  
- Vertical rendering (1080×1920)  
- Auto-fix aspect ratio  
- Ensures mobile playback compatibility:
  - libx264  
  - yuv420p  
  - 24fps  
- Saves generated videos to: static/timecapsule_<date>.mp4
