import datetime
import xml.etree.ElementTree as Et

from os import path
from requests import Session
import sys
from selenium import webdriver


def icsTime(subjectTime, time, startDate):
    start = datetime.datetime(int(startDate[:4]), int(startDate[5:7]), int(startDate[8:]))
    icsDateFront = (start + datetime.timedelta(days=subjectTime - start.weekday())).strftime('%Y%m%d')
    icsDateRear = f'{"0" if time // 12 < 10 else ""}{str(time // 12)}{"30" if time % 12 != 0 else "00"}00'
    return f'{icsDateFront}T{icsDateRear}'


class everyTable:
    __s = Session()

    def __init__(self, userid, passwd):
        agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 ' \
                'Safari/537.36 '

        headers = {'User-Agent': agent}

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument('User-Agent=' + agent)

        if getattr(sys, 'frozen', False):
            chromedriver_path = path.join(sys._MEIPASS, "chromedriver.exe")
            driver = webdriver.Chrome(chromedriver_path, options=options)
        else:
            driver = webdriver.Chrome(options=options)

        driver.implicitly_wait(1)

        print("애브리타임 접속중...")

        driver.get('https://everytime.kr/login')
        driver.find_element_by_name('userid').send_keys(userid)
        driver.find_element_by_name('password').send_keys(passwd)
        driver.find_element_by_xpath('//*[@class="submit"]/input').click()
        driver.implicitly_wait(1)

        self.__s.headers.update(headers)

        for cookie in driver.get_cookies():
            c = {cookie['name']: cookie['value']}
            self.__s.cookies.update(c)

        driver.quit()

    def getTerm(self, year, semester):
        response = self.__s.get('https://api.everytime.kr/find/timetable/subject/semester/list')
        root = Et.fromstring(response.text)

        for term in root.findall('semester'):
            if term.attrib['year'] == str(year) and term.attrib['semester'] == str(semester):
                return {'start': term.attrib["start_date"], 'end': term.attrib["end_date"]}

    def getTable(self, year, semester):
        response = self.__s.get(
            f'https://api.everytime.kr/find/timetable/table/list/semester?year={year}&semester={semester}')
        root = Et.fromstring(response.text)
        table_id = root.find('table').attrib['id']

        response = self.__s.get(f'https://api.everytime.kr/find/timetable/table?id={table_id}')
        root = Et.fromstring(response.text)
        return root.find('table')

    def subjectSet(self, year, semester):
        subset = []
        root = self.getTable(year, semester)

        for table in root.findall('subject'):
            sub = {}
            time = []
            sub['name'] = table.find('name').attrib['value']
            sub['internal'] = table.find('internal').attrib['value']
            sub['professor'] = table.find('professor').attrib['value']
            sub['place'] = table.find('place').attrib['value']

            for t in table.find('time').findall('data'):
                time.append([icsTime(int(t.attrib['day']), int(t.attrib['starttime']), self.getTerm(year, semester)['start']), icsTime(int(t.attrib['day']), int(t.attrib['endtime']), self.getTerm(year, semester)['start']), t.attrib['day']])

            sub['time'] = time
            subset.append(sub)

        return {'info': {'name': root.attrib['name'], 'year': year, 'semester': semester, 'term': self.getTerm(year, semester)}, 'data': subset}

    def __del__(self):
        self.__s.close()
