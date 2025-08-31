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
        return os.environ.get("OMDB_API_KEY")

    def get_entry(self, imdb_id: str, genre: Optional[str] = None):
        content = requests.get(URL, params= {"apiKey": self.api_key, "i": imdb_id}).json()
        genre = genre or content.get("Genre")
        return {
            "title": content.get("Title"),
            "poster": content.get("Poster"),
            "url": f"https://www.imdb.com/title/{imdb_id}/",
            "id": imdb_id,
            "genre": None,
            "rating": None,
            "status": None,
            "director": content.get('director'),
            "year": content.get("Year"),
        }

    def verify_poster(self, entry):
        try:
            requests.head(entry.get("poster"), allow_redirects=True).raise_for_status()
        except Exception as e:
            print(f"Invalid Poster: {entry.get('title')} ({entry.get('id')})")


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
        if db_api.exists(args.imdb_id):
            entry = {"id": args.imdb_id} 
        else:
            entry = imdb_api.get_entry(args.imdb_id, args.genre)
        if args.status: entry["status"] = args.status
        if args.rating: entry["rating"] = args.rating + STAR
        if args.genre: entry["genre"] = sorted([g.strip() for g in args.genre.split(",")])
        db_api.upsert(args.imdb_id, entry)
        db_api.commit(sort_key=lambda entry: entry["title"])
    elif args.command == "update":
        if db_api.exists(args.imdb_id):
            if args.field == 'rating': args.value += STAR
            db_api.upsert(args.imdb_id, {"id": args.imdb_id, args.field: args.value})
        else:
            print(f"Entry not found for ID: {args.imdb_id}")
        db_api.commit(sort_key=lambda entry: entry["title"])
    elif args.command == "verify":
        db_api.verify(imdb_api.verify_poster)



if __name__ == '__main__':
    main()
