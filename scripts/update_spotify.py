import datetime
import html
import os
import re
import requests

N = 5
BADGE = (
    "https://img.shields.io/badge/{}-LAST_6_MONTHS-39FF14"
    "?style=for-the-badge&logo=spotify&logoColor=black&labelColor=0d1117"
)


def get_token():
    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={"grant_type": "refresh_token", "refresh_token": os.environ["SPOTIFY_REFRESH_TOKEN"]},
        auth=(os.environ["SPOTIFY_CLIENT_ID"], os.environ["SPOTIFY_CLIENT_SECRET"]),
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def top(kind, token):
    r = requests.get(
        f"https://api.spotify.com/v1/me/top/{kind}",
        headers={"Authorization": f"Bearer {token}"},
        params={"time_range": "medium_term", "limit": N},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["items"]


def short(text, n=20):
    return text if len(text) <= n else text[: n - 1] + "…"


def cover(item):
    images = item.get("images") or item.get("album", {}).get("images") or []
    if not images:
        return ""
    return images[1]["url"] if len(images) > 1 else images[0]["url"]


def cell(rank, item, title, sub):
    link = item["external_urls"]["spotify"]
    src = cover(item)
    pic = f'<img src="{src}" width="110" height="110" alt="{html.escape(title)}"/>' if src else ""
    return (
        '<td align="center" valign="top" width="130">'
        f"<sub>{rank:02d}</sub><br/>"
        f'<a href="{link}">{pic}</a><br/>'
        f"<b>{html.escape(short(title))}</b><br/>"
        f"<sub>{html.escape(short(sub, 22))}</sub>"
        "</td>"
    )


def table(cells):
    return '<table align="center"><tr>' + "".join(cells) + "</tr></table>"


def render(artists, tracks):
    a_cells = [
        cell(i, a, a["name"], (a.get("genres") or ["artist"])[0])
        for i, a in enumerate(artists, 1)
    ]
    t_cells = [
        cell(i, t, t["name"], t["artists"][0]["name"])
        for i, t in enumerate(tracks, 1)
    ]
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return "\n".join(
        [
            "<!--SPOTIFY:START-->",
            '<div align="center">',
            "",
            f'<img src="{BADGE.format("TOP_ARTISTS")}" alt="Top artists"/>',
            "",
            table(a_cells),
            "",
            f'<img src="{BADGE.format("TOP_TRACKS")}" alt="Top tracks"/>',
            "",
            table(t_cells),
            "",
            f"<sub>updated {today} UTC</sub>",
            "",
            "</div>",
            "<!--SPOTIFY:END-->",
        ]
    )


if __name__ == "__main__":
    token = get_token()
    block = render(top("artists", token), top("tracks", token))
    md = open("README.md", encoding="utf-8").read()
    md = re.sub(r"<!--SPOTIFY:START-->.*?<!--SPOTIFY:END-->", lambda _: block, md, flags=re.S)
    open("README.md", "w", encoding="utf-8").write(md)