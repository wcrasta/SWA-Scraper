from selenium import webdriver
import sys
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from twilio.rest import TwilioRestClient
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# Change the four following variables appropriately.
# account_sid and auth_token can be found at https://www.twilio.com/console.
account_sid = "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
auth_token = "YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY"
fromNumber = "+1123456789"
toNumber = "+1123456789"

def main(argv):
    # Get the command line arguments.
    argsDict = {}
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
        elif argv[arg] == '--email':        
            argsDict[argv[arg]] = argv[arg + 1]     
        elif argv[arg] == '--password':     
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
            print('Current Lowest Outbound Fare: $' + str(lowestOutboundFare) + '.')
            print('Current Lowest Return Fare: $' + str(lowestReturnFare) + '.')
        else:
            realTotal = lowestOutboundFare
            print('Current Lowest Outbound Fare: $' + str(lowestOutboundFare) + '.')

        # Found a good deal. 
        if realTotal < int(argsDict['--desired-total']):
            # Send a text via Twilio and then stop running.     
            print('Found a deal. Desired total: $' + argsDict['--desired-total'] + '. Current Total: $' + str(realTotal) + '.')
            client = TwilioRestClient(account_sid, auth_token)

            message = client.messages.create(to=toNumber, from_=fromNumber,
                                             body='Found a deal. Desired total: $' + argsDict['--desired-total'] + '. Current Total: $' + str(realTotal)+ '.')
            print('Text message sent!')

            # Send email and then stop running. Requires turning on access to less secure apps to the sending gmail account     
            # See here : https://www.google.com/settings/security/lesssecureapps        
            if '--email' in argsDict and '--password' in argsDict:      
                fromaddr = argsDict['--email']      
                password = argsDict['--password']       
                toaddr = argsDict['--email']        
                msg = MIMEMultipart()       
                msg['From'] = fromaddr      
                msg['To'] = toaddr      
                msg['Subject'] = "Found Flight Deal!"       
                desired_total = argsDict['--desired-total']     
                body = 'Found a deal. Desired total: $' + desired_total + '. Current Total: $' + str(realTotal) + '.'       
                msg.attach(MIMEText(body, 'plain'))     
                        
                server = smtplib.SMTP('smtp.gmail.com', 587)        
                server.starttls()       
                server.login(fromaddr, password)        
                text = msg.as_string()      
                server.sendmail(fromaddr, toaddr, text)     
                server.quit()       
        
                print('Email sent!')        
            else:       
                print('Email and/or password not entered.Please check if email is preceded by --email and password by --password.')
            sys.exit()



        # Keep scraping according to the interval the user specified.
        time.sleep(int(argsDict['--interval']) * 60)

main(sys.argv[1:])
