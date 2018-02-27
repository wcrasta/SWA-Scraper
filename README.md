# Flight Prices Scraper

**Screenshots**: http://imgur.com/a/k8JnL

Inspired by [ezekg's swa-dashboard](https://github.com/ezekg/swa-dashboard), I created a command line tool that scrapes various airline websites and displays the current lowest price of airplane tickets. When the current lowest price gets under some threshold that you specify, a text message will be sent to you.

While ezekg's tool was coded in Node, I wanted to use Python + Selenium for a learning experience. If you liked this project, please consider starring this repository.

## Use for this program

Airlines often change their prices on random days/times. By using this program, you'll get a text message notification when the prices have fallen by a certain amount. You can run this script locally, or you can hook it up to Digital Ocean/AWS EC2.

## Installation

1. Clone this repository. `git clone https://github.com/wcrasta/SWA-Scraper.git`
2. Make sure you have Python (code was tested for 3.X, might work with 2.X) and pip. Install required modules by `pip install -r requirements.txt`
3. Download [PhantomJS](http://phantomjs.org/download.html) and put phantomjs.exe in your Scripts folder (Windows) or /usr/bin folder (Mac/Linux).
4. Register for a free account on https://www.twilio.com and get a phone number.
5. Edit config.ini with your Twilio details.

## Usage

Scrapes airline websites according to the interval you set. For best results when using this program, I recommend setting the interval between 2-3 hours. A more frequent interval than that might be excessive. When the price goes under a certain amount, you will be notified via text message.

`--one-way # Optional. By default, a round trip is assumed.`

`--company, -c [company name] # The company to scrape prices from.`

`--depart, -d [airport code] # The airport to depart from.`

`--arrive, -a [airport code] # The airport to arrive in.`

`--departure-date, -dd [date] # Date to leave.`

`--return-date, -rd [date] # Optional. Date to return.`

`--passengers, -p [adults] # Number of passengers.`

`--seniors, -s [seniors] # Number of passengers.`

`--max-price, -m [dollars] # The total fare for one person should be under this amount (in dollars).`

`--interval, -i [minutes] # Optional. How often to scrape the airline's website (in minutes). Default value = 3 hours.`

For more information on the available command line arguments use the following command.

`python app.py --help`

Sample commands:

**NOTE:** Error checking is non-existent, so make sure to enter the commands properly as specified below.

`$ python app.py --company Southwest --depart HOU --arrive MDW --departure-date 05/12/2018 --departure-time AFTER_6PM --return-date 05/14/2018 --return-time ANYTIME --seniors 2 --max-price 215 --interval 30`

`$ python app.py --company Southwest --depart HOU --arrive MDW --departure-date 05/12/2018 --return-date 05/14/2018 --passengers 2 --max-price 215 --interval 30`

`$ python app.py --one-way --company Southwest --depart HOU --arrive MDW --departure-date 05/12/2018 --passengers 2 --max-price 215 --interval 30`

## Improvements / Possible Added Features

Feel free to contribute to this project! There are many improvements that can be made, both in terms of code quality and in terms of whole new ideas that can be implemented. Thoughts I have for new features (may or may not ever be implemented):

1. Add flags so that the user can further filter results (nonstop only, direct only).
2. Add flight details to the notification system (flight numbers, flight times etc).
3. Implement scraping for other websites, making use of nargs and choices attributes for a flag.
4. Add code to SWA Scraper for multiple flights for a trip.
5. Add automated testing.
6. Add some sanity testing for the arguments (Is the number of passengers greater than 0, is the number of passengers below a given threshold, is the interval within a certain range etc).

## Instructions for contributing

1. Fork the repository!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

If you do contribute, be advised that it may take some time to get your PR merged in. If you're interested in being a collaborator, e-mail me. If you don't know how to implement something, but do have an idea that you would like to see implemented, feel free to shoot me an e-mail and I can try to implement it.

## Credits

Author: Warren Crasta (warrencrasta@gmail.com)
Contributor: Kyle Jones (kylejones1310@outlook.com)
Contributor: Joseph Watters
Contributor: Christopher J Marvin