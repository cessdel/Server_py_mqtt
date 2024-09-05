# storage.py
import json
import os

class FileStorage:
    def __init__(self, filename="config.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            self.save({})

    def save(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f)

    def load(self):
        with open(self.filename, 'r') as f:
            return json.load(f)

    def setItem(self, key, value):
        data = self.load()
        data[key] = value
        self.save(data)

    def getItem(self, key):
        data = self.load()
        return data.get(key, None)
