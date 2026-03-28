Global + Topic-Specific Memory — Pool Shot App (Topic 166)

Hardware & Setup:
- Developer machine: Lenovo Ryzen 5, 40 GB RAM, 1 TB SSD
- Running latest OpenClaw as 24/7 daemon with MiniMax M2.7 ($10 tier)
- Current flagship project: Pool Shot App — AI pool shot coach mobile app

Project Vision — Pool Shot App:
- Core flow: Photo of pool table → select game type + skill level → professional shot diagram (cue path, object path, ghost ball, power, English/spin).
- Key differentiators: Works from reasonable angles (30°–90°), no hardware required, no manual calibration (table size selection only), cross-platform (React Native).
- Tech direction: React Native frontend, Python/FastAPI backend, OpenCV rule-based ball detection for MVP, programmatic SVG shot diagrams (zero cost for core feature), Supabase + Auth0.
- Pricing structure: Free (3 shots/day), Pro $7.99/month or $49.99/year, Pool Hall $14.99/month.

Curated Decisions & Mitigations:
- No corner calibration: User selects Bar 7ft (78"×39") or Regulation 9ft (100"×50") → automatic homography.
- Camera angle: Live overlay enforces 30°–90° (green/red feedback).
- Ball detection: Start with rule-based OpenCV (HSV color + edge detection). Add YOLO only later if needed.
- Shot rendering: Pure programmatic Canvas/SVG (fast, accurate, $0 cost). AI image gen only as optional Pro feature.
- Risks addressed: App Store gambling flags (frame strictly as coaching tool), lighting (use HSV), user friction minimized.

Past Discussions:
- Closest competitor: CueSports (requires overhead hardware).
- Revenue projections: ~$1,149 net/month at 1,000 users; ~$11,770 net/month at 10,000 users.
- Build approach: MVP with rule-based detection → physics engine → beautiful diagrams → polish & launch.

Daily Curation Instruction:
"Review today's Pool Shot App discussion. Curate only high-signal decisions, technical choices, cost estimates, risks/mitigations, and action items into MEMORY.md. Keep under 100 lines total."

## Technical Lessons Learned (2026-03-27)

- **max_cut_angle = 0 bug:** Formula `90 - (POCKET_DIAMETER_CORNER / BALL_DIAMETER) * 90 / 2` simplified to `90 - 90 = 0`. Fixed by hardcoding 67.5° (corner) and 75° (side).
- **angle_diff not wrapped at π:** `atan2` angle differences > 180° weren't wrapped, causing `shot_angle` to exceed 90° and fail skill filters. Fixed: `if angle_diff > π: angle_diff = 2π - angle_diff`.
- **Hough circles > HSV masks:** LED lighting washes out color (saturation near 0 even for colored balls). Hough circle detection on grayscale finds actual circles; HSV then classifies center pixel color — much more robust than pixel-level color masks.
- **Cue ball detection:** Use broad HSV range (S < 55, V > 80) + bright circle fallback. Dim bar rooms need low V threshold (100 instead of 150).
- **Homography validation:** Detected corner aspect ratio is the best quick-check. Pool tables are 2:1. Reject if detected aspect < 1.5 or > 3.0.
- **No external network on dev machine:** GitHub, npm, Supabase all unreachable from this Windows machine. CLI installs and API calls fail. All verification must happen locally or skip to user-side steps.
- **`.env` is gitignored** — credentials not pushed to GitHub. Keep backup of Supabase keys.

## Build Status — LIVE (2026-03-27)

GitHub: https://github.com/SimbaTeron/pool-shot-app (public, main branch)
GitHub token: stored in .env (autonomous push access confirmed)

### What's Built

**Backend (Python/FastAPI):**
- OpenCV ball detection (Hough circles + HSV center sampling) — robust to LED lighting
- Homography engine with aspect-ratio validation (rejects bad corner detection)
- Shot calculator physics (angle, power, english, ghost ball) — skill-adaptive
- Programmatic SVG renderer (dark theme, animated paths, power/english arcs)
- Combined `/detect-and-calculate` endpoint
- Graceful fallback when cue ball not detected
- Bugs fixed: max_cut_angle formula (was 0°), angle normalization at π, skill range (was too narrow)
- Backend running on port 8000

**Frontend (React Native/Expo):**
- Home, Camera, Processing, Diagram, Settings screens
- Sign In + Sign Up screens (Supabase auth)
- Zustand store with auth state + user profile
- Live camera angle overlay (green 30°–90°, red otherwise)
- SVG diagram display with share
- Expo prebuild: Android native project generated at `frontend/android/`
- EAS Build configured (eas.json)
- TypeScript: 0 errors

**Database (Supabase):**
- `backend/supabase_schema.sql` — profiles table, shots table, RLS policies
- Profiles auto-created on user signup via trigger
- Free tier: 3 shots/day tracked in `shots_used_today`

### What's Built

**Backend (Python/FastAPI):**
- OpenCV ball detection (Hough circles + HSV center sampling) — robust to LED lighting
- Homography engine with aspect-ratio validation (rejects bad corner detection)
- Shot calculator physics (angle, power, english, ghost ball) — skill-adaptive
- Programmatic SVG renderer (dark theme, animated paths, power/english arcs)
- Combined `/detect-and-calculate` endpoint
- Graceful fallback when cue ball not detected
- Bugs fixed: max_cut_angle formula (was 0°), angle normalization at π, skill range (was too narrow)
- Backend running on port 8000

**Frontend (React Native/Expo):**
- Home, Camera, Processing, Diagram, Settings screens
- Sign In + Sign Up screens (Supabase auth)
- Zustand store with auth state + user profile
- Live camera angle overlay (green 30°–90°, red otherwise)
- SVG diagram display with share
- Expo prebuild: Android native project generated at `frontend/android/`
- EAS Build configured (eas.json)
- TypeScript: 0 errors

**Database (Supabase):**
- Project: `pool-shot-app` at `https://shwhispjtdmriysljdqze.supabase.co`
- Schema applied: profiles (auto-created on signup), shots tables
- Anon key stored in `frontend/.env` (NOT in Git — gitignored)
- RLS policies set; free tier 3 shots/day

### Not Yet Done
1. EAS Build: `eas login` then `eas build --platform android --profile preview`
2. Fix corner/table detection — current fallback (10%/90% of image) gives poor homography
3. LED lighting degrades ball color classification — consider brightness-only fallback for cue ball
4. Test with more varied lighting conditions (dim, bright, mixed)