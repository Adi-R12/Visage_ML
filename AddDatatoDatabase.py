import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://paperless-boarding-system-default-rtdb.firebaseio.com/"
})

ref = db.reference('Users')

data = {
    "134567":
        {
            "name": "Aditya",
            "Flight_No": 123456,
            "PNR": 20176790,
            "Seat_No": 7,
            "Date": 4,
            "Departure": "2022-01-20",
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "321654":
        {
            "name": "Murtaza Hassan",
            "Flight_No": 123456,
            "PNR": 20176790,
            "Seat_No": 7,
            "Date": 4,
            "Departure": "2022-01-20",
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "852741":
        {
            "name": "Emly Blunt",
            "Flight_No": 123456,
            "PNR": 20176790,
            "Seat_No": 7,
            "Date": 4,
            "Departure": "2022-01-20",
            "last_attendance_time": "2022-12-11 00:54:34"
        },
    "963852":
        {
            "name": "Elon Musk",
            "Flight_No": 123456,
            "PNR": 20176790,
            "Seat_No": 7,
            "Date": 4,
            "Departure": "2022-01-20",
            "last_attendance_time": "2022-12-11 00:54:34"
        }
}

for key, value in data.items():
    ref.child(key).set(value)
