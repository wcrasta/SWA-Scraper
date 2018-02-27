import argparse
import configparser
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import TwilioRestClient

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')
ACCOUNT_SID = CONFIG['twilio']['account_sid']
AUTH_TOKEN = CONFIG['twilio']['auth_token']
FROM_NUMBER = CONFIG['twilio']['from_number']
TO_NUMBER = CONFIG['twilio']['to_number']

def main():
    """
    Perform a search on southwest.com for the given flight parameters.
    """
    args = parse_args()
    scrape(args)

def parse_args():
    """
    Parse the command line for search parameters.
    """
    parser = argparse.ArgumentParser(description='Process command line arguments')

    parser.add_argument(
        "--one-way",
        action="store_true",
        help="If present, the search will be limited to one-way tickets.")

    parser.add_argument(
        "--depart",
        "-d",
        type=str,
        required=True,
        help="Origin airport code.")

    parser.add_argument(
        "--arrive",
        "-a",
        type=str,
        required=True,
        help="Destination airport code.")

    parser.add_argument(
        "--departure-date",
        "-dd",
        type=str,
        required=True,
        help="Date of departure flight.")
    
    parser.add_argument(
        "--departure-time",
        "-dt",
        type=str,
        choices=["BEFORE_NOON", "NOON_TO_6PM", "AFTER_6PM", "ANYTIME"],
        help="Time period of departure flight.")

    parser.add_argument(
        "--return-date",
        "-rd",
        type=str,
        required=True,
        help="Date of return flight.")
    
    parser.add_argument(
        "--return-time",
        "-rt",
        type=str,
        choices=["BEFORE_NOON", "NOON_TO_6PM", "AFTER_6PM", "ANYTIME"],
        help="Time period of return flight.")

    parser.add_argument(
        "--passengers",
        "-p",
        action="store",
        type=int,
        help="Number of passengers.")

    parser.add_argument(
        "--seniors",
        "-s",
        action="store",
        type=int,
        help="Number of seniors.")

    parser.add_argument(
        "--max-price",
        "-m",
        type=int,
        required=True,
        help="Maximum total cost of flights.")

    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        required=True,
        default=180,
        help="Refresh time period.")

    args = parser.parse_args()

    return args

def scrape(args):
    """
    Run scraper on Southwest Airlines website
    If we find a flight that meets our search parameters, send an SMS message.
    """
    while True:
        # PhantomJS is headless, so it doesn't open up a browser.
        browser = webdriver.PhantomJS()
        browser.get("https://www.southwest.com/flight/?int=HOME-BOOKING-WIDGET-ADVANCED-AIR/")

        if args.one_way:
            # Set one way trip with click event.
            one_way_elem = browser.find_element_by_id("oneWay")
            one_way_elem.click()

        # Set the departing airport.
        depart_airport = browser.find_element_by_id("originAirport_displayed")
        browser.execute_script("arguments[0].removeAttribute('readonly', 0);", depart_airport)
        depart_airport.clear()
        depart_airport.send_keys(args.depart)

        # Set the arrival airport.
        arrive_airport = browser.find_element_by_id("destinationAirport_displayed")
        arrive_airport.clear()
        arrive_airport.send_keys(args.arrive)

        # Set departure date.
        depart_date = browser.find_element_by_id("outboundDate")
        depart_date.clear()
        depart_date.send_keys(args.departure_date)
        
        if args.departure_time:
            # Set departure time.
            depart_time = browser.find_element_by_id("outboundTimeOfDay")
            depart_time.send_keys(args.departure_time)

        if not args.one_way:
            # Set return date.
            return_date = browser.find_element_by_id("returnDate")
            return_date.clear()
            return_date.send_keys(args.return_date)

            if args.return_time:
                # Set return time.
                return_time = browser.find_element_by_id("returnTimeOfDay")
                return_time.send_keys(args.return_time)

        if args.passengers:
            # Set number of passengers.
            passengers = browser.find_element_by_id("adultPassengerCount")
            passengers.send_keys(args.passengers)

        if args.seniors:
            # Set number of seniors.
            seniors = browser.find_element_by_id("seniorPassengerCount")
            seniors.send_keys(args.seniors)

        # Submit Form
        search = browser.find_element_by_id("submitButton")
        search.click()

        print("[%s] Submitting form..." % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        outbound_array = []
        return_array = []

        try:
            # Webdriver might be too fast. Tell it to slow down.
            wait = WebDriverWait(browser, 120)
            wait.until(EC.element_to_be_clickable((By.ID, "faresOutbound")))
            print("[%s] Results loaded." % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        except TimeoutError:
            print("[%s] Results took too long!" % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        
        # TODO: Add further filtering on results (nonstop only, direct only)
        outbound_fares = browser.find_element_by_id("faresOutbound")
        outbound_prices = outbound_fares.find_elements_by_class_name("product_price")

        for price in outbound_prices:
            realprice = price.text.replace("$", "")
            outbound_array.append(int(realprice))

        lowest_outbound_fare = min(outbound_array)

        if not args.one_way:
            # TODO: Add further filtering on results (nonstop only, direct only)
            return_fares = browser.find_element_by_id("faresReturn")
            return_prices = return_fares.find_elements_by_class_name("product_price")

            for price in return_prices:
                realprice = price.text.replace("$", "")
                return_array.append(int(realprice))

            lowest_return_fare = min(return_array)
            real_total = lowest_outbound_fare + lowest_return_fare

            print("[%s] Current Lowest Outbound Fare: $%s." % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(lowest_outbound_fare)))

            print("[%s] Current Lowest Return Fare: $%s." % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(lowest_return_fare)))

        else:
            real_total = lowest_outbound_fare
            print("[%s] Current Lowest Outbound Fare: $%s." % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                str(lowest_outbound_fare)))

        # Found a good deal. Send a text via Twilio and then stop running.
        # TODO: Add flight details to notification
        if real_total <= args.max_price:
            print("[%s] Found a deal. Max Total: $%s. Current Total: $%s." % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                args.max_price, str(real_total)))

            client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
            client.messages.create(
               to=TO_NUMBER,
               from_=FROM_NUMBER,
               body="[%s] Found a deal. Max Total: $%s. Current Total: $%s" % (
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   args.max_price,
                   str(real_total)))

            print(
                "[%s] Text message sent!" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )

            sys.exit()

        print(
            '''
            [%s] Couldn\'t find a deal under the amount you specified.
            Trying again to find cheaper prices...
            ''' % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        # Keep scraping according to the interval the user specified.
        time.sleep(args.interval * 60)

if __name__ == "__main__":
    main()