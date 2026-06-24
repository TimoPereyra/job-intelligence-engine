import json
import time


class Qualification:

    POSITIVE = {
        # Backend principal
        "php": 50,
        "laravel": 60,
        "symfony": 40,
        "codeigniter": 35,
        "wordpress": 25,

        # Oracle stack
        "oracle": 35,
        "apex": 40,
        "plsql": 35,
        "pl/sql": 35,

        # Frontend
        "javascript": 15,
        "jquery": 20,
        "react": 25,
        "vue": 20,
        "vuejs": 20,
        "typescript": 15,

        # Otros lenguajes relacionados
        "python": 20,
        "node": 15,
        "node.js": 15,

        # Bases de datos
        "mysql": 20,
        "postgresql": 15,
        "postgres": 15,
        "sql": 10,
        "mongodb": 10,

        # Infraestructura
        "docker": 15,
        "aws": 15,
        "git": 10,

        # Frontend base
        "html": 5,
        "css": 5,
        "tailwind": 10,
        "bootstrap": 10,

        # Contexto favorable
        "fullstack": 20,
        "full stack": 20,
        "backend": 15,
        "frontend": 10,
        "api": 10,
        "rest": 10,
        "microservices": 10,
        "remote": 10,
        "remoto": 10,
        "latam": 10,
    }

    NEGATIVE = {
        # Seniority
        "senior": -15,
        "sr.": -15,
        "sr ": -15,
        "staff": -30,
        "principal": -25,
        "lead": -20,
        "manager": -30,
        "architect": -25,

        # Tecnologías alejadas
        "golang": -15,
        "ruby": -10,
        "rails": -10,
        "scala": -15,
        ".net": -10,
        "c#": -10,
        "java ": -10,

        # Mobile
        "ios": -20,
        "android": -20,
        "swift": -20,
        "flutter": -15,
        "kotlin": -10,

        # Otros perfiles
        "devops": -10,
        "sre": -10,
        "machine learning": -10,
        "data engineer": -10,
        "salesforce": -20,
        "sap": -20,
        "security": -10,
        "support": -10,
        "qa ": -15,
        "tester": -15,
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
        return (
            f"{job.get('title', '')} "
            f"{job.get('description', '')} "
            f"{job.get('company', '')}"
        ).lower()

    def _score(self, job):
        text = self._text(job)

        score = 0
        pos = []
        neg = []

        for keyword, value in self.POSITIVE.items():
            if keyword in text:
                score += value
                pos.append(keyword)

        for keyword, value in self.NEGATIVE.items():
            if keyword in text:
                score += value
                neg.append(keyword)

        # -------------------------
        # Bonus por combinaciones
        # -------------------------

        if "php" in text and "laravel" in text:
            score += 30

        if "laravel" in text and "mysql" in text:
            score += 15

        if "php" in text and "mysql" in text:
            score += 10

        if "oracle" in text and "apex" in text:
            score += 30

        if "codeigniter" in text:
            score += 10

        if ("php" in text or "laravel" in text) and (
            "javascript" in text or
            "jquery" in text or
            "react" in text or
            "vue" in text
        ):
            score += 25

        if "react" in text and "php" in text:
            score += 20

        if "react" in text and "node" in text:
            score += 10

        if ("remote" in text or "remoto" in text) and "latam" in text:
            score += 15

        if (
            "wordpress" in text and
            (
                "php" in text or
                "plugin" in text or
                "custom" in text
            )
        ):
            score += 20

        # -------------------------
        # Piso mínimo para PHP/Laravel
        # -------------------------

        if score < 20 and ("php" in text or "laravel" in text):
            score = 20

        return score, pos, neg

    def _ai(self, job, pos):
        if not self.client:
            return "IA desactivada"

        try:
            self._wait()

            prompt = f"""
Trabajo: {job.get('title')}
Descripción: {job.get('description', '')[:500]}
Skills detectadas: {', '.join(pos)}

Devuelve únicamente este JSON:

{{
    "summary": "máximo 20 palabras"
}}
"""

            response = self.client.models.generate_content(
                model="models/gemini-2.5-flash-lite",
                contents=prompt
            )

            text = (
                response.text
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            data = json.loads(text)

            return data.get("summary", "Sin resumen")

        except Exception:
            return "Error IA"

    def qualify(self, job):
        key = job.get("url", job.get("title"))

        if key in self.cache:
            return self.cache[key]

        score, pos, neg = self._score(job)

        result = {
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "url": job.get("url"),
            "description": job.get("description"),
            "source": job.get("source"),
            "posted_at": job.get("posted_at"),

            "score": score,
            "recommended": score >= 20,

            "tier": (
                "excellent" if score >= 80 else
                "good" if score >= 40 else
                "possible" if score >= 20 else
                "discard"
            ),

            "matched_positive": pos,
            "matched_negative": neg,
            "ai_summary": "No analizado"
        }

        if result["recommended"] and self.client:
            result["ai_summary"] = self._ai(job, pos)
        else:
            result["ai_summary"] = "Filtrado por puntaje"

        self.cache[key] = result

        print(
            f"📄 {result['title']} → "
            f"{score} ({result['tier']})"
        )

        return result

    def qualify_jobs(self, jobs):
        results = [self.qualify(job) for job in jobs]

        return sorted(
            results,
            key=lambda x: x["score"],
            reverse=True
        )