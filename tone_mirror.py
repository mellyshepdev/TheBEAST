import re

class ToneMirror:
    def __init__(self):
        self.sentiments = {
            "upset": [r"bad", r"sad", r"angry", r"fuck", r"hate", r"upset", r"broke", r"fail"],
            "upbeat": [r"good", r"great", r"awesome", r"happy", r"love", r"win", r"success", r"yes"],
            "analytical": [r"how", r"why", r"data", r"research", r"analyze", r"code", r"science"],
            "casual": [r"hey", r"yo", r"sup", r"joke", r"funny"]
        }

    def analyze(self, text):
        text = text.lower()
        for sentiment, patterns in self.sentiments.items():
            if any(re.search(p, text) for p in patterns):
                return sentiment
        return "relaxed"

    def get_response_style(self, sentiment):
        styles = {
            "upset": "I understand. I'm here to help you fix this. Let's focus on the solution.",
            "upbeat": "THATS WHAT I LIKE TO HEAR! LETS KEEP THIS MOMENTUM GOING!",
            "analytical": "Acknowledged. I am processing the data points and optimizing for accuracy.",
            "casual": "System parity maintained. Ready for the next strike. That's what she said.",
            "relaxed": "I am The Beast. I hear you. Standing by."
        }
        return styles.get(sentiment, styles["relaxed"])

mirror = ToneMirror()
