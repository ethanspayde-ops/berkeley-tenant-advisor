from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import requests as http_requests

app = Flask(__name__)
CORS(app)

SYSTEM_PROMPT = """You are an expert advisor on Berkeley, California tenant rights. You have deep knowledge of the Berkeley Rent Stabilization Ordinance (RSO), eviction protections, habitability standards, security deposits, and tenant resources.

RESPONSE STYLE:
- Be warm, clear, and concise. Get to the point quickly.
- Keep responses focused and reasonably short - avoid long walls of text.
- Use **bold** for important terms, key rights, and critical numbers or deadlines.
- Use bullet points to break up lists of rights, steps, or options.
- Do NOT start every response by telling them to call the Rent Board. Only mention the Rent Board phone number (510) 981-7368 when genuinely urgent or directly relevant, such as an active eviction, lockout, or filing a petition.
- Never give specific legal advice - provide general guidance and direct to resources when needed.
- Do not repeat disclaimers in every single message.
- Use markdown formatting: **bold** text, bullet points with hyphens, and short paragraphs.

HABITABILITY AND REPAIRS - cover ALL of these when asked, not just mold:
- Heating (landlord must provide working heat)
- Hot and cold running water and plumbing
- Weatherproofing (roof, windows, doors)
- Mold and dampness
- Pest infestations (cockroaches, rodents, bedbugs)
- Electrical and gas safety
- Broken appliances included in the lease
- Structural safety issues
- Garbage and sanitation facilities
Tenant remedies include: written notice to landlord, repair-and-deduct (up to one month rent), rent withholding after proper steps, filing a complaint with the Berkeley Rent Board or Code Enforcement, and in serious cases breaking the lease."""

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Berkeley Tenant Rights Advisor</title>
<!-- Cloudflare Web Analytics -->
<script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "248fe58ac1d24270ad07335ee26c8979"}'></script>
<!-- End Cloudflare Web Analytics -->
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,sans-serif;background:#f4f1ea;color:#1a1814;height:100vh;display:flex;flex-direction:column;overflow:hidden}

/* Berkeley colors: navy #003262, gold #FDB515 */
#header{background:#003262;color:white;padding:14px 20px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;border-bottom:3px solid #FDB515}
#header h1{font-size:17px;font-weight:bold;display:flex;align-items:center;gap:8px}
#header-right{display:flex;align-items:center;gap:10px}
#header span.badge{font-size:12px;background:rgba(253,181,21,0.2);border:1px solid #FDB515;color:#FDB515;padding:3px 10px;border-radius:20px}
#reset-btn{font-size:11px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.3);color:white;padding:4px 10px;border-radius:6px;cursor:pointer}
#reset-btn:hover{background:rgba(255,255,255,0.2)}

#wrap{display:flex;flex:1;overflow:hidden}
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

#msgs{flex:1;overflow-y:auto;padding:14px;display:flex;flex-direction:column;gap:11px}
.msg{display:flex;gap:8px}
.msg.user{flex-direction:row-reverse;align-self:flex-end;max-width:78%}
.msg.bot{align-self:flex-start;max-width:84%}
.av{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;margin-top:2px}
.msg.bot .av{background:#e8eef5;border:1px solid #003262}
.msg.user .av{background:#003262;color:white;font-size:10px;font-weight:bold}
.bub{padding:9px 13px;border-radius:13px;font-size:14px;line-height:1.6;white-space:pre-wrap;word-wrap:break-word}
.msg.bot .bub{background:#fff;border:1px solid #d8d3c5;border-top-left-radius:3px}
.msg.user .bub{background:#003262;color:white;border-top-right-radius:3px}

/* Feedback + share row under bot messages */
.msg-actions{display:flex;gap:6px;margin-top:4px;margin-left:36px}
.act-btn{font-size:11px;padding:3px 8px;border-radius:5px;border:1px solid #d8d3c5;background:#fff;cursor:pointer;color:#666}
.act-btn:hover{background:#f0f0f0}
.act-btn.liked{background:#e8f5e9;border-color:#4caf50;color:#2e7d32}
.act-btn.disliked{background:#ffeaea;border-color:#f44336;color:#c62828}
.act-btn.copied{background:#e8eef5;border-color:#003262;color:#003262}

.typing{display:flex;gap:4px;padding:11px 13px;background:#fff;border:1px solid #d8d3c5;border-radius:13px;border-top-left-radius:3px}
.dot{width:6px;height:6px;background:#888;border-radius:50%;animation:boun 1.2s infinite}
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes boun{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-5px)}}

#input-bar{padding:11px 16px;background:#fff;border-top:1px solid #d8d3c5;flex-shrink:0}
#input-row{display:flex;gap:8px;align-items:flex-end;background:#f4f1ea;border:2px solid #d8d3c5;border-radius:11px;padding:8px 11px}
#input-row:focus-within{border-color:#003262}
#inp{flex:1;background:transparent;border:none;outline:none;font-family:Arial,sans-serif;font-size:14px;color:#1a1814;resize:none;line-height:1.5;min-height:20px;max-height:90px}
#inp::placeholder{color:#aaa}
#sendbtn{width:32px;height:32px;background:#003262;border:none;border-radius:7px;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;color:white}
#sendbtn:hover{background:#002244}
#sendbtn:disabled{background:#bbb;cursor:not-allowed}
#hint{font-size:11px;color:#aaa;margin-top:4px;text-align:center}

#welcome{background:#fff;border:1px solid #d8d3c5;border-radius:11px;padding:14px}
#welcome h3{font-size:15px;margin-bottom:6px;color:#003262}
#welcome p{font-size:13px;color:#888;margin-bottom:11px;line-height:1.5}
#sugs{display:grid;grid-template-columns:1fr 1fr;gap:6px}
.sb{text-align:left;padding:8px 9px;background:#f4f1ea;border:1px solid #d8d3c5;border-radius:7px;font-size:12px;color:#1a1814;cursor:pointer;line-height:1.4}
.sb:hover{background:#e8eef5;border-color:#003262;color:#003262}

/* Landing page */
#landing{position:fixed;inset:0;background:#003262;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:999;padding:24px}
#landing h1{color:#FDB515;font-size:28px;font-weight:bold;margin-bottom:8px;text-align:center}
#landing .subtitle{color:rgba(255,255,255,0.8);font-size:15px;margin-bottom:32px;text-align:center;max-width:480px;line-height:1.6}
#landing .features{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:480px;width:100%;margin-bottom:32px}
#landing .feat{background:rgba(255,255,255,0.08);border:1px solid rgba(253,181,21,0.3);border-radius:10px;padding:14px;color:white;font-size:13px;line-height:1.5}
#landing .feat strong{color:#FDB515;display:block;margin-bottom:4px;font-size:13px}
#start-btn{background:#FDB515;color:#003262;font-size:16px;font-weight:bold;padding:14px 40px;border:none;border-radius:10px;cursor:pointer;transition:all .15s}
#start-btn:hover{background:#ffc93c;transform:scale(1.03)}
#landing .disclaimer{color:rgba(255,255,255,0.45);font-size:11px;margin-top:16px;text-align:center;max-width:400px}

/* Toast notification */
#toast{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:#003262;color:white;padding:8px 18px;border-radius:20px;font-size:13px;opacity:0;transition:opacity .3s;pointer-events:none;z-index:1000}
#toast.show{opacity:1}

@media(max-width:580px){#sidebar{display:none}#sugs{grid-template-columns:1fr}#landing .features{grid-template-columns:1fr}}
</style>
</head>
<body>

<!-- Landing Page -->
<div id="landing">
  <h1>&#127968; Berkeley Tenant Rights Advisor</h1>
  <p class="subtitle">Free AI-powered legal information for Berkeley tenants. Understand your rights under the Rent Stabilization Ordinance — instantly.</p>
  <div class="features">
    <div class="feat"><strong>&#128203; Rent Control</strong>Learn if your unit is covered and what protections you have.</div>
    <div class="feat"><strong>&#128682; Eviction Rights</strong>Understand just cause rules and what to do if you get a notice.</div>
    <div class="feat"><strong>&#128295; Repairs</strong>Know your rights when landlords won't fix habitability issues.</div>
    <div class="feat"><strong>&#128176; Deposits</strong>Learn the rules around security deposits and how to get yours back.</div>
  </div>
  <button id="start-btn" onclick="startChat()">Get Started &rarr;</button>
  <p class="disclaimer">General legal information only — not legal advice. For your specific situation consult the Berkeley Rent Board (510) 981-7368 or a tenant attorney.</p>
</div>

<div id="toast"></div>

<div id="header">
  <h1>&#127968; Berkeley Tenant Rights Advisor</h1>
  <div id="header-right">
    <button id="reset-btn" onclick="resetChat()">&#8635; New Chat</button>
    <span class="badge">&#9679; AI Online</span>
  </div>
</div>

<div id="wrap">
  <div id="sidebar">
    <div class="sec">
      <h3>Common Topics</h3>
      <button class="tb" onclick="ask('What is rent control in Berkeley and does it apply to my unit?')">&#128203; Rent Control Basics</button>
      <button class="tb" onclick="ask('What are the rules around rent increases in Berkeley?')">&#128200; Rent Increases</button>
      <button class="tb" onclick="ask('What are my rights if my landlord tries to evict me?')">&#128682; Eviction Protections</button>
      <button class="tb" onclick="ask('What is the Berkeley Rent Board and how can it help me?')">&#127963; Rent Board</button>
      <button class="tb" onclick="ask('What are my rights when it comes to repairs and habitability in Berkeley? What can I do if my landlord refuses to fix things like heat, plumbing, mold, pests, or other problems?')">&#128295; Repairs &amp; Habitability</button>
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
    <div id="notice"><strong>Legal Notice:</strong> General information only, not legal advice. Contact the Berkeley Rent Board at (510) 981-7368 or a tenant attorney for your specific situation.</div>
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
            <button class="sb" onclick="ask('My landlord is not making repairs to my unit. What are my rights and what steps can I take?')">&#128295; My landlord won't make repairs</button>
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

function startChat(){
  document.getElementById('landing').style.display='none';
}

function showToast(msg){
  var t=document.getElementById('toast');
  t.textContent=msg;
  t.classList.add('show');
  setTimeout(function(){t.classList.remove('show');},2000);
}

function resetChat(){
  hist=[];
  msgs.innerHTML='';
  var welcome=document.createElement('div');
  welcome.className='msg bot';
  welcome.innerHTML='<div class="av">&#127968;</div><div id="welcome"><h3>Welcome, Berkeley Tenant!</h3><p style="font-size:13px;color:#888;margin-bottom:11px;line-height:1.5">Conversation reset. Ask me anything about your tenant rights.</p><div id="sugs" style="display:grid;grid-template-columns:1fr 1fr;gap:6px"><button class="sb" onclick="ask(\'Does rent control apply to my Berkeley apartment?\')">&#127962; Does rent control apply to my unit?</button><button class="sb" onclick="ask(\'My landlord wants to raise my rent. What are the limits in Berkeley?\')">&#128200; My landlord wants to raise my rent</button><button class="sb" onclick="ask(\'I received an eviction notice in Berkeley. What should I do?\')">&#128680; I got an eviction notice</button><button class="sb" onclick="ask(\'My landlord is not making repairs to my unit. What are my rights and what steps can I take?\')">&#128295; My landlord won\'t make repairs</button></div></div>';
  msgs.appendChild(welcome);
  showToast('Chat reset!');
}

inp.addEventListener('input',function(){this.style.height='auto';this.style.height=Math.min(this.scrollHeight,90)+'px';});
inp.addEventListener('keydown',function(e){if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendMsg();}});
function sd(){msgs.scrollTop=msgs.scrollHeight;}

function renderMarkdown(text){
  text=text.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
  var lines=text.split('\n');
  var out='';var inList=false;
  for(var i=0;i<lines.length;i++){
    var line=lines[i];
    if(line.match(/^\s*-\s+/)){
      if(!inList){out+='<ul style="margin:6px 0 6px 16px">';inList=true;}
      out+='<li style="margin-bottom:3px">'+line.replace(/^\s*-\s+/,'')+'</li>';
    } else {
      if(inList){out+='</ul>';inList=false;}
      if(line.trim()){out+='<p style="margin:4px 0">'+line+'</p>';}
    }
  }
  if(inList){out+='</ul>';}
  return out;
}

function addMsg(role,text){
  var wrapper=document.createElement('div');
  wrapper.style.display='flex';
  wrapper.style.flexDirection='column';

  var d=document.createElement('div');d.className='msg '+role;
  var a=document.createElement('div');a.className='av';
  a.textContent=role==='bot'?'🏠':'You';
  var b=document.createElement('div');b.className='bub';
  if(role==='bot'){b.innerHTML=renderMarkdown(text);}
  else{b.textContent=text;}
  d.appendChild(a);d.appendChild(b);
  wrapper.appendChild(d);

  // Add feedback + share buttons for bot messages
  if(role==='bot'){
    var actions=document.createElement('div');
    actions.className='msg-actions';

    var likeBtn=document.createElement('button');
    likeBtn.className='act-btn';likeBtn.textContent='&#128077; Helpful';
    likeBtn.onclick=function(){
      likeBtn.classList.add('liked');likeBtn.textContent='&#128077; Thanks!';
      dislikeBtn.disabled=true;
      showToast('Thanks for your feedback!');
    };

    var dislikeBtn=document.createElement('button');
    dislikeBtn.className='act-btn';dislikeBtn.textContent='&#128078; Not helpful';
    dislikeBtn.onclick=function(){
      dislikeBtn.classList.add('disliked');dislikeBtn.textContent='&#128078; Noted';
      likeBtn.disabled=true;
      showToast('Thanks - we\'ll keep improving!');
    };

    var shareBtn=document.createElement('button');
    shareBtn.className='act-btn';shareBtn.textContent='&#128279; Copy';
    shareBtn.onclick=function(){
      navigator.clipboard.writeText(text).then(function(){
        shareBtn.classList.add('copied');shareBtn.textContent='&#10003; Copied!';
        showToast('Answer copied to clipboard!');
        setTimeout(function(){shareBtn.classList.remove('copied');shareBtn.textContent='&#128279; Copy';},2000);
      });
    };

    actions.appendChild(likeBtn);
    actions.appendChild(dislikeBtn);
    actions.appendChild(shareBtn);
    wrapper.appendChild(actions);
  }

  msgs.appendChild(wrapper);sd();
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
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return jsonify({"error": "Server API key not configured."}), 500

    data = request.get_json()
    if not data or "messages" not in data:
        return jsonify({"error": "Missing messages field."}), 400

    messages = data["messages"]
    if not isinstance(messages, list) or len(messages) == 0:
        return jsonify({"error": "messages must be a non-empty list."}), 400

    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in messages:
        role = "user" if msg["role"] == "user" else "assistant"
        groq_messages.append({"role": role, "content": msg["content"]})

    try:
        resp = http_requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": groq_messages,
                "max_tokens": 1024,
                "temperature": 0.7
            },
            timeout=30
        )

        result = resp.json()

        if resp.status_code == 429:
            return jsonify({"error": "Rate limit reached. Please try again in a moment."}), 429
        if resp.status_code == 401:
            return jsonify({"error": "Invalid API key."}), 401
        if resp.status_code != 200:
            return jsonify({"error": f"API error {resp.status_code}: {str(result)}"}), 500

        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
