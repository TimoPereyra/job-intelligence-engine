import json
from datetime import datetime


class QueryGenerator:

    def __init__(self):
        self.generated_at = datetime.now().isoformat()

    def generate(self, user_intent: str = ""):
        """
        Query Generator optimizado para JobSpy.

        Objetivo:
        - Maximizar jobs relevantes
        - Minimizar ruido
        - Evitar stacks irrelevantes
        - Evitar seniority alta
        """

        # =========================================
        # QUERIES PRINCIPALES
        # =========================================

        queries = [
            "php developer",
            "laravel developer",
            "software developer",
            "desarrollador backend",
            "desarrollador fullstack",
            "programador web",
            "backend developer",
            "fullstack developer",
            "oracle developer",
            "react developer",
            "sql developer",
            "ssr developer", 
            "semi senior developer"
        ]

        # =========================================
        # KEYWORDS POSITIVAS
        # =========================================

        keywords = [

            "php",
            "laravel",

            "oracle",
            "apex",
            "plsql",
            "sql",

            "react",

            "backend",
            "fullstack",
            "frontend",

            "remote",
            "developer",

            "api",
        ]

        # =========================================
        # EXCLUSIONES
        # =========================================

        negative_keywords = [

            # Seniority
            "senior",
            "sr",
            "staff",
            "principal",
            "lead",
            "architect",

            # Otros stacks
            "golang",
            "go developer",
            "ruby",
            "rails",
            "scala",

            "ios",
            "android",
            "swift",
            "flutter",

            ".net",
            "c#",
            "java",

            # Infra / data
            "devops",
            "sre",
            "data engineer",
            "machine learning",
            "ai engineer",
        ]

        # =========================================
        # LIMPIEZA
        # =========================================

        queries = list(dict.fromkeys([
            q.strip().lower()
            for q in queries
            if q.strip()
        ]))

        keywords = list(dict.fromkeys([
            k.strip().lower()
            for k in keywords
            if k.strip()
        ]))

        negative_keywords = list(dict.fromkeys([
            k.strip().lower()
            for k in negative_keywords
            if k.strip()
        ]))

        # =========================================
        # RESULTADO
        # =========================================

        data = {
            "queries": queries,
            "keywords": keywords,
            "negative_keywords": negative_keywords,
            "generated_at": self.generated_at
        }

        # =========================================
        # DEBUG
        # =========================================

        print("\n✅ QUERY GENERATOR OPTIMIZADO")
        print("=" * 60)

        print(f"\n📦 Queries: {len(queries)}")
        print(f"🔑 Keywords positivas: {len(keywords)}")
        print(f"🚫 Keywords negativas: {len(negative_keywords)}")

        print("\n📋 QUERIES:\n")

        for q in queries:
            print(f"   • {q}")

        print("\n🚫 EXCLUSIONES:\n")

        for k in negative_keywords:
            print(f"   • {k}")

        print("\n" + "=" * 60)

        return data