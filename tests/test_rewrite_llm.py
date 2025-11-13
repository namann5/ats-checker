import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_rewrite_bullets_requires_role():
    r = client.post('/api/rewrite-bullets', json={})
    assert r.status_code == 200
    data = r.json()
    assert 'error' in data

*** End Patch