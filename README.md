# starnet-video
Automatic 9:16 explainer videos (black/white line-art animation + free offline English voice).

Flow: Make -> `repository_dispatch` (event type `render-video`) -> GitHub Actions renders -> public release asset ->
(if `publish: true`) POSTs `{video_url, viral_title, caption, hashtags}` to the Make hook stored in the secret `MAKE_PUBLISH_HOOK`.

Request body (client_payload):
```json
{"event_type":"render-video","client_payload":{
  "title":"...", "caption":"...", "hashtags":"#crypto #Shorts", "publish": false,
  "scenes":[{"head":"BINANCE GOT HACKED","icon":"hack","narration":"..."}]
}}
```
Allowed icons: question, exchange, key, risk, wallet, scales, compare, outro, hack, record, laptop, paused, frozen, safe, scam, lesson.
Scene timing is computed from the voice. Test without publishing: Actions -> render-video -> Run workflow.
Local build: `pip install playwright && playwright install chromium && python3 build.py examples/binance_hack.json out.mp4`
