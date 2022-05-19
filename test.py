import pytest
import pickle

def test_trip():
    testtrip = Trip('Münzstraße', '123')
    testtrip2 = Trip('Berliner Straße', '234')
    event_id = '123'
    d = {event_id: testtrip }


with open('leftlinks.pickle', 'rb') as fp:
    test = pickle.load(fp)

print("hello")