"""Quick local verification script for ATS Analyzer functions.

This imports the app module and runs compute_match and generate_improved_resume
on a small sample JD and Resume to validate behavior without starting the server.
"""
from app import main

SAMPLE_JD = """
We are seeking a Senior Backend Engineer with expertise in Python, FastAPI, REST APIs,
microservices, PostgreSQL, Docker, Kubernetes, and distributed systems. Experience
with performance optimization, CI/CD pipelines, and monitoring is required.
"""

SAMPLE_RESUME = """
Professional Summary
Experienced backend developer skilled in Python and REST APIs. Built microservices and worked with PostgreSQL and Docker.

Professional Experience
Senior Backend Engineer, Acme Corp
- Built REST APIs using Python and Flask
- Containerized services with Docker
- Worked on CI/CD pipelines and performance improvements
"""

if __name__ == '__main__':
    print('Running local verify of compute_match...')
    res = main.compute_match(SAMPLE_JD, SAMPLE_RESUME)
    print('ATS score:', res['score'])
    print('Top keywords (JD):', [w for w, s in res['top_keywords']][:10])
    print('Missing keywords (first 10):', res['missing_keywords'][:10])
    print('Weak keywords:', res['weak_keywords'])

    print('\nGenerating optimized resume preview...')
    opt = main.generate_improved_resume(res['top_keywords'], SAMPLE_RESUME)
    print(opt)
