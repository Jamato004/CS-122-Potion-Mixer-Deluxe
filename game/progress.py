import os, json

class LevelProgress:
    def __init__(self, path="data/levels/level_stats.json"):
        self.path = path
        self.data = {"levels": {}}  # "1": {"best_retries": 2, "completed": true}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.data = json.load(f)

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def get_level_info(self, level):
        return self.data["levels"].get(str(level), {})

    def get_best_retries(self, level):
        return self.get_level_info(level).get("best_retries")

    def is_completed(self, level):
        return bool(self.get_level_info(level).get("completed"))

    def record_completion(self, level, retries):
        key = str(level)
        info = self.data["levels"].get(key, {})
        best = info.get("best_retries")
        if best is None or retries < best:
            info["best_retries"] = retries
        info["completed"] = True
        self.data["levels"][key] = info
        self.save()
