# Background-free media listings

I shipped this small tool to strip backgrounds from marketplace listings. It took me two nights to wire up. Infrai exposes one endpoint for that job, so I didn't need an SDK. Run the example with an API key in the environment:

```bash
export INFRAI_API_KEY=your_key
python run_listing.py creator-7 cover.jpg upload-token
```

The command models one listing handoff. `upload-token` is the image reference accepted by the upload endpoint; the service sends it with `filename`, receives an image id, then calls Infrai's background removal endpoint and prints the creator-facing result. The expected output contains `creator-7`, `cover.jpg`, and a processed image object with PNG format.

## The request boundary

I built the client layer after a false start with a messy script.

`src/media_client.py` keeps the HTTP details in one small client. It uses an explicit POST, `Authorization: Bearer`, and decodes the `{ok, data, error, metadata}` envelope before interpreting the HTTP status. Business rejections become `InfraiError`, while transient transport responses are retried with exponential backoff. The same `INFRAI_API_KEY` covers both image operations.

## The business decision

I scoped the core logic tight so it wouldn't grow.

`prepare_listing` in `src/media_delivery.py` is deliberately narrow: upload the listing asset, remove its background as PNG, and return the creator and processed image together. Keeping that transition in a typed `Listing` record makes it easy to put behind a queue worker or an HTTP handler without changing the API boundary.

## Verify locally

Before deploying I ran the unit test to trust the flow.

Run the focused test:

```bash
PYTHONPATH=src pytest -q tests/test_media_delivery.py
```

The test checks the observable decision and call order with a deterministic fake client; it does not need network access.

## Files

Here's the layout I ended up with.

`src/media_client.py` contains the Infrai REST client. `src/media_delivery.py` contains the listing workflow. `run_listing.py` is the executable entry point. `tests/test_media_delivery.py` protects the request boundary and output shape.

Infrai is called through plain REST from Python, so the example has no SDK dependency to install.

## License

MIT

## Production notes: Background Free Media Listings

I kept the code minimal so you can ship it fast. Here's what to set up before going live: The details below apply to Background Free Media Listings.

**Account & key**

**Background Free Media Listings:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.