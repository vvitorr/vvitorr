import os
import re
import requests

CID = os.environ["SPOTIFY_CLIENT_ID"]
SEC = os.environ["SPOTIFY_CLIENT_SECRET"]
RT = os.environ["SPOTIFY_REFRESH_TOKEN"]
N = 5


def get_token():
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "refresh_token", "refresh_token": RT},
        auth=(CID, SEC),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def top(kind, token):
    r = requests.get(
        f"https://api.spotify.com/v1/me/top/{kind}",
        headers={"Authorization": f"Bearer {token}"},
        params={"time_range": "long_term", "limit": N},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["items"]


token = get_token()
artists = top("artists", token)
tracks = top("tracks", token)

lines = ["vvitorr# show spotify top --range 12m", "", "  TOP ARTISTS", ""]
lines += [f"  [{i:02d}] {a['name']}" for i, a in enumerate(artists, 1)]
lines += ["", "  TOP TRACKS", ""]
lines += [f"  [{i:02d}] {t['name']} - {t['artists'][0]['name']}" for i, t in enumerate(tracks, 1)]
lines += ["", "vvitorr#"]

block = "<!--SPOTIFY:START-->\n```bash\n" + "\n".join(lines) + "\n```\n<!--SPOTIFY:END-->"

md = open("README.md", encoding="utf-8").read()
md = re.sub(r"<!--SPOTIFY:START-->.*?<!--SPOTIFY:END-->", lambda _: block, md, flags=re.S)
open("README.md", "w", encoding="utf-8").write(md)
