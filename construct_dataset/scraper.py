#!/usr/bin/python
from time import time
from crawler import get_matches
from selenium import webdriver
from bs4 import BeautifulSoup
import re
from csv import writer
from datetime import date, timedelta
from selenium.webdriver.common.proxy import Proxy, ProxyType

sdate = date(2022,1,18)   # start date
edate = date(2022,2,1)   # end date

def dates_bwn_twodates(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

proxy = Proxy({
    'proxyType': ProxyType.MANUAL,
    'socksProxy': '127.0.0.1:9050',
    'socksVersion': 5,
})


def get_corners(code, home, away):
    start = code.find("Score After First Half")
    end = code[start:].find("Pitch:")
    code_fh = code[start:start+end]
    
    times = re.findall(r'\d+\'', code_fh)
    corner_home_fh = 0
    corner_away_fh = 0
    i= 0

    for time in times:
        start = code_fh.find(time)
        end = code_fh[start:].find("</li>")
        
        #print(code_fh[start:start+end])
        
        if(code_fh[start:start+end].find("Corner -")!=-1 and code_fh[start:start+end].replace(" ","").find(home)!=-1):
            corner_home_fh += 1
        elif(code_fh[start:start+end].find("Corner -")!=-1 and code_fh[start:start+end].replace(" ","").find(away)!=-1):
            corner_away_fh += 1
        code_fh = code_fh[end:]
    
    return corner_away_fh, corner_home_fh

def get_serial(code, home, away):
    start = code.find("Score After Full Time")
    end = code[start:].find("Score After First Half ")
    code_lh = code[start:start+end]
    
    times = re.findall(r'\d+\'', code_lh)
    data=[[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
    i= 0
    for time in times:
        if(int(time.replace("\'","")) < 50):
            i = 4
        elif(int(time.replace("\'","")) < 60):
            i = 3
        elif(int(time.replace("\'","")) < 70):
            i = 2
        elif(int(time.replace("\'","")) < 80):
            i = 1
        elif(int(time.replace("\'","")) >= 80):
            i = 0
        
        start = code_lh.find(time)
        end = code_lh[start:].find("</li>")
        
        #print(code_lh[start:start+end])
        if(code_lh[start:start+end].find("Corner -")!=-1 and code_lh[start:start+end].replace(" ","").find(home)!=-1):
            data[4-i][0] += 1
        elif(code_lh[start:start+end].find("Corner -")!=-1 and code_lh[start:start+end].replace(" ","").find(away)!=-1):
            data[4-i][1] += 1   
        elif(code_lh[start:start+end].find("Goal ")!=-1 and code_lh[start:start+end].replace(" ","").find(home)!=-1):
            data[4-i][2] += 1
        elif(code_lh[start:start+end].find("Goal ")!=-1 and code_lh[start:start+end].replace(" ","").find(away)!=-1):
            data[4-i][3] += 1  
        elif(code_lh[start:start+end].find("Red Card ")!=-1 and code_lh[start:start+end].replace(" ","").find(home)!=-1):
            data[4-i][4] += 1
        elif(code_lh[start:start+end].find("Red Card ")!=-1 and code_lh[start:start+end].replace(" ","").find(away)!=-1):
            data[4-i][5] += 1
        code_lh = code_lh[start+end:]


    start = code.find("Score After First Half")
    end = code[start:].find("Pitch:")
    code_fh = code[start:start+end]
    
    times = re.findall(r'\d+\'', code_fh)
    data_fh=[[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
    
    i= 0

    for time in times:
        if(int(time.replace("\'","")) < 10):
            i = 4
        elif(int(time.replace("\'","")) < 20):
            i = 3
        elif(int(time.replace("\'","")) < 30):
            i = 2
        elif(int(time.replace("\'","")) < 40):
            i = 1
        elif(int(time.replace("\'","")) >= 40):
            i = 0
        start = code_fh.find(time)
        end = code_fh[start:].find("</li>")
        
        #print(code_fh[start:start+end])
        
        if(code_fh[start:start+end].find("Corner -")!=-1 and code_fh[start:start+end].replace(" ","").find(home)!=-1):
            data_fh[4-i][0] += 1
        elif(code_fh[start:start+end].find("Corner -")!=-1 and code_fh[start:start+end].replace(" ","").find(away)!=-1):
            data_fh[4-i][1] += 1   
        elif(code_fh[start:start+end].find("Goal ")!=-1 and code_fh[start:start+end].replace(" ","").find(home)!=-1):
            data_fh[4-i][2] += 1
        elif(code_fh[start:start+end].find("Goal ")!=-1 and code_fh[start:start+end].replace(" ","").find(away)!=-1):
            data_fh[4-i][3] += 1  
        elif(code_fh[start:start+end].find("Red Card ")!=-1 and code_fh[start:start+end].replace(" ","").find(home)!=-1):
            data_fh[4-i][4] += 1
        elif(code_fh[start:start+end].find("Red Card ")!=-1 and code_fh[start:start+end].replace(" ","").find(away)!=-1):
            data_fh[4-i][5] += 1
        code_fh = code_fh[end:]
    
    return data_fh, data

def get_features(url):
    fire_options = webdriver.FirefoxOptions()

    #fire_options.headless = True
    fire_options.proxy = proxy
    fire_options.binary_location = '/home/adriel/Desktop/tor-browser_en-US/Browser/firefox'
    fire_options.headless = True
    driver = webdriver.Firefox(options=fire_options) # Could be any other browser you have the drivers for
    connected = False
    while not connected:
        try:
            driver.get(url)
            connected = True
        except:
            pass
    html = driver.page_source
    code = str(BeautifulSoup(html, 'html.parser'))
    driver.close()

    start = code.find("Pitch: ")
    end = code[start:].find("</li>")

    pitch = code[start + 7:start+end].replace(" ", "")


    start = code.find("Weather: ")
    end = code[start:].find("</li>")

    weather = code[start + 9:start+end].replace(" ", "")

    s_start = code.find("Full Time")
    data = []
    for i in range(20):
        start2 = code[s_start:].find("<div class=\"small-2 text-center columns\">")+len("<div class=\"small-2 text-center columns\">")
        s_start += start2
        end = code[s_start:].find("</div>")

        data.append(code[s_start:s_start+end])
    
    start = code.find("Score After Full Time - ")
    end1 = code[start+len("Score After Full Time - "):].find("-")
    end2 = code[start+len("Score After Full Time - "):].find("</li>")

    score_home_f_time = code[start+len("Score After Full Time - "):start+len("Score After Full Time - ")+end1]
    score_away_f_time = code[start+len("Score After Full Time - ")+end1+1:start+len("Score After Full Time - ")+end2].replace(" ", "")

    start = code.find("Score After First Half - ")
    end1 = code[start+len("Score After First Half - "):].find("-")
    end2 = code[start+len("Score After First Half - "):].find("</li>")

    score_home_h_time = code[start+len("Score After First Half - "):start+len("Score After First Half - ")+end1]
    score_away_h_time = code[start+len("Score After First Half - ")+end1+1:start+len("Score After First Half - ")+end2].replace(" ", "")
    

    start = code.find("Live Scores of ")+len("Live Scores of ")
    end = code.find("vs")
    home = code[start:end].replace(" ", "")

    start = code.find("vs")+len("vs")

    end = code[start:].find("-")
    away = code[start:start+end].replace(" ", "")

    start = code.find("Score After Full Time - ")
    end = code.find("Score After First Half - ")
    corners_away = code[start:end].replace(" ","").count("thCorner-"+away)+code[start:end].replace(" ","").count("stCorner-"+away)+code[start:end].replace(" ","").count("ndCorner-"+away)+code[start:end].replace(" ","").count("rdCorner-"+away)
    corners_home = code[start:end].replace(" ","").count("thCorner-"+home)+code[start:end].replace(" ","").count("stCorner-"+home)+code[start:end].replace(" ","").count("ndCorner-"+home)+code[start:end].replace(" ","").count("rdCorner-"+home)
    
    start = code.find("Score After First Half - ")
    end = code.find("Pitch: ")
    corners_away_FH = code[start:end].replace(" ","").count("thCorner-"+away)+code[start:end].replace(" ","").count("stCorner-"+away)+code[start:end].replace(" ","").count("ndCorner-"+away)+code[start:end].replace(" ","").count("rdCorner-"+away)
    corners_home_FH = code[start:end].replace(" ","").count("thCorner-"+home)+code[start:end].replace(" ","").count("stCorner-"+home)+code[start:end].replace(" ","").count("ndCorner-"+home)+code[start:end].replace(" ","").count("rdCorner-"+home)
    
    start = code.find("Score After Full Time - ")
    end = code.find("Score After First Half - ")

    last_half = code[start:end]

    start = last_half.find("th Corner - ")
    if(start == -1):
        start = last_half.find("rd Corner - ")

    if(start == -1):
        start = last_half.find("nd Corner - ")

    if(start == -1):
        start = last_half.find("st Corner - ")
    
    end = last_half[start-10:].find("</li>")

    

    times = re.findall(r'\d+', last_half[start-10:start-10+end])
    times = [int(i) for i in times]

    target_last_half = any([i > 88 for i in times])


    start = code.find("Score After First Half - ")
    end = code.find("Pitch: ")

    last_half = code[start:end]

    start = last_half.find("th Corner - ")
    if(start == -1):
        start = last_half.find("rd Corner - ")

    if(start == -1):
        start = last_half.find("nd Corner - ")

    if(start == -1):
        start = last_half.find("st Corner - ")
    
    end = last_half[start-10:].find("</li>")

    serial_datafh, serial_datalh = get_serial(code, home, away)

    file = open("MyFile.txt", "w")
    file.write(code)
    file.close
    
    times = re.findall(r'\d+', last_half[start-10:start-10+end])
    times = [int(i) for i in times]

    target_first_half = any([i > 39 for i in times])
    condition = False
    for d in data:
        if(len(d) > 10):
            condition = True
    if(len(score_home_h_time) > 3 or len(score_home_f_time) > 3 or len(score_away_f_time) > 3 or len(score_away_h_time) > 3):
        condition = True
    if(condition):
        return ([],[],[],[])
    else:
        return (serial_datafh, serial_datalh, [pitch, weather, score_home_h_time, score_away_h_time, corners_home_FH, corners_away_FH, data[0], data[1],data[2], data[3],data[4], data[5], data[6], data[7], data[8], data[9], target_first_half],[pitch, weather, score_home_f_time, score_away_f_time, corners_home, corners_away, data[10], data[11],data[12], data[13],data[14], data[15], data[16], data[17], data[18], data[19], target_last_half])

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

def get_league(url):
    fire_options = webdriver.FirefoxOptions()

    #fire_options.headless = True
    fire_options.proxy = proxy
    fire_options.binary_location = '/home/adriel/Desktop/tor-browser_en-US/Browser/firefox'
    fire_options.headless = True
    driver = webdriver.Firefox(options=fire_options) # Could be any other browser you have the drivers for
    connected = False
    while not connected:
        try:
            driver.get(url)
            connected = True
        except:
            pass
    html = driver.page_source
    code = str(BeautifulSoup(html, 'html.parser'))
    driver.close()

    start = code.find("<td class=\"bg")
    end = code[start:].find("</a></td>")
    
    
    return code[start+len("<td class=\"bg2\"><a>"):start+end]

    


def fill_table(list_dates):
    for date in list_dates:
        print("Actual date is: "+date)
        matches,basics = get_matches(date)
        #print(get_league("https://www.scorebing.com"+basics[0]))
        
        counter = 1
        for (match,basic) in zip(matches, basics):
            print("line: "+str(counter))
            counter+=1
            league = get_league("https://www.scorebing.com"+basic)
            if(len(league) > 50):
                continue
            s_fh, s_lh, list1, list2 = get_features("https://www.scorebing.com"+match)
            
            if(list1):
                append_list_as_row("Dataset.csv", ["fh", league] + list1)
                for j in range(6):
                    append_list_as_row("serialDataset.csv", [i[j] for i in s_fh])
            if(list2):
                append_list_as_row("Dataset.csv", ["lh", league] + list2)
                for j in range(6):
                    append_list_as_row("serialDataset.csv", [i[j] for i in s_lh])
            
        



dates = [str(d).replace("-", "") for d in dates_bwn_twodates(sdate,edate)]


fill_table(dates)
