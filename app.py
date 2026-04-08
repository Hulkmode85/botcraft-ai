import os
from flask import Flask, request, render_template_string
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

FORM_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BotCraft AI - Chatbot Builder</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0;min-height:100vh}
.container{max-width:800px;margin:0 auto;padding:40px 20px}
h1{font-size:2rem;background:linear-gradient(135deg,#00d4ff,#7b2dff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}
p.sub{color:#888;margin-bottom:30px}
form{background:#151515;border:1px solid #222;border-radius:12px;padding:30px}
label{display:block;margin-bottom:6px;color:#aaa;font-size:.9rem}
input,textarea,select{width:100%;padding:12px;background:#0a0a0a;border:1px solid #333;border-radius:8px;color:#fff;font-size:1rem;margin-bottom:20px}
textarea{height:120px;resize:vertical}
button{width:100%;padding:14px;background:linear-gradient(135deg,#00d4ff,#7b2dff);border:none;border-radius:8px;color:#fff;font-size:1.1rem;cursor:pointer;font-weight:600}
button:hover{opacity:.9}
.loading{display:none;text-align:center;padding:20px;color:#00d4ff}
</style>
</head>
<body>
<div class="container">
<h1>BotCraft AI</h1>
<p class="sub">Generate a complete customer support chatbot configuration in seconds</p>
<form method="POST" action="/generate" onsubmit="document.getElementById('load').style.display='block'">
<label>Business Name</label>
<input type="text" name="business_name" placeholder="e.g. Sunrise Dental Clinic" required>
<label>Business Description</label>
<textarea name="description" placeholder="Describe your business, services, hours, location..." required></textarea>
<label>FAQ List (one per line)</label>
<textarea name="faqs" placeholder="What are your hours?&#10;Do you accept insurance?&#10;How do I book an appointment?" required></textarea>
<label>Chatbot Tone</label>
<select name="tone">
<option value="friendly and professional">Friendly & Professional</option>
<option value="warm and casual">Warm & Casual</option>
<option value="formal and authoritative">Formal & Authoritative</option>
<option value="enthusiastic and helpful">Enthusiastic & Helpful</option>
</select>
<button type="submit">Generate Chatbot Config</button>
</form>
<div id="load" class="loading">Building your chatbot... 20-40 seconds...</div>
</div>
</body>
</html>
"""

RESULT_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Your Chatbot - BotCraft AI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0a0a0a;color:#e0e0e0;min-height:100vh}
.container{max-width:900px;margin:0 auto;padding:40px 20px}
h1{font-size:1.8rem;background:linear-gradient(135deg,#00d4ff,#7b2dff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:20px}
.section{background:#151515;border:1px solid #222;border-radius:12px;padding:20px;margin-bottom:20px}
.section h3{color:#00d4ff;margin-bottom:10px}
.content{line-height:1.8;white-space:pre-wrap}
.copy-btn{display:inline-block;margin:20px 10px 20px 0;padding:12px 24px;background:linear-gradient(135deg,#00d4ff,#7b2dff);border:none;border-radius:8px;color:#fff;cursor:pointer;font-size:1rem;font-weight:600}
.copy-btn:hover{opacity:.9}
a{color:#00d4ff;text-decoration:none}
.demo-widget{background:#1a1a2e;border:1px solid #333;border-radius:12px;padding:20px;margin:20px 0}
.demo-widget .chat-msg{padding:8px 14px;margin:6px 0;border-radius:10px;max-width:80%}
.demo-widget .bot{background:#222;color:#e0e0e0}
.demo-widget .user{background:#7b2dff;color:#fff;margin-left:auto;text-align:right}
.demo-input{display:flex;gap:10px;margin-top:15px}
.demo-input input{flex:1;padding:10px;background:#0a0a0a;border:1px solid #333;border-radius:8px;color:#fff}
.demo-input button{padding:10px 20px;background:#7b2dff;border:none;border-radius:8px;color:#fff;cursor:pointer}
</style>
</head>
<body>
<div class="container">
<h1>Your Chatbot Configuration</h1>
<button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('config').innerText);this.textContent='Copied!'">Copy Full Config</button>
<button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('sysprompt').innerText);this.textContent='Copied!'">Copy System Prompt</button>

<div class="section">
<h3>System Prompt</h3>
<div class="content" id="sysprompt">{{ system_prompt }}</div>
</div>
<div class="section">
<h3>Response Templates</h3>
<div class="content">{{ templates }}</div>
</div>
<div class="section">
<h3>Escalation Rules</h3>
<div class="content">{{ escalation }}</div>
</div>
<div class="section" id="config" style="display:none">{{ full_config }}</div>

<div class="demo-widget">
<h3 style="color:#00d4ff;margin-bottom:15px">Live Preview</h3>
<div id="chat-area">
<div class="chat-msg bot">{{ greeting }}</div>
</div>
<div class="demo-input">
<input type="text" id="user-msg" placeholder="Type a message to test..." onkeypress="if(event.key==='Enter')testChat()">
<button onclick="testChat()">Send</button>
</div>
</div>
<br><a href="/">&larr; Build Another Chatbot</a>
</div>
<script>
const sysPrompt = document.getElementById('sysprompt').innerText;
async function testChat() {
    const input = document.getElementById('user-msg');
    const msg = input.value.trim();
    if (!msg) return;
    const area = document.getElementById('chat-area');
    area.innerHTML += '<div class="chat-msg user">' + msg + '</div>';
    input.value = '';
    area.innerHTML += '<div class="chat-msg bot" id="typing">Typing...</div>';
    try {
        const resp = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({message:msg, system_prompt:sysPrompt})});
        const data = await resp.json();
        document.getElementById('typing').innerText = data.reply;
        document.getElementById('typing').removeAttribute('id');
    } catch(e) {
        document.getElementById('typing').innerText = 'Error - please try again';
        document.getElementById('typing').removeAttribute('id');
    }
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return FORM_PAGE

@app.route("/generate", methods=["POST"])
def generate():
    business_name = request.form.get("business_name", "")
    description = request.form.get("description", "")
    faqs = request.form.get("faqs", "")
    tone = request.form.get("tone", "friendly and professional")

    prompt = f"""Create a complete customer support chatbot configuration for this business:

Business Name: {business_name}
Description: {description}
FAQs: {faqs}
Desired Tone: {tone}

Generate the following sections, each clearly labeled:

SYSTEM_PROMPT:
Write a detailed system prompt for the chatbot. Include the business name, personality, tone guidelines, what it can/cannot do, and how to handle unknown questions.

RESPONSE_TEMPLATES:
Create 8-10 response templates for common scenarios (greeting, FAQ answers, appointment booking, complaint handling, after-hours, etc.)

ESCALATION_RULES:
Define 5-7 rules for when the bot should escalate to a human (angry customer, complex issues, billing disputes, etc.) with specific trigger phrases.

GREETING:
Write a single welcome message the bot would use (1-2 sentences only)."""

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    text = msg.content[0].text
    system_prompt = ""
    templates = ""
    escalation = ""
    greeting = f"Hi! Welcome to {business_name}. How can I help you today?"

    if "SYSTEM_PROMPT:" in text:
        parts = text.split("SYSTEM_PROMPT:", 1)[1]
        if "RESPONSE_TEMPLATES:" in parts:
            system_prompt, parts = parts.split("RESPONSE_TEMPLATES:", 1)
            system_prompt = system_prompt.strip()
            if "ESCALATION_RULES:" in parts:
                templates, parts = parts.split("ESCALATION_RULES:", 1)
                templates = templates.strip()
                if "GREETING:" in parts:
                    escalation, greeting_text = parts.split("GREETING:", 1)
                    escalation = escalation.strip()
                    greeting = greeting_text.strip()
                else:
                    escalation = parts.strip()
            else:
                templates = parts.strip()
    else:
        system_prompt = text

    full_config = f"SYSTEM PROMPT:\n{system_prompt}\n\nRESPONSE TEMPLATES:\n{templates}\n\nESCALATION RULES:\n{escalation}"

    return render_template_string(RESULT_PAGE,
        system_prompt=system_prompt, templates=templates,
        escalation=escalation, greeting=greeting, full_config=full_config)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_msg = data.get("message", "")
    sys_prompt = data.get("system_prompt", "You are a helpful customer support chatbot.")

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=sys_prompt,
        messages=[{"role": "user", "content": user_msg}]
    )
    return {"reply": msg.content[0].text}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
