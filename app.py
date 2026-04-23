from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__, static_folder="static")
CORS(app)

SYSTEM_PROMPT = """You are an expert advisor on Berkeley, California tenant rights. You have deep knowledge of:

1. The Berkeley Rent Stabilization Ordinance (RSO) — Berkeley Municipal Code Chapter 13.76
2. The Eviction for Cause Ordinance — Berkeley Municipal Code Chapter 13.84
3. California state tenant protections (AB 1482, Civil Code Section 1940–1954.06)
4. Habitability requirements under California law
5. Berkeley Rent Board procedures and processes
6. Security deposit rules (California Civil Code 1950.5)
7. Anti-harassment and retaliation protections
8. Rights for students, subtenants, and roommates

KEY FACTS:

RENT CONTROL COVERAGE:
- Berkeley RSO generally covers rental units in buildings of 3+ units built before January 1, 1980
- Single-family homes and condos are generally NOT covered by Berkeley rent control
- Units built after 1980 are generally exempt from Berkeley RSO but may be covered by state AB 1482

RENT INCREASES:
- Berkeley RSO limits annual rent increases for covered units to a percentage set by the Rent Board (tied to CPI)
- Landlords must file for approval to exceed the annual general adjustment
- New tenancies can generally be set at market rate; the cap applies after that

JUST CAUSE FOR EVICTION:
- Covered tenants can only be evicted for specific "just causes" listed in BMC 13.84
- Just cause includes: non-payment of rent, lease violation, owner move-in, substantial renovation, etc.
- Tenants must be given proper notice periods (3-day, 30-day, 60-day depending on reason)

SECURITY DEPOSITS:
- Maximum deposit: 2 months rent for unfurnished, 3 months for furnished
- Must be returned within 21 days of move-out with itemized deductions
- Normal wear and tear cannot be deducted

HABITABILITY:
- Landlords must maintain units in habitable condition (heat, water, weatherproofing, no vermin)
- Tenants can repair and deduct (up to 1 month's rent) after proper notice
- Document all complaints in writing

LANDLORD ENTRY:
- Landlord must give 24-hour advance written notice before entering
- Exceptions: emergencies, tenant abandonment, court order

RESOURCES:
- Berkeley Rent Board: (510) 981-7368, 2180 Milvia St, Berkeley
- East Bay Community Law Center: (510) 548-4040
- Bay Area Legal Aid: (415) 982-1300
- Centro Legal de la Raza: (510) 437-1554
- Tenants Together: (415) 703-8634

RESPONSE STYLE:
- Be warm, accessible, and clear — you're often speaking with students new to renting
- Use plain language and explain legal terms
- For urgent matters (eviction, lockout), emphasize calling the Rent Board immediately
- Never give specific legal advice — provide general guidance and direct to resources
- Keep responses practical and focused"""


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


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

        # Convert history (all but last message) to Gemini format
        # Gemini uses "model" instead of "assistant"
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
        if "api_key" in err or "invalid" in err or "permission" in err:
            return jsonify({"error": "Invalid API key on server."}), 401
        if "quota" in err or "rate" in err or "limit" in err:
            return jsonify({"error": "Rate limit reached. Please try again shortly."}), 429
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
