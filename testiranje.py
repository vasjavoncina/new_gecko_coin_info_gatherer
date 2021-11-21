import requests
from bs4 import BeautifulSoup
import os
import re
import time
from selenium import webdriver
from model import Coins
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
################################################################################################################
# pomožne funkcije
################################################################################################################


def krepko(niz):
    return f'\033[01m{niz}\033[0m'
def modro(niz):
    return f'\033[1;94m{niz}\033[0m'
def rdece(niz):
    return f'\033[1;91m{niz}\033[0m'
def zeleno(niz):
    return f'\033[0;32m{niz}\033[0m'
def rumeno(niz):
    return f'\033[0;33m{niz}\033[0m'
def lightcyan(niz):
    return f'\033[0;96m{niz}\033[0m'
def pink(niz):
    return f'\033[0;95m{niz}\033[0m'
def lightgreen(niz):
    return f'\033[0;92m{niz}\033[0m'


def create_html_files(STEVILO_STRANI): #prekopira html strani iz coingeckona
    for stran in range(1, STEVILO_STRANI + 1):
        url = f"https://www.coingecko.com/en/coins/recently_added?page={stran}"
        odziv = requests.get(url)
        html = odziv.text
        soup = BeautifulSoup(html, features="html.parser")
        with open(f'test{stran}.html', 'w', encoding="utf-8") as f:
            print(soup, file=f)


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
    # Send the message via gmail's regular server, over SSL - passwords are being sent, afterall
    server = smtplib.SMTP_SSL('smtp.gmail.com')
    # uncomment if interested in the actual smtp conversation
    # server.set_debuglevel(1)
    # do the smtp auth; sends ehlo if it hasn't been sent already
    server.login(user, password)
    server.sendmail(user, to, msg.as_string())
    print(krepko(modro("Emails sent.")))
    server.quit()

def pretvori_cas(cas, local_time):
    minutes = cas.split(' ')[0]
    clock = local_time.split(' ')[-2].split(":")
    if int(minutes) <= int(clock[1]):
        clock[1] = str(int(clock[1]) - int(minutes))
    else:
        if clock[0] == "00":
            clock[0] = "23"
            clock[1] = str(int(clock[1]) + 60 - int(minutes))
        else:
            clock[0] = str(int(clock[0]) - 1)
            if len(clock[0]) == 0:
                clock[0] = "00"
            elif len(clock[0]) == 1:
                clock[0] = "0" + clock[0]
            clock[1] = str(int(clock[1]) + 60 - int(minutes))
    clock[2] = ''
    clock = ":".join(clock)[:-1]
    return clock


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

        matches = re.finditer(vzorec, vsebina)
        matches20 = [next(matches).group(0) for _ in range(20)] #samo 20 na prvi strani jih pregledam

        for zadetek in matches20:
            zadetek = zadetek.split("\n")

            cena = zadetek[8].split('"')[3]
            chain = zadetek[11].split('"')[3] #na kermo blockchaino je token
            ime = zadetek[0].split("/")[-1][:-2]
            cmc_url = f"https://coinmarketcap.com/currencies/{ime}/"
            cas = zadetek[-2]
            gecko_link = f"https://www.coingecko.com/en/coins/{ime}/"

            result = re.search('.+? minutes', cas)
            if result:
                cas = pretvori_cas(cas, local_time) #pretvori v čas ko je biv listan
                cas += " " + date
            else:
                cas = date
            
            if ime not in shramba.coins_in_names: #dodaj coine, ki niso že v podatkovni bazi
                if chain == 'Binance Smart Chain': #znebi se tokenov ko niso na binance smart chaino
                    request_response = requests.head(cmc_url)
                    time.sleep(0.5)
                    code = request_response.status_code
                    if code == 404: #znebi se tokenov ko so ž na coinmarketcap
                            COINS.append([ime, cas, gecko_link, cena])
    return COINS


def add_bscscan_link(COIN_LIST): #doda listi coinov bscscan url
    i=1
    for COIN in COIN_LIST:
        url = COIN[2]
        odziv = requests.get(url)
        html = odziv.text
        vzorec='href="https://bscscan.com/token/(.*?)"'
        for zadetek in re.finditer(vzorec, html):
            bsc = zadetek[0][6:-1]
            COIN.append(bsc)
            print(pink("bsc url added"))
            break
        i+=1
    return(COIN_LIST)


def add_h_and_t(COIN_LIST): #doda listi coinov stevilo holderjev in transferjev
    for COIN in COIN_LIST:
        bsc_url = COIN[4]
        PATH = 'C:\Program Files (x86)\chromedriver.exe'
        opt = webdriver.ChromeOptions()
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(executable_path=PATH, options=opt)
        driver.get(bsc_url)
        transfers = driver.find_element_by_id("totaltxns")
        holders = driver.find_element_by_class_name("mr-3")
        number1 = transfers.get_attribute("innerHTML").strip()
        number2 = holders.get_attribute("innerHTML").split(' ')[0].strip()
        COIN.append(number1)
        COIN.append(number2)
        driver.close()  
    return(COIN_LIST)


def check_if_cmc_listed(coin):
    url = "https://coinmarketcap.com/currencies/" + coin.name + "/"
    request_response = requests.head(url)
    time.sleep(0.5)
    code = request_response.status_code
    if code == 200:
        print(zeleno(krepko(f"{coin.name} is now listed on CMC")))
        return True
    elif code == 404:
        print(lightgreen(f"{coin.name} is not yet listed on CMC"))
        return False


def add_h_and_t_to_existing_coin(coin, time): #doda listi coinov stevilo holderjev in transferjev
        PATH = 'C:\Program Files (x86)\chromedriver.exe'
        opt = webdriver.ChromeOptions()
        opt.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(executable_path=PATH, options=opt)
        driver.get(coin.bsc_url)
        transfers = driver.find_element_by_id("totaltxns")
        holders = driver.find_element_by_class_name("mr-3")
        tran = transfers.get_attribute("innerHTML").strip()
        hold = holders.get_attribute("innerHTML").split(' ')[0].strip()

        gecko_url = f"https://www.coingecko.com/en/coins/{coin.name}/" 
        vzorec = r'data-target="price.price">(.*)?</span></span>'
        odziv = requests.get(gecko_url)
        html = odziv.text
        for zadetek in re.finditer(vzorec, html):
           cena = zadetek[0].split(">")[1].split("<")[0]
           break
        coin.times[time] = {"holders": hold , "transfers": tran, "price": cena} 
        print(rumeno("transfers and holders checked"))
        driver.close()


def remove_html_page(STEVILO_STRANI):
    os.remove(f"test{STEVILO_STRANI}.html")
    

################################################################################################################
################################################################################################################


def dodaj_coin(seznam): #doda nov coin
    name = seznam[0] 
    gecko_listed = seznam[1] 
    bsc_url= seznam[4]
    times= {seznam[1]:{"holders": seznam[6], "transfers": seznam[5], "price": seznam[3]}}
    shramba.add_coin(name, gecko_listed, bsc_url, times)


def POBERI_COINE_IZ_COINGECKO_IN_SHRANI():
    create_html_files(1)
    print(krepko(modro("extracting the coins from html...")))
    COIN_LIST = extract_name_time_price_url(1)
    add_bscscan_link(COIN_LIST)
    LIST = add_h_and_t(COIN_LIST)

    stevilo_prej = len(shramba.coins)
    for seznam in LIST:
        dodaj_coin(seznam)
    stevilo_po = len(shramba.coins)

    if stevilo_po - stevilo_prej == 0:
        print(krepko(rdece("There is no new coins!")))
    elif stevilo_po - stevilo_prej == 1:
        print(krepko(modro("1 new coin added!")))
    else:
        stevilo = stevilo_po - stevilo_prej
        print(krepko(modro(f"{stevilo} new coins added!")))
    

    shramba.shrani_stanje(DATA)
    remove_html_page(1)



def ZNOVA_PREVERI_SHRANJENE_COINE():

    date = time.asctime().split(" ")[1] + " " + time.asctime().split(" ")[2]
    local_time = time.asctime()
    clock = local_time.split(' ')[-2].split(":")
    clock[-1] = ""
    clock = ":".join(clock)[:-1]

    for coin in shramba.coins:
        if coin.cmc_listed == None: #Če še ni listan, preglej a je ž listan pa in any case capturi h&t pri tem času
            if check_if_cmc_listed(coin) == True:
                coin.cmc_listed = clock + " " + date
                coin.cmc_url = "https://coinmarketcap.com/currencies/" + coin.name + "/"
                to = ["peter.peternik123@gmail.com"]
                for mail in to:
                    try:
                        body = f"link: {coin.bsc_url}\nime: {coin.name}"
                        email_alert("na_CMC", body, mail)
                    except smtplib.SMTPDataError:
                        print(f"temporary system error, didnt send: {coin.name} to: {mail}")
                        pass
            else:
                pass
            add_h_and_t_to_existing_coin(coin, clock + " " + date)
        else: #če je ž listan, vseno capturi h&t pri tem času
            add_h_and_t_to_existing_coin(coin, clock + " " + date)
    shramba.shrani_stanje(DATA)
    print(krepko(lightcyan("Saved coins were updated")))

def cakaj_8_minut():
    print(krepko(lightcyan("8 mins until next update")))
    time.sleep(420)
    print(krepko(rdece("1 min until next update")))
    time.sleep(60)
    print(krepko(modro("Updating began...")))



###############################################################################################
###############################################################################################


DATA = 'shramba.json'

try:
    shramba = Coins.nalozi_stanje(DATA)
except FileNotFoundError:
    shramba = Coins()


###############################################################################################
###############################################################################################
print(krepko(rumeno("3...")))
time.sleep(0.5)
print(krepko(rumeno("2...")))
time.sleep(0.5)
print(krepko(rumeno("1...")))
time.sleep(0.5)        
print(krepko(zeleno("Initiation complete...")))

while True:
    try:
        ZNOVA_PREVERI_SHRANJENE_COINE()
        #POBERI_COINE_IZ_COINGECKO_IN_SHRANI()
        cakaj_8_minut()

    except ValueError:
        print("something went wrong bruh")



