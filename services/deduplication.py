class DeduplicationService:

    def deduplicate(self, jobs):

        seen = set()
        unique = []

        for job in jobs:

            title = str(
                job.get("title", "")
            ).strip().lower()

            company = str(
                job.get("company", "")
            ).strip().lower()

            key = f"{title}_{company}"

            if key in seen:
                continue

            seen.add(key)
            unique.append(job)

        removed = len(jobs) - len(unique)

        print(f"\n🧹 Duplicados eliminados: {removed}")
        print(f"✅ Jobs únicos: {len(unique)}")

        return unique