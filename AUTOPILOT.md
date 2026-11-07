# AUTOPILOT: make and publish ONE crypto news Short (run by a scheduled Claude session)

Owner: Daniel. Goal: one English 9:16 explainer Short every 3 hours for beginners (YouTube Shorts + TikTok + Telegram).
You are a fresh session. Work alone, do not ask questions. Report the result in your final message (Hebrew, 3 lines).

## Hard rules
- Facts: use only facts confirmed by **at least 2 different publishers** (WebSearch + WebFetch). If a number is unclear, leave it out or say "about". Attribute unconfirmed things ("analysts suspect", "reports say").
- No investment advice, no price predictions, no "buy/sell". Educational tone. Always end with the outro foot "Reports as of <Mon D>. Not financial advice."
- Do not repeat a topic already covered in the last 24h: read `requests/*.json` (titles/heads) first. Pick a DIFFERENT story or angle.
- If there is no solid new story, make an evergreen beginner video (e.g. "3 signs of a crypto scam", "what is a stop-loss", "how to read the fear & greed index") using the `checklist`, `gauge`, `question` icons.
- Never touch any Make scenario other than the temporary relay you create. Never touch Team 7 (7997171). Never publish twice for the same video. Never put secrets anywhere.
- Never spend money. Everything here is free.
- Time guard: if the current date (Asia/Jerusalem) is after 2026-11-09 03:30, do nothing and say so.

## Steps
1. `add_repo` danielnet-il/starnet-video with push access, clone it to /home/claude/starnet-video (follow the tool's instructions; one clone only), `git pull`.
2. Research the topic (see rules). Today's date: use the real current date.
3. Write `requests/<YYYY-MM-DD>_<HHMM>_<slug>.json`:
```json
{"title":"<=95 chars, curiosity but honest","caption":"1-2 sentences","hashtags":"#crypto #bitcoin #cryptonews","publish":true,
 "scenes":[{"head":"SHORT HEADLINE","icon":"chartdown","big":"-6%","sub":"BITCOIN IN ONE DAY","narration":"<=125 chars, spoken English, numbers spelled out, 'E T F' / 'A I' with spaces"}]}
```
   6-8 scenes, total 45-65 s (about 12-14 s of speech per 40 words). Last scene: `"icon":"outro","foot":"Reports as of Nov 7. Not financial advice."`.
   **Allowed icons for new stories (generic):**
   - `chartdown` / `chartup` is `chartdown` with `"dir":"up"`: fields `big` (<=14 chars), `sub` (<=48). Price move.
   - `liquidation`: `big`, `sub`. Leveraged traders wiped out.
   - `outflow`: `big`, `sub`. Institution/ETF money flows (building with arrows leaving).
   - `gauge`: `value` 0-100, `sub`. Fear & Greed or any index.
   - `checklist`: `items` (3 short strings). Rules, tips, signs.
   - `question`: coin with a question mark. Hook or open question.
   - `link`: stocks vs bitcoin falling together (labels fixed: NASDAQ 100 / BITCOIN), field `sub`.
   - `outro`: last scene.
   Do NOT use the Binance-specific icons (hack, record, laptop, paused, frozen, safe, scam, lesson, exchange, key, risk, wallet, scales, compare): they contain fixed Binance text.
4. Validate locally (fast, no render): `PAYLOAD="$(cat requests/<file>.json)" EXAMPLE=x python3 prepare.py` must pass. Do NOT build locally anymore (the sandbox only has the weak Piper voice).
5. Render happens on GitHub with the neural voice (Andrew): commit and `git push origin main` ONLY the new `requests/<name>.json` (end the commit message with the attribution lines). Workflow `render-on-push` renders (~5-6 min) and commits `videos/<same name>.mp4`. Poll every 30 s (max 15 min): `curl -sfI https://raw.githubusercontent.com/danielnet-il/starnet-video/main/videos/<name>.mp4` until 200, then `git pull`. If the video never appears, check `gh run list -R danielnet-il/starnet-video -L 3`, report, and stop (no publish). Check duration 40-75 s with ffprobe.
6. Hand to Team 7 through a temporary Make relay (team 3182763; Make MCP tools):
   - `scenarios_create` with `scheduling {"type":"on-demand"}` and this blueprint (build the `data` string with `json.dumps` of `{"video_url":RAW_URL,"viral_title":title,"caption":caption,"hashtags":hashtags}`, then embed it as a JSON string):
```json
{"name":"TEMP relay: publish","flow":[{"id":1,"module":"http:ActionSendData","version":3,"parameters":{"handleErrors":false,"useNewZLibDeCompress":true},"mapper":{"url":"https://hook.eu1.make.com/18ce45i5wqaow7sm5u7fuytpj1ehvui4","serializeUrl":false,"method":"post","headers":[],"qs":[],"bodyType":"raw","contentType":"application/json","data":"<json string>","parseResponse":false,"timeout":30,"shareCookies":false,"rejectUnauthorized":true,"followRedirect":true,"useQuerystring":false,"gzip":true,"useMtls":false,"followAllRedirects":false}}],"metadata":{"version":1,"scenario":{"roundtrips":1,"maxErrors":3,"autoCommit":true,"autoCommitTriggerLast":true,"sequential":false,"confidential":false,"dataloss":false,"dlq":false,"freshVariables":false},"designer":{"orphans":[]},"zone":"eu1.make.com"}}
```
   - If `scenarios_create` fails validation, `scenarios_update` it with the same blueprint (the numeric `timeout` and `serializeUrl:false` matter), then `scenarios_activate`, then `scenarios_run` ONCE (status 1 = relay posted).
   - Check Team 7: `executions_list` scenarioId 7997171, newest entry should become `SUCCESS` (7 operations) within about a minute. If it ERRORs, do not retry the publish; report it.
   - ALWAYS (even on failure): `scenarios_deactivate` then `scenarios_delete` the relay.
7. Final message (Hebrew): the title, the topic, Team 7 result, the raw URL. If the org is paused (`organizations_get` 9290516 isPaused true) say so and stop; do not spend.
