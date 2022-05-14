import pytest

def test_trip():
    testtrip = Trip('Münzstraße', '123')
    testtrip2 = Trip('Berliner Straße', '234')
    event_id = '123'
    d = {event_id: testtrip }



globals()[f"evt_{event_id}"] = Trip('Münzstraße', '123')
print(evt_123)

