class FilteringService:

    GOOD_KEYWORDS = [
        "php",
        "laravel",
        "oracle",
        "apex",
        "sql",
        "plsql",
        "react",
        "backend",
        "fullstack",
        "api"
    ]

    BAD_KEYWORDS = [
        "ios",
        "android",
        "mobile",
        "qa",
        "tester",
        "marketing",
        "sales",
        "designer",
        "security",
        "devops",
        "network",
        "data scientist",
        "machine learning"
    ]

    def filter_jobs(self, jobs):

        filtered = []

        for job in jobs:

            text = f"""
            {job.get("title", "")}
            {job.get("description", "")}
            """.lower()

            has_good = any(
                k in text
                for k in self.GOOD_KEYWORDS
            )

            has_bad = any(
                k in text
                for k in self.BAD_KEYWORDS
            )

            if has_bad and not has_good:
                continue

            filtered.append(job)

        removed = len(jobs) - len(filtered)

        print(f"\n🧹 Filtrados: {removed}")
        print(f"✅ Restantes: {len(filtered)}")

        return filtered