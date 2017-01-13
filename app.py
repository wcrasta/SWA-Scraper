from selenium import webdriver
import configparser
import sys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import TwilioRestClient
from datetime import datetime

config = configparser.SafeConfigParser()
config.read('config.ini')
account_sid = config.get('twilio', 'account_sid')
auth_token = config.get('twilio', 'auth_token')
fromNumber = config.get('twilio', 'fromNumber')
toNumber = config.get('twilio', 'toNumber')

def main(argv):
    # Get the command line arguments.
    argsDict = {}
    # If no interval was specified, assume a default interval of 3 hours.
    argsDict['--interval'] = '180'
    for arg in range(len(argv)):
        if argv[arg] == '--one-way':
            argsDict[argv[arg]] = argv[arg]
        if argv[arg] == '--from':
            argsDict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--to':
            argsDict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--departure-date':
            argsDict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--return-date':
            argsDict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--passengers':
            argsDict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--desired-total':
            argsDict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--interval':
            argsDict[argv[arg]] = argv[arg + 1]
    scrape(argsDict)

def scrape(argsDict):
    while True:
        # PhantomJS is headless, so it doesn't open up a browser.
        browser = webdriver.PhantomJS()
        browser.get('https://www.southwest.com/')
        # Assumed to be round trip by default.
        oneWayBool = False
        if '--one-way' in argsDict:
            if argsDict['--one-way'] == '--one-way':
                oneWayBool = True
                onewayElem = browser.find_element_by_id('trip-type-one-way')
                onewayElem.click()
        departAirport = browser.find_element_by_id('air-city-departure')
        departAirport.send_keys(argsDict['--from'])
        arriveAirport = browser.find_element_by_id('air-city-arrival')
        arriveAirport.send_keys(argsDict['--to'])
        depart_date = browser.find_element_by_id('air-date-departure')
        depart_date.clear()
        depart_date.send_keys(argsDict['--departure-date'])
        if not oneWayBool:
            return_date = browser.find_element_by_id('air-date-return')
            return_date.clear()
            return_date.send_keys(argsDict['--return-date'])
        passengers = browser.find_element_by_id('air-pax-count-adults')
        browser.execute_script("arguments[0].removeAttribute('readonly', 0);", passengers)
        passengers.click()
        passengers.clear()
        passengers.send_keys(argsDict['--passengers'])
        passengers.click()
        search = browser.find_element_by_id('jb-booking-form-submit-button')
        search.click()

        outboundArray = []
        returnArray = []

        # Webdriver might be too fast. Tell it to slow down.
        wait = WebDriverWait(browser, 120)
        wait.until(EC.element_to_be_clickable((By.ID, 'faresOutbound')))

        outboundFares = browser.find_element_by_id('faresOutbound')
        outboundPrices = outboundFares.find_elements_by_class_name('product_price')
        for price in outboundPrices:
            realprice = price.text.replace("$", "")
            outboundArray.append(int(realprice))
        lowestOutboundFare = min(outboundArray)

        if not oneWayBool:
            returnFares = browser.find_element_by_id('faresReturn')
            returnPrices = returnFares.find_elements_by_class_name('product_price')
            for price in returnPrices:
                realprice = price.text.replace("$", "")
                returnArray.append(int(realprice))
            lowestReturnFare = min(returnArray)
            realTotal = lowestOutboundFare + lowestReturnFare
            print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Current Lowest Outbound Fare: $' + str(lowestOutboundFare) + '.')
            print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Current Lowest Return Fare: $' + str(lowestReturnFare) + '.')
        else:
            realTotal = lowestOutboundFare
            print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Current Lowest Outbound Fare: $' + str(lowestOutboundFare) + '.')

        # Found a good deal. Send a text via Twilio and then stop running.
        if realTotal < int(argsDict['--desired-total']):
            print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Found a deal. Desired total: $' + argsDict['--desired-total'] + '. Current Total: $' + str(realTotal) + '.')
            client = TwilioRestClient(account_sid, auth_token)

            message = client.messages.create(to=toNumber, from_=fromNumber,
                                             body='[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Found a deal. Desired total: $' + argsDict['--desired-total'] + '. Current Total: $' + str(realTotal)+ '.')
            print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Text message sent!')
            sys.exit()
        print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Couldn\'t find a deal under the amount you specified. Trying again to find cheaper prices...')
        # Keep scraping according to the interval the user specified.
        time.sleep(int(argsDict['--interval']) * 60)

main(sys.argv[1:])
