import re
import os
import yaml
import requests

class IndentDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

class DbApi:
    def __init__(self, db_type):
        self.type = db_type
        with open(self.filename) as file:
            self.db = yaml.safe_load(file)

    @property
    def filename(self):
        dirname = os.path.dirname(__file__)
        filepath = os.path.join(dirname, f"../src/media/{self.type}/{self.type}.yaml")
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
            yaml.dump(self.db, file, allow_unicode=True, sort_keys=False, Dumper=IndentDumper)

    def show_entry(self, entry):
        print(yaml.dump(entry, allow_unicode=True, sort_keys=False, Dumper=IndentDumper))

    def get_imdb_id(self, entry):
        match = re.search(r'(tt\d{7,8})', entry.get("url"))
        return match.group(1) 
