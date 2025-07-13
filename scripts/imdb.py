#! /usr/bin/env nix-shell
#! nix-shell -i python3 -p python3 python313Packages.requests

import os
import sys
import json
import requests
import argparse

URL = "https://omdbapi.com"
STAR = "⭐"

def get_imdb(imdb_id: str, api_key: str):
    content = requests.get(URL, params= {"apiKey": api_key, "i": imdb_id}).json()
    return {
        "title": content.get("Title"),
        "poster": content.get("Poster"),
        "url": f"https://www.imdb.com/title/{imdb_id}",
        "genre": content.get("Genre"),
        "director": content.get("Director"),
        "rating": "",
        "status": "",
        "year": content.get("Year"),
    }

def parse_args():
    parser = argparse.ArgumentParser(prog="IMDB",
            description="Add IMDB Movie To JSON File")
    parser.add_argument("filename")
    parser.add_argument("imdb_id")
    parser.add_argument("api_key")
    parser.add_argument("-r", "--rating")
    parser.add_argument("-s", "--status")
    return parser.parse_args()

def show_entry(entry):
    for key, value in entry.items():
        print(key, ": ", value)

def find_entry(entries, imdb_id):
    for index, entry in enumerate(entries):
        if imdb_id in entry["url"]:
            return index

def update_entry(filename, entry, imdb_id):
    with open(filename, "r") as file:
        db = json.load(file)
        index = find_entry(db["entries"], imdb_id)
        if index:
            print("Updating Existing Entry.")
            db["entries"][index] = entry
        else:
            print("Creating New Entry.")
            db["entries"].append(entry)
        db["entries"] = sorted(db["entries"], key=lambda entry: entry["title"])

    with open(filename, "w") as file:
        json.dump(db, file, indent="\t", ensure_ascii=False)

def customize(entry):
    if input(f"Do you want to change the genre? (Y/N)").lower() == "y":
        genre = input("Please Enter Genre:")
        if genre:   entry["genre"] = genre.split(",")
        else:   del entry["genre"]

    if input(f"Do you want to keep the director? (Y/N)").lower() == "n":
        del entry["director"]

    return entry

def main():
    args = parse_args()
    entry = get_imdb(args.imdb_id, args.api_key)
    entry["rating"] = f"{args.rating}{STAR}" if args.rating else "Unwatched"
    entry["status"] = args.status or "Unwatched"

    show_entry(entry)
    entry = customize(entry)
    print("Final Entry:")
    show_entry(entry)

    if input("Confirm DB Update (Y/N):").lower() == "y":
        update_entry(args.filename, entry, args.imdb_id)



if __name__ == '__main__':
    main()
