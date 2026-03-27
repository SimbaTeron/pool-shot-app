# 🎱 Pool Shot App

AI-powered pool shot coach — turn your phone into a professional pool coach.

## What It Does

1. **Take a photo** of your pool table (any angle between 30°–90°)
2. **Select** game type (8-ball, 9-ball, Straight Pool) and skill level
3. **Get a professional shot diagram** showing:
   - Ghost ball position (where the cue ball needs to be at impact)
   - Cue path (white line)
   - Object ball path (blue line)
   - Power indicator
   - English/spin recommendation

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React Native + Expo |
| Backend | Python FastAPI |
| Ball Detection | OpenCV 4 (HSV + Hough circles) |
| Homography | OpenCV findHomography |
| Physics | Custom shot calculator |
| Rendering | Programmatic SVG ($0 API cost) |

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npx expo start
# Press 'i' for iOS simulator, 'a' for Android, or scan QR with Expo Go
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/detect` | Detect balls in a base64 image |
| POST | `/calculate-shot` | Calculate optimal shot |
| POST | `/diagram` | Render shot diagram as SVG |
| POST | `/detect-and-calculate` | Combined: detect + calculate + render |

## Project Structure

```
pool-shot-app/
├── SPEC.md                    # Full technical specification
├── backend/
│   ├── main.py               # FastAPI app
│   ├── detection/            # OpenCV ball detection
│   ├── homography/           # Perspective correction
│   ├── physics/              # Shot calculator
│   └── rendering/            # SVG renderer
└── frontend/
    ├── app/                  # Expo Router screens
    ├── store/                # Zustand state
    └── services/             # API client
```

## Pricing

| Tier | Price | Shots/day |
|---|---|---|
| Free | $0 | 3 |
| Pro | $7.99/mo | Unlimited |
| Pool Hall | $14.99/mo | Unlimited + multi-table |

## License

MIT
