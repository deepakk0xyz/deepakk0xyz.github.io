import sys
import re
import requests
import bs4
import yaml
import argparse
from db import DbApi

URL = "https://www.goodreads.com/book/show/{id}"
SERIES_REGEX = re.compile(r"^https://www\.goodreads\.com/series/")
STAR = "⭐"

class GoodreadsApi:
    def __init__(self):
        pass

    def get_series(self, soup):
        series = soup.find("a", href=SERIES_REGEX)
        if series:
            return series.text

    def get_entry(self, goodreads_id: str):
        url = URL.format(id=goodreads_id)
        response = requests.get(url)
        soup = bs4.BeautifulSoup(response.content, features="html.parser")
        return {
            "title": soup.find("h1", attrs={"data-testid": "bookTitle"}).text,
            "series": self.get_series(soup),
            "author": soup.find("span", attrs={"data-testid": "name"}).text,
            "poster": soup.find("img", class_="ResponsiveImage").get("src"),
            "url": url,
            "genre": None,
            "rating": None,
            "status": None,
            "year": soup.find("p", attrs={"data-testid": "publicationInfo"}).text.split(" ")[-1],
            "id": goodreads_id,
        }

    def verify_poster(self, entry):
        try:
            requests.head(entry.get("poster"), allow_redirects=True).raise_for_status()
        except Exception as e:
            print(f"Invalid Poster: {entry.get('title')} ({entry.get('id')})")

def parse_args():
    parser = argparse.ArgumentParser(prog="Goodreads",
            description="Add Goodreads Entry To DB File")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("goodreads_id")
    add_parser.add_argument("-r", "--rating", choices=["1", "2", "3", "4", "5"])
    add_parser.add_argument("-s", "--status", choices=["Currently Reading", "Read", "Want To Read"])
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

def sort_key(entry):
    if entry.get("series"):
        return entry.get("series")
    return entry.get("title")

if __name__ == '__main__':
    args = parse_args()
    goodreads_api = GoodreadsApi()
    db_api = DbApi("books")

    if args.command == "add":
        if db_api.exists(args.goodreads_id):
            print("Found Existing Entry")
            entry = {"id": args.goodreads_id} 
        else:
            entry = goodreads_api.get_entry(args.goodreads_id)

        if args.status: entry["status"] = args.status
        if args.rating: entry["rating"] = args.rating + STAR
        if args.genre: entry["genre"] = sorted([g.strip() for g in args.genre.split(",")])
        
        db_api.upsert(args.goodreads_id, entry)
        db_api.commit(sort_key)
    elif args.command == "update":
        if db_api.exists(args.goodreads_id) is not None:
            if args.field == 'rating': args.value += STAR
            db_api.upsert(args.goodreads_id, {"id": args.goodreads_id, args.field: args.value})
        else:
            print(f"Entry not found for ID: {args.imdb_id}")
        db_api.commit(sort_key)
    elif args.command == "verify":
        db_api.verify(goodreads_api.verify_poster)
