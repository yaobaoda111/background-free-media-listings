import json
import sys

from src.media_client import InfraiClient
from src.media_delivery import Listing, prepare_listing


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: python run_listing.py CREATOR FILENAME IMAGE_REFERENCE")
    listing = Listing(sys.argv[1], sys.argv[2], sys.argv[3])
    print(json.dumps(prepare_listing(listing, InfraiClient()), indent=2))


if __name__ == "__main__":
    main()
