from dataclasses import dataclass
from typing import Any, Dict

from src.media_client import InfraiClient


@dataclass(frozen=True)
class Listing:
    creator: str
    filename: str
    source_image: str


def prepare_listing(listing: Listing, client: InfraiClient) -> Dict[str, Any]:
    uploaded = client.upload(listing.source_image, listing.filename)
    image_id = uploaded["data"]["id"]
    processed = client.background_remove(image_id, format="png")
    return {"creator": listing.creator, "filename": listing.filename, "image": processed["data"]}
