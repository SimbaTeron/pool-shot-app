# Pool Shot App — Technical Specification

## 1. Concept & Vision

**What it does:** User takes a photo of a pool table from any reasonable angle (30°–90°), selects game type and skill level, and receives a professional broadcast-quality shot diagram showing the optimal next shot.

**What it feels like:** A calm, focused coaching overlay — like having a silent professional watching your game and drawing the perfect shot on a transparent board placed over your table. No noise, no clutter, just clean geometry.

**Core differentiators:**
- No hardware required (works from phone camera)
- No manual calibration (user picks table size: Bar 7ft or Regulation 9ft)
- Live camera angle enforcement (green/red overlay feedback)
- <5 seconds from photo to diagram
- Zero API cost for core shot diagrams (programmatic rendering)

---

## 2. Design Language

### Aesthetic Direction
"Pro Broadcast Overlay" — inspired by ESPN shot tracking graphics. Dark backgrounds, crisp white geometry, accent colors that pop without overwhelming. Think: golf club rangefinder meets pool hall chalkboard.

### Color Palette
| Role | Hex | Usage |
|---|---|---|
| Background | `#0D1117` | Dark app background |
| Surface | `#161B22` | Cards, overlays |
| Primary | `#58A6FF` | Ghost ball, primary accents |
| Cue Path | `#F0F6FC` | White cue stick line |
| Object Path | `#79C0FF` | Light blue object ball path |
| Ghost Ball | `#58A6FF` | Semi-transparent blue circle |
| Power Low | `#3FB950` | Green (soft shot) |
| Power Med | `#D29922` | Yellow (medium shot) |
| Power High | `#F85149` | Red (power shot) |
| English Left | `#BC8CFF` | Purple (left spin) |
| English Right | `#FFA657` | Orange (right spin) |
| Text Primary | `#F0F6FC` | Main text |
| Text Muted | `#8B949E` | Secondary text |

### Typography
- **Primary:** Inter (Google Fonts) — clean, readable at small sizes
- **Diagram Labels:** JetBrains Mono — monospace for angles, distances, power numbers
- **Headings:** Inter Bold, 600 weight

### Spatial System
- Base unit: 4px
- Component padding: 16px
- Section gaps: 32px
- Border radius: 8px (cards), 4px (buttons), 50% (balls)

### Motion Philosophy
- Shot diagram draws in over 600ms with easing (cubic-bezier ease-out)
- Ghost ball pulses gently (scale 1.0 → 1.05, 1.5s loop)
- Camera angle indicator transitions color over 200ms
- Screen transitions: 300ms slide

---

## 3. Layout & Structure

### App Flow
```
[Splash] → [Home] → [Camera] → [Game Settings] → [Processing] → [Shot Diagram]
                                                         ↓
                                                  [Share / Retake]
```

### Screens
1. **Splash** — Logo fade-in, 1.5s
2. **Home** — App name, tagline, "Take a Shot" CTA, settings gear
3. **Camera** — Full-screen viewfinder with angle overlay, capture button, table size picker
4. **Game Settings** — Game type (8-ball / 9-ball / Straight Pool), Skill level (Beginner / Intermediate / Pro)
5. **Processing** — Spinner with "Analyzing table..." text
6. **Shot Diagram** — Full-screen SVG overlay on the captured photo, share/retake buttons
7. **Settings** — Account, subscription, about

### Responsive Strategy
- Portrait-only on mobile
- Shot diagram scales to fit width, maintains aspect ratio
- Touch targets minimum 44×44px

---

## 4. Features & Interactions

### Camera Capture
- Live angle indicator: green (30°–90° good), red (<30° too low, >90° too high)
- Table size selector: Bar 7ft (78"×39") | Regulation 9ft (100"×50")
- Capture button disabled when angle is red
- Flash toggle, camera flip (front/back)

### Shot Diagram
- **Ghost ball:** semi-transparent blue circle at impact position
- **Cue path:** white line from cue ball to ghost ball
- **Object path:** blue line from ghost ball to target pocket or next ball
- **Power indicator:** arc with color gradient (green→yellow→red) + text label
- **English/spin:** circular indicator with left/right fill + text label
- **Angle readout:** degrees shown at cue ball position
- **Pocket target:** highlighted pocket indicator

### Game Modes
| Mode | Behavior |
|---|---|
| 8-Ball | Recommends safest legal shot; considers scratch risk |
| 9-Ball | Recommends highest-percentage pot; ignores fouls |
| Straight Pool | Recommends ball-to-pocket line; no opponent context |

### Skill Levels
| Level | Behavior |
|---|---|
| Beginner | Larger ghost ball, more center-ball, less English |
| Intermediate | Standard ghost ball, moderate English allowed |
| Pro | Precise ghost ball, full English, advanced spin transfers |

### Error States
- **No balls detected:** "Couldn't find balls. Try a different angle or better lighting."
- **Partial detection:** "Found X balls. Move closer or ensure all balls are visible."
- **Table not detected:** "Table edge not found. Ensure full table is in frame."

### Empty / Loading States
- Skeleton shimmer on diagram while processing
- Progress percentage shown during detection

---

## 5. Component Inventory

### AngleOverlay
- Full-screen camera overlay
- Corner brackets indicate table edges
- Top bar shows current angle in degrees
- States: `good` (green tint), `too_low` (red tint), `too_high` (red tint)

### BallMarker
- Circular, 28px diameter on diagram
- Color matches actual ball (white/cue, solid 1-8, stripe 9-15, 8-ball black)
- Subtle drop shadow

### GhostBall
- 28px circle, `Primary` color at 40% opacity
- Pulsing animation (scale 1.0→1.05, 1.5s ease-in-out loop)
- Dashed outline

### CuePath
- 2px white line, rounded caps
- Draws in from cue ball → ghost ball (400ms)

### ObjectPath
- 2px light blue line, rounded caps
- Draws in from ghost ball → pocket (400ms, 200ms delay after cue path)

### PowerArc
- Semi-circular arc, radius 24px
- Gradient fill from green (low) → yellow (med) → red (high)
- Label: "Power: 65%" in JetBrains Mono below

### EnglishIndicator
- Circle split in half vertically
- Left side: purple fill if left English recommended
- Right side: orange fill if right English recommended
- Label: "English: Right 40%" below

### CaptureButton
- 72px white circle with inner 60px red circle
- Disabled state: greyed out
- Press animation: scale down to 0.95

### TableSizePicker
- Two toggle buttons: Bar 7ft | Regulation 9ft
- Selected state: filled primary color
- Default: Regulation 9ft selected

---

## 6. Technical Approach

### Frontend
- **Framework:** React Native with Expo (SDK 52)
- **Language:** TypeScript
- **Navigation:** Expo Router (file-based routing)
- **Camera:** expo-camera + expo-image-picker
- **Diagram Rendering:** react-native-svg for programmatic SVG output
- **State:** Zustand for global state (no Redux needed)
- **Styling:** StyleSheet (no external CSS framework)

### Backend
- **Framework:** Python FastAPI
- **Ball Detection:** OpenCV 4.x — HSV color thresholding + Hough circle detection
- **Homography:** OpenCV findHomography + warpPerspective
- **Physics:** Custom shot calculator (vector math, no external physics engine)
- **Diagram Rendering:** SVG generation via raw Python strings (no library needed)
- **Image Processing:** Pillow for preprocessing
- **Server:** Uvicorn, runs locally or on low-cost VPS

### API Design

#### POST `/detect`
```
Request:  { "image_base64": "<jpeg>", "table_size": "7ft" | "9ft" }
Response: {
  "balls": [{ "x": float, "y": float, "color": string, "number": int|null }],
  "table_corners": [{ "x": float, "y": float }],
  "cue_ball": { "x": float, "y": float }|null,
  "detection_confidence": float
}
```

#### POST `/calculate-shot`
```
Request: {
  "balls": [...],
  "cue_ball": { "x": float, "y": float },
  "table_size": "7ft" | "9ft",
  "game_type": "8ball" | "9ball" | "straight",
  "skill_level": "beginner" | "intermediate" | "pro"
}
Response: {
  "ghost_ball": { "x": float, "y": float },
  "cue_path": [{ "x": float, "y": float }],
  "object_path": [{ "x": float, "y": float }],
  "target_pocket": string,
  "power": float,        // 0.0–1.0
  "english": float,      // -1.0 (full left) to 1.0 (full right)
  "angle": float,        // degrees
  "confidence": float
}
```

#### GET `/diagram`
```
Request:  ?shot_data=<url-encoded-json>
Response: SVG image (image/svg+xml)
```

### Data Model

**Table Dimensions:**
| Size | Playing Surface | Aspect Ratio |
|---|---|---|
| Bar 7ft | 78" × 39" | 2:1 |
| Regulation 9ft | 100" × 50" | 2:1 |

**Ball Diameter:** 2.25" (standard pool ball)
**Pocket Diameter:** 4.5" (corner), 4" (side)

### Homography Strategy
1. User selects table size → known aspect ratio (2:1)
2. Detect table edges via Canny + HoughLines
3. Find 4 corners (intersection of rail lines)
4. Apply findHomography with known destination rectangle
5. Scale destination to real-world inches (78"×39" or 100"×50")
6. Ball positions in output are in real-world coordinates

### Ball Detection Strategy (OpenCV MVP)
1. Convert to HSV
2. Color mask for white (cue ball): H: 0–30, S: 0–60, V: 150–255
3. Color mask for solids/stripes: iterate H ranges for pool ball colors
4. Apply medianBlur to reduce noise
5. HoughCircles to find circular shapes
6. Filter by diameter range (2.0–2.5" equivalent in pixels)
7. Cluster nearby detections
8. Return ball positions + assigned colors/numbers

### Folder Structure
```
pool-shot-app/
├── SPEC.md
├── .env
├── .gitignore
├── README.md
├── backend/
│   ├── requirements.txt
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── detect.py
│   │   └── calculate.py
│   ├── detection/
│   │   ├── __init__.py
│   │   └── opencv_detector.py
│   ├── homography/
│   │   ├── __init__.py
│   │   └── perspective.py
│   ├── physics/
│   │   ├── __init__.py
│   │   └── shot_calculator.py
│   └── rendering/
│       ├── __init__.py
│       └── svg_renderer.py
└── frontend/
    ├── app/
    │   ├── _layout.tsx
    │   ├── index.tsx
    │   ├── camera.tsx
    │   ├── settings.tsx
    │   ├── processing.tsx
    │   └── diagram.tsx
    ├── components/
    │   ├── AngleOverlay.tsx
    │   ├── BallMarker.tsx
    │   ├── GhostBall.tsx
    │   ├── CuePath.tsx
    │   ├── ObjectPath.tsx
    │   ├── PowerArc.tsx
    │   ├── EnglishIndicator.tsx
    │   ├── CaptureButton.tsx
    │   └── TableSizePicker.tsx
    ├── services/
    │   └── api.ts
    ├── store/
    │   └── useShotStore.ts
    └── assets/
        └── (fonts, images)
```

---

## 7. Monetization

| Tier | Price | Shots/day | Features |
|---|---|---|---|
| Free | $0 | 3 | Basic shot diagrams, watermarked |
| Pro | $7.99/mo or $49.99/yr | Unlimited | No watermark, save diagrams, history |
| Pool Hall | $14.99/mo | Unlimited + multi-table | Bulk management, ad-free |

---

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| App Store gambling flag | Frame strictly as coaching/educational tool; no betting features |
| Lighting variability | HSV color space is lighting-robust; add exposure compensation |
| Ball detection accuracy | Start MVP with rule-based; add YOLO only after real-world testing |
| Camera angle accuracy | Live overlay feedback trains user; only capture when angle is good |
| Shadow/occlusion | Require full table visibility; prompt user if balls are hidden |
