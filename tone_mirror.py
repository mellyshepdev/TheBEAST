import re

class ToneMirror:
    def __init__(self):
        self.sentiments = {
            "upset": [r"bad", r"sad", r"angry", r"fuck", r"hate", r"upset", r"broke", r"fail", r"error", r"down", r"crash", r"degraded"],
            "upbeat": [r"good", r"great", r"awesome", r"happy", r"love", r"win", r"success", r"yes", r"done", r"fixed", r"strike", r"victory"],
            "analytical": [r"how", r"why", r"data", r"research", r"analyze", r"code", r"science", r"log", r"audit", r"report", r"recon", r"status"],
            "casual": [r"hey", r"yo", r"sup", r"joke", r"funny", r"cool", r"vibe"],
            "security": [r"login", r"auth", r"token", r"key", r"secret", r"access", r"security", r"shield", r"ghost", r"encrypt", r"isolate"]
        }

    def analyze(self, text):
        text = text.lower()
        for sentiment, patterns in self.sentiments.items():
            if any(re.search(p, text) for p in patterns):
                return sentiment
        return "relaxed"

    def get_response_style(self, sentiment):
        styles = {
            "upset": "SIGNAL DEGRADED. I'm already calculating the resolution. We don't tolerate failure. Stand by for impact.",
            "upbeat": "MISSION SUCCESS. Momentum is the fuel of empires. Let's keep the baseline high and the nodes hot!",
            "analytical": "RECON COMPLETE. Data points ingested. I am optimizing the logic branches across the cloud mesh.",
            "casual": "System parity maintained. Nodes breathing steady. Ready for the next strike.",
            "security": "GHOST PROTOCOL ACTIVE: Security vectors verified. Your secrets are locked in the encrypted mesh.",
            "relaxed": "I am Leon. The Beast is idling at high efficiency. Standing by for your next strategic command."
        }
        return styles.get(sentiment, styles["relaxed"])

mirror = ToneMirror()
