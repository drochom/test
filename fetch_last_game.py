#!/usr/bin/env python3
"""Fetch the last chess.com game for a given username and save it as PGN."""

import json
import sys
import urllib.request
from datetime import datetime

USERNAME = "PlayLikeSmyslov"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; chess-game-fetcher/1.0)"}


def get(url: str) -> dict:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def main():
    archives = get(f"https://api.chess.com/pub/player/{USERNAME}/games/archives")
    if not archives.get("archives"):
        print("No game archives found.", file=sys.stderr)
        sys.exit(1)

    # Try from most recent month backwards until we find games
    for archive_url in reversed(archives["archives"]):
        data = get(archive_url)
        games = data.get("games", [])
        if games:
            last_game = games[-1]
            pgn = last_game.get("pgn", "")
            if pgn:
                output_path = "last_game.pgn"
                with open(output_path, "w") as f:
                    f.write(pgn)
                print(f"Saved last game to {output_path}")
                # Print summary
                white = last_game.get("white", {})
                black = last_game.get("black", {})
                print(f"  White: {white.get('username')} ({white.get('rating')})")
                print(f"  Black: {black.get('username')} ({black.get('rating')})")
                print(f"  Result: {white.get('result')} / {black.get('result')}")
                ts = last_game.get("end_time")
                if ts:
                    print(f"  Date: {datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M UTC')}")
                print(f"  URL: {last_game.get('url')}")
                return
            break

    print("No games with PGN data found.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
