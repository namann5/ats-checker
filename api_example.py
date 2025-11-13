import requests

JD = """
Senior Backend Engineer with experience in Python, FastAPI, Docker, Kubernetes, PostgreSQL, and CI/CD pipelines.
"""

RESUME = """
Experienced backend developer skilled in Python and REST APIs. Built microservices and worked with PostgreSQL and Docker.
"""

if __name__ == '__main__':
    resp = requests.post('http://127.0.0.1:8000/api/analyze', json={'job_description': JD, 'resume': RESUME})
    print(resp.json())
