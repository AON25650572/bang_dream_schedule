# bang_dream_schedule

バンドリの公式が発表するカレンダーをGoogleカレンダーがインポートできる形で吐いてやる

## 0. 下処理的な話

カレンダーのURLは「https\://bang-dream.com/news/schedule?ym=**YYYYMM**」

例えば、https://bang-dream.com/news/schedule?ym=202102 みたいな感じ

よって実行時には入力として年と月の情報がいる。めんどくさい運用をしない場合は「\_\_name\_\_ == '\_\_main\_\_'」で現在の時間情報をぶち込む仕組みにしておく

あとは、1ケタの整数をぶち込んだら2ケタの整数の文字列になって帰ってくる関数とかを用意してあげる


```python
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
```


```python
import datetime

if __name__ == '__main__':
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    url = "https://bang-dream.com/news/schedule?ym="

    url += str(year) + niketa(month)
    
    # 後の処理
```

## 1. beautifulsoupなるもの

pythonのスクレイピングの世界にはbeautifulsoupなるものが存在して、楽に情報を抜き出すことができるらしい。知らんけど。

ここら辺のQiitaを参考にした。<br>
https://qiita.com/itkr/items/513318a9b5b92bd56185


```python
# requestsとbeautifulsoup4のインストール
!pip install requests
!pip install beautifulsoup4
```

    Requirement already satisfied: requests in /home/naoaki/anaconda3/lib/python3.8/site-packages (2.24.0)
    Requirement already satisfied: urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1 in /home/naoaki/anaconda3/lib/python3.8/site-packages (from requests) (1.25.11)
    Requirement already satisfied: certifi>=2017.4.17 in /home/naoaki/anaconda3/lib/python3.8/site-packages (from requests) (2020.6.20)
    Requirement already satisfied: chardet<4,>=3.0.2 in /home/naoaki/anaconda3/lib/python3.8/site-packages (from requests) (3.0.4)
    Requirement already satisfied: idna<3,>=2.5 in /home/naoaki/anaconda3/lib/python3.8/site-packages (from requests) (2.10)
    Requirement already satisfied: beautifulsoup4 in /home/naoaki/anaconda3/lib/python3.8/site-packages (4.9.3)
    Requirement already satisfied: soupsieve>1.2; python_version >= "3.0" in /home/naoaki/anaconda3/lib/python3.8/site-packages (from beautifulsoup4) (2.0.1)



```python
import requests
from bs4 import BeautifulSoup
```

あとは、よしなに


```python
def schedule_information_extraction(url=url):
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
```


```python
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
```

これを良い感じにGoogleカレンダーの入力形式にぶち込む

https://support.google.com/a/users/answer/37118?hl=ja&co=GENIE.Platform%3DDesktop#zippy=%2Ccsv-%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%81%AE%E4%BD%9C%E6%88%90%E3%81%A8%E7%B7%A8%E9%9B%86

- **`Subject`**
  予定の名前（必須）。
  例: **`期末試験`**
- **`Start Date`**
  予定の開始日（必須）。
  例: **`05/30/2020`**
- **`Start Time`**
  予定の開始時刻。
  例: **`10:00 AM`**
- **`End Date`**
  予定の終了日。
  例: `05/30/2020`
- **`End Time`**
  予定の終了時刻。
  例: **`1:00 PM`**
- **`All Day Event`**
  終日の予定であるかどうかを指定します。終日の予定の場合は **`True`**、そうでない場合は **`False`** と入力します。
  例: **`False`**
- **`Description`**
  予定の説明やメモ。
  例: `**選択式問題 50 問と論文 2,000 字** `
- **`Location`**
  予定の場所。
  例: **`"614 教室"`**
- **`Private`**
  予定を限定公開にするかどうかを指定します。予定が限定公開の場合は **`True`**、そうでない場合は **`False`** と入力します。
  例: **`True`**

今回は**`Subject`**と**`Start Date`**と**`Description`**と**`Private`**を使用


```python
# Googleカレンダーにインポートする用のファイルを作成
def make_import_file(calendar_yotei,year=year,month=month,private="False"):
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
```

これで直下フォルダに「bang_dream_schedule_YYYYMM.csv」ができているはず

Googleカレンダーにぶち込む方法はググって
