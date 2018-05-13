import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def correct_date(date):
    """
    Converts the date format to one accepted by SWA

    SWA form cannot accept slashes for dates and is in the format YYYY-MM-DD
    :param date: Date string to correct
    :return: Corrected date string

    """
    a, b, c = date.split("/")

    if(len(a) == 4):
        # Assumed format is year, month, day
        return "%s-%s-%s"%(a, b, c)
    else:
        # Assumed format is month, day, year
        return "%s-%s-%s" % (c, a, b)

def correct_time_string(timeString):
    """
    Returns a valid string version of the time of departure/arrival based on
    given argument value

    If no-value is given, "ALL_DAY" will be returned

    :param timeString: String to correct
    :return: Corrected string value
    """
    if timeString == "BEFORE_NOON":
        return "BEFORE_NOON"

    elif timeString == "NOON_TO_6PM":
        return "NOON_TO_SIX"

    elif timeString == "AFTER_6PM":
        return "AFTER_SIX"

    else:
        return "ALL_DAY"

def direct_load(args, browser):
    """
    Creates and sends a HTTP GET request for ticket prices based on the
    given arguments

    :param args: Arguments used to form request
    :param browser: Browser object used to make request
    :return: None
    """
    
    commandString = ""

    if args.passengers:
        # Set number of passengers.
        commandString += "adultPassengersCount=%s&" % (args.passengers)
    else:
        commandString += "adultPassengersCount=%s&" % ("0")

    # Set departure date.
    cleanedUpDate = correct_date(args.departure_date)
    commandString += "departureDate=%s&" % (cleanedUpDate)

    # Set the departure time
    correctedTime = correct_time_string(args.departure_time)
    commandString += "departureTimeOfDay=%s&" % (correctedTime)

    # Set the arrival airport.
    commandString += "destinationAirportCode=%s&" % (args.arrive)

    # How is the fare to be paid, USD or POINTS
    commandString += "fareType=USD&"

    commandString +="int=HOMEQBOMAIR&leapfrogRequest=true&"

    # Set the departing airport.
    commandString += "originationAirportCode=%s&" % (args.depart)

    # If there are any seniors load the senior column
    # If there are no seniors, bnut the senior column is loaded, no prices
    # will get loaded
    if args.seniors and int(args.seniors) > 0:
        commandString += "passengerType=SENIOR&"
    else:
        commandString += "passengerType=ADULT&"

    # Promo code entry
    commandString += "promoCode=&"

    # No idea what this is for, but it is in the GET string
    commandString += "redirectToVision=true&reset=true&"

    # Used in mult-stop trips
    commandString += "returnAirportCode=&"

    # Return date is always in form, even if it is a one-way trip
    # When it is one-way, the form item will have no value
    cleanedUpDate = correct_date(args.return_date)
    commandString += "returnDate=%s&" % (cleanedUpDate)

    # Set return time, even if the trip is a one-way trip.
    correctedTime = correct_time_string(args.return_time)
    commandString += "returnTimeOfDay=%s&" % (correctedTime)

    # Set number of seniors.
    if args.seniors:
        commandString += "seniorPassengersCount=%s&" % (args.seniors)
    else:
        commandString += "seniorPassengersCount=%s&" % ("0")

    # Set type of trip
    if args.one_way:
        commandString += "tripType=%s&" % ("one-way")
    else:
        commandString += "tripType=%s&" % ("roundtrip")

    # Put the URL together
    outStr = "https://www.southwest.com/air/booking/select.html?"
    outStr += commandString

    browser.get(outStr)


def scrape(args):
    """
    Run scraper on Southwest Airlines website
    If we find a flight that meets our search parameters, send an SMS message.
    """
    # Tell ChromeDriver to be headless, so it doesn't open up a browser.
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('log-level=3')

    while True:

        browser = webdriver.Chrome(chrome_options=options)

        direct_load(args, browser)

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