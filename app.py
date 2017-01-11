import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import TwilioRestClient
from config import CONFIG

def main(argv):
    """
    Missing docstring
    """

    # Get the command line arguments.
    args_dict = {}

    # If no interval was specified, assume a default interval of 3 hours.
    args_dict['--interval'] = '180'

    for arg, item in enumerate(argv):
        if argv[arg] == '--one-way':
            args_dict[argv[arg]] = argv[arg]
        if argv[arg] == '--from':
            args_dict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--to':
            args_dict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--departure-date':
            args_dict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--return-date':
            args_dict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--passengers':
            args_dict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--desired-total':
            args_dict[argv[arg]] = argv[arg + 1]
        elif argv[arg] == '--interval':
            args_dict[argv[arg]] = argv[arg + 1]

    scrape(args_dict)


def scrape(args_dict):
    """
    Missing docstring
    """

    while True:
        # PhantomJS is headless, so it doesn't open up a browser.
        browser = webdriver.PhantomJS()
        browser.get('https://www.southwest.com/')

        # Assumed to be round trip by default.
        one_way_bool = False
        if '--one-way' in args_dict:
            if args_dict['--one-way'] == '--one-way':
                one_way_bool = True
                one_way_elem = browser.find_element_by_id('trip-type-one-way')
                one_way_elem.click()

        depart_airport = browser.find_element_by_id('air-city-departure')
        depart_airport.send_keys(args_dict['--from'])
        arrive_airport = browser.find_element_by_id('air-city-arrival')
        arrive_airport.send_keys(args_dict['--to'])
        depart_date = browser.find_element_by_id('air-date-departure')
        depart_date.clear()
        depart_date.send_keys(args_dict['--departure-date'])

        if not one_way_bool:
            return_date = browser.find_element_by_id('air-date-return')
            return_date.clear()
            return_date.send_keys(args_dict['--return-date'])

        passengers = browser.find_element_by_id('air-pax-count-adults')
        browser.execute_script("arguments[0].removeAttribute('readonly', 0);", passengers)
        passengers.click()
        passengers.clear()
        passengers.send_keys(args_dict['--passengers'])
        passengers.click()
        search = browser.find_element_by_id('jb-booking-form-submit-button')
        search.click()

        outbound_array = []
        return_array = []

        # Webdriver might be too fast. Tell it to slow down.
        wait = WebDriverWait(browser, 120)
        wait.until(EC.element_to_be_clickable((By.ID, 'faresOutbound')))

        outbound_fares = browser.find_element_by_id('faresOutbound')
        outbound_prices = outbound_fares.find_elements_by_class_name('product_price')

        for price in outbound_prices:
            realprice = price.text.replace("$", "")
            outbound_array.append(int(realprice))

        lowest_outbound_fare = min(outbound_array)

        if not one_way_bool:
            return_fares = browser.find_element_by_id('faresReturn')
            return_prices = return_fares.find_elements_by_class_name('product_price')

            for price in return_prices:
                realprice = price.text.replace("$", "")
                return_array.append(int(realprice))

            lowest_return_fare = min(return_array)
            real_total = lowest_outbound_fare + lowest_return_fare

            print('[%s] Current Lowest Outbound Fare: $%s.' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                str(lowest_outbound_fare)))

            print('[%s] Current Lowest Return Fare: $%s.' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                str(lowest_return_fare)))

        else:
            real_total = lowest_outbound_fare
            print('[%s] Current Lowest Outbound Fare: $%s.' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                str(lowest_outbound_fare)))

        # Found a good deal. Send a text via Twilio and then stop running.
        if real_total < int(args_dict['--desired-total']):
            print('[%s] Found a deal. Desired total: $%s. Current Total: $%s.' % (
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                args_dict['--desired-total'], str(real_total)))

            client = TwilioRestClient(CONFIG.get('account_sid'), CONFIG.get('auth_token'))

            client.messages.create(
                to=CONFIG.get('to_number'),
                from_=CONFIG.get('from_number'),
                body='[%s] Found a deal. Desired total: $%s. Current Total: $%s' % (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    args_dict['--desired-total'],
                    str(real_total)))

            print(
                '[%s] Text message sent!' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )

            sys.exit()

        print(
            '''
            [%s] Couldn\'t find a deal under the amount you specified.
            Trying again to find cheaper prices...
            ''' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )

        # Keep scraping according to the interval the user specified.
        time.sleep(int(args_dict['--interval']) * 60)

main(sys.argv[1:])
