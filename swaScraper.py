import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

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
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "currency_dollars")))
            print("[%s] Results loaded." % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        except TimeoutError:
            print("[%s] Results took too long!" % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        outbound_fares = browser.find_elements_by_tag_name("ul")[2]
        outbound_prices = outbound_fares.find_elements_by_class_name("currency_dollars")

        for price in outbound_prices:
            realprice = price.text.replace("$", "")
            outbound_array.append(int(realprice))

        lowest_outbound_fare = min(outbound_array)

        if not args.one_way:
            return_fares = browser.find_elements_by_tag_name("ul")[5]
            return_prices = return_fares.find_elements_by_class_name("currency_dollars")

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
        if real_total <= args.max_price:
            return real_total

        print(
            '''
            [%s] Couldn\'t find a deal under the amount you specified.
            Trying again to find cheaper prices...
            ''' % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

        # Keep scraping according to the interval the user specified.
        time.sleep(int(args.interval) * 60)