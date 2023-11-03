from .scrapper import BirthRegistration
import datetime


# Example
students = [
    {
        'brn': '2010xxxxxxxxxxxxx',
        'dob': datetime.date(year=2010,month=1,day=1)
    },
]

for student in students:
    obj = BirthRegistration(student['brn'],student['dob'])
    obj.verify()
    print(obj.data)