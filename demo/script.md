# SmartBank — 5-Minute Demo Video Script

---

## [00:00–00:30] HOOK — Problem Statement

**Visual:**
- Split screen. Left side: a frustrated man in a shalwar kameez stands at an ATM, inserting his card repeatedly. The screen flashes "CARD BLOCKED". He pulls out his phone, dials a helpline — gets put on hold.
- Right side: grainy phone footage of a long queue outside a bank branch. Text overlay: "40M+ debit cards in Pakistan. 1 call centre for millions."
- The screen freezes. Audio dips. A glitch effect transitions to clean UI.

**Narration (Voiceover — urgent, relatable):**

"You're at an ATM in Karachi. Your card gets blocked. You call the helpline — busy. You go to the branch — the queue is out the door. This isn't a one-off. It's the daily reality for 40 million debit card users in Pakistan.

But what if an AI agent could resolve this — in under sixty seconds — without a single phone call?"

**Transition:**
- Screen wipes to SmartBank logo + tagline: "Banking, Reimagined by AI."
- Subtle whoosh sound effect.

---

## [00:30–01:00] SOLUTION OVERVIEW

**Visual:**
- Animated architecture slide. Background: dark blue gradient with moving particle network.
- Centre: SmartBank logo. Spokes radiate out:
  - **Conversational AI** (multilingual NLU engine)
  - **UiPath RPA** (automation layer)
  - **Maestro BPMN** (workflow orchestration)
  - **Open Banking APIs** (CBS / NADRA / SimSim / Raast)
  - **Operations Dashboard** (real-time analytics)
- Each spoke lights up sequentially as mentioned.
- Bottom bar: "Powered by OpenAI + UiPath + Django."

**Narration (Voiceover — authoritative, paced):**

"Introducing SmartBank — an agentic AI platform purpose-built for Pakistan's banking ecosystem.

We combine three layers: a multilingual conversational AI that understands Urdu, Roman Urdu, and English; UiPath robots that execute banking operations; and a Maestro BPMN engine that orchestrates every workflow end to end.

All connected through open banking APIs to core systems — CBS, NADRA verification, SimSim, and Raast — with zero legacy migration required."

---

## [01:00–02:00] LIVE DEMO — Customer Journey (DEB03 Card Block)

**Visual:**
- Screen recording (browser window, clean Chrome with SmartBank portal).
- Customer opens chat widget (bottom-right slide-in). Types: "Mera debit card block karo."
- Chat bubble appears: AI Agent responds in Roman Urdu: "Ji, main aapki madad kar sakta hoon. Apna CNIC number share karein?"
- User types CNIC. Loading spinner.
- Right panel overlay: **Intent Classification** box shows `DEB03 (Card Block) — Confidence: 0.94`.
- Screen splits: left stays on chat, right shows animated **Maestro BPMN** flowchart.
  - Nodes light up in sequence: `START → Validate Customer → Check Card Status → Block Card → Notify → END`.
  - Green checkmark on each completed node.
- UiPath Robot icon (UiPath logo) appears. Terminal-style output: `Calling CBS API... card_status=ACTIVE → executing BLOCK... Done.`
- Phone mockup pops in: SMS received. "Your debit card xxxx-xxxx-xxxx-1234 has been blocked successfully. Ref #SBK-28491."
- Email preview: formal notification with reference number.
- Chat widget confirms in Urdu: "Aapka debit card block kar diya gaya hai. Ref #SBK-28491."

**Narration (Voiceover — upbeat, demonstration energy):**

"Let's watch a real customer journey.

A user opens the SmartBank chat widget and types in Urdu: 'Block my debit card.' The AI agent responds naturally, asks for their CNIC — and within seconds classifies this as a Card Block intent with ninety-four percent confidence.

Behind the scenes, the Maestro engine kicks off a BPMN workflow. Each step — validate, check status, execute, notify — lights up in real time.

Our UiPath robot calls the bank's CBS API, performs the block, and immediately triggers an SMS and email notification to the customer. All of this — zero human intervention."

---

## [02:00–03:00] HUMAN APPROVAL DEMO (NIC06 — ID Update)

**Visual:**
- Browser tab switches to **NIC Update** flow in SmartBank.
- Chat widget: User uploads a photo of their new CNIC (front & back).
- Right panel: **OCR Engine** box. Scanned document data pops in: Name, Father's Name, ID Number, Date of Birth, Expiry Date.
- Fraud scoring overlay: `Fraud Score: 12/100 (Low Risk)` with green badge.
- Screen transitions to **SmartBank Action Centre** (agent dashboard).
- A task appears: **NIC06 - ID Update - Awaiting Approval**.
  - Fields: Customer info, old vs new ID side by side, fraud score, document images.
- Manager clicks **Approve**.
  - Confirmation modal. Click.
- CBS call animation (similar to before). Notification sent to customer.
- Chat updates: "Your CNIC update has been approved. Thank you."

**Narration (Voiceover — explanatory, calm):**

"Some operations need a human in the loop — like an ID update.

Here a customer uploads a photo of their new CNIC. The AI immediately performs OCR extraction, pulls the key fields, and runs a fraud risk assessment. Low risk — just twelve out of a hundred.

This automatically creates a task in the Action Centre, the operations dashboard used by bank managers.

With a single click, the manager approves the update. SmartBank calls CBS, updates the record, and notifies the customer. The entire cycle — under ninety seconds."

---

## [03:00–04:00] DASHBOARD & ANALYTICS

**Visual:**
- Full screen: **SmartBank Operations Dashboard** (dark theme, glassmorphism cards).
- Top row — KPI cards with animated counters:
  - `Cases Today: 1,247` (incrementing)
  - `Avg Resolution: 38s` (green arrow down)
  - `Auto Resolution Rate: 87%` (green)
  - `SLA Compliance: 96%` (green)
- Centre: **Case Timeline** — horizontal stacked bar chart showing workflows executed today. Each bar is coloured by workflow type (DEB03 = blue, NIC06 = orange, P2P = green, etc.).
- Bottom: **Recent Activity** table — live-streaming rows of resolved cases with timestamps.
- Right panel: **SLA Breach Alerts** — currently empty, green tick: "No active breaches."
- Camera zoom on the automation rate: 87%.

**Narration (Voiceover — confident, data-driven):**

"Now the command centre — the SmartBank Operations Dashboard.

Real-time KPIs: over twelve hundred cases handled today. Average resolution time — thirty-eight seconds. Eighty-seven percent of all cases resolved without any human touch. SLA compliance at ninety-six percent.

The case timeline gives operations managers a live view of every workflow executed — colour-coded by type. And the SLA breach panel stays clean. SmartBank doesn't just automate — it monitors, measures, and improves."

---

## [04:00–04:30] INNOVATION HIGHLIGHTS

**Visual:**
- Montage-style rapid cuts (each ~5 seconds):
  1. Chat widget cycling through Urdu, Roman Urdu, English messages.
  2. BPMN diagram for each of the 6 automated workflow types (DEB03, DEB05, NIC06, P2P, BALANCE, STATUS) — 6 highlighted green, 2 greyed out.
  3. Stopwatch animation stopping at "42s" with "AVG RESOLUTION" text.
  4. PCI-DSS shield badge animates in + "Compliant" stamp.
  5. Puzzle pieces labelled "CBS", "NADRA", "SimSim", "Raast", "Email", "SMS" slotting into a central hub.

**Narration (Voiceover — faster, punchy):**

"Here's what makes SmartBank different.

One — multilingual AI that speaks your customer's language.

Two — six out of eight workflow types achieve full zero-touch automation.

Three — average resolution time under forty-five seconds.

Four — enterprise-grade PCI-DSS compliance built in from day one.

And five — a plug-in adapter architecture that connects to any CBS, any third-party API, without changing a single line of core banking code."

---

## [04:30–05:00] CLOSING & CTA

**Visual:**
- Screen fades to a dark gradient background. Centre text appears letter by letter:
  - "SmartBank: Making banking intelligent, accessible, and instant — for every Pakistani."
- Below, team credits scroll slowly (marquee style):
  - Full names, roles (e.g., "Muhammad Ali — AI Engineer", "Ayesha Khan — Product Lead" — use actual team names).
- Bottom third: **QR Code** (placeholder — "SCAN TO VIEW ON GITHUB") + text: `github.com/your-org/smartbank`
- Contact line: `team@smartbank.ai`
- Final frame: SmartBank logo + tagline + "Thank You" in Urdu (شکریہ).
- Fade to black.

**Narration (Voiceover — warm, inspirational, slower pace):**

"SmartBank is more than a demo. It's a blueprint for the future of banking in Pakistan — where every customer gets instant service in their own language, without standing in a single queue.

This was built by [Team Name], in forty-eight hours, for the Agentic AI Banking Hackathon.

Scan the code to explore the full repository. Contribute. Fork it. Build the next piece.

Thank you — and banking, reimagined by AI."

**[END — 05:00]**

---

## Appendix: Narration Script (Raw VO Text)

Use this standalone block for recording voiceover if needed.

```
[00:00-00:30]
You're at an ATM in Karachi. Your card gets blocked. You call the helpline — busy. You go to the branch — the queue is out the door. This isn't a one-off. It's the daily reality for 40 million debit card users in Pakistan. But what if an AI agent could resolve this — in under sixty seconds — without a single phone call?

[00:30-01:00]
Introducing SmartBank — an agentic AI platform purpose-built for Pakistan's banking ecosystem. We combine three layers: a multilingual conversational AI that understands Urdu, Roman Urdu, and English; UiPath robots that execute banking operations; and a Maestro BPMN engine that orchestrates every workflow end to end. All connected through open banking APIs to core systems — CBS, NADRA verification, SimSim, and Raast — with zero legacy migration required.

[01:00-02:00]
Let's watch a real customer journey. A user opens the SmartBank chat widget and types in Urdu: 'Block my debit card.' The AI agent responds naturally, asks for their CNIC — and within seconds classifies this as a Card Block intent with ninety-four percent confidence. Behind the scenes, the Maestro engine kicks off a BPMN workflow. Each step — validate, check status, execute, notify — lights up in real time. Our UiPath robot calls the bank's CBS API, performs the block, and immediately triggers an SMS and email notification to the customer. All of this — zero human intervention.

[02:00-03:00]
Some operations need a human in the loop — like an ID update. Here a customer uploads a photo of their new CNIC. The AI immediately performs OCR extraction, pulls the key fields, and runs a fraud risk assessment. Low risk — just twelve out of a hundred. This automatically creates a task in the Action Centre, the operations dashboard used by bank managers. With a single click, the manager approves the update. SmartBank calls CBS, updates the record, and notifies the customer. The entire cycle — under ninety seconds.

[03:00-04:00]
Now the command centre — the SmartBank Operations Dashboard. Real-time KPIs: over twelve hundred cases handled today. Average resolution time — thirty-eight seconds. Eighty-seven percent of all cases resolved without any human touch. SLA compliance at ninety-six percent. The case timeline gives operations managers a live view of every workflow executed — colour-coded by type. And the SLA breach panel stays clean. SmartBank doesn't just automate — it monitors, measures, and improves.

[04:00-04:30]
Here's what makes SmartBank different. One — multilingual AI that speaks your customer's language. Two — six out of eight workflow types achieve full zero-touch automation. Three — average resolution time under forty-five seconds. Four — enterprise-grade PCI-DSS compliance built in from day one. And five — a plug-in adapter architecture that connects to any CBS, any third-party API, without changing a single line of core banking code.

[04:30-05:00]
SmartBank is more than a demo. It's a blueprint for the future of banking in Pakistan — where every customer gets instant service in their own language, without standing in a single queue. This was built by [Team Name], in forty-eight hours, for the Agentic AI Banking Hackathon. Scan the code to explore the full repository. Contribute. Fork it. Build the next piece. Thank you — and banking, reimagined by AI.
```
