#!/usr/bin/env python3
# Created by Tejas — https://github.com/Tejas-pr/claude-editing-style (Apache-2.0; keep this notice, see NOTICE)
"""Download Wikimedia Commons files (<=2880 px) and append credits.
Usage: python3 -I commons.py OUT_DIR name="File:Title.jpg" [name2="File:..."]
       python3 -I commons.py --search "query" [--search "query2"]
"""
import json, os, re, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "video-edit-research/1.0 (personal use)"}
def api(**p):
    p["format"] = "json"
    return json.load(urllib.request.urlopen(urllib.request.Request(
        "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p), headers=UA)))
args = sys.argv[1:]
if args and args[0] == "--search":
    for q in args[1::2]:
        r = api(action="query", generator="search", gsrsearch=q, gsrnamespace=6, gsrlimit=8,
                prop="imageinfo", iiprop="size|extmetadata")
        print("==", q)
        for p in r.get("query", {}).get("pages", {}).values():
            ii = p["imageinfo"][0]
            print("  ", p["title"], ii["width"], ii["height"],
                  ii.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "?"))
        time.sleep(3)
    sys.exit()
out = args[0]; os.makedirs(out, exist_ok=True)
for spec in args[1:]:
    name, title = spec.split("=", 1)
    for attempt in range(4):
        try:
            r = api(action="query", titles=title, prop="imageinfo", iiprop="url|extmetadata|size", iiurlwidth="2880")
            ii = next(iter(r["query"]["pages"].values()))["imageinfo"][0]
            url = ii.get("thumburl") if ii["width"] > 2880 else ii["url"]
            ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
            time.sleep(2)
            open(f"{out}/{name}{ext}", "wb").write(urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read())
            m = ii["extmetadata"]; art = re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "?")).strip()
            line = f"- {name}: {title} | {m.get('LicenseShortName',{}).get('value','?')} | {art[:70]} | {ii['descriptionurl']}"
            open(f"{out}/credits.txt", "a").write(line + "\n"); print(name, ii["width"], ii["height"], ext); break
        except Exception as e:
            print(name, "retry", e); time.sleep(6)
    time.sleep(3)
