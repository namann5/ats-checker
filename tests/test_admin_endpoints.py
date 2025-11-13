import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_app_id_endpoint():
    r = client.get('/api/app-id')
    assert r.status_code == 200
    data = r.json()
    assert 'application_id' in data


def test_rewrite_bullets_fallback():
    # No OPENAI_API_KEY in test env, ensure fallback bullets are returned
    payload = {'role_text': 'Senior Engineer. Improved platform performance by 30%. Used Python and Docker.', 'jd': 'Senior backend role with Python and Docker.'}
    r = client.post('/api/rewrite-bullets', json=payload)
    assert r.status_code == 200
    data = r.json()
    assert 'bullets' in data
    assert isinstance(data['bullets'], list)

*** End Patch