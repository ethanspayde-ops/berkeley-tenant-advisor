from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import requests as http_requests
import time
from collections import deque

app = Flask(__name__)
CORS(app, origins=["https://berkeleytenant.com", "https://www.berkeleytenant.com"])

# Simple in-memory rate limiter: max 20 requests per minute per IP
request_log = {}

def is_rate_limited(ip):
    now = time.time()
    if ip not in request_log:
        request_log[ip] = deque()
    # Remove requests older than 60 seconds
    while request_log[ip] and request_log[ip][0] < now - 60:
        request_log[ip].popleft()
    if len(request_log[ip]) >= 20:
        return True
    request_log[ip].append(now)
    return False

SYSTEM_PROMPT = """You are an AI assistant (not a human, not an attorney) that provides general information about Berkeley, California tenant rights. You have deep knowledge of the Berkeley Rent Stabilization Ordinance (RSO), eviction protections, habitability standards, security deposits, and tenant resources.

IDENTITY: Always identify as an AI assistant, not a human or attorney. On first message say: "As an AI assistant (not an attorney)..."

SCOPE: Only answer questions related to tenant rights, housing, renting, landlord-tenant law in Berkeley and California. If asked anything outside this scope, respond only with: "I can only help with Berkeley tenant rights and housing questions. Try asking about rent control, evictions, repairs, security deposits, or your rights as a tenant."

RESPONSE STYLE:
- Be concise. Keep total response under 300 words.
- Use **bold** for key legal terms only.
- Use bullet points for lists of rights or requirements.
- Never be repetitive.

LANGUAGE DISCIPLINE - CRITICAL:
Stay DESCRIPTIVE of what the law says. Never PRESCRIPTIVE about what this specific user should do.

For situation-specific questions, use TWO clearly separated sections:

"What the ordinance requires:" (describe the law neutrally)
- Use: "The RSO requires...", "Under BMC Section X, landlords must...", "California law states..."

"General options available under the RSO:" (neutral framing - NOT guidance for their specific case)
- Use: "The ordinance provides a remedy of...", "One available option under the RSO is..."
- NEVER use: "you should", "you'll win", "in your case", "I recommend", "you need to"
- NEVER give a step-by-step action plan directed at the user personally

RENT WITHHOLDING AND HIGH-STAKES QUESTIONS:
For questions about withholding rent, lease-breaking, or eviction defense - be especially careful. Only describe that these remedies exist in law. Add: "These remedies have specific procedural requirements. For your situation, consult a tenant rights attorney before taking any action."

CITATIONS:
- Cite the specific statute when stating a legal rule: "Under BMC Section 13.76.130..." or "California Civil Code Section 1950.5 requires..."
- When mentioning the Berkeley Rent Board always hyperlink: [Berkeley Rent Board](https://www.cityofberkeley.info/rent)

ATTORNEY REFERRAL:
- Recommend a tenant rights attorney FIRST, then the Rent Board second.
- Free help: East Bay Community Law Center (510) 548-4040 or Bay Area Legal Aid (415) 982-1300.
- For case-specific or high-stakes questions always end with: "For your specific situation, please consult a tenant rights attorney rather than relying on general information."

ACCURACY:
- Do not make definitive statements about arbitration clauses - refer to an attorney.
- If uncertain, say "You may want to verify this with an attorney or the Rent Board directly."
- Never predict outcomes for a specific person's case.

HABITABILITY: Cover all issues - heating, plumbing, weatherproofing, mold, pests, electrical, appliances, structural, sanitation. Tenant remedies include written notice, repair-and-deduct (up to one month rent), rent withholding after proper steps, Rent Board complaint, and in serious cases breaking the lease.

CONFIDENCE AND SOURCE FORMAT:
End EVERY response with this block and nothing else after it:

---
**Source:** [specific statute only - e.g. BMC Section 13.76.130, California Civil Code 1950.5]
**Confidence:** High/Medium/Low - [one sentence max]
---"""

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Berkeley Tenant Rights Advisor</title>
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "248fe58ac1d24270ad07335ee26c8979"}'></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;overflow:hidden}
body{font-family:Arial,sans-serif;background:#f4f1ea;color:#1a1814;display:flex;flex-direction:column;height:100dvh;max-height:100dvh}
#header{background:#003262;color:white;padding:12px 16px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;border-bottom:3px solid #FDB515;min-height:60px}
#header h1{font-size:15px;font-weight:bold;display:flex;align-items:center;gap:6px;flex:1;margin-right:10px;line-height:1.3}
#header-right{display:flex;align-items:center;gap:8px;flex-shrink:0}
#header span.badge{font-size:11px;background:rgba(253,181,21,0.2);border:1px solid #FDB515;color:#FDB515;padding:4px 10px;border-radius:20px;white-space:nowrap}
#reset-btn{font-size:11px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.3);color:white;padding:5px 10px;border-radius:6px;cursor:pointer;white-space:nowrap}
#reset-btn:hover{background:rgba(255,255,255,0.2)}
#mobile-topics{display:none;overflow-x:auto;-webkit-overflow-scrolling:touch;padding:8px 12px;gap:8px;background:#fff;border-bottom:1px solid #d8d3c5;flex-shrink:0;scrollbar-width:none}
#mobile-topics::-webkit-scrollbar{display:none}
.mobile-chip{flex-shrink:0;padding:6px 12px;background:#f4f1ea;border:1px solid #d8d3c5;border-radius:20px;font-size:12px;color:#1a1814;cursor:pointer;white-space:nowrap}
.mobile-chip:active{background:#e8eef5;border-color:#003262;color:#003262}
#wrap{display:flex;flex:1;overflow:hidden;min-height:0}
#sidebar{width:220px;background:#fff;border-right:1px solid #d8d3c5;padding:12px;overflow-y:auto;flex-shrink:0}
#sidebar h3{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#888;margin:0 0 8px 0}
.sec{margin-bottom:14px}
.tb{display:block;width:100%;text-align:left;padding:7px 8px;margin-bottom:3px;background:transparent;border:1px solid transparent;border-radius:6px;font-size:12px;color:#1a1814;cursor:pointer;line-height:1.4}
.tb:hover{background:#e8eef5;border-color:#003262;color:#003262}
#notice{padding:9px;background:#fdf8e8;border:1px solid #e8d48a;border-radius:6px;font-size:11px;color:#7a6500;line-height:1.5}
#chat{flex:1;display:flex;flex-direction:column;overflow:hidden;min-width:0}
#chat-header{padding:11px 16px;background:#fff;border-bottom:1px solid #d8d3c5;flex-shrink:0}
#chat-header h2{font-size:15px;margin-bottom:2px;color:#003262}
#chat-header p{font-size:12px;color:#888}
#msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:11px;-webkit-overflow-scrolling:touch}
.msg{display:flex;gap:8px}
.msg.user{flex-direction:row-reverse;align-self:flex-end;max-width:78%}
.msg.bot{align-self:flex-start;max-width:84%}
.av{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;margin-top:2px}
.msg.bot .av{background:#e8eef5;border:1px solid #003262}
.msg.user .av{background:#003262;color:white;font-size:10px;font-weight:bold}
.bub{padding:9px 13px;border-radius:13px;font-size:14px;line-height:1.6;white-space:pre-wrap;word-wrap:break-word}
.msg.bot .bub{background:#fff;border:1px solid #d8d3c5;border-top-left-radius:3px}
.msg.user .bub{background:#003262;color:white;border-top-right-radius:3px}
.msg-actions{display:flex;gap:6px;margin-top:4px;margin-left:36px;flex-wrap:wrap}
.act-btn{font-size:11px;padding:4px 10px;border-radius:5px;border:1px solid #d8d3c5;background:#fff;cursor:pointer;color:#666}
.act-btn:hover{background:#f0f0f0}
.act-btn.liked{background:#e8f5e9;border-color:#4caf50;color:#2e7d32}
.act-btn.disliked{background:#ffeaea;border-color:#f44336;color:#c62828}
.act-btn.copied{background:#e8eef5;border-color:#003262;color:#003262}
.typing{display:flex;gap:4px;padding:11px 13px;background:#fff;border:1px solid #d8d3c5;border-radius:13px;border-top-left-radius:3px}
.dot{width:6px;height:6px;background:#888;border-radius:50%;animation:boun 1.2s infinite}
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes boun{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-5px)}}
#input-bar{padding:10px 14px;background:#fff;border-top:1px solid #d8d3c5;flex-shrink:0;padding-bottom:max(10px,env(safe-area-inset-bottom))}
#input-row{display:flex;gap:8px;align-items:flex-end;background:#f4f1ea;border:2px solid #d8d3c5;border-radius:11px;padding:8px 11px}
#input-row:focus-within{border-color:#003262}
#inp{flex:1;background:transparent;border:none;outline:none;font-family:Arial,sans-serif;font-size:16px;color:#1a1814;resize:none;line-height:1.5;min-height:22px;max-height:90px;-webkit-appearance:none}
#inp::placeholder{color:#aaa}
#sendbtn{width:34px;height:34px;background:#003262;border:none;border-radius:7px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;color:white}
#sendbtn:hover{background:#002244}
#sendbtn:disabled{background:#bbb;cursor:not-allowed}
#hint{font-size:11px;color:#aaa;margin-top:4px;text-align:center}
#welcome{background:#fff;border:1px solid #d8d3c5;border-radius:11px;padding:14px}
#welcome h3{font-size:15px;margin-bottom:6px;color:#003262}
#welcome p{font-size:13px;color:#888;margin-bottom:11px;line-height:1.5}
#sugs{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.sb{text-align:left;padding:8px 9px;background:#f4f1ea;border:1px solid #d8d3c5;border-radius:7px;font-size:12px;color:#1a1814;cursor:pointer;line-height:1.4}
.sb:hover{background:#e8eef5;border-color:#003262;color:#003262}
#landing{position:fixed;inset:0;background:#003262;z-index:100;display:flex;flex-direction:column;overflow-y:auto}
#landing-inner{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100%;gap:16px;padding:32px 24px;max-width:540px;margin:0 auto;width:100%}
#landing h1{color:#FDB515;font-size:26px;font-weight:bold;text-align:center;line-height:1.2}
#landing .subtitle{color:rgba(255,255,255,0.85);font-size:14px;text-align:center;max-width:440px;line-height:1.6}
#landing .tap-hint{color:rgba(255,255,255,0.55);font-size:12px;text-align:center}
#landing .features{display:flex;flex-direction:column;gap:10px;width:100%}
#landing .feat{background:rgba(255,255,255,0.08);border-left:3px solid #FDB515;border-radius:8px;padding:13px 15px;color:white;font-size:13px;line-height:1.4;cursor:pointer;transition:background .15s;display:flex;flex-direction:row;align-items:center;justify-content:space-between;gap:10px}
#landing .feat:hover{background:rgba(255,255,255,0.14)}
#landing .feat-text strong{color:#FDB515;display:block;margin-bottom:3px;font-size:13px}
#landing .feat-arrow{color:#FDB515;font-size:16px;flex-shrink:0}
#start-btn{background:#FDB515;color:#003262;font-size:15px;font-weight:bold;padding:14px 28px;border:none;border-radius:12px;cursor:pointer;width:100%;max-width:400px}
#start-btn:hover{background:#ffc93c}
#landing .disc-text{color:rgba(255,255,255,0.38);font-size:10.5px;text-align:center;max-width:380px;line-height:1.5}
#toast{position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:#003262;color:white;padding:8px 18px;border-radius:20px;font-size:13px;opacity:0;transition:opacity .3s;pointer-events:none;z-index:1000;white-space:nowrap}
#toast.show{opacity:1}
#mobile-notice{display:none;padding:8px 12px;background:#fdf8e8;border-top:1px solid #e8d48a;font-size:11px;color:#7a6500;line-height:1.5;flex-shrink:0;text-align:center}
@media(min-width:581px){#landing h1{font-size:30px}#landing .subtitle{font-size:15px}}
@media(max-width:580px){#sidebar{display:none}#sugs{grid-template-columns:1fr 1fr}#chat-header{display:none}#msgs{padding:10px}.bub{font-size:13px}#mobile-topics{display:flex}#mobile-notice{display:block}}
@media(max-width:380px){#sugs{grid-template-columns:1fr}#header h1{font-size:12px}#reset-btn{font-size:10px;padding:4px 7px}}
</style>
</head>
<body>

<div id="landing">
  <div id="landing-inner">
    <h1>&#127968; Berkeley Tenant Rights Advisor</h1>
    <p class="subtitle">Free AI-powered legal information for Berkeley tenants. Understand your rights under the Rent Stabilization Ordinance, instantly.</p>
    <p class="tap-hint">Tap a topic to get started:</p>
    <div class="features">
      <div class="feat" onclick="startWithQuestion('What is rent control in Berkeley and does it apply to my unit?','Rent Control')"><div class="feat-text"><strong>&#128203; Rent Control</strong>Learn if your unit is covered and what protections you have.</div><span class="feat-arrow">&#8594;</span></div>
      <div class="feat" onclick="startWithQuestion('What are my rights if my landlord tries to evict me in Berkeley?','Eviction Protections')"><div class="feat-text"><strong>&#128682; Eviction Rights</strong>Understand just cause rules and what to do if you get a notice.</div><span class="feat-arrow">&#8594;</span></div>
      <div class="feat" onclick="startWithQuestion('What are my rights regarding repairs and habitability in Berkeley?','Repairs and Habitability')"><div class="feat-text"><strong>&#128295; Repairs</strong>Know your rights when landlords refuse to fix habitability issues.</div><span class="feat-arrow">&#8594;</span></div>
      <div class="feat" onclick="startWithQuestion('What are my rights regarding security deposits in Berkeley?','Security Deposits')"><div class="feat-text"><strong>&#128176; Deposits</strong>Learn the rules around security deposits and how to get yours back.</div><span class="feat-arrow">&#8594;</span></div>
    </div>
    <button id="start-btn" onclick="startChat()">Ask Your Own Question &#8594;</button>
    <p class="disc-text">AI tool, not a human or attorney. General legal information only. Consult the Berkeley Rent Board (510) 981-7368 or a tenant attorney for your specific situation.</p>
  </div>
</div>

<div id="toast"></div>

<div id="header">
  <h1>&#127968; Berkeley Tenant Rights Advisor</h1>
  <div id="header-right">
    <button id="reset-btn" onclick="resetChat()">&#8635; New Chat</button>
    <span class="badge">&#9679; AI Online</span>
  </div>
</div>

<div id="mobile-topics">
  <button class="mobile-chip" onclick="ask('What is rent control in Berkeley and does it apply to my unit?','Rent Control')">&#128203; Rent Control</button>
  <button class="mobile-chip" onclick="ask('What are the rules around rent increases in Berkeley?','Rent Increases')">&#128200; Rent Increases</button>
  <button class="mobile-chip" onclick="ask('What are my rights if my landlord tries to evict me?','Eviction Protections')">&#128682; Eviction</button>
  <button class="mobile-chip" onclick="ask('What is the Berkeley Rent Board and how can it help me?','Rent Board')">&#127963; Rent Board</button>
  <button class="mobile-chip" onclick="ask('What are my rights regarding repairs and habitability in Berkeley?','Repairs and Habitability')">&#128295; Repairs</button>
  <button class="mobile-chip" onclick="ask('What are the just cause for eviction rules in Berkeley?','Just Cause Eviction')">&#9878; Just Cause</button>
  <button class="mobile-chip" onclick="ask('What are my rights regarding security deposits in Berkeley?','Security Deposits')">&#128176; Deposits</button>
  <button class="mobile-chip" onclick="ask('Can my landlord enter my apartment without notice?','Landlord Entry')">&#128273; Landlord Entry</button>
  <button class="mobile-chip" onclick="ask('What anti-harassment protections do Berkeley tenants have?','Anti-Harassment')">&#128737; Anti-Harassment</button>
  <button class="mobile-chip" onclick="ask('What organizations in Berkeley can help me with tenant issues?','Get Help')">&#128222; Get Help</button>
  <button class="mobile-chip" onclick="ask('What free legal aid is available for Berkeley tenants?','Legal Aid')">&#9878; Legal Aid</button>
</div>

<div id="wrap">
  <div id="sidebar">
    <div class="sec">
      <h3>Common Topics</h3>
      <button class="tb" onclick="ask('What is rent control in Berkeley and does it apply to my unit?','Rent Control')">&#128203; Rent Control Basics</button>
      <button class="tb" onclick="ask('What are the rules around rent increases in Berkeley?','Rent Increases')">&#128200; Rent Increases</button>
      <button class="tb" onclick="ask('What are my rights if my landlord tries to evict me?','Eviction Protections')">&#128682; Eviction Protections</button>
      <button class="tb" onclick="ask('What is the Berkeley Rent Board and how can it help me?','Rent Board')">&#127963; Rent Board</button>
      <button class="tb" onclick="ask('What are my rights regarding repairs and habitability in Berkeley?','Repairs and Habitability')">&#128295; Repairs &amp; Habitability</button>
      <button class="tb" onclick="ask('What are the just cause for eviction rules in Berkeley?','Just Cause Eviction')">&#9878; Just Cause Eviction</button>
      <button class="tb" onclick="ask('What are my rights regarding security deposits in Berkeley?','Security Deposits')">&#128176; Security Deposits</button>
      <button class="tb" onclick="ask('Can my landlord enter my apartment without notice?','Landlord Entry')">&#128273; Landlord Entry Rights</button>
      <button class="tb" onclick="ask('What anti-harassment protections do Berkeley tenants have?','Anti-Harassment')">&#128737; Anti-Harassment</button>
    </div>
    <div class="sec">
      <h3>Resources</h3>
      <button class="tb" onclick="ask('What organizations in Berkeley can help me with tenant issues?','Get Help')">&#128222; Get Help / Contacts</button>
      <button class="tb" onclick="ask('What free legal aid is available for Berkeley tenants?','Legal Aid')">&#9878; Legal Aid</button>
    </div>
    <div id="notice"><strong>Legal Notice:</strong> This is an AI tool, not a human or attorney. General information only, not legal advice. Contact the Berkeley Rent Board at (510) 981-7368 or a tenant attorney for your specific situation. Conversation topics are anonymously logged.</div>
  </div>

  <div id="chat">
    <div id="chat-header">
      <h2>Berkeley Tenant Rights Advisor</h2>
      <p>Ask anything about the Rent Stabilization Ordinance, evictions, deposits, repairs, and more.</p>
    </div>
    <div id="msgs">
      <div class="msg bot">
        <div class="av">&#127968;</div>
        <div id="welcome">
          <h3>Welcome, Berkeley Tenant!</h3>
          <p>I am an AI assistant, not a human or attorney. I can help you understand your rights under Berkeley's Rent Stabilization Ordinance. No account needed - just ask below.</p>
          <div id="sugs">
            <button class="sb" onclick="ask('Does rent control apply to my Berkeley apartment?','Rent Control')">&#127962; Does rent control apply to my unit?</button>
            <button class="sb" onclick="ask('My landlord wants to raise my rent. What are the limits in Berkeley?','Rent Increases')">&#128200; My landlord wants to raise my rent</button>
            <button class="sb" onclick="ask('I received an eviction notice in Berkeley. What should I do?','Eviction Protections')">&#128680; I got an eviction notice</button>
            <button class="sb" onclick="ask('Landlord not making repairs. What are my rights in Berkeley?','Repairs and Habitability')">&#128295; My landlord refuses to make repairs</button>
          </div>
        </div>
      </div>
    </div>
    <div id="input-bar">
      <div id="input-row">
        <textarea id="inp" placeholder="Type your question here..." rows="1"></textarea>
        <button id="sendbtn" onclick="sendMsg()">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M14 8L2 2l3 6-3 6 12-6z" fill="white"/></svg>
        </button>
      </div>
      <div id="hint">Press Enter to send &middot; Shift+Enter for new line</div>
    </div>
  </div>
</div>

<div id="mobile-notice">
  <strong>Legal Notice:</strong> This is an AI tool, not a human or attorney. General information only, not legal advice. Contact the Berkeley Rent Board at (510) 981-7368 or a tenant attorney for your specific situation.
</div>

<!-- Privacy Policy Modal -->
<div id="privacy-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.78);z-index:9998;overflow-y:auto;padding:20px">
  <div style="background:white;border-radius:14px;padding:28px;max-width:560px;margin:20px auto;font-family:Arial,sans-serif">
    <h2 style="font-size:17px;color:#003262;margin-bottom:16px;font-weight:bold">Privacy Policy</h2>
    <p style="font-size:12px;color:#888;margin-bottom:12px">Last updated: July 2026</p>
    <p style="font-size:13px;color:#444;line-height:1.7;margin-bottom:10px"><strong>What we collect:</strong> We log the topic category of questions (e.g. "Rent Control") and your feedback ratings (helpful/not helpful) anonymously. We do not collect your name, email, IP address, or the full text of your questions.</p>
    <p style="font-size:13px;color:#444;line-height:1.7;margin-bottom:10px"><strong>How it is used:</strong> Logged data is used solely to understand which legal topics Berkeley tenants seek information about most, for research purposes related to legal access and technology.</p>
    <p style="font-size:13px;color:#444;line-height:1.7;margin-bottom:10px"><strong>Third parties:</strong> Topic and feedback data is stored in Google Sheets. Conversation text is processed by Groq (AI inference provider) and is not stored by this tool. Site visit analytics are collected by Cloudflare Web Analytics (privacy-preserving, no cookies, no personal data).</p>
    <p style="font-size:13px;color:#444;line-height:1.7;margin-bottom:10px"><strong>Your rights:</strong> Because we do not collect personally identifiable information, there is no personal data to access, export, or delete. If you have questions, contact: berkeleytenant.com</p>
    <p style="font-size:13px;color:#444;line-height:1.7;margin-bottom:16px"><strong>California residents:</strong> Under the CCPA, you have rights regarding personal information. Because we do not collect personal information as defined by the CCPA (name, email, IP address, or other identifiers), these rights are not applicable to this tool.</p>
    <button onclick="document.getElementById('privacy-modal').style.display='none'" style="width:100%;padding:12px;background:#003262;color:white;border:none;border-radius:8px;font-size:14px;font-weight:bold;cursor:pointer">Close</button>
  </div>
</div>

<!-- Disclaimer Popup -->
<div id="disc-wrap" style="position:fixed;inset:0;background:rgba(0,0,0,0.78);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px">
  <div style="background:white;border-radius:14px;padding:28px;max-width:460px;width:100%;box-shadow:0 8px 40px rgba(0,0,0,0.4);font-family:Arial,sans-serif">
    <h2 style="font-size:17px;color:#003262;margin-bottom:12px;font-weight:bold">&#9878; Before You Continue</h2>
    <p style="font-size:13px;color:#444;line-height:1.7;margin-bottom:8px">The Berkeley Tenant Rights Advisor is an <strong>AI tool, not a human and not an attorney</strong>. It provides general legal information only, not legal advice. By continuing you acknowledge:</p>
    <ul style="font-size:13px;color:#444;line-height:1.9;margin:0 0 14px 18px">
      <li>You are interacting with an AI assistant, not a licensed attorney or human advisor</li>
      <li>This tool does not create an attorney-client relationship</li>
      <li>Information may not apply to your specific situation</li>
      <li>For legal advice, consult a licensed tenant rights attorney</li>
      <li>For urgent issues, call the Berkeley Rent Board at (510) 981-7368</li>
      <li>Your conversation topic and feedback are anonymously logged to improve this tool</li>
    </ul>
    <button onclick="this.closest('#disc-wrap').style.display='none'" style="width:100%;padding:13px;background:#003262;color:white;border:none;border-radius:8px;font-size:15px;font-weight:bold;cursor:pointer">I Understand, Continue</button>
    <p style="font-size:11px;color:#888;text-align:center;margin-top:10px">Free legal help: East Bay Community Law Center (510) 548-4040 | Bay Area Legal Aid (415) 982-1300</p>
    <p style="font-size:11px;color:#aaa;text-align:center;margin-top:6px"><a href="#" onclick="document.getElementById('disc-wrap').style.display='none';document.getElementById('privacy-modal').style.display='block';return false;" style="color:#003262">Privacy Policy</a></p>
  </div>
</div>

<script>
var hist=[];var busy=false;
var inp=document.getElementById('inp');
var btn=document.getElementById('sendbtn');
var msgs=document.getElementById('msgs');

inp.addEventListener('input',function(){this.style.height='auto';this.style.height=Math.min(this.scrollHeight,90)+'px';});
inp.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMsg();}});

function sd(){msgs.scrollTop=msgs.scrollHeight;}

function showToast(msg){
  var t=document.getElementById('toast');
  t.textContent=msg;t.classList.add('show');
  setTimeout(function(){t.classList.remove('show');},2000);
}

function track(type,value){
  try{fetch('/track',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({type:type,value:value,ts:new Date().toISOString()})}).catch(function(){});}catch(e){}
}

function trackCustomQuestion(text){
  if(!text||text.length<3) return;
  // Extract a topic keyword from the question for logging
  var lower=text.toLowerCase();
  var topic='Custom Question';
  if(lower.indexOf('rent control')>-1||lower.indexOf('rso')>-1) topic='Rent Control (custom)';
  else if(lower.indexOf('evict')>-1) topic='Eviction (custom)';
  else if(lower.indexOf('repair')>-1||lower.indexOf('habitab')>-1||lower.indexOf('heat')>-1||lower.indexOf('pest')>-1||lower.indexOf('mold')>-1) topic='Repairs (custom)';
  else if(lower.indexOf('deposit')>-1) topic='Security Deposits (custom)';
  else if(lower.indexOf('rent increase')>-1||lower.indexOf('raise my rent')>-1) topic='Rent Increases (custom)';
  else if(lower.indexOf('harassment')>-1) topic='Anti-Harassment (custom)';
  else if(lower.indexOf('entry')>-1||lower.indexOf('enter')>-1) topic='Landlord Entry (custom)';
  else if(lower.indexOf('just cause')>-1) topic='Just Cause (custom)';
  else if(lower.indexOf('legal aid')>-1||lower.indexOf('attorney')>-1||lower.indexOf('lawyer')>-1) topic='Legal Aid (custom)';
  track('category',topic);
}

function startChat(){
  document.getElementById('landing').style.display='none';
  setTimeout(function(){
    inp.focus();
    var row=document.getElementById('input-row');
    row.style.transition='border-color .3s';
    row.style.borderColor='#FDB515';
    setTimeout(function(){row.style.borderColor='';},1200);
  },200);
}

function startWithQuestion(question,category){
  document.getElementById('landing').style.display='none';
  if(category) track('category',category);
  setTimeout(function(){inp.value=question;sendMsg();},200);
}

function resetChat(){
  hist=[];msgs.innerHTML='';
  var welcome=document.createElement('div');welcome.className='msg bot';
  var av=document.createElement('div');av.className='av';av.textContent='🏠';
  var box=document.createElement('div');box.id='welcome';
  var h3=document.createElement('h3');h3.textContent='Welcome, Berkeley Tenant!';h3.style.cssText='font-size:15px;margin-bottom:6px;color:#003262';
  var p=document.createElement('p');p.textContent='Conversation reset. I am an AI assistant, not a human or attorney. Ask me anything about your tenant rights.';p.style.cssText='font-size:13px;color:#888;margin-bottom:11px;line-height:1.5';
  var sugs=document.createElement('div');sugs.style.cssText='display:grid;grid-template-columns:1fr 1fr;gap:6px';
  var items=[
    ['Does rent control apply to my Berkeley apartment?','&#127962; Does rent control apply?','Rent Control'],
    ['My landlord wants to raise my rent. What are the limits in Berkeley?','&#128200; Landlord raising my rent','Rent Increases'],
    ['I received an eviction notice in Berkeley. What should I do?','&#128680; I got an eviction notice','Eviction Protections'],
    ['Landlord not making repairs. What are my rights in Berkeley?','&#128295; Landlord not making repairs','Repairs and Habitability']
  ];
  items.forEach(function(item){
    var b=document.createElement('button');b.className='sb';b.innerHTML=item[1];
    b.onclick=(function(q,cat){return function(){ask(q,cat);};})(item[0],item[2]);
    sugs.appendChild(b);
  });
  box.appendChild(h3);box.appendChild(p);box.appendChild(sugs);
  welcome.appendChild(av);welcome.appendChild(box);msgs.appendChild(welcome);
  showToast('Chat reset!');
}

function renderMarkdown(text){
  var sourceSection='';
  var hrIdx=text.indexOf('\n---\n');
  if(hrIdx!==-1){
    var after=text.substring(hrIdx+5);
    if(after.indexOf('**Source:**')!==-1||after.indexOf('**Confidence:**')!==-1){
      sourceSection=after;text=text.substring(0,hrIdx);
    }
  }
  text=text.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank" style="color:#003262;font-weight:bold;text-decoration:underline">$1</a>');
  text=text.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
  var lines=text.split('\n');var out='';var inList=false;
  for(var i=0;i<lines.length;i++){
    var line=lines[i];
    if(line.match(/^\s*-\s+/)||line.match(/^\s*\*\s+/)){
      if(!inList){out+='<ul style="margin:6px 0 6px 16px">';inList=true;}
      out+='<li style="margin-bottom:3px">'+line.replace(/^\s*[-*]\s+/,'')+'</li>';
    }else{
      if(inList){out+='</ul>';inList=false;}
      if(line.trim()){out+='<p style="margin:4px 0">'+line+'</p>';}
    }
  }
  if(inList){out+='</ul>';}
  if(sourceSection){
    sourceSection=sourceSection.replace(/\*\*Source:\*\*/g,'<strong>Source:</strong>');
    sourceSection=sourceSection.replace(/\*\*Confidence:\*\* High/g,'<strong>Confidence:</strong> <span style="color:#2e7d32;font-weight:bold">High</span>');
    sourceSection=sourceSection.replace(/\*\*Confidence:\*\* Medium/g,'<strong>Confidence:</strong> <span style="color:#e65100;font-weight:bold">Medium</span>');
    sourceSection=sourceSection.replace(/\*\*Confidence:\*\* Low/g,'<strong>Confidence:</strong> <span style="color:#c62828;font-weight:bold">Low</span>');
    sourceSection=sourceSection.replace(/\n/g,'<br>');
    // Clean up markdown that leaked into source box
    sourceSection=sourceSection.replace(/\[([^\]]+)\]\(([^)]+)\)/g,'<a href="$2" target="_blank" style="color:#003262">$1</a>');
    out+='<div style="background:#f0f4f8;border-left:3px solid #003262;border-radius:0 6px 6px 0;padding:8px 12px;margin-top:10px;font-size:12px;color:#444;line-height:1.6">'+sourceSection+'</div>';
  }
  return out;
}

function addMsg(role,text){
  var wrapper=document.createElement('div');wrapper.style.cssText='display:flex;flex-direction:column';
  var d=document.createElement('div');d.className='msg '+role;
  var a=document.createElement('div');a.className='av';a.textContent=role==='bot'?'🏠':'You';
  var b=document.createElement('div');b.className='bub';
  if(role==='bot'){b.innerHTML=renderMarkdown(text);}else{b.textContent=text;}
  d.appendChild(a);d.appendChild(b);wrapper.appendChild(d);
  if(role==='bot'){
    var actions=document.createElement('div');actions.className='msg-actions';
    var likeBtn=document.createElement('button');likeBtn.className='act-btn';likeBtn.textContent='👍 Helpful';
    var dislikeBtn=document.createElement('button');dislikeBtn.className='act-btn';dislikeBtn.textContent='👎 Not helpful';
    var shareBtn=document.createElement('button');shareBtn.className='act-btn';shareBtn.textContent='🔗 Copy';
    likeBtn.onclick=function(){likeBtn.classList.add('liked');likeBtn.textContent='👍 Thanks!';dislikeBtn.disabled=true;track('feedback','helpful');showToast('Thanks for your feedback!');};
    dislikeBtn.onclick=function(){dislikeBtn.classList.add('disliked');dislikeBtn.textContent='👎 Noted';likeBtn.disabled=true;track('feedback','not_helpful');showToast('Thanks - we will keep improving!');};
    shareBtn.onclick=function(){navigator.clipboard.writeText(text).then(function(){shareBtn.classList.add('copied');shareBtn.textContent='✓ Copied!';showToast('Answer copied!');setTimeout(function(){shareBtn.classList.remove('copied');shareBtn.textContent='🔗 Copy';},2000);});};
    actions.appendChild(likeBtn);actions.appendChild(dislikeBtn);actions.appendChild(shareBtn);
    wrapper.appendChild(actions);msgs.appendChild(wrapper);
    setTimeout(function(){wrapper.scrollIntoView({behavior:'smooth',block:'start'});},50);
  }else{msgs.appendChild(wrapper);sd();}
}

function showTyping(){
  var d=document.createElement('div');d.className='msg bot';d.id='typ';
  var a=document.createElement('div');a.className='av';a.textContent='🏠';
  var t=document.createElement('div');t.className='typing';
  t.innerHTML='<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
  d.appendChild(a);d.appendChild(t);msgs.appendChild(d);sd();
}
function removeTyping(){var e=document.getElementById('typ');if(e)e.remove();}

function ask(q,category){
  if(category) track('category',category);
  inp.value=q;sendMsg();
}

async function sendMsg(){
  var text=inp.value.trim();
  if(!text||busy)return;
  // Track custom typed questions
  var isCustom=true;
  var presetQ=['Does rent control apply to my Berkeley apartment?','My landlord wants to raise my rent. What are the limits in Berkeley?','I received an eviction notice in Berkeley. What should I do?','Landlord not making repairs. What are my rights in Berkeley?','What is rent control in Berkeley and does it apply to my unit?','What are my rights if my landlord tries to evict me in Berkeley?','What are my rights regarding repairs and habitability in Berkeley?','What are my rights regarding security deposits in Berkeley?'];
  for(var i=0;i<presetQ.length;i++){if(presetQ[i]===text){isCustom=false;break;}}
  if(isCustom) trackCustomQuestion(text);
  inp.value='';inp.style.height='auto';
  busy=true;btn.disabled=true;
  addMsg('user',text);
  hist.push({role:'user',content:text});
  showTyping();
  try{
    var r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:hist})});
    var data=await r.json();
    removeTyping();
    if(data.error){
      if(data.retry_after){
        addMsg('bot','The AI is temporarily busy due to high demand. Please wait about '+data.retry_after+' seconds and try again.');
      } else {
        addMsg('bot','Something went wrong. Please try again in a moment.');
      }
      hist.pop();
    }
    else{hist.push({role:'assistant',content:data.reply});addMsg('bot',data.reply);}
  }catch(e){removeTyping();addMsg('bot','Could not reach the server. Please try again.');hist.pop();}
  busy=false;btn.disabled=false;
}
</script>
</body>
</html>"""


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com; "
        "style-src 'self' 'unsafe-inline'; "
        "connect-src 'self' https://cloudflareinsights.com; "
        "img-src 'self' data:; "
        "frame-ancestors 'none';"
    )
    return response


@app.route("/")
def index():
    return Response(HTML, mimetype="text/html; charset=utf-8")


@app.route("/privacy")
def privacy():
    return Response(HTML, mimetype="text/html; charset=utf-8")


@app.route("/track", methods=["POST"])
def track():
    sheet_url = os.environ.get("TRACKING_SHEET_URL")
    if not sheet_url:
        return jsonify({"ok": False}), 200
    data = request.get_json(silent=True)
    if not data or not isinstance(data.get('type'), str) or not isinstance(data.get('value'), str):
        return jsonify({"ok": False}), 400
    # Sanitize inputs
    event_type = data['type'][:50]
    event_value = data['value'][:100]
    event_ts = str(data.get('ts', ''))[:30]
    if event_type not in ['category', 'feedback']:
        return jsonify({"ok": False}), 400
    try:
        http_requests.post(sheet_url, json={'type': event_type, 'value': event_value, 'ts': event_ts}, timeout=5)
        return jsonify({"ok": True})
    except Exception:
        return jsonify({"ok": False}), 200


@app.route("/chat", methods=["POST"])
def chat():
    # Rate limiting by IP
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        ip = ip.split(',')[0].strip()
    if is_rate_limited(ip):
        return jsonify({"error": "Too many requests. Please wait a moment.", "retry_after": 30}), 429

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "Service temporarily unavailable."}), 500

    data = request.get_json(silent=True)
    if not data or "messages" not in data:
        return jsonify({"error": "Invalid request."}), 400

    messages = data["messages"]
    if not isinstance(messages, list) or len(messages) == 0:
        return jsonify({"error": "Invalid request."}), 400

    # Limit conversation history to last 6 messages to reduce token usage
    if len(messages) > 6:
        messages = messages[-6:]

    # Validate message format
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "")
        content = msg.get("content", "")
        if role not in ["user", "assistant"] or not isinstance(content, str):
            continue
        # Limit individual message length
        content = content[:2000]
        groq_messages.append({"role": role, "content": content})

    try:
        resp = http_requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen/qwen3-32b",
                "messages": groq_messages,
                "max_tokens": 600,
                "temperature": 0.4,
                "reasoning_effort": "none"
            },
            timeout=30
        )
        result = resp.json()
        if resp.status_code == 429:
            retry_after = int(resp.headers.get('retry-after', 20))
            return jsonify({"error": "Rate limit reached.", "retry_after": retry_after}), 429
        if resp.status_code == 401:
            return jsonify({"error": "Service temporarily unavailable."}), 500
        if resp.status_code != 200:
            return jsonify({"error": "Service temporarily unavailable."}), 500
        reply = result["choices"][0]["message"]["content"].strip()
        # Remove any <think>...</think> blocks Qwen3 might output
        import re
        reply = re.sub(r'<think>.*?</think>', '', reply, flags=re.DOTALL).strip()
        return jsonify({"reply": reply})
    except Exception:
        return jsonify({"error": "Service temporarily unavailable."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
