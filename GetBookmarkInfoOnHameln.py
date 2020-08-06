import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv

def post_ifttt(json):
    # json: {value1: " content "}
    url = (
        "https://maker.ifttt.com/trigger/"
        + "isUpdated"
        + "/with/key/"
        + "ikH_VxOPXE8lXUBPT7tXkoT5QgjEkkiz5r0Xsx9T4Jr"
    )
    requests.post(url, json)


def extract(info, condition, li):
    for item in info:
        if condition in str(item):
            a = ""
            is_a = 0
            if condition!="href":
                for s in str(item):
                    if s=="<" and is_a==1:
                        is_a = 0
                        li.append(a)
                        #print(a)
                        break
                    if is_a==1:
                        if condition=="最新":
                            if "0" <= s and s <= "9":
                                a+=s
                        else:
                            a += s
                    if s==">" and is_a==0:
                        is_a = 1
            else:
                if "mode=user" in str(item):
                    continue
                for s in str(item):
                    if s=="\"" and is_a==1:
                        is_a = 0
                        li.append(a)
                        break
                    if is_a==1:
                        a += s
                    if s=="\"" and is_a==0:
                        is_a = 1

##############################################################
#                           Log in                           #
##############################################################
# id, pass
print("input your ID/e-mail address: ")
ID = input()
print("input your password: ")
PASS = input()

session = requests.session()

url_login = "https://syosetu.org/?mode=login"
response = session.get(url_login)

login_info = {
    "id":ID,
    "pass":PASS,
    "mode":"login_entry_end"
}

res = session.post(url_login, data=login_info)
res.raise_for_status() # for error

print("--------------------------------------------------------")
###############################################################
#                        Print User Name                      #
###############################################################

soup_myage = BeautifulSoup(res.text, "html.parser")

account_href = soup_myage.select_one(".spotlight li a").attrs["href"]
url_account = urljoin(url_login, account_href)

res_account = session.get(url_account)
res_account.raise_for_status()

soup_account = BeautifulSoup(res_account.text, "html.parser")
user_name = str((soup_account.select(".section3 h3"))[0])[4:-5].split("／")[0]

print("Hello "+ user_name + "!")
print("--------------------------------------------------------")
###############################################################
#                        Page Transition                      #
###############################################################
a_list = soup_myage.select(".section.pickup a")
favo_a = ""
for _ in a_list:
    if("お気に入り一覧へ" in _):
        favo_a = _
        break

url_favo = urljoin(url_login, favo_a.attrs["href"])

res_favo = session.get(url_favo)
res_favo.raise_for_status()
#print(res_favo.text)

# bookmark = []
soup_favo = BeautifulSoup(res_favo.text, "html.parser")
bookmark_titles = soup_favo.select(".section3 h3 a")
bookmark_latest = soup_favo.select(".section3 p a")
titles = []
latest_no = []
ncode = []

extract(bookmark_titles, "novel", titles)
extract(bookmark_latest, "最新", latest_no)
extract(bookmark_titles, "href", ncode)
###############################################################
#                     Start Page Transition                   #
###############################################################
number_of_bookmarks_h2 = soup_favo.select_one(".heading h2")
number_of_bookmarks = ""
for s in str(number_of_bookmarks_h2)[4:-5]:
    if s>="0" and s<='9':
        number_of_bookmarks += s
number_of_bookmarks = int(number_of_bookmarks)
number_of_favo_pages = number_of_bookmarks // 10 + 1

for i in range(2,number_of_favo_pages+1):
    url_favo = "https://syosetu.org/?mode=favo&word=&gensaku=&type=&page=" + str(i)
    res_favo = session.get(url_favo)
    res_favo.raise_for_status()
    soup_favo = BeautifulSoup(res_favo.text, "html.parser")
    bookmark_titles = soup_favo.select(".section3 h3 a")
    bookmark_latest = soup_favo.select(".section3 p a")
    extract(bookmark_titles, "novel", titles)
    extract(bookmark_latest, "最新", latest_no)
    extract(bookmark_titles, "href", ncode)

###############################################################
#                        Get Latest Data                      #
###############################################################
bookmark_info = []
for i in range(len(titles)):
    bookmark_info.append([titles[i], latest_no[i], ncode[i]])

###############################################################
#                       Get Previous Data                     #
###############################################################
read_file = "hameln.csv"
with open(read_file, encoding="utf-8") as f:
    reader = csv.reader(f)
    data = [row for row in reader]

###############################################################
#              Check Whether Novels are Updated               #
###############################################################
"""
previous data: data
latest data: bookmark_info
"""
for prev in data:
    for latest in bookmark_info:
        if prev[0] == latest[0]:
            # check
            if prev[1] != latest[1]:
                print(str(latest[0]) + "が更新されました。\n" + latest[2])
                json = {"value1" : str(latest[0]) +"が更新されました。\n" + latest[2]}
                post_ifttt(json)

###############################################################
#                    Write Latest Information                 #
###############################################################
output = "hameln.csv"
with open(output, mode='w', newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for i in range(len(bookmark_info)):
        writer.writerow([bookmark_info[i][0], bookmark_info[i][1], bookmark_info[i][2]])
        #writer.writerow([titles[i], latest_no[i], ncode[i]])
print("--------------------------------------------------------")