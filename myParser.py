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
        "--departure-time",
        "-dt",
        type=str,
        choices=["BEFORE_NOON", "NOON_TO_6PM", "AFTER_6PM", "ANYTIME"],
        help="Time period of departure flight.")

    parser.add_argument(
        "--return-date",
        "-rd",
        type=str,
        required=True,
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
        help="Number of passengers.")

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
        help="Maximum total cost of flights.")

    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        required=True,
        default=180,
        help="Refresh time period.")

    parser.add_argument(
        "--no-text",
        "-nt",
        action="store_true",
        help="If present, no text message will get sent on cheaper flight")

    args = parser.parse_args()

    return args