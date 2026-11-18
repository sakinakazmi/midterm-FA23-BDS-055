import json
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

import app as api
import train

CONFIG = json.loads(Path('config.json').read_text())


def test_dataset_has_required_columns_and_rows():
    df = pd.read_csv('dataset/train.csv')
    assert len(df) >= 100
    assert set(CONFIG['features'] + ['label']).issubset(df.columns)
    assert df['label'].nunique() == 2


def test_model_is_accurate_enough():
    df = pd.read_csv('dataset/train.csv')
    _, accuracy = train.fit_reference(df, CONFIG)
    assert accuracy > 0.6


def test_metrics_endpoint():
    train.main()
    client = TestClient(api.app)
    body = client.get('/metrics').json()
    for key in ('student_id', 'accuracy', 'training_rows', 'model_version', 'git_sha'):
        assert key in body
    assert body['student_id'] == CONFIG['student_id']


def test_predict_endpoint():
    client = TestClient(api.app)
    record = {f: 0.5 for f in CONFIG['features']}
    r = client.post('/predict', json={'records': [record]})
    assert r.status_code == 200
    assert len(r.json()['predictions']) == 1
