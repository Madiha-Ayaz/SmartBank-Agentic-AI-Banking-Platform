# SmartBank — Demo Video Preparation Checklist

---

## 1. Screen Recording Checklist

### Pre-Recording Setup
- [ ] Close all unnecessary browser tabs and applications
- [ ] Disable desktop notifications (Windows: Focus Assist / Do Not Disturb)
- [ ] Set Chrome to Incognito / Guest mode (clean bookmarks bar)
- [ ] Set browser zoom to 100%
- [ ] Set display resolution to 1920×1080 (16:9)
- [ ] Mute system audio (record VO separately)
- [ ] Close Slack, Teams, Outlook pop-up notifications
- [ ] Disable microphone for system (voiceover recorded later)
- [ ] Clean desktop — remove all icons, files, shortcuts
- [ ] Set desktop background to dark solid colour or SmartBank wallpaper
- [ ] Open OBS / Camtasia / ScreenRec — verify recording area is full screen
- [ ] Set recording FPS to 30 (sufficient for demo; 60 if smooth BPMN animation)
- [ ] Test recording 10 seconds, playback check (audio sync, frame drop, resolution)

### Scenario Data Prepared
- [ ] Test customer account with **blocked card** scenario (DEB03)
  - Name: Ahmad Raza
  - CNIC: 42201-1234567-1
  - Phone: +92 300 1112233
  - Card: xxxx-xxxx-xxxx-1234 (status: ACTIVE)
- [ ] Test customer account for **NIC Update** (NIC06)
  - Name: Fatima Ahmed
  - Old CNIC: 42201-7654321-1
  - New CNIC: 42201-7654321-2
  - Fraud score pre-configured: 12/100
- [ ] Sample document images (front & back of NIC) saved to desktop
- [ ] Dashboard pre-populated with at least 1,000+ mock cases
- [ ] Action Centre has at least 1 pending NIC06 task

### Chat Widget Pre-Conditions
- [ ] Chat widget URL / embed configured and loaded
- [ ] Intent classification returns exactly `DEB03` with `confidence 0.94` for test phrase
- [ ] AI responses in Roman Urdu configured (not English fallback)
- [ ] Typing indicator animation working (verified)

### BPMN / Maestro
- [ ] Maestro BPMN diagram rendering in browser (clean, readable)
- [ ] Node animations configured (highlight + transition, ~0.5s delay per node)
- [ ] CBS API mock/stub returning success for card block
- [ ] SMS gateway mock returning 200 OK
- [ ] Email SMTP mock returning accepted

### Dashboard
- [ ] KPI counters animated (not static)
- [ ] Case timeline populated with coloured workflow bars
- [ ] Recent activity table live-updating (or simulated with JS interval)
- [ ] SLA breach panel empty (green indicator)

---

## 2. Slide Deck Outline

| Time | Slide # | Content | Type |
|------|---------|---------|------|
| 00:00 | 1 | **Hook — Problem Statement** — ATM frustration image, phone helpline queue, "40M cards, 1 call centre" stat | Full-bleed image + text overlay |
| 00:25 | 2 | **Transition** — SmartBank logo + tagline ("Banking, Reimagined by AI") | Logo animation, smooth transition |
| 00:30 | 3 | **Architecture Overview** — SmartBank as centre hub, 5 spokes: Conversational AI / UiPath / Maestro / Open Banking / Dashboard | Animated diagram (spokes light up sequentially) |
| 01:00 | 4 | **Live Demo — DEB03 Card Block** — Chat widget (full screen), BPMN, CBS call, SMS+Email | Screen recording (no slide, overlay graphics) |
| 02:00 | 5 | **Live Demo — NIC06 ID Update** — Document upload, OCR, fraud score, Action Centre, manager approval | Screen recording (no slide, overlay graphics) |
| 03:00 | 6 | **Operations Dashboard** — KPI cards, case timeline, activity table, SLA panel | Screen recording (no slide, overlay callouts) |
| 04:00 | 7 | **Innovation Highlights** — 5 key differentiators (multi-lingual, 6/8 zero-touch, <45s, PCI-DSS, plug-in) | Montage / rapid cut animation |
| 04:30 | 8 | **Closing Screen** — Impact statement, team credits, QR code, GitHub link, contact | Static screen with scroll credits |

### Slides to Prepare (as separate files if needed)
- `slide_01_hook.png` — ATM frustration + text
- `slide_02_transition.png` — SmartBank logo + tagline
- `slide_03_architecture.png` — Animated architecture (or HTML/CSS for recording)
- `slide_07_highlights.png` — 5-point innovation slide
- `slide_08_closing.png` — Closing + credits + QR

---

## 3. B-Roll / Visual Asset List

| Asset | Format | Source | Used In |
|-------|--------|--------|---------|
| ATM frustration footage | MP4 (stock or filmed) | Pexels / Mixkit / self-record | 00:00–00:20 |
| Phone helpline queue footage | MP4 | Pexels / self-record | 00:10–00:25 |
| SmartBank logo (animated) | MP4 or Lottie JSON | Design team / Canva | 00:25 transition |
| Architecture diagram (animated) | HTML/CSS or MP4 | Framer / After Effects | 00:30–01:00 |
| Chat widget UI (clean state) | Screenshot | Browser inspect | Overlay reference |
| Maestro BPMN diagram (DEB03) | SVG or HTML | BPMN.io / draw.io export | 01:15–01:45 |
| UiPath robot animation | MP4 or GIF | UiPath brand kit / self-record | 01:30–01:40 |
| SMS notification mockup | PNG/PSD | Smartphone mockup template | 01:40–01:45 |
| Email notification mockup | PNG | Email template screenshot | 01:45–01:50 |
| OCR extraction animation | Screen recording | App recording | 02:05–02:15 |
| Fraud score badge graphic | PNG | Design tool | 02:15–02:20 |
| Action Centre UI (clean state) | Screenshot | Browser inspect | 02:20–02:40 |
| Manager approval click highlight | Screen recording | App recording | 02:35–02:45 |
| Operations Dashboard (animated) | Screen recording / HTML | App recording / coded | 03:00–04:00 |
| Multi-lingual chat cycling | Screen recording | App recording | 04:00–04:05 |
| 6/8 workflow BPMN thumbnails | MP4 montage | BPMN.io exports | 04:05–04:10 |
| Stopwatch animation | MP4 / Lottie | After Effects / LottieFiles | 04:10–04:15 |
| PCI-DSS shield badge | PNG/SVG | Compliance asset | 04:15–04:20 |
| Puzzle-piece plug-in animation | MP4 / Lottie | After Effects | 04:20–04:25 |
| QR code placeholder | PNG | QR generator (set to GitHub repo) | 04:30–04:45 |
| Team photo or avatars | PNG | Self-provided | 04:35–04:45 |
| SmartBank logo (final / static) | PNG/PDF | Design team | 04:55–05:00 |

### Audio Assets
| Asset | Format | Notes |
|-------|--------|-------|
| Background music (low, ambient) | MP3, ~5min loop | royalty-free (e.g., Uppbeat / Pixabay — "Corporate Tech" or "Ambient Innovation") |
| Whoosh transition SFX | WAV/MP3 | ~0.5s, for 00:25 transition |
| Click / UI sound effects | WAV/MP3 | for chat send, BPMN node complete, manager approve |
| Tone / notification ping | WAV/MP3 | for SMS received in demo |

---

## 4. Technical Rehearsal Checklist

### API Keys & Services
- [ ] OpenAI / LLM API key active with sufficient credits
- [ ] UiPath Orchestrator connection verified (or mock RPA endpoint configured)
- [ ] Maestro BPMN engine running (localhost or deployed)
- [ ] CBS mock API endpoints responding (POST /block-card, POST /update-nic)
- [ ] SMS gateway mock endpoint (returns 200 + message ID)
- [ ] SMTP email mock (Mailpit / MailHog / Papercut running)
- [ ] NADRA verification mock endpoint (returns verified=true for test CNIC)
- [ ] OCR engine / document parser configured with test CNIC images
- [ ] Fraud scoring model returning predictable value (12) for test data

### Sample Data Checklist
- [ ] Test CNIC images (front + back) saved at known paths
- [ ] Test customer record in CBS mock with card = ACTIVE
- [ ] Test customer record in CBS mock with old NIC not expired
- [ ] Dashboard seeded with ≥1,200 mock case records
- [ ] Action Centre seeded with ≥1 pending NIC06 task
- [ ] Chat conversation history cleared (fresh session)
- [ ] All mock data uses non-sensitive, fake PII

### Browser & Environment
- [ ] Chrome Version 120+ (or latest stable)
- [ ] All browser extensions disabled (especially adblock, password managers)
- [ ] Browser window maximised / full-screen mode ready
- [ ] Camera and mic permissions pre-granted (if any)
- [ ] Pop-up blockers disabled for demo domain (localhost / staging)
- [ ] Cache disabled / incognito mode for clean recording runs
- [ ] Network throttling: disable (use local network — do not simulate slow 3G)

### Recording Software
- [ ] OBS Studio / Camtasia / ScreenRec installed and configured
- [ ] Recording profile set: 1920×1080, 30 fps, MP4 (H.264)
- [ ] Audio input source: None (VO recorded separately)
- [ ] Cursor highlight / click animation enabled (accessibility setting)
- [ ] Hotkeys memorised: Start/Stop Recording, Pause, Scene Switch
- [ ] Storage: ≥10 GB free on recording drive
- [ ] External monitor disconnected (record on single screen to avoid confusion)

### Rehearsal Runs
- [ ] **Run 1 (Dry — no recording):** Walk through entire flow. Check every click path. Fix broken links, missing data, slow responses.
- [ ] **Run 2 (Timed — with stopwatch):** Record app flow only (no VO). Measure each segment. Adjust pacing.
- [ ] **Run 3 (Full — with VO playback):** Play pre-recorded scratch VO. Sync B-roll and screen recording timings. Identify cuts.
- [ ] **Run 4 (Dress — recorded):** Full recording with final VO + music. Export and review.
- [ ] **Run 5 (Backup):** Record each segment separately (iso clips) for easier re-editing if needed.

### Fallback Plan
- [ ] Screenshots of every screen saved in `demo/screenshots/` (in case recording fails)
- [ ] Each demo flow can be narrated over static screenshots as worst-case backup
- [ ] PDF export of this script printed / second screen for VO reference
- [ ] Power bank / laptop charger plugged in (no battery surprises)
- [ ] Offline copies of all dependencies (BPMN engine, mock APIs) if internet drops
