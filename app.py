from selenium import webdriver
import configparser
import sys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import TwilioRestClient
from datetime import datetime
import click

config = configparser.ConfigParser()
config.read('config.ini')
account_sid = config['twilio']['account_sid']
auth_token = config['twilio']['auth_token']
fromNumber = config['twilio']['fromNumber']
toNumber = config['twilio']['toNumber']

# this allows us to use -h in addition to --help
# for command line help
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.command(help="""Scrapes the Southwest website according to the interval you set. For best results when using this program, I recommend setting the interval between 2-3 hours. A more frequent interval than that might be excessive. When the price goes under a certain amount, you will be notified via text message.""",
               context_settings=CONTEXT_SETTINGS)
@click.option('--one-way',
              help='One-way flight flag.',
              is_flag=True)
@click.option('--from',
              help='Departure airport.')
@click.option('--to',
              help='Arrival airport.')
@click.option('--departure-date',
              help='Departure date in DD/MM format.')
@click.option('--return-date',
              help='Return date in DD/MM format.')
@click.option('--passengers',
              help='Number of passengers.',
              type=int,
              default=1)
@click.option('--desired-total',
              help='The total fare for one person should be under this amount (dollars).',
              type=int,
              default=200)
@click.option('--interval',
              help="How often to scrape Southwest's website (minutes)",
              type=int,
              default=180)
def main(**argv):
    scrape(argv)

def scrape(argsDict):
    while True:
        # PhantomJS is headless, so it doesn't open up a browser.
        browser = webdriver.PhantomJS()
        browser.get('https://www.southwest.com/')
        # Assumed to be round trip by default.
        oneWayBool = False
        if argsDict['one_way']:
            oneWayBool = True
            onewayElem = browser.find_element_by_id('trip-type-one-way')
            onewayElem.click()
        departAirport = browser.find_element_by_id('air-city-departure')
        departAirport.send_keys(argsDict['from'])
        arriveAirport = browser.find_element_by_id('air-city-arrival')
        arriveAirport.send_keys(argsDict['to'])
        depart_date = browser.find_element_by_id('air-date-departure')
        depart_date.clear()
        depart_date.send_keys(argsDict['departure_date'])
        if not oneWayBool:
            return_date = browser.find_element_by_id('air-date-return')
            return_date.clear()
            return_date.send_keys(argsDict['return_date'])
        passengers = browser.find_element_by_id('air-pax-count-adults')
        browser.execute_script("arguments[0].removeAttribute('readonly', 0);", passengers)
        passengers.click()
        passengers.clear()
        passengers.send_keys(argsDict['passengers'])
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
        if realTotal < argsDict['desired_total']:
            print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Found a deal. Desired total: $' + str(argsDict['desired_total']) + '. Current Total: $' + str(realTotal) + '.')
            client = TwilioRestClient(account_sid, auth_token)

            message = client.messages.create(to=toNumber, from_=fromNumber,
                                             body='[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Found a deal. Desired total: $' + str(argsDict['desired_total']) + '. Current Total: $' + str(realTotal)+ '.')
            print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Text message sent!')
            sys.exit()
        print('[' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '] Couldn\'t find a deal under the amount you specified. Trying again to find cheaper prices...')
        # Keep scraping according to the interval the user specified.
        time.sleep(int(argsDict['interval']) * 60)

if __name__ == '__main__':
    main()
