import json
import os


class StorageManager:

    def __init__(self, db_path="jobs_db.json"):
        self.db_path = os.path.abspath(db_path)
        self._ensure_db()

    # =========================
    # INIT
    # =========================

    def _ensure_db(self):
        if not os.path.exists(self.db_path):
            self._write([])

    # =========================
    # IO
    # =========================

    def _read(self):
        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    def _write(self, data):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # =========================
    # CORE
    # =========================

    def load_jobs(self):
        return self._read()

    def save_jobs(self, jobs):
        self._write(jobs)

    # =========================
    # INSERT + DEDUP
    # =========================

    def mark_as_new(self, job):
        jobs = self._read()

        url = job.get("url")
        if any(j.get("url") == url for j in jobs):
            return False

        job["status"] = "new"
        jobs.append(job)
        self._write(jobs)
        return True

    # =========================
    # FILTER
    # =========================

    def get_jobs_by_status(self, status):
        return [
            j for j in self._read()
            if j.get("status") == status
        ]

    # =========================
    # UPDATE SINGLE JOB
    # =========================

    def update_job(self, job_url, data):
        jobs = self._read()

        for job in jobs:
            if job.get("url") == job_url:
                job.update(data)
                break

        self._write(jobs)

    # =========================
    # RANKING
    # =========================

    def save_ranked_jobs(self, jobs):
        self._write(
            sorted(jobs, key=lambda x: x.get("score", 0), reverse=True)
        )