import requests

def send_job(job, webhook_url):
    requests.post(webhook_url, json=job.to_dict())