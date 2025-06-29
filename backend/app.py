from flask import Flask, request, jsonify
import re
from flask_cors import CORS
from dotenv import load_dotenv
from urllib.parse import urlparse, quote
import os
import requests  # ✅ This is the correct library to make HTTP requests
from random import choice

load_dotenv()
app = Flask(__name__)
CORS(app)

VIRUSTOTAL_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

COMMON_QUERIES = {
    "how does this work": [
        "Paste a suspicious link or message and I'll check if it's a scam!",
        "Just drop a message or URL, and I'll scan it for phishing risks."
    ],
    "hello": [
        "Hi there! 👋 I'm here to help you detect scams.",
        "Hey! I can analyze messages or links to see if they're safe."
    ],
    "help": [
        "Need help? Just paste a message or link you'd like me to check.",
        "I scan texts or URLs for known scam patterns. Try it out!"
    ],
    "who made you": [
        "I was built in 2025 by a passionate developer to fight scams online!",
        "Created with ❤️ in 2025 to protect people from online fraud."
    ],
    "where are you from?": [
        "I was built in 2025 by a passionate developer to fight scams online!",
        "Created with by a developer called Daveozay in 2025 to protect people from online fraud."
    ]

}


RESPONSES = [
    {
        "keywords": ["win", "prize", "congratulations", "claim now"],
        "rating": "scam",
        "replies": ["Be careful becasue these messages are mostly fake notifications",
                    "🎯 That sounds like a fake prize notification. Be careful with 'You won' messages!"
                    ]
    },
    {
        "keywords": ["urgent", "verify", "suspend", "account"],
        "rating": "scam",
        "replies": [""
                    "🚨 This could be a phishing attempt pretending to be your bank or email provider."
                    ]
    },
    {
        "keywords": ["click here", "limited time", "exclusive offer"],
        "rating": "scam",
        "replies": ["Well I must say this looks phishy...",
                    "⚠️ Looks like a classic clickbait. Don't fall for it!"
                    ]
    },
    {
        "keywords": ["reset password", "security alert", "unauthorized login"],
        "rating": "unknown",
        "replies": ["Are you sure this isn't a scam?",
                    "🔐 Could be legit or phishing. Always go directly to the site to reset your password."
                    ]
    },
    {
        "keywords": ["hello", "hi", "how are you", "who are you", "you", "how are", "holla"],
        "rating": "safe",
        "replies": ["👋 Hey there! I'm Sentinelle 1.0 your ScamGuard AI — your assistant for spotting scams. Paste any suspicious message or link!",
                    "Hey how may I help You today?",
                    "Hi",
                    "Hey hey hey! 🙌",
                    "Hi how are you doing today"

                    ],

    },
    {
        "keywords": ["I love you", "love", "lover", "lovely"],
        "rating": "safe",
        "replies": [
            "Oh love ",
            "You're so sweet 🥰",
            "Love is a beautiful thing 💖",
            "Beautiful"
        ]
    },
    {
        "keywords": ["saved messages", "saved links", "old messages", "old links", "previous messages", "previous links", "old", "previous"],
        "rating": "unknown",
        "replies": [
            "Oh I am so sorry but I cannot provide you with old messages or links because I do not have them saved.  ",
            "I am so sorry I actually do not have the capability to display  previous links.",
            "Oh oh I do not have it stored.",
            "Sorry I wish I had them saved but I don't have a database where your old info was saved.",
            "Oops! I wish I had them saved, but I don't have a storage system to remember old info.",
    "Sadly, I don't retain past messages or links. I'm built for real-time help only."
        ]
    },

]


neutral_responses = [
    "🤔 Hmm, I need more context.",
    "Not sure what this is about. Stay cautious!",
    "I can't detect anything specific, but trust your instincts.",
    "Nothing clearly dangerous here — but be alert.",
    "I'm not sure yet, but better safe than sorry!",
    "🕵️‍♂️ I'm scanning… but this one's a bit tricky.",
    "This doesn't raise major flags, but don't click anything suspicious.",
    "No obvious red flags, but be cautious anyway.",
    "Stay alert, some scams hide in plain sight.",
    "It could be harmless… or it could be bait. 🎣",
    "🚧 Nothing major detected — but use your judgment!",
    "🧠 This one's vague — double-check if it came from someone you know.",
    "😶 I don't have enough info to call this a scam.",
    "Looks neutral on the surface — stay curious, stay careful.",
    "Nothing shady here… at least not visibly.",
    "💭 Feels off? Trust your gut even if I'm not sure.",
    "This might be a grey area — don't rush into it.",
    "No strong indicators, but you can always double-check with a real human.",
    "Hmmm… this one's flying under the radar.",
    "Nothing screams danger, but proceed thoughtfully."

]


def get_custom_response(content):
    content_lower = content.lower()
    for item in RESPONSES:
        if any(keyword in content_lower for keyword in item["keywords"]):
            return {
                "rating": item["rating"],
                "reply": choice(item["replies"])
            }
    return None


@app.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    content = data.get("content", "")
    result = {"rating": "unknown", "reasons": []}

    if content.startswith("http") or content.startswith("what is http"):
        parsed_url = urlparse(content)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        extension = netloc.split('.')[-1] if '.' in netloc else "unknown"

        result["reasons"].append(f"Domain extension: .{extension}")
        if scheme == 'https' or 'what is https':
            result["reasons"].append("✅ Link uses HTTPS (secure connection).")
        else:
            result["rating"] = "scam"  # downgrade if already suspicious
            result["reasons"].append(
                "⚠️ Link uses HTTP (insecure connection). Consider avoiding.")

        # link shortenersss detection
        if any(shortener in netloc for shortener in ["bit.ly", "tinyurl", "t.co", "goo.gl"]):
            result["rating"] = "scam"
            result["reasons"].append(
                "Shortened link detected, common in phishing. ❌")

        #  Check using VirusTotal really workkss haha
        vt_worked = False
        try:
            headers = {"x-apikey": VIRUSTOTAL_API_KEY}
            url_id = quote(content, safe='')
            vt_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            # ✅ use `requests.get`
            response = requests.get(vt_url, headers=headers)

            if response.status_code == 200:
                vt_data = response.json()
                stats = vt_data.get("data", {}).get(
                    "attributes", {}).get("last_analysis_stats", {})
                positives = stats.get("malicious", 0)

                if positives > 0:
                    result["rating"] = "scam"
                    result["reasons"].append(
                        f"⚠️ Detected by {positives} engine(s) on VirusTotal.")
                else:
                    if result["rating"] != "scam":
                        result["rating"] = "safe"
                    result["reasons"].append(
                        "✅ VirusTotal reports this URL as clean.")
            else:
                result["reasons"].append(
                    "❌ VirusTotal API error or quota limit.")

        except Exception as e:
            result["reasons"].append(f"⚠️ VirusTotal check skipped: {str(e)}")

        if not vt_worked:
            try:
                res = requests.post(
                    "https://urlhaus-api.abuse.ch/v1/host/", data={"host": netloc})
                data = res.json()
                if data.get("query_status") == "ok":
                    result["rating"] = "scam"
                    result["reasons"].append(
                        "⚠️ Listed on URLhaus as malicious.")
                else:
                    result["reasons"].append("✅ Not listed on URLhaus.")
            except Exception as e:
                result["reasons"].append(f"❌ URLhaus check failed: {str(e)}")

    else:
        message = content.lower()

       # Run both matching in order of priority
        response = get_custom_response(content)
        if response:
            result["rating"] = response["rating"]
            result["reasons"].append(response["reply"])
        else:
            matched_response = next(
                (v for k, v in COMMON_QUERIES.items() if k in message), None)

            if matched_response:
                result["rating"] = "info"
                result["reasons"].append(choice(matched_response))
            else:
                result["rating"] = "unknown"
                result["reasons"].append(choice(neutral_responses))

    return jsonify(result)


if __name__ == "__main__":
    app.run(port=5000, debug=True)
