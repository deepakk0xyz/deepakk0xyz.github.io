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

    def get(self, index):
        return self.db.get("entries")[index]

    def find(self, db_id):
        for index, entry in enumerate(self.db.get("entries", [])):
            if db_id in entry.get("id"):
                return index

    def upsert(self, db_id, new_entry):
        index = self.find(db_id)
        if index:
            entry = self.get(index)
            print("Exisiting Entry:")
            self.show(entry)

            print("New Entry:")
            self.show(entry | new_entry)

            for key, value in new_entry.items():
                entry[key] = value
        else:
            print("New Entry:")
            self.show(new_entry)
            self.db["entries"].append(new_entry)

    def verify(self):
        ids = set()
        for index, entry in enumerate(self.db.get("entries")):
            db_id = entry.get("id")

            if db_id in ids:
                print(f"Found Duplicate Entry: {entry.get('title')} ({db_id})")
                del self.db.get("entries")[index]
                continue

            ids.add(db_id)
            try:
                requests.head(entry.get("poster"), allow_redirects=True).raise_for_status()
            except Exception as ex:
                print(f"Invalid Poster: {entry.get('title')} ({db_id}): ", ex)


    def fix(self, entry):
        pass

    def commit(self, sort_key):
        if input("Confirm Commit? (y/n) ") == "n":
            print("Skipped Commit.")
            return
        self.db["entries"] = sorted(self.db.get("entries"), key=sort_key)
        with open(self.filename, "w") as file:
            yaml.dump(self.db, file, allow_unicode=True, sort_keys=False, Dumper=IndentDumper)

    def show(self, entry):
        print(yaml.dump(entry, allow_unicode=True, sort_keys=False, Dumper=IndentDumper))
