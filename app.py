from flask import Flask,render_template,request # Import Flask to allow us to create our app
from bs4 import BeautifulSoup
import requests
import smtplib
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask_apscheduler import APScheduler


app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)


def connect():
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('GOOGLE_APPLICATION_CREDENTIALS', scope)
    client = gspread.authorize(creds)
    sheet = client.open('Books').sheet1
    return sheet


def getInfo():
    sheet = connect()
    data = sheet.get_all_records()
    return data


def deleteRow(idx):
    sheet = connect()
    sheet.delete_rows(idx+2)


def checkAvailability(url,mailId,idx):
    print("checking availability")
    print(url)
    print(mailId)
    print(idx)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    table  = soup.table.tbody
    availability  = table.find_all("span",class_="item-status")
   
    status = False

    for i in availability:
        
        if(str(i.text).strip().lower() == "available"):
            status = True
           
            break

        
    print(status)
    if(status == True):
        conn = smtplib.SMTP('smtp.gmail.com', 587) # smtp address and port
        conn.ehlo() # call this to start the connection
        conn.starttls() # starts tls encryption. When we send our password it will be encrypted.
        conn.login('orionteam5.tech@gmail.com', 'MAIL_APPKEY')
        conn.sendmail('orionteam5.tech@gmail.com', mailId, 'Subject: Alert!\n\nAttention!\n\nBook is Now available.\n\nRegards,\nOrion Team 5')
        conn.quit()
        deleteRow(idx)
        print('Sent notificaton e-mails for the following recipients:\n')
    else:
        print("Book is not available")


def isValidUrl(url):
    if(url.find("http://10.21.25.60/cgi-bin/koha/opac-detail.pl?") == -1):
        return False
    else:
        return True

# @scheduler.task('interval', id='runForAll', seconds=5)
def runForAll():
    data = getInfo()
    for idx,i in enumerate(data):
        checkAvailability(i['URL'],i['Email'],idx)
        break


@app.route("/",methods =["GET", "POST"])
def home():
    if request.method == "POST":
        url = request.form.get("url")
        mailId = request.form.get("email")
        if(isValidUrl(url)):
            sheet = connect()
            sheet.insert_row([url,mailId],2)
            return "Subscribed Succesfully! Dont Worry our Server will Trigger a mail when the book is available Thanks for using our service"
        return "Enter a valid URL"
    return "Hello World"
   
@app.route("/about")
def about():
    runForAll()
    return "waiting for 5 seconds"



if __name__ == "__main__":
    # scheduler.start()
    app.run(debug=True)
   

   
