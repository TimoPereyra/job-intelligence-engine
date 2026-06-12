import json
import time
from datetime import datetime


class Qualification:

    POSITIVE = {
        # stack fuerte (experiencia real)
        "php": 40,
        "laravel": 50,
        "codeigniter": 35,
        "wordpress": 30,
        "oracle": 35,
        "apex": 40,
        "plsql": 35,
        "pl/sql": 35,

        # stack actual/crecimiento
        "react": 25,
        "python": 20,
        "node": 15,
        "node.js": 15,

        # base de datos
        "mysql": 15,
        "sql": 10,
        "mongodb": 10,

        # frontend general
        "javascript": 15,
        "jquery": 20,        # usaste mucho en Uakika
        "html": 5,
        "css": 5,
        "tailwind": 10,
        "bootstrap": 10,

        # contexto laboral favorable
        "fullstack": 15,
        "full stack": 15,
        "backend": 10,
        "frontend": 10,
        "api": 10,
        "rest": 10,
        "remote": 10,
        "remoto": 10,
        "latam": 10,
    }

    NEGATIVE = {
        # seniority fuera de alcance
        "senior": -40, "sr.": -35, "sr ": -35,
        "staff": -60, "principal": -50,
        "lead": -50, "manager": -50, "architect": -40,

        # stacks que no manejás
        "golang": -30, "ruby": -25, "rails": -25,
        "scala": -30, ".net": -25, "c#": -25,
        "java ": -20,   # espacio para no matchear "javascript"
        "ios": -35, "android": -35, "swift": -35, "flutter": -30,
        "kotlin": -30,

        # roles que no son dev
        "devops": -20, "sre": -20,
        "machine learning": -15, "data engineer": -15,
        "salesforce": -30, "sap": -30,
        "security": -20, "support": -15,
        "qa ": -20, "tester": -20,
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

        # stack fuerte comprobado
        if "laravel" in text and "php" in text:
            score += 25
        if "oracle" in text and "apex" in text:
            score += 30
        if "laravel" in text and "mysql" in text:
            score += 15
        if "codeigniter" in text:
            score += 10

        # stack actual en crecimiento
        if "react" in text and "python" in text:
            score += 15
        if "react" in text and "php" in text:
            score += 20
        if "react" in text and "node" in text:
            score += 10

        # fullstack end-to-end (lo que hacías en Uakika)
        if ("php" in text or "laravel" in text) and ("javascript" in text or "jquery" in text):
            score += 15

        # WordPress con desarrollo real (no solo contenido)
        if "wordpress" in text and ("php" in text or "plugin" in text or "custom" in text):
            score += 20

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
            "title":            job.get("title"),
            "company":          job.get("company"),
            "location":         job.get("location"),
            "url":              job.get("url"),
            "description":      job.get("description"),
            "source":           job.get("source"),
            "posted_at":        job.get("posted_at"),
            "score":            score,
            "recommended":      score >= 50,
            "matched_positive": pos,
            "matched_negative": neg,
            "ai_summary":       "No analizado",
        }

        if result["recommended"] and self.client:
            result["ai_summary"] = self._ai(job, pos)
        else:
            result["ai_summary"] = "Filtrado por puntaje (IA desactivada)"

        self.cache[key] = result

        print(f"📄 {result['title']} → {score}")

        return result

    def qualify_jobs(self, jobs):
        res = [self.qualify(j) for j in jobs]
        return sorted(res, key=lambda x: x["score"], reverse=True)