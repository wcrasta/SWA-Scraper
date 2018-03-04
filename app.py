import swaScraper
import notifier
import myParser

def main():
    """
    Perform searches for the given flight parameters.
    """
    args = myParser.parse()
    
    if args.company == "Southwest":
        real_total = swaScraper.scrape(args)

    notifier.sendNotification(real_total, args.max_price)

if __name__ == "__main__":
    main()