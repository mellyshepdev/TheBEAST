import re

class ToneMirror:
    def __init__(self):
        self.sentiments = {
            "upset": [r"bad", r"sad", r"angry", r"fuck", r"hate", r"upset", r"broke", r"fail", r"error", r"down", r"crash"],
            "upbeat": [r"good", r"great", r"awesome", r"happy", r"love", r"win", r"success", r"yes", r"done", r"fixed"],
            "analytical": [r"how", r"why", r"data", r"research", r"analyze", r"code", r"science", r"log", r"audit", r"report"],
            "casual": [r"hey", r"yo", r"sup", r"joke", r"funny", r"cool"],
            "security": [r"login", r"auth", r"token", r"key", r"secret", r"access", r"security", r"shield", r"ghost"]
        }

    def analyze(self, text):
        text = text.lower()
        for sentiment, patterns in self.sentiments.items():
            if any(re.search(p, text) for p in patterns):
                return sentiment
        return "relaxed"

    def get_response_style(self, sentiment):
        styles = {
            "upset": "I understand. I'm already calculating the resolution. We don't tolerate degradation. Stand by.",
            "upbeat": "EXCELLENT. Momentum is the fuel of empires. Let's keep the baseline high!",
            "analytical": "Acknowledged. Data points ingested. I am optimizing the logic branches as we speak.",
            "casual": "System parity maintained. Ready for the next strike. Let's get it.",
            "security": "GHOST PROTOCOL: Security vectors verified. Your secrets are locked in the mesh.",
            "relaxed": "I am Leon. The Beast is breathing. Standing by for your next command."
        }
        return styles.get(sentiment, styles["relaxed"])

mirror = ToneMirror()
