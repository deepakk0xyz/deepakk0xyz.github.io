#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python313Packages.requests

import re
import os
import sys
import json
import requests
import argparse
import subprocess
from typing import Optional

URL = "https://omdbapi.com"
STAR = "⭐"

class ImdbApi:
    def __init__(self):
        self.api_key = self.get_api_key()

    def get_api_key(self):
        process = subprocess.run(["pass", "show", "api/omdb"], capture_output=True)
        return process.stdout.decode("utf-8").split("\n")[0]

    def get_entry(self, imdb_id: str, genre: Optional[str]):
        content = requests.get(URL, params= {"apiKey": self.api_key, "i": imdb_id}).json()
        genre = genre or content.get("Genre")
        return {
            "title": content.get("Title"),
            "poster": self.verify_poster(content.get("Poster")),
            "url": f"https://www.imdb.com/title/{imdb_id}/",
            "genre": genre.split(", ") if genre else [],
            "director": content.get("Director"),
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


class DbApi:
    def __init__(self, db_type):
        self.type = db_type
        with open(self.filename) as file:
            self.db = json.load(file)

    @property
    def filename(self):
        dirname = os.path.dirname(__file__)
        filepath = os.path.join(dirname, f"../src/media/{self.type}/{self.type}.json")
        return os.path.realpath(filepath)

    def get_entry(self, index):
        return self.db.get("entries")[index]

    def find_entry(self, imdb_id):
        for index, entry in enumerate(self.db.get("entries", [])):
            if imdb_id in entry.get("url"):
                return index

    def update_entry(self, imdb_id, new_entry):
        index = self.find_entry(imdb_id)
        if index:
            entry = self.get_entry(index)
            print("Exisiting Entry:")
            self.show_entry(entry)

            # Preserve poster, rating and status if not provided or invalid.
            new_entry["poster"] = new_entry.get("poster") or entry.get("poster")
            new_entry["status"] = new_entry.get("status") or entry.get("status")
            new_entry["rating"] = new_entry.get("rating") or entry.get("rating")

            print("New Entry:")
            self.show_entry(new_entry)

            if input("Confirm Update? (y/n) ") != "n":
                self.db.get("entries")[index] = new_entry
            else:
                print("Skipped Update.")
        else:
            print("New Entry:")
            self.show_entry(new_entry)
            if not new_entry.get("poster"): 
                new_entry = self.fix_poster(new_entry)
            self.db["entries"].append(new_entry)

    def refresh_all(self, imdb_api):
        for entry in self.db.get("entries"):
            print("Refreshing: ", entry.get("title"))
            imdb_id = self.get_imdb_id(entry)
            print("ID: ", imdb_id)
            new_entry = imdb_api.get_entry(imdb_id)

            for key, value in entry.items():
                if key == "genre": continue
                entry[key] = new_entry.get(key) or value

    def verify_all(self):
        ids = set()
        for index, entry in enumerate(self.db.get("entries")):
            imdb_id = self.get_imdb_id(entry)

            if imdb_id in ids:
                print(f"Found Duplicate Entry: {entry.get('title')} ({imdb_id})")
                del self.db.get("entries")[index]
                continue

            ids.add(imdb_id)
            try:
                requests.head(entry.get("poster"), allow_redirects=True).raise_for_status()
            except Exception as ex:
                print(f"Invalid Poster: {entry.get('title')} ({imdb_id}): ", ex)
                self.fix_poster(entry)


    def fix_poster(self, entry):
        if input("Poster is Invalid. Do you want to add a custom poster? (y/n)") == "y":
            entry["poster"] = input("Enter Poster URL: ")
        return entry

    def commit(self):
        if input("Confirm Commit? (y/n) ") == "n":
            print("Skipped Commit.")
            return
        self.db["entries"] = sorted(self.db.get("entries"), key=lambda entry: entry["title"])
        with open(self.filename, "w") as file:
            json.dump(self.db, file, indent="\t", ensure_ascii=False)

    def show_entry(self, entry):
        for key, value in entry.items():
            print(key, ": ", value)

    def get_imdb_id(self, entry):
        match = re.search(r'(tt\d{7,8})', entry.get("url"))
        return match.group(1) 

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
