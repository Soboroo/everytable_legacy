import everytable as nt
import iCal
import os

userid = input('아이디: ')
passwd = input('비밀번호: ')
year = input('연도: ')
semester = input('학기: ')

eTable = nt.everyTable(userid, passwd)
root = eTable.getTable(year, semester)

print(f'{year}년 {semester}학기')
print(f'기간: {eTable.getTerm(year, semester)["start"]}부터 {eTable.getTerm(year, semester)["end"]}')

subject = eTable.subjectSet(year, semester)

for item in subject['data']:
    print('=' * 30)
    print(f'{item["name"]} ({item["internal"]})')
    print(f'{item["professor"]} 교수')
    print(f'{item["place"]}에서')

    for t in item['time']:
        print(f'{t}')

iCal.getIcs(subject)
os.system('pause')
