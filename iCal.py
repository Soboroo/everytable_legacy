from icalendar import Calendar, Event
import datetime


def untilDate(date):
    return f'{datetime.datetime(int(date[:4]), int(date[5:7]), int(date[8:]) + 1).strftime("%Y%m%d")}T000000'


def display(cal):
    return cal.to_ical().decode('utf-8').replace("\r\n", "\n").replace("\;", ";").strip()


def getIcs(subjectSet):
    cal = Calendar()

    for item in subjectSet['data']:
        for single in item['time']:
            event = Event()
            event['summary'] = f'{item["name"]} ({item["internal"]})'
            event['dtstart'] = single[0]
            event['dtend'] = single[1]
            event['rrule'] = f'FREQ=WEEKLY;UNTIL={untilDate(subjectSet["info"]["term"]["end"])}'
            event['description'] = f'{item["professor"]} 교수'
            event['location'] = f'{item["place"]}'

            cal.add_component(event)

    f = open('result.ics', 'w', encoding='utf-8')
    f.write(display(cal))
    f.close()
    print('생성 완료')
