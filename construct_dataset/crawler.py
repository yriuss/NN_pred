from time import sleep
from anyio import open_file
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.proxy import Proxy, ProxyType

proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'socksProxy': '127.0.0.1:9050',
    'socksVersion': 5,
})

def get_matches(date):
    fire_options = webdriver.FirefoxOptions()

    #fire_options.headless = True
    fire_options.proxy = proxy
    fire_options.binary_location = '/home/adriel/Desktop/tor-browser_en-US/Browser/firefox'
    fire_options.headless = True
    driver = webdriver.Firefox(options=fire_options) # Could be any other browser you have the drivers for
    connected = False
    while not connected:
        try:
            driver.get('https://www.scorebing.com/fixtures/'+date)
            connected = True
        except:
            pass
    html = driver.page_source
    code = str(BeautifulSoup(html, 'html.parser'))

    

    driver.close()
    stop = False
    counter = 0
    matches = []
    basic = []
    while(not stop):
        stop = False
        start = code.find("/match_live/")
        start2 = code.find("/match/")
        if(start == -1):
            stop = True
        end = code[start:].find("\"") + start
        end2 = code[start2:].find("\"") + start2
        if(start != -1):       
            matches.append(code[start:end])
            basic.append(code[start2:end2])
        code = code[end2+1:]
        counter+=1
    return matches, basic

