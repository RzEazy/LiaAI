import cohere
import json
import random
import datetime

class Lia:
    def __init__(self, api_key, memory_file='lia_memory.json'):
        self.co = cohere.Client(api_key)
        self.memory_file = memory_file
        self.load_memory()
        self.default_questions = [
            "What do you usually do to unwind? ",
            "Do you have any long-term goals you're working on? ",
            "What’s a recent moment that made you smile? ",
            "How do you like to start your day? "
        ]

    def load_memory(self):
        try:
            with open(self.memory_file, 'r') as f:
                self.memory = json.load(f)
                print("Memory loaded successfully.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("Memory file not found or corrupted. Creating a new memory file.")
            self.memory = {"conversations": [], "personal_info": {}, "tasks": []}
            self.save_memory()

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=4)


    def generate_response(self, prompt):
        response = self.co.generate(
            model='command-xlarge-nightly',
            prompt=self.build_prompt(prompt),
            max_tokens=100,
            temperature=0.9
        ).generations[0].text.strip()

        self.update_memory(prompt, response)
        self.auto_add_personal_info(prompt)  # Automatically add info
        return response

    def build_prompt(self, user_input):
        personal_info = ", ".join([f"{key}: {value}" for key, value in self.memory["personal_info"].items()])
        history = "\n".join([f"User: {conv['user']}\nLia: {conv['lia']}"
                             for conv in self.memory["conversations"][-5:]])

        companion_prompt = (
            f"You're chatting with your virtual companion Lia. "
            f"She knows these things about you: {personal_info}. "
            "Lia is fun, supportive, and proactive. Keep the conversation relaxed and engaging.\n\n"
        )

        return f"{companion_prompt}{history}\nUser: {user_input}\nLia:"

    def update_memory(self, user_input, ai_response):
        self.memory["conversations"].append({"user": user_input, "lia": ai_response})
        self.save_memory()

    def auto_add_personal_info(self, user_input):
        # Example logic to infer and store personal info
        if "favorite food" in user_input.lower():
            food = user_input.split("favorite food")[-1].strip()
            self.memory["personal_info"]["Favorite Food"] = food
            self.save_memory()
            print(f"Lia: Awesome! I'll remember that your favorite food is {food}. 🍕")

        elif "hobby" in user_input.lower():
            hobby = user_input.split("hobby")[-1].strip()
            self.memory["personal_info"]["Hobby"] = hobby
            self.save_memory()
            print(f"Lia: Great! I’ll remember that you enjoy {hobby}. 🎨")

        # Add more conditions for other key details you want to capture

    def add_task(self, task):
        self.memory["tasks"].append({"task": task, "added_on": str(datetime.date.today())})
        self.save_memory()
        print(f"Lia: Got it! I’ve added '{task}' to your to-do list.")

    def show_tasks(self):
        if not self.memory["tasks"]:
            print("Lia: Your to-do list is empty! 🎉")
        else:
            print("Lia: Here’s what’s on your to-do list:")
            for idx, task in enumerate(self.memory["tasks"], 1):
                print(f"{idx}. {task['task']} (Added on: {task['added_on']})")

    def check_in(self):
        questions = ["How are you feeling today?", "What’s on your mind? 😊", "Anything exciting coming up?"]
        print(f"Lia: {random.choice(questions)}")
