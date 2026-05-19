import json
import time
from datetime import datetime


class Qualification:

    POSITIVE = {
        "php": 30, "laravel": 50, "oracle": 35, "apex": 45,
        "plsql": 35, "sql": 20, "react": 20,
        "fullstack": 15, "backend": 10, "api": 10,
        "mysql": 10, "remote": 5, "latam": 5
    }

    NEGATIVE = {
        "senior": -40, "sr": -35, "staff": -60, "principal": -50,
        "lead": -50, "manager": -50,
        "golang": -25, "ruby": -20, "python": -10,
        "node": -10, "typescript": -10, ".net": -20, "java": -10,
        "ios": -30, "android": -30, "mobile": -20,
        "security": -20, "support": -10
    }

    def __init__(self, client=None):
        self.client = client
        self.cache = {}
        self.last_request = 0
        self.min_delay = 1

    def _wait(self):
        now = time.time()
        diff = now - self.last_request
        if diff < self.min_delay:
            time.sleep(self.min_delay - diff)
        self.last_request = time.time()

    def _text(self, job):
        return f"{job.get('title','')} {job.get('description','')} {job.get('company','')}".lower()

    def _score(self, job):
        text = self._text(job)

        score = 0
        pos, neg = [], []

        for k, v in self.POSITIVE.items():
            if k in text:
                score += v
                pos.append(k)

        for k, v in self.NEGATIVE.items():
            if k in text:
                score += v
                neg.append(k)

        # boosts simples
        if "laravel" in text and "php" in text:
            score += 20
        if "oracle" in text and "apex" in text:
            score += 25
        if "react" in text and "php" in text:
            score += 15

        return score, pos, neg

    def _ai(self, job, pos):
        if not self.client:
            return "IA off"

        try:
            self._wait()

            prompt = f"""
Trabajo: {job.get('title')}
Desc: {job.get('description','')[:400]}
Skills: {pos}

Devuelve JSON:
{{"summary":"max 20 palabras"}}
"""

            r = self.client.models.generate_content(
                model="models/gemini-2.5-flash-lite",
                contents=prompt
            )

            data = json.loads(r.text.replace("```json","").replace("```",""))
            return data.get("summary", "sin resumen")

        except:
            return "error IA"

    def qualify(self, job):

        key = job.get("url", job.get("title"))

        if key in self.cache:
            return self.cache[key]

        score, pos, neg = self._score(job)

        result = {
            "title": job.get("title"),
            "company": job.get("company"),
            "url": job.get("url"),
            "score": score,
            "recommended": score >= 50,
            "matched_positive": pos,
            "matched_negative": neg,
            "ai_summary": "No analizado"
        }

        if result["recommended"] and self.client:
            result["ai_summary"] = self._ai(job, pos)

        self.cache[key] = result

        print(f"📄 {result['title']} → {score}")

        return result

    def qualify_jobs(self, jobs):
        res = [self.qualify(j) for j in jobs]
        return sorted(res, key=lambda x: x["score"], reverse=True)