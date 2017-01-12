import sys
import time
import optparse

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import TwilioRestClient
from config import CONFIG

def main():
    """
    Perform a search on southwest.com for the given flight parameters.
    """
    options = parse_options()
    scrape(options)

def parse_options():
    """
    Parse the command line for search parameters.
    """
    usage = ("")
    parser = optparse.OptionParser(usage=usage)

    parser.add_option(
        "--one-way",
        action="store_true",
        default=False,
        help="If present, the search will be limited to one-way tickets.")

    parser.add_option(
        "--depart",
        action="store",
        type="string",
        dest="depart",
        help="Origin airport code.")

    parser.add_option(
        "--arrive",
        action="store",
        type="string",
        dest="arrive",
        help="Destination airport code.")

    parser.add_option(
        "--departure-date",
        action="store",
        type="string",
        dest="departure_date",
        help="Date of departure flight.")

    parser.add_option(
        "--return-date",
        action="store",
        type="string",
        dest="return_date",
        help="Date of return flight.")

    parser.add_option(
        "--passengers",
        action="store",
        type="string",
        dest="passengers",
        help="Number of passengers.")

    parser.add_option(
        "--desired-total",
        action="store",
        type="string",
        dest="desired_total",
        help="Ceiling on the total cost of flights.")

    parser.add_option(
        "--interval",
        action="store",
        type="string",
        default=1,
        dest="interval",
        help="Refresh time period.")

    parsed_args = parser.parse_args()

    return parsed_args[0]

def scrape(options):
    """
    Run scraper on Southwest.com.
    If we find a flight that meets our search parameters, send an SMS message.
    """

    while True:
        # PhantomJS is headless, so it doesn't open up a browser.
        browser = webdriver.PhantomJS()
        browser.get("https://www.southwest.com/")

        if options.one_way:
            # Set one way trip with click event
            one_way_elem = browser.find_element_by_id("trip-type-one-way")
            one_way_elem.click()

        # Set the departing airport
        depart_airport = browser.find_element_by_id("air-city-departure")
        depart_airport.send_keys(options.depart)

        # Set the arrival airport
        arrive_airport = browser.find_element_by_id("air-city-arrival")
        arrive_airport.send_keys(options.arrive)

        # Set departure date
        depart_date = browser.find_element_by_id("air-date-departure")
        depart_date.clear()
        depart_date.send_keys(options.departure_date)

        if not options.one_way:
            # Set return date
            return_date = browser.find_element_by_id("air-date-return")
            return_date.clear()
            return_date.send_keys(options.return_date)

        passengers = browser.find_element_by_id("air-pax-count-adults")
        browser.execute_script("arguments[0].removeAttribute('readonly', 0);", passengers)
        passengers.click()
        passengers.clear()
        
        # Set passenger count
        passengers.send_keys(options.passengers)
        passengers.click()
        search = browser.find_element_by_id("jb-booking-form-submit-button")
        search.click()

        outbound_array = []
        return_array = []

        # Webdriver might be too fast. Tell it to slow down.
        wait = WebDriverWait(browser, 120)
        wait.until(EC.element_to_be_clickable((By.ID, "faresOutbound")))

        outbound_fares = browser.find_element_by_id("faresOutbound")
        outbound_prices = outbound_fares.find_elements_by_class_name("product_price")

        for price in outbound_prices:
            realprice = price.text.replace("$", "")
            outbound_array.append(int(realprice))

        lowest_outbound_fare = min(outbound_array)

        if not options.one_way:
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
        if real_total < int(options.desired_total):
            print("[%s] Found a deal. Desired total: $%s. Current Total: $%s." % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                options.desired_total, str(real_total)))

            client = TwilioRestClient(CONFIG.get("account_sid"), CONFIG.get("auth_token"))

            client.messages.create(
                to=CONFIG.get("to_number"),
                from_=CONFIG.get("from_number"),
                body="[%s] Found a deal. Desired total: $%s. Current Total: $%s" % (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    options.desired_total,
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
        time.sleep(int(options.interval) * 60)

if __name__ == "__main__":
    main()
