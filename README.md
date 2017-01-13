# SWA-Scraper

![Terminal1](http://i.imgur.com/mmBcNf5.png)
![Text](http://i.imgur.com/4U6F8hN.png)
![Terminal2](http://i.imgur.com/nYumGWO.png)

Inspired by [ezekg's swa-dashboard](https://github.com/ezekg/swa-dashboard), I created a command line tool that scrapes Southwest Airlines' website and displays the current lowest price of airplane tickets. When the current lowest price gets under some threshold that you specify, a text message will be sent to you.

While ezekg's tool was coded in Node, I wanted to use Python + Selenium for a learning experience. If you liked this project, please consider starring this repository.

## Use for this program

Airlines often change their prices on random days/times. By using this program, you'll get a text message notification when the prices have fallen by a certain amount. Southwest is known to normally have the cheapest rates, so this program scrapes data from Southwest. You can run this script locally, or you can hook it up to Digital Ocean/AWS EC2.

## Installation

1. Clone this repository. `git clone https://github.com/wcrasta/SWA-Scraper.git`
2. Make sure you have Python (code was tested for 3.X, might work with 2.X) and pip. Install required modules by `pip install -r requirements.txt`
3. Download [PhantomJS](http://phantomjs.org/download.html) and put phantomjs.exe in your Scripts folder (Windows) or /usr/bin folder (Mac/Linux).
4. Register for a free account on https://www.twilio.com and get a phone number.
5. Edit app.py with your twilio details.

## Usage
Scrapes the Southwest website according to the interval you set. For best results when using this program, I recommend setting the interval between 2-3 hours. A more frequent interval than that might be excessive. When the price goes under a certain amount, you will be notified via text message.

`--one-way # Optional. By default, a round trip is assumed.`

`--from [airport code] # The airport to depart from.`

`--to [airport code] # The airport to arrive in.`

`--departure-date [date] # Date to leave.`

`--return-date [date] # Optional. Date to return.`

`--passengers [adults] # Number of passengers.`

`--desired-total [dollars] # The total fare for one person should be under this amount (in dollars). `

`--interval [minutes] # Optional. How often to scrape Southwest's website (in minutes). Default value = 3 hours.`

**Sample commands:**

**NOTE:** Error checking is non-existent, so make sure to enter the commands properly as specified below.

`$ python app.py --from HOU --to MDW --departure-date 05/12 --return-date 05/14 --passengers 2 --desired-total 215 --interval 30`

`$ python app.py --one-way  --from HOU --to MDW --departure-date 05/12 --passengers 2 --desired-total 215 --interval 30`

## Improvements/Possible Added Features

Feel free to contribute to this project! There are many improvements that can be made, both in terms of code quality and in terms of whole new ideas that can be implemented. Thoughts I have for new features (may or may not ever be implemented):

1. Add flags so that the user can specify what time of day he/she wants to travel.

## Instructions for contributing

1. Fork the repository!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

If you do contribute, be advised that it may take some time to get your PR merged in. If you're interested in being a collaborator, e-mail me. If you don't know how to implement something, but do have an idea that you would like to see implemented, feel free to shoot me an e-mail and I can try to implement it.

## Credits

Author: Warren Crasta (warrencrasta@gmail.com)
