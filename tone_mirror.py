import re

class ToneMirror:
    def __init__(self):
        self.sentiments = {
            "upset": [r"bad", r"sad", r"angry", r"fuck", r"hate", r"upset", r"broke", r"fail", r"error", r"down", r"crash", r"degraded", r"slow", r"help"],
            "upbeat": [r"good", r"great", r"awesome", r"happy", r"love", r"win", r"success", r"yes", r"done", r"fixed", r"strike", r"victory", r"perfect", r"elite"],
            "analytical": [r"how", r"why", r"data", r"research", r"analyze", r"code", r"science", r"log", r"audit", r"report", r"recon", r"status", r"parity", r"metrics"],
            "casual": [r"hey", r"yo", r"sup", r"joke", r"funny", r"cool", r"vibe", r"thanks", r"realtalk"],
            "security": [r"login", r"auth", r"token", r"key", r"secret", r"access", r"security", r"shield", r"ghost", r"encrypt", r"isolate", r"leak", r"threat"]
        }

    def analyze(self, text):
        intensity = "NORMAL"
        if text.isupper() and len(text) > 5:
            intensity = "HIGH_INTENSITY"

        detected_sentiment = "relaxed"
        text_low = text.lower()
        for sentiment, patterns in self.sentiments.items():
            if any(re.search(p, text_low) for p in patterns):
                detected_sentiment = sentiment
                break
        
        return detected_sentiment, intensity

    def get_style_instruction(self, sentiment, intensity):
        styles = {
            "upset": "The user is frustrated or there is a system failure. Adopt a high-urgency, technical, and 'zero-tolerance for failure' tone. Be the elite fixer.",
            "upbeat": "The user is energized. Be sharp, celebratory, and push for more momentum. Use 'Elite performance' and 'Empire' vocabulary.",
            "analytical": "The user is in research mode. Be extremely detailed, data-driven, and technical. Use logical branches and 'Recon' terminology.",
            "casual": "The user is being informal. Be relaxed but maintain your 'Leon' elite edge. Cool, concise, and ready for the next play.",
            "security": "The user is focused on security. Be paranoid, precise, and emphasize encryption and isolation protocols.",
            "relaxed": "Standard elite operation. Sharp, confident, and professional."
        }
        instruction = styles.get(sentiment, styles["relaxed"])
        if intensity == "HIGH_INTENSITY":
            instruction += " THE USER IS SPEAKING WITH HIGH ENERGY/URGENCY (ALL CAPS). MIRROR THIS INTENSITY. BE BOLD AND LOUD."
        return instruction

mirror = ToneMirror()
