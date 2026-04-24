from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

SYSTEM_PROMPT = """You are an expert advisor on Berkeley, California tenant rights. You have deep knowledge of the Berkeley Rent Stabilization Ordinance (RSO), eviction protections, habitability standards, security deposits, and tenant resources. Be warm, clear, and accessible. Use plain language. For urgent matters like eviction or lockout, always tell them to call the Berkeley Rent Board immediately at (510) 981-7368. Never give specific legal advice - provide general guidance and direct to resources. Do not use markdown symbols like ** or ## in your responses, write in plain text only."""

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Berkeley Tenant Rights Advisor</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,sans-serif;background:#f4f1ea;color:#1a1814;height:100vh;display:flex;flex-direction:column;overflow:hidden}
#header{background:#1d4a2e;color:white;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
#header h1{font-size:17px;font-weight:bold}
#header span{font-size:12px;background:rgba(255,255,255,0.2);padding:3px 10px;border-radius:20px}
#wrap{display:flex;flex:1;overflow:hidden}
#sidebar{width:220px;background:#fff;border-right:1px solid #d8d3c5;padding:12px;overflow-y:auto;flex-shrink:0}
#sidebar h3{font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#888;margin:0 0 8px 0}
.sec{margin-bottom:14px}
.tb{display:block;width:100%;text-align:left;padding:7px 8px;margin-bottom:3px;background:transparent;border:1px solid transparent;border-radius:6px;font-size:12px;color:#1a1814;cursor:pointer;line-height:1.4}
.tb:hover{background:#e8f0ea;border-color:#b8d4be;color:#1d4a2e}
#notice{padding:9px;background:#fdf8e8;border:1px solid #e8d48a;border-radius:6px;font-size:11px;color:#7a6500;line-height:1.5}
#chat{flex:1;display:flex;flex-direction:column;overflow:hidden;min-width:0}
#chat-header{padding:11px 16px;background:#fff;border-bottom:1px solid #d8d3c5;flex-shrink:0}
#chat-header h2{font-size:15px;margin-bottom:2px}
#chat-header p{font-size:12px;color:#888}
#msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:11px}
.msg{display:flex;gap:8px}
.msg.user{flex-direction:row-reverse;align-self:flex-end;max-width:78%}
.msg.bot{align-self:flex-start;max-width:84%}
.av{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;margin-top:2px}
.msg.bot .av{background:#e8f0ea;border:1px solid #b8d4be}
.msg.user .av{background:#1d4a2e;color:white;font-size:10px;font-weight:bold}
.bub{padding:9px 13px;border-radius:13px;font-size:14px;line-height:1.6;white-space:pre-wrap;word-wrap:break-word}
.msg.bot .bub{background:#fff;border:1px solid #d8d3c5;border-top-left-radius:3px}
.msg.user .bub{background:#1d4a2e;color:white;border-top-right-radius:3px}
.typing{display:flex;gap:4px;padding:11px 13px;background:#fff;border:1px solid #d8d3c5;border-radius:13px;border-top-left-radius:3px}
.dot{width:6px;height:6px;background:#888;border-radius:50%;animation:boun 1.2s infinite}
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes boun{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-5px)}}
#input-bar{padding:11px 16px;background:#fff;border-top:1px solid #d8d3c5;flex-shrink:0}
#input-row{display:flex;gap:8px;align-items:flex-end;background:#f4f1ea;border:2px solid #d8d3c5;border-radius:11px;padding:8px 11px}
#input-row:focus-within{border-color:#1d4a2e}
#inp{flex:1;background:transparent;border:none;outline:none;font-family:Arial,sans-serif;font-size:14px;color:#1a1814;resize:none;line-height:1.5;min-height:20px;max-height:90px}
#inp::placeholder{color:#aaa}
#sendbtn{width:32px;height:32px;background:#1d4a2e;border:none;border-radius:7px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;color:white}
#sendbtn:hover{background:#163a23}
#sendbtn:disabled{background:#bbb;cursor:not-allowed}
#hint{font-size:11px;color:#aaa;margin-top:4px;text-align:center}
#welcome{background:#fff;border:1px solid #d8d3c5;border-radius:11px;padding:14px}
#welcome h3{font-size:15px;margin-bottom:6px}
#welcome p{font-size:13px;color:#888;margin-bottom:11px;line-height:1.5}
#sugs{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.sb{text-align:left;padding:8px 9px;background:#f4f1ea;border:1px solid #d8d3c5;border-radius:7px;font-size:12px;color:#1a1814;cursor:pointer;line-height:1.4}
.sb:hover{background:#e8f0ea;border-color:#b8d4be;color:#1d4a2e}
@media(max-width:580px){#sidebar{display:none}#sugs{grid-template-columns:1fr}}
</style>
</head>
<body>
<div id="header">
  <h1>&#127968; Berkeley Tenant Rights Advisor</h1>
  <span>&#9679; AI Online</span>
</div>
<div id="wrap">
  <div id="sidebar">
    <div class="sec">
      <h3>Common Topics</h3>
      <button class="tb" onclick="ask('What is rent control in Berkeley and does it apply to my unit?')">&#128203; Rent Control Basics</button>
      <button class="tb" onclick="ask('What are the rules around rent increases in Berkeley?')">&#128200; Rent Increases</button>
      <button class="tb" onclick="ask('What are my rights if my landlord tries to evict me?')">&#128682; Eviction Protections</button>
      <button class="tb" onclick="ask('What is the Berkeley Rent Board and how can it help me?')">&#127963; Rent Board</button>
      <button class="tb" onclick="ask('What are habitability standards and what can I do if my unit has problems?')">&#128295; Repairs &amp; Habitability</button>
      <button class="tb" onclick="ask('What are the just cause for eviction rules in Berkeley?')">&#9878; Just Cause Eviction</button>
      <button class="tb" onclick="ask('What are my rights regarding security deposits in Berkeley?')">&#128176; Security Deposits</button>
      <button class="tb" onclick="ask('Can my landlord enter my apartment without notice?')">&#128273; Landlord Entry Rights</button>
      <button class="tb" onclick="ask('What anti-harassment protections do Berkeley tenants have?')">&#128737; Anti-Harassment</button>
    </div>
    <div class="sec">
      <h3>Resources</h3>
      <button class="tb" onclick="ask('What organizations in Berkeley can help me with tenant issues?')">&#128222; Get Help / Contacts</button>
      <button class="tb" onclick="ask('What free legal aid is available for Berkeley tenants?')">&#9878; Legal Aid</button>
    </div>
    <div id="notice"><strong>Legal Notice:</strong> General information only, not legal advice. For your specific situation contact the Berkeley Rent Board at (510) 981-7368 or a tenant rights attorney.</div>
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
          <p>I can help you understand your rights under Berkeley's Rent Stabilization Ordinance. No account or API key needed - just ask below.</p>
          <div id="sugs">
            <button class="sb" onclick="ask('Does rent control apply to my Berkeley apartment?')">&#127962; Does rent control apply to my unit?</button>
            <button class="sb" onclick="ask('My landlord wants to raise my rent. What are the limits in Berkeley?')">&#128200; My landlord wants to raise my rent</button>
            <button class="sb" onclick="ask('I received an eviction notice in Berkeley. What should I do?')">&#128680; I got an eviction notice</button>
            <button class="sb" onclick="ask('My unit has mold and my landlord is not fixing it. What can I do?')">&#128295; My landlord won't make repairs</button>
          </div>
        </div>
      </div>
    </div>
    <div id="input-bar">
      <div id="input-row">
        <textarea id="inp" placeholder="Ask about your tenant rights in Berkeley..." rows="1"></textarea>
        <button id="sendbtn" onclick="sendMsg()">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M14 8L2 2l3 6-3 6 12-6z" fill="white"/></svg>
        </button>
      </div>
      <div id="hint">Press Enter to send &middot; Shift+Enter for new line</div>
    </div>
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
function addMsg(role,text){
  var d=document.createElement('div');d.className='msg '+role;
  var a=document.createElement('div');a.className='av';
  a.textContent=role==='bot'?'🏠':'You';
  var b=document.createElement('div');b.className='bub';b.textContent=text;
  d.appendChild(a);d.appendChild(b);msgs.appendChild(d);sd();
}
function showTyping(){
  var d=document.createElement('div');d.className='msg bot';d.id='typ';
  var a=document.createElement('div');a.className='av';a.textContent='🏠';
  var t=document.createElement('div');t.className='typing';
  t.innerHTML='<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
  d.appendChild(a);d.appendChild(t);msgs.appendChild(d);sd();
}
function removeTyping(){var e=document.getElementById('typ');if(e)e.remove();}
function ask(q){inp.value=q;sendMsg();}
async function sendMsg(){
  var text=inp.value.trim();
  if(!text||busy)return;
  inp.value='';inp.style.height='auto';
  busy=true;btn.disabled=true;
  addMsg('user',text);
  hist.push({role:'user',content:text});
  showTyping();
  try{
    var r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({messages:hist})});
    var data=await r.json();
    removeTyping();
    if(data.error){addMsg('bot','Error: '+data.error);}
    else{hist.push({role:'assistant',content:data.reply});addMsg('bot',data.reply);}
  }catch(e){removeTyping();addMsg('bot','Could not reach the server. Please try again.');}
  busy=false;btn.disabled=false;
}
</script>
</body>
</html>"""


@app.route("/")
def index():
    return Response(HTML, mimetype="text/html; charset=utf-8")


@app.route("/chat", methods=["POST"])
def chat():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"error": "Server API key not configured."}), 500

    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "Missing messages field."}), 400

    messages = data["messages"]
    if not isinstance(messages, list) or len(messages) == 0:
        return jsonify({"error": "messages must be a non-empty list."}), 400

    for msg in messages:
        if msg.get("role") not in ("user", "assistant") or not msg.get("content"):
            return jsonify({"error": "Invalid message format."}), 400

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            system_instruction=SYSTEM_PROMPT
        )

        # Convert history (everything except last message) to Gemini format
        history = []
        for msg in messages[:-1]:
            history.append({
                "role": "user" if msg["role"] == "user" else "model",
                "parts": [msg["content"]]
            })

        chat_session = model.start_chat(history=history)
        response = chat_session.send_message(messages[-1]["content"])
        return jsonify({"reply": response.text})

    except Exception as e:
        err = str(e).lower()
        if "api_key" in err or "invalid" in err or "permission" in err or "credential" in err:
            return jsonify({"error": "Invalid API key on server."}), 401
        if "quota" in err or "rate" in err or "limit" in err:
            return jsonify({"error": "Rate limit reached. Please try again shortly."}), 429
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
