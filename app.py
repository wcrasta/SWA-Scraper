import swaScraper
import myParser

def main():
    """
    Perform searches for the given flight parameters.
    """
    args = myParser.parse()
    
    if args.company == "Southwest":
        real_total = swaScraper.scrape(args)

    # If the user doesn't want text notifications, just print the result to the console.
    if real_total is None:
        exit
    elif args.no_text:
        from datetime import datetime

        print("[%s] Found a deal. Max Total: %s. Current Total: %s." % (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            args.max_price, str(real_total)))
    else:
        # Send a text notifying the user that a lower price was found.
        import notifier
        notifier.sendNotification(real_total, args.max_price)

if __name__ == "__main__":
    main()
