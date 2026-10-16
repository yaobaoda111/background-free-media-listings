from media_delivery import Listing, prepare_listing


class FakeClient:
    def __init__(self):
        self.calls = []

    def upload(self, file, filename):
        self.calls.append(("upload", file, filename))
        return {"ok": True, "data": {"id": "img_123"}}

    def background_remove(self, image, format="png"):
        self.calls.append(("background_remove", image, format))
        return {"ok": True, "data": {"id": "cutout_123", "format": format}}


def test_listing_is_uploaded_then_delivered_as_png_cutout():
    client = FakeClient()
    result = prepare_listing(Listing("creator-7", "cover.jpg", "upload-token"), client)
    assert client.calls == [
        ("upload", "upload-token", "cover.jpg"),
        ("background_remove", "img_123", "png"),
    ]
    assert result == {"creator": "creator-7", "filename": "cover.jpg", "image": {"id": "cutout_123", "format": "png"}}
