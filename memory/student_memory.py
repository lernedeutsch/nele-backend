import json
import os


class StudentMemory:

    def __init__(self):
        self.file_path = "data/student_memory.json"

        self.name = None
        self.country = None
        self.city = None
        self.work = None
        self.start_time = None

        self.load()

    def save_answer(self, question, answer):
        answer = answer.lower().strip()

        if "heiße" in answer or "heisse" in answer:
            if "monika" in answer:
                self.name = "Monika"

        if "polen" in answer:
            self.country = "Polen"

        if "heidelberg" in answer:
            self.city = "Heidelberg"

        if "hotel" in answer:
            self.work = "Hotel"

        if "7" in answer or "sieben" in answer:
            self.start_time = "7 Uhr"

        self.save()

    def save(self):
        os.makedirs("data", exist_ok=True)

        data = {
            "name": self.name,
            "country": self.country,
            "city": self.city,
            "work": self.work,
            "start_time": self.start_time
        }

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def load(self):
        if not os.path.exists(self.file_path):
            return

        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.name = data.get("name")
        self.country = data.get("country")
        self.city = data.get("city")
        self.work = data.get("work")
        self.start_time = data.get("start_time")

    def summary(self):
        parts = []

        if self.name:
            parts.append("Sie heißen " + self.name + ".")

        if self.country:
            parts.append("Sie kommen aus " + self.country + ".")

        if self.city:
            parts.append("Sie wohnen in " + self.city + ".")

        if self.work:
            parts.append("Sie arbeiten in einem " + self.work + ".")

        if self.start_time:
            parts.append("Sie fangen um " + self.start_time + " an.")

        if not parts:
            return "Ich weiß noch nicht viel über Sie."

        return "\n".join(parts)
