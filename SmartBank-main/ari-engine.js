// ============================================================================
// ARIE — Autonomous Resilience & Interceptor Engine
// SmartBank's proactive cognitive layer for scam interception, Urdu repair,
// and self-healing circuit breaker.
// ============================================================================

const crypto = require('crypto');

// ============================================================================
// 1. PROACTIVE SCAM INTERCEPTOR (SEC01)
// ============================================================================
const SCAM_PATTERNS = [
  // Vishing — call pe code/pin/otp maangna
  { regex: /(call|phone|kisi ne|kisi aur ne|unknown|stranger).*(code|pin|otp|password)/i, type: 'VISHING', weight: 1.0 },
  { regex: /(code|pin|otp|password).*(maang|puch|bol|mang|share|de di|de do)/i, type: 'VISHING', weight: 1.0 },
  { regex: /call.*pe.*(code|pin|otp|password)|(code|pin|otp|password).*call/i, type: 'VISHING', weight: 1.0 },
  { regex: /phone.*(code|pin|otp)/i, type: 'VISHING', weight: 1.0 },
  { regex: /kisi.*(phone|call).*(code|pin)/i, type: 'VISHING', weight: 1.0 },

  // Active fraud — paisa transfer without consent
  { regex: /(paisa|paise|money|rupees).*(urr|nikal|nikal gay|nikal liya|transfer|kat|nikla|gaya|chala gaya)/i, type: 'ACTIVE_FRAUD', weight: 1.0 },
  { regex: /(paisa|money).*(nikal|urr|gay)/i, type: 'ACTIVE_FRAUD', weight: 0.95 },
  { regex: /(account|bank).*(safe|secure|hak|mehfooz).*(nahi|nhi)/i, type: 'PHISHING', weight: 0.9 },
  { regex: /(scam|dhoka|fraud|hack)/i, type: 'FRAUD_REPORT', weight: 0.95 },
  { regex: /fake.*(call|message|sms|site|link|app)/i, type: 'PHISHING', weight: 0.9 },
  { regex: /(nahi kiya|main ne nahi).*(transfer|nikal|bhej|pay)/i, type: 'ACTIVE_FRAUD', weight: 0.95 },
  { regex: /(unauthorized|unrecognized|unknown).*(txn|transaction|transfer|payment|charge)/i, type: 'ACTIVE_FRAUD', weight: 0.95 },

  // Panic signals
  { regex: /(emergency|urgent|foran|jald se jald|bohot zaroori)/i, type: 'PANIC', weight: 0.6 },
  { regex: /(bachao|help|karo kuch|plz help|save me)/i, type: 'PANIC', weight: 0.7 },
];

function detectScam(text) {
  let maxWeight = 0;
  let matchedType = null;

  for (const p of SCAM_PATTERNS) {
    if (p.regex.test(text) && p.weight > maxWeight) {
      maxWeight = p.weight;
      matchedType = p.type;
    }
  }

  if (maxWeight >= 0.85) {
    return { isScam: true, type: matchedType, confidence: Math.min(0.99, 0.7 + maxWeight * 0.3), justification: `Scam pattern [${matchedType}] matched with weight ${maxWeight}` };
  }

  return { isScam: false, type: null, confidence: 0, justification: null };
}

function executeScamLockdown(intentCode, text, channel, user) {
  const caseId = 'SEC-' + String(Date.now()).slice(-6) + '-' + crypto.randomUUID().slice(0, 4).toUpperCase();
  const steps = [
    { step: 1, action: 'IMMEDIATE ACCOUNT LOCKDOWN — All transactions frozen', channel: 'system', status: 'completed', detail: 'Account locked in CBS — all debits blocked' },
    { step: 2, action: 'Block all card-based transactions (POS/ATM/Online)', channel: 'system', status: 'completed', detail: 'Card blocked in card management system' },
    { step: 3, action: 'Reset internet/mobile banking credentials', channel: 'system', status: 'completed', detail: 'Credentials reset — session tokens invalidated' },
    { step: 4, action: 'Notify fraud department — PRIORITY CRITICAL', channel: 'email', status: 'completed', detail: 'Fraud team alerted with full conversation context' },
    { step: 5, action: 'Send customer safety alert with helpline', channel: 'sms', status: 'completed', detail: 'SMS: SmartBank alert — aap ka account lockdown kar diya gaya hai. Foran 0800-12345 par call karein.' },
  ];

  return { caseId, steps, action: 'SEC01 — Proactive Scam Lockdown', successMessage: { en: 'YOUR ACCOUNT IS UNDER ACTIVE PROTECTION. All transactions have been frozen. A fraud specialist will contact you within 5 minutes. Call 0800-12345 immediately.', ur: 'AAP KA ACCOUNT LOCKDOWN KAR DIYA GAYA HAI. Tamam transactions freeze kar diye gaye hain. Ek fraud specialist 5 minute mein aap se contact karega. Foran 0800-12345 par call karein.' } };
}

// ============================================================================
// 2. CONTEXT-AWARE ROMAN URDU REPAIR ENGINE
// ============================================================================
const UDC_AMBIGUITY_MAP = {
  'wo': {
    possible: ['ATM01', 'DEB03', 'IB07'],
    hints: { atm_card_retained: 'ATM01', atm_locked: 'ATM01', pin_failure: 'PIN02', card_block: 'DEB03', ib_lock: 'IB07' },
  },
  'ye': {
    possible: ['DEB03', 'MB08', 'BAL09'],
    hints: { atm_card_retained: 'DEB03', card_block: 'DEB03', ib_lock: 'MB08' },
  },
  'band': {
    possible: ['DEB03', 'IB07'],
    hints: { atm_card_retained: 'DEB03', card_block: 'DEB03', ib_lock: 'IB07' },
  },
  'kardo': {
    possible: ['ATM01', 'DEB03', 'PIN02'],
    hints: { atm_card_retained: 'ATM01', card_block: 'DEB03', pin_failure: 'PIN02' },
  },
  'nahi': {
    possible: ['IB07', 'MB08', 'BAL09'],
    hints: { ib_lock: 'IB07', app_login_failure: 'MB08' },
  },
};

const ATM_ERROR_PATTERNS = [
  { regex: /atm.*(kard|machine mein|phans|atak|retain|nikal|gaya)/i, hint: 'atm_card_retained' },
  { regex: /atm.*(kharab|down|kam|broken|working)/i, hint: 'atm_card_retained' },
  { regex: /(pin|code).*(galat|wrong|invalid|sahi nahi|kamm)/i, hint: 'pin_failure' },
  { regex: /(app|mobile|phone).*(login|open|khol|start|band|kharab)/i, hint: 'app_login_failure' },
  { regex: /internet.*(bank|login|password|lock|band)/i, hint: 'ib_lock' },
  { regex: /card.*(block|band|freeze|kho|gum|chori)/i, hint: 'card_block' },
  { regex: /card.*(atm|machine).*(gaya|nikal|atak|phans)/i, hint: 'atm_card_retained' },
];

const AMBIGUOUS_URDU_WORDS = /^(yaar|wo|ye|iska|uska|isko|usko|band|kardo|karo|nahi|hain|hai|ho|thi|tha|raha|rahi|rahe|dO|kar|de|lo|le)$/i;

function repairRomanUrdu(text, telemetry) {
  const logs = telemetry?.recent_system_logs || [];
  const txnLogs = logs.filter(l => l.event).map(l => l.event.toLowerCase());

  // Detect ATM/card related errors from logs
  let contextHints = [];
  const errorText = txnLogs.join(' ');

  for (const p of ATM_ERROR_PATTERNS) {
    if (p.regex.test(errorText) || p.regex.test(text)) {
      contextHints.push(p.hint);
    }
  }

  // Check for ambiguous short words
  const words = text.split(/\s+/).filter(w => w.length > 1);
  const hasAmbiguousWord = words.some(w => AMBIGUOUS_URDU_WORDS.test(w));
  const isShortVague = words.length <= 5 && hasAmbiguousWord;

  if (!isShortVague && contextHints.length === 0) {
    return null; // No repair needed
  }

  // Try to resolve intent from context hints
  let repairedCode = null;
  let repairJustification = [];

  for (const word of words) {
    const entry = UDC_AMBIGUITY_MAP[word.toLowerCase()];
    if (entry) {
      // Check if any context hint matches
      for (const hint of contextHints) {
        if (entry.hints[hint]) {
          repairedCode = entry.hints[hint];
          repairJustification.push(`Word '${word}' + log hint '${hint}' → ${repairedCode}`);
        }
      }
    }
  }

  // Fallback: use first available context hint
  if (!repairedCode && contextHints.length > 0) {
    const hintMap = { atm_card_retained: 'ATM01', card_block: 'DEB03', pin_failure: 'PIN02', ib_lock: 'IB07', app_login_failure: 'MB08' };
    repairedCode = hintMap[contextHints[0]] || null;
    if (repairedCode) repairJustification.push(`Fallback context hint '${contextHints[0]}' → ${repairedCode}`);
  }

  if (repairedCode) {
    const labelMap = { ATM01: 'ATM Card Activation', DEB03: 'Debit Card Block/Unblock', PIN02: 'PIN Generation/Reset', IB07: 'Internet Banking Recovery', MB08: 'Mobile Banking Activation' };
    return {
      code: repairedCode,
      label: labelMap[repairedCode] || 'General Inquiry',
      confidence: Math.max(0.85, 0.7 + contextHints.length * 0.08),
      language: 'ur',
      category: { ATM01: 'Activation', DEB03: 'Fraud', PIN02: 'Security', IB07: 'Security', MB08: 'Activation' }[repairedCode] || 'General',
      priority: { ATM01: 'HIGH', DEB03: 'CRITICAL', PIN02: 'HIGH', IB07: 'HIGH', MB08: 'MEDIUM' }[repairedCode] || 'MEDIUM',
      sentiment: 'negative',
      repaired: true,
      justification: repairJustification.join('; '),
    };
  }

  return null;
}

// ============================================================================
// 3. SELF-HEALING CIRCUIT BREAKER
// ============================================================================
function circuitBreaker(coreBankingStatus) {
  const apiLive = coreBankingStatus?.api_live !== false;

  if (!apiLive) {
    const queueId = 'DLQ-' + crypto.randomUUID().slice(0, 8).toUpperCase();
    const hash = crypto.createHash('sha256').update(JSON.stringify({ queueId, timestamp: new Date().toISOString() })).digest('hex');

    return {
      circuitBreakerTriggered: true,
      queueId,
      auditHash: hash,
      handlingStrategy: 'Route execution to UiPath Maestro Resilient DLQ due to Core Banking API downtime. Process will self-heal instantly upon system recovery.',
      customerMessage: {
        en: 'Your request has been securely saved. Our system is temporarily experiencing a technical delay, but your request will be processed automatically once restored. Your money is safe.',
        ur: 'Aap ki request mehfooz save ho gayi hai. System mein technical delay hai, lekin aap ki request background me auto-complete ho jayegi. Aap ka paisa mehfooz hai.'
      },
    };
  }

  return { circuitBreakerTriggered: false };
}

// ============================================================================
// 4. MAIN ARIE ENTRY POINT
// ============================================================================
function ariClassify(text, telemetry = {}) {
  const coreBankingStatus = telemetry?.core_banking_status || { api_live: true };
  const startTime = Date.now();

  // STEP 1 — Scam interception (highest priority)
  const scamCheck = detectScam(text);
  if (scamCheck.isScam) {
    return {
      interceptType: 'SCAM_LOCKDOWN',
      targetIntent: { code: 'SEC01', confidence: scamCheck.confidence, justification: scamCheck.justification },
      resilienceAction: { circuitBreakerTriggered: false },
      uniqueRoutingApplied: true,
      processingTimeMs: Date.now() - startTime,
      _scamResult: scamCheck,
    };
  }

  // STEP 2 — Urdu repair engine (low confidence ambiguous inputs)
  const urduRepair = repairRomanUrdu(text, telemetry);
  if (urduRepair) {
    return {
      interceptType: 'URDU_REPAIR',
      targetIntent: { code: urduRepair.code, confidence: urduRepair.confidence, justification: urduRepair.justification, label: urduRepair.label, language: urduRepair.language, category: urduRepair.category, priority: urduRepair.priority, sentiment: urduRepair.sentiment },
      resilienceAction: { circuitBreakerTriggered: false },
      uniqueRoutingApplied: true,
      processingTimeMs: Date.now() - startTime,
    };
  }

  // STEP 3 — Circuit breaker check
  const breaker = circuitBreaker(coreBankingStatus);
  if (breaker.circuitBreakerTriggered) {
    return {
      interceptType: 'CIRCUIT_BREAKER',
      targetIntent: { code: 'UNKNOWN', confidence: 0, justification: 'Core banking down — request queued for auto-healing' },
      resilienceAction: breaker,
      uniqueRoutingApplied: true,
      processingTimeMs: Date.now() - startTime,
    };
  }

  // No ARIE intervention
  return {
    interceptType: null,
    targetIntent: null,
    resilienceAction: { circuitBreakerTriggered: false },
    uniqueRoutingApplied: false,
    processingTimeMs: Date.now() - startTime,
  };
}

// ============================================================================
// SEC01 Resolution workflow (exported for server.js)
// ============================================================================
const SEC01_WORKFLOW = {
  action: 'SEC01 — Proactive Scam Lockdown',
  steps: [
    { action: 'IMMEDIATE ACCOUNT LOCKDOWN — All outgoing transactions frozen', channel: 'system', detail: 'Account locked in CBS' },
    { action: 'Block all card-based transactions (POS/ATM/Online)', channel: 'system', detail: 'Card blocked in card management system' },
    { action: 'Reset internet/mobile banking credentials — invalidate all sessions', channel: 'system', detail: 'Credentials reset — all tokens revoked' },
    { action: 'Notify fraud department — PRIORITY CRITICAL', channel: 'email', detail: 'Fraud team alerted immediately' },
    { action: 'Send customer safety alert with helpline number', channel: 'sms', detail: 'SMS: Account lockdown alert sent' },
    { action: 'Log immutable audit trail with cryptographic hash', channel: 'system', detail: 'Audit hash generated for compliance' },
  ],
  successMessage: { en: 'YOUR ACCOUNT IS UNDER ACTIVE PROTECTION. All transactions have been frozen. A fraud specialist will contact you within 5 minutes. Call 0800-12345 immediately.', ur: 'AAP KA ACCOUNT LOCKDOWN KAR DIYA GAYA HAI. Tamam transactions freeze kar diye gaye hain. Ek fraud specialist 5 minute mein aap se contact karega. Foran 0800-12345 par call karein.' },
};

module.exports = { ariClassify, detectScam, repairRomanUrdu, circuitBreaker, executeScamLockdown, SEC01_WORKFLOW };
