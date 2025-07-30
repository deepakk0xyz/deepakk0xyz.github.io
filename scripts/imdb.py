#!/usr/bin/env python3

import re
import os
import sys
import yaml
import requests
import argparse
import subprocess
from typing import Optional
from db import DbApi

URL = "https://omdbapi.com"
STAR = "⭐"


class ImdbApi:
    def __init__(self):
        self.api_key = self.get_api_key()

    def get_api_key(self):
        process = subprocess.run(["pass", "show", "api/omdb"], capture_output=True)
        return process.stdout.decode("utf-8").split("\n")[0]

    def get_entry(self, imdb_id: str, genre: Optional[str] = None):
        content = requests.get(URL, params= {"apiKey": self.api_key, "i": imdb_id}).json()
        genre = genre or content.get("Genre")
        director = content.get("Director")
        if not director or director == "N/A" or input(f"Do you want to keep director ({director})? (y/n)") != "y":
            director = None
        return {
            "title": content.get("Title"),
            "poster": self.verify_poster(content.get("Poster")),
            "url": f"https://www.imdb.com/title/{imdb_id}/",
            "id": imdb_id,
            "genre": genre.split(", ") if genre else [],
            "director": director,
            "rating": None,
            "status": None,
            "year": content.get("Year"),
        }

    def verify_poster(self, poster):
        try:
            requests.head(poster, allow_redirects=True).raise_for_status()
            return poster
        except Exception as e:
            pass
        return None



def parse_args():
    parser = argparse.ArgumentParser(prog="IMDB",
            description="Add IMDB Entry To DB File")
    parser.add_argument("type", choices=["anime", "films", "shows"])
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("imdb_id")
    add_parser.add_argument("-r", "--rating", choices=["1", "2", "3", "4", "5"])
    add_parser.add_argument("-s", "--status", choices=["Ongoing", "Watched", "Unwatched"])
    add_parser.add_argument("-g", "--genre")
    add_parser.set_defaults(command="add")

    refresh_parser = subparsers.add_parser("refresh")
    refresh_parser.set_defaults(command="refresh")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.set_defaults(command="verify")

    update_parser = subparsers.add_parser("update")
    update_parser.add_argument("imdb_id")
    update_parser.add_argument("field")
    update_parser.add_argument("value")
    update_parser.set_defaults(command="update")

    return parser.parse_args()

def main():
    args = parse_args()
    imdb_api = ImdbApi()
    db_api = DbApi(args.type)

    if args.command == "add":
        entry = imdb_api.get_entry(args.imdb_id, args.genre)
        entry["status"] = args.status
        entry["rating"] = args.rating + STAR if args.rating else None

        db_api.update_entry(args.imdb_id, entry)
    elif args.command == "refresh":
        db_api.refresh_all(imdb_api)
    elif args.command == "verify":
        db_api.verify_all()
    elif args.command == "update":
        index = db_api.find_entry(args.imdb_id)
        if not index:
            print("Entry Not Found.")
            return
        entry = db_api.get_entry(index)
        entry[args.field] = args.value.split(",") if "," in args.value else args.value
        db_api.update_entry(args.imdb_id, entry)


    db_api.commit()


if __name__ == '__main__':
    main()
