from models.job import Job
class SearchService:
    def __init__(self, adapter, dispatcher, webhook_url):
        self.adapter = adapter
        self.dispatcher = dispatcher
        self.webhook_url = webhook_url

    def run(self, queries):
        for query in queries:
            jobs = self.adapter.search(query)

            for job_data in jobs:
                job = Job(**job_data)
                self.dispatcher(job, self.webhook_url)