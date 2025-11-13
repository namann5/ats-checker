import os
import sys
import re

# Ensure project root is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import main


def test_compute_match_basic():
    jd = '''Senior Backend Engineer experienced with Python, FastAPI, Docker, Kubernetes, PostgreSQL, CI/CD, monitoring.'''
    resume = '''Experienced backend developer. Built REST APIs using Python and FastAPI. Containerized applications with Docker and deployed to Kubernetes. Worked with PostgreSQL and CI/CD pipelines.'''
    res = main.compute_match(jd, resume)
    assert isinstance(res, dict)
    assert 'score' in res
    assert 0 <= res['score'] <= 100
    # Top keywords should be present
    assert isinstance(res['top_keywords'], list)
    # Missing keywords should be a list
    assert isinstance(res['missing_keywords'], list)
    # At least some overlap expected
    assert len(res['present_keywords']) >= 1


def test_generate_bullets_detects_metrics():
    jd_top = [('python', 0.9), ('docker', 0.8), ('kubernetes', 0.7), ('postgresql', 0.6)]
    role_text = '''Senior Engineer — improved platform performance, reduced latency by 30% and saved $120k in operational costs. Implemented Docker-based CI/CD and automated deployments.'''
    bullets = main.generate_bullets_for_role(role_text, jd_top)
    assert isinstance(bullets, list)
    assert len(bullets) >= 1
    # At least one bullet should include a detected metric (percent or $)
    has_metric = any(re.search(r"\d{1,3}%|\$\s?\d+", b) for b in bullets)
    assert has_metric, f"Expected a metric in bullets but got: {bullets}"
