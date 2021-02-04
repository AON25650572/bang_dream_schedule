import datetime
import requests
from bs4 import BeautifulSoup

def niketa(num):
    """
    入力（int）を2ケタにする
    出力はstr
    """
    if 0 <= num < 10 and type(num) == int:
        return "0" + str(num)
    elif num < 100:
        return str(num)
    else:
        return None
    
def schedule_information_extraction(url):
    """
    今月の予定情報（bs4.element.Tag）が入ったlistを返す
    """
    # Requestsを利用してWebページを取得する
    r = requests.get(url)

    # BeautifulSoupを利用してWebページを解析する
    soup = BeautifulSoup(r.text, "html.parser")

    # calendarCellでイベント情報をごっそりとってくる
    calendarCell = soup.find_all(class_="calendarCell")

    # calendarCell notCurrentで先月来月の情報をとってくる
    calendarCell_notCurrent = soup.find_all(class_="calendarCell notCurrent")

    # 先月来月の情報はひとまずいらないので削除
    remake = [info for info in calendarCell if info not in calendarCell_notCurrent]

    return remake

def schedule_extraction(informations):
    """
    今月の予定情報（bs4.element.Tag）が入ったlistをぶち込むと
    
    {2（'date'）: {'date': 2,
        'yobi': '土曜日',
        'yotei': [{'text': '🎍《22:00》朝までバンドリ！TV 2021', 'url_link': 'https://bang-dream.com/news/1095'},
                {'text': '📻【第14回】Afterglowの夕焼けSTUDIO＋', 'url_link': 'https://hibiki-radio.jp/description/Afterglowplus/detail'}]},
    }
    
    みたいな感じの形式で返してくれる
    """
    calendar_yotei = {}

    for info in informations:
        # 日付と曜日情報
        day = info.find(class_="calendarCellDate").get_text()
        date = int(day[:-3])
        yobi = day[-3:]

        # 予定情報
        yotei = []
        for link in info.find(class_="calendarCellContent").find_all("a"):
            text,url_link = link.get_text(),link.get("href")
            yotei.append({"text":text, "url_link":url_link})

        calendar_yotei[date] = {"date":date, "yobi":yobi, "yotei":yotei}

    return calendar_yotei

# Googleカレンダーにインポートする用のファイルを作成
def make_import_file(calendar_yotei,year,month,private="False"):
    header = "Subject,Start Date,Description,Private\n"

    with open("bang_dream_schedule_"+str(year)+niketa(month)+".csv","w",encoding="utf8") as f:
        f.write(header)

        for info in calendar_yotei.values():
            # 予定が無かったらcontinue
            if len(info["yotei"]) == 0:
                continue

            # 日付合成（DD/MM/YYYY）
            Start_Date = niketa(info["date"]) + "/" + niketa(month) + "/" + str(year)

            for subject in info["yotei"]:
                f.write(subject["text"] + "," + Start_Date + "," + subject["url_link"]+"," + private + "\n") # 限定公開にすると共有したときに内容が見れない

if __name__ == '__main__':
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    url = "https://bang-dream.com/news/schedule?ym="

    url += str(year) + niketa(month)
    
    informations = schedule_information_extraction(url)
    calendar_yotei = schedule_extraction(informations)
    make_import_file(calendar_yotei,year,month)