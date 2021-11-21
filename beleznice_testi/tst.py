import requests
from bs4 import BeautifulSoup
import os
import re
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib

def no_CMC_urls(SEZNAM_COINOV): #vzame seznam coinov, vrne seznam coin url-jov ki niso na CMC
    NO_CMC = []
    d = len(SEZNAM_COINOV)
    i=0
    while i < d:
        name = SEZNAM_COINOV[i]
        url = "https://coinmarketcap.com/currencies/" + name + "/"
        request_response = requests.head(url)
        time.sleep(0.5)
        code = request_response.status_code
        if code == 200:
            print(f"{name} is listed on CMC   ({i})")
        elif code == 404:
            print(f"{name} is not listed on CMC   ({i})")
            link =  "https://www.coingecko.com/en/coins/" + name + "/"
            NO_CMC.append(link)
        i+=1
    return NO_CMC

#print(time.asctime().split(" ")[1] + " " + time.asctime().split(" ")[2])

def price(STEVILO_STRANI): 
    vzorec = (
    r'<a class="d-lg-none font-bold" href="/en/coins/(.+?)">'
    r'((.|\n)*?)'
    r'<td class="trade p-0 col-market pl-2 text-center">'
    r'(.|\n)*?'
    r'</td>'
    )
    for stran in range(STEVILO_STRANI):
        with open(f'test{stran+1} copy.html', 'r', encoding="utf-8") as f:
            vsebina = f.read()
        for zadetek in re.finditer(vzorec, vsebina):
            vsi_podatki = zadetek[0].split("\n")
            print(vsi_podatki[8].split('"')[3])
            print("=" * 100)


seznam = ['sol-fox', 'shaman-king-inu', 'good-fire', 'samusky-token', 'ethzilla', 'hughug-coin', 'unbanked', 'aave-interest-bearing-ampl']
print(no_CMC_urls(seznam))



def create_html_files(STEVILO_STRANI): #prekopira html strani iz coingeckona
    for stran in range(1, STEVILO_STRANI + 1):
        url = f"https://www.coingecko.com/en/coins/recently_added?page={stran}"
        odziv = requests.get(url)
        html = odziv.text
        soup = BeautifulSoup(html, features="html.parser")
        with open(f'test{stran}.html', 'w', encoding="utf-8") as f:
            print(soup, file=f)

def extract_name_time_price_url(STEVILO_STRANI): 
    #Sprejme število scrapanih html strani
    #Odstrani tokene ko niso na BSC pa tste ko so na CMC.
    #Vrne seznam seznamov ostalih tokenov: [[ime tokena, čas listinga na gecko, url],...]
    date = time.asctime().split(" ")[1] + " " + time.asctime().split(" ")[2]
    local_time = time.asctime()
    COINS = []
    vzorec = (
    r'<a class="d-lg-none font-bold" href="/en/coins/(.+?)">'
    r'((.|\n)*?)'
    r'<td class="trade p-0 col-market pl-2 text-center">'
    r'(.|\n)*?'
    r'</td>'
    )
    for stran in range(STEVILO_STRANI):
        with open(f'test{stran+1}.html', 'r', encoding="utf-8") as f:
            vsebina = f.read()
    
        matches =re.finditer(vzorec, vsebina)
        matches20 = [next(matches).group(0) for _ in range(2)]

        for zadetek in matches20:
            zadetek = zadetek.split("\n")
            cena = zadetek[8].split('"')[3]
            chain = zadetek[11].split('"')[3] #na kermo blockchaino je token
            ime = zadetek[0].split("/")[-1][:-2]
            cmc_url = "https://coinmarketcap.com/currencies/" + ime + "/"
            cas = zadetek[-2]

        
            print(cena)
            print(chain)
            print(ime)
            print(cmc_url) 
            print(cas)



#create_html_files(1)
#extract_name_time_price_url(1)


def email_alert(subject, body, to):

    user = "vasja.voncina123@gmail.com"
    password = "dyphwqvtshlbunmf"


    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = to
    
    html = f'<html><body><p>Brt, buraz moj, nove linke mam za tbe:<br>{body}</p></body></html>'
    part2 = MIMEText(html, 'html')
    msg.attach(part2)
    with open("gg.jpg", 'rb') as f:
        img_data = f.read()
    image = MIMEImage(img_data, name=os.path.basename("gg.jpg"))
    msg.attach(image)
    # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
    server = smtplib.SMTP_SSL('smtp.gmail.com')
    # uncomment if interested in the actual smtp conversation
    # server.set_debuglevel(1)
    # do the smtp auth; sends ehlo if it hasn't been sent already
    server.login(user, password)
    server.sendmail(user, to, msg.as_string())
    print("Emails sent.")
    server.quit()

#email_alert("tryout", "", "peter.peternik123@gmail.com")
