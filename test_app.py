from fastapi.testclient import TestClient
import json

from main import app

client = TestClient(app)

#README: only test 1 case at a time, doing all tests causes issues with the async methods and event loops


def test_filter_trips_empty():
    # TEST: checking response when nothing passed
    response = client.post(url="/trips/filter", json={
        'location': None,
        'start_date': None,
        'end_date': None
    })
    print(len(json.loads(response.json()['body'])['trips']))

    assert response.status_code == 200

def test_filter_trips_location():
    # TEST: checking response when only location passed
    response = client.post(url="/trips/filter", json={
        'location': {
            'code': 'AU',
            'name': 'Australia'
        },
        'start_date': None,
        'end_date': None
    })
    print(len(json.loads(response.json()['body'])['trips']))

    assert response.status_code == 200

def test_filter_trips_joinedtrips():
    # TEST: getting trips that the user has joined
    response = client.post(url="/trips/filter", json={
        'user_email': 1,
    })
    print(len(json.loads(response.json()['body'])['trips']))

    assert response.status_code == 200