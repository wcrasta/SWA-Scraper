# SWA-Scraper

![Terminal](http://i.imgur.com/7hiOKJC.png)
![Text](http://i.imgur.com/sFksFBC.png)

Inspired by [https://github.com/ezekg/swa-dashboard](ezekg's swa-dashboard), I created a command line tool that scrapes Southwest Airlines' website and displays the current lowest price of airplane tickets. When the current lowest price gets under some threshold that you specify, a text message will be sent to you.

While ezekg's tool was coded in Node, I wanted to use Python + Selenium.

## Use for this program

Airlines often change their prices on random days/times. By using this program, you'll get a text message notification when the prices have fallen by a certain amount. Southwest is known to normally have the cheapest rates, so this program scrapes data from Southwest.

## Installation

1. Clone this repository. `git clone https://github.com/wcrasta/SWA-Scraper.git`
2. Make sure you have Python 3+ and pip. Install required modules (if needed) by `pip install -r requirements.txt`
3. If needed, download [PhantomJS](http://phantomjs.org/download.html) and put phantomjs.exe in your Scripts folder
4. Register for a free account on https://www.twilio.com and get a phone number.
5. Edit app.py with your twilio details.

## Usage
Scrapes the Southwest website according to the interval you set. When the price goes under a certain amount, you will be notified via text message.

`--one-way # Optional. By default, a round trip is assumed.`

`--from [-f] # The airport to depart from.`

`--to [-t] # The airport to arrive in.`

`--departure-date [-dd] # Date to leave.`

`--return-date [-rd] # Optional. Date to return.`

`--passengers [-p] # Number of passengers.`

`--desired-total [-dt] # The total fare for one person should be under this amount (in dollars). `

`--interval [-i] # How often to scrape Southwest's website (in minutes)`

Sample commands:

`$ python app.py --from HOU --to MDW --departure-date 05/12 --return-date 05/14 --passengers 2 --desired-total 215 --interval 30`

`$ python app.py --one-way  --from HOU --to MDW --departure-date 05/12 --return-date 05/14 --passengers 2 --desired-total 215 --interval 30`

## Improvements/Possible Added Features

Feel free to contribute to this project! There are many improvements that can be made, both in terms of code quality and in terms of whole new ideas that can be implemented. Thoughts I have for new features (may or may not ever be implemented):

1. Add flags so that the user can specify what time of day he/she wants to travel.

## Instructions for contributing

1. Fork the repository!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

If you don't know how to implement something, but do have an idea that you would like to see implemented, feel free to shoot me an e-mail and I can try to implement it.

## Credits

Author: Warren Crasta (warrencrasta@gmail.com)

ezekg -- For the idea.
