import argparse

def parse():
    """
    Parse the command line for search parameters.
    """
    parser = argparse.ArgumentParser(description='Process command line arguments')

    parser.add_argument(
        "--one-way",
        action="store_true",
        help="If present, the search will be limited to one-way tickets.")

    parser.add_argument(
        "--company",
        "-c",
        type=str,
        required=True,
        choices=["Southwest"],
        help="Airline company name.")

    parser.add_argument(
        "--depart",
        "-d",
        type=str,
        required=True,
        help="Origin airport code.")

    parser.add_argument(
        "--arrive",
        "-a",
        type=str,
        required=True,
        help="Destination airport code.")

    parser.add_argument(
        "--departure-date",
        "-dd",
        type=str,
        required=True,
        help="Date of departure flight.")
    
    parser.add_argument(
        "--flightnum",
        "-fn",
        type=str,
        help="Specific flight number to check if desired")

    parser.add_argument(
        "--departure-time",
        "-dt",
        type=str,
        choices=["BEFORE_NOON", "NOON_TO_6PM", "AFTER_6PM", "ANYTIME"],
        help="Time period of departure flight.")

    parser.add_argument(
        "--return-date",
        "-rd",
        type=str,
        help="Date of return flight.")
    
    parser.add_argument(
        "--return-time",
        "-rt",
        type=str,
        choices=["BEFORE_NOON", "NOON_TO_6PM", "AFTER_6PM", "ANYTIME"],
        help="Time period of return flight.")

    parser.add_argument(
        "--passengers",
        "-p",
        action="store",
        type=int,
        help="Number of passengers (who are not seniors).")

    parser.add_argument(
        "--points",
        "-pt",
        action="store_true",
        help="If present, search by points instead of dollars.")

    parser.add_argument(
        "--seniors",
        "-s",
        action="store",
        type=int,
        help="Number of passengers who are seniors.")

    parser.add_argument(
        "--max-price",
        "-m",
        type=int,
        required=True,
        help="The total fare for one person should be under this amount (in dollars or points).")

    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        help="How often to scrape the airline's website (in minutes).")

    parser.add_argument(
        "--no-text",
        "-nt",
        action="store_true",
        help="Do not send a text message when a lower price is found.")

    args = parser.parse_args()

    return args
