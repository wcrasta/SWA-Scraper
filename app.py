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


SWA_AIRPORTS = {'BZE': 'Belize City, Belize', 'MEX': 'Mexico City, Mexico', 
                'BWI': 'Baltimore/Washington, MD', 'MEM': 'Memphis, TN', 'LAS': 'Las Vegas, NV', 
                'FNT': 'Flint, MI', 'PHL': 'Philadelphia, PA', 'GCM': 'Grand Cayman Island, KY', 
                'NAS': 'Nassau, Bahamas', 'SAT': 'San Antonio, TX', 'SFO': 'San Francisco, CA', 
                'PNS': 'Pensacola, FL', 'RDU': 'Raleigh/Durham, NC', 'ROC': 'Rochester, NY', 
                'MSP': 'Minneapolis/St. Paul (Terminal 2), MN', 'PBI': 'West Palm Beach, FL', 
                'TPA': 'Tampa, FL', 'ORF': 'Norfolk, VA', 'MCO': 'Orlando, FL', 'STL': 'St. Louis, MO', 
                'SLC': 'Salt Lake City, UT', 'DAY': 'Dayton, OH', 'RSW': 'Ft. Myers, FL', 
                'MBJ': 'Montego Bay, Jamaica', 'BOI': 'Boise, ID', 'BHM': 'Birmingham, AL', 
                'BUR': 'Burbank, CA', 'CUN': 'Cancun, Mexico', 'PIT': 'Pittsburgh, PA', 'ISP': 'Long Island/Islip, NY', 
                'FLL': 'Ft. Lauderdale, FL', 'MDW': 'Chicago (Midway), IL', 'ECP': 'Panama City Beach, FL', 
                'CLT': 'Charlotte, NC', 'CHS': 'Charleston, SC', 'AUA': 'Aruba, Aruba', 'DEN': 'Denver, CO', 
                'PVR': 'Puerto Vallarta, MX', 'PHX': 'Phoenix, AZ', 'SNA': 'Orange County/Santa Ana, CA', 
                'VRA': 'Varadero, Cuba', 'ATL': 'Atlanta, GA', 'SMF': 'Sacramento, CA', 'HOU': 'Houston (Hobby), TX', 
                'ONT': 'Ontario/LA, CA', 'RNO': 'Reno/Tahoe, NV', 'SEA': 'Seattle/Tacoma, WA', 'BDL': 'Hartford, CT', 
                'LGA': 'New York (LaGuardia), NY', 'CAK': 'Akron-Canton, OH', 'CMH': 'Columbus, OH', 'TUS': 'Tucson, AZ', 
                'PVD': 'Providence, RI', 'DAL': 'Dallas (Love Field), TX', 'ICT': 'Wichita, KS', 'DTW': 'Detroit, MI', 
                'LIR': 'Liberia, Costa Rica', 'SJC': 'San Jose, CA', 'MSY': 'New Orleans, LA', 'SDF': 'Louisville, KY', 
                'OMA': 'Omaha, NE', 'RIC': 'Richmond, VA', 'CRP': 'Corpus Christi, TX', 'EWR': 'New York/Newark, NJ', 
                'ELP': 'El Paso, TX', 'MCI': 'Kansas City, MO', 'PWM': 'Portland, ME', 'SJU': 'San Juan, PR', 
                'SJD': 'Cabo San Lucas/Los Cabos, MX', 'BUF': 'Buffalo/Niagara, NY', 'ABQ': 'Albuquerque, NM', 
                'DCA': 'Washington (Reagan National), DC', 'DSM': 'Des Moines, IA', 'GEG': 'Spokane, WA', 
                'JAX': 'Jacksonville, FL', 'AUS': 'Austin, TX', 'SAN': 'San Diego, CA', 'CLE': 'Cleveland, OH', 
                'OKC': 'Oklahoma City, OK', 'MHT': 'Manchester, NH', 'GRR': 'Grand Rapids, MI', 
                'HAV': 'Havana, Cuba', 'BOS': 'Boston Logan, MA', 'SJO': 'San Jose, Costa Rica', 
                'ALB': 'Albany, NY', 'AMA': 'Amarillo, TX', 'IAD': 'Washington (Dulles), DC', 'HRL': 'Harlingen, TX', 
                'OAK': 'Oakland, CA', 'LAX': 'Los Angeles, CA', 'LBB': 'Lubbock, TX', 'GSP': 'Greenville/Spartanburg, SC', 
                'LIT': 'Little Rock, AR', 'PDX': 'Portland, OR', 'PUJ': 'Punta Cana, DO', 'BNA': 'Nashville, TN', 
                'SNU': 'Santa Clara, Cuba', 'IND': 'Indianapolis, IN', 'LGB': 'Long Beach, CA', 'MKE': 'Milwaukee, WI', 
                'MAF': 'Midland/Odessa, TX', 'TUL': 'Tulsa, OK', 'CVG': 'Cincinnati, OH'}

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
        help="Origin airport code.",
        choices = list(SWA_AIRPORTS.keys()))

    parser.add_argument(
        "--arrive",
        "-a",
        type=str,
        help="Destination airport code.",
        choices = list(SWA_AIRPORTS.keys()))

    parser.add_argument(
        "--departure-date",
        "-dd",
        type=str,
        help="Date of departure flight.")

    parser.add_argument(
        "--return-date",
        "-rd",
        type=str,
        help="Date of return flight.")

    parser.add_argument(
        "--passengers",
        "-p",
        action="store",
        type=str,
        help="Number of passengers.")

    parser.add_argument(
        "--desired-total",
        "-dt",
        type=str,
        help="Ceiling on the total cost of flights.")

    parser.add_argument(
        "--interval",
        "-i",
        type=str,
        default=180,
        help="Refresh time period.")

    args = parser.parse_args()

    return args

def scrape(args):
    """
    Run scraper on Southwest.com.
    If we find a flight that meets our search parameters, send an SMS message.
    """
    while True:
        # PhantomJS is headless, so it doesn't open up a browser.
        browser = webdriver.PhantomJS()
        browser.get("https://www.southwest.com/")

        if args.one_way:
            # Set one way trip with click event.
            one_way_elem = browser.find_element_by_id("trip-type-one-way")
            one_way_elem.click()

        # Set the departing airport.
        depart_airport = browser.find_element_by_id("air-city-departure")
        depart_airport.send_keys(args.depart)

        # Set the arrival airport.
        arrive_airport = browser.find_element_by_id("air-city-arrival")
        arrive_airport.send_keys(args.arrive)

        # Set departure date.
        depart_date = browser.find_element_by_id("air-date-departure")
        depart_date.clear()
        depart_date.send_keys(args.departure_date)

        if not args.one_way:
            # Set return date.
            return_date = browser.find_element_by_id("air-date-return")
            return_date.clear()
            return_date.send_keys(args.return_date)

        # Clear the readonly attribute from the element.
        passengers = browser.find_element_by_id("air-pax-count-adults")
        browser.execute_script("arguments[0].removeAttribute('readonly', 0);", passengers)
        passengers.click()
        passengers.clear()

        # Set passenger count.
        passengers.send_keys(args.passengers)
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

        if not args.one_way:
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
        if real_total <= int(args.desired_total):
            print("[%s] Found a deal. Desired total: $%s. Current Total: $%s." % (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                args.desired_total, str(real_total)))

            client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
            client.messages.create(
                to=TO_NUMBER,
                from_=FROM_NUMBER,
                body="[%s] Found a deal. Desired total: $%s. Current Total: $%s" % (
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    args.desired_total,
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
        time.sleep(int(args.interval) * 60)

if __name__ == "__main__":
    main()
