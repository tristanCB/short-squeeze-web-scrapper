#!/usr/bin/env python
import signal
import sys
import urllib
from urllib.parse import urljoin
import argparse
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from collections import defaultdict
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# proxy = "localhost:8080"
# desired_capabilities = webdriver.DesiredCapabilities.CHROME.copy()
# desired_capabilities['proxy'] = {
#     "httpProxy": proxy,
#     "ftpProxy": proxy,
#     "sslProxy": proxy,
#     "noProxy": None,
#     "proxyType": "MANUAL",
#     "class": "org.openqa.selenium.Proxy",
#     "autodetect": False
# }

### ///
# driver = webdriver.Chrome(ChromeDriverManager().install())
# driver.get("http://whatismyipaddress.com")

### /// USING TOR PROXY MUST BE INSTALLED AND RUNNING
chrome_options = Options()
chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:9150")
# driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
# driver.get('https://whatismyipaddress.com/')
### ///

def selenium_get(dx_url):
    """
    Uses selenium to return soup.
    """
    # Make sure to appropriatly link driver for selenium
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    driver.get(dx_url)
    # wait = WebDriverWait(driver, 5)
    soup = BeautifulSoup(driver.page_source)
    driver.quit()
    return soup

def signal_handler(signal, frame):
    """
    https://gist.github.com/rtfpessoa/e3b1fe0bbfcd8ac853bf
    Saves data retreived if program is stopped using ctr-c.
    """
    df = pd.DataFrame(metaShort)
    df.T.to_csv('results.csv', index=True)
    sys.exit(0)

def sp500_tickers():
    """
    Scrappes wikipedia for companies on the SPX and return a list of them
    """
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        tickers.append(ticker[:-2])
    return tickers

def retreiveShort(ticker):
    """
    Given a ticker located elements of interest from shortsqueeze.com and return a dictionary
    """
    # We will return the quote given by shortsqueeze.com
    quote = {}

    soup = selenium_get("http://shortsqueeze.com/?symbol={}&submit=Short+Quote%E2%84%A2".format(ticker))
    data = soup.find_all('table', attrs={'width':'400'})
    
    whitelist = [
    'td',
    'div'
    ]

    text_elements = [t for t in soup.find_all(text=True) if t.parent.name in whitelist]
    
    try: # handles cases when elements are not defined
        quote["Short Percent of Float"] = float(text_elements[text_elements.index("Short Percent of Float")+1].strip(" %"))
    except:
        quote["Short Percent of Float"] = "NAN"

    quote["Short % Increase / Decrease"] = float(text_elements[text_elements.index("Short % Increase / Decrease")+1].strip(" %"))

    try: # handles cases when elements are not defined
        quote["% Owned by Insiders"] = float(text_elements[text_elements.index("% Owned by Insiders")+1].strip(" %"))
        quote["% Owned by Institutions"] = float(text_elements[text_elements.index("% Owned by Institutions")+1].strip(" %"))
    except:
        quote["% Owned by Insiders"] = "NAN"
        quote["% Owned by Institutions"] = "NAN"

    quote["Trading Volume - Today"] = float(text_elements[text_elements.index("Trading Volume - Today")+1].replace(",",""))
    quote["Trading Volume - Average"] = float(text_elements[text_elements.index("Trading Volume - Today")+1].replace(",",""))
    quote["Short Interest Ratio (Days To Cover)"] = float(text_elements[text_elements.index("Short Interest Ratio (Days To Cover)")+1].replace(",",""))

    return quote

if __name__  == "__main__":
    # Resolve output filename
    parser = argparse.ArgumentParser()  
    parser.add_argument('--outputFileName', type=str, help='Output filename. Should end with .csv', default='results.csv')
    args = parser.parse_args()
    
    # This program scrapes http://shortsqueeze.com/ using a list of tickers on the SPX. It outputs a csvfile.
    # TOR browser proxy is used to surpass daily quote limit which is probably assigned based on I.P. addresses.
    print("Ensure that TOR browser is running. Starting program main loop in 5 seconds")
    time.sleep(5)
    
    # Objects handles when program is stopped using ctrl-c, making sure scrapped data is saved before exiting.
    signal.signal(signal.SIGINT, signal_handler)
    
    # Vars
    metaShort = {}
    errors = []

    # Get a list of all tickers on the SPX
    tickers = sp500_tickers()

    # Main program loop. Iterates Through all the companies on the SPX calling the function to scrape data from
    # shortsqueeze.com. Warning: It takes quite a long time to complete and clutters GUI.
    for i in tickers:
        try:
            metaShort[i]= retreiveShort(i)
            # time.sleep(1)
            print(f"Sucessfully retrieved ... {len(metaShort)} stonk short info")
        except Exception as e:
            errors.append(i)
            print(f"Error retreiving {i} /// total error --> {len(errors)}")

    # print(metaShort)
    
    # Format data using pandas and save as a csv file.
    df = pd.DataFrame(metaShort)
    df.T.to_csv(args.outputFileName, index=True)

