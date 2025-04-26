import cohere
import json
import random
import datetime
import subprocess
import sys
import os
import pip

class Lia:
    def __init__(self, api_key, memory_file='lia_memory.json'):
        self.co = cohere.Client(api_key)
        self.memory_file = memory_file
        self.load_memory()

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
        # Check if the prompt is a system command
        if "run command" in prompt.lower():
            command = prompt.split("run command")[-1].strip()
            return self.run_command(command)  # Call run_command method

        # If it's not a system command, generate an AI response
        response = self.co.generate(
            model='command',
            prompt=self.build_prompt(prompt),
            max_tokens=500,  # Changed from 10000 to 500
            temperature=1.0
        ).generations[0].text.strip()

        self.update_memory(prompt, response)
        return response

    def build_prompt(self, user_input):
        # Include full personal info (Optional)
        personal_info = ", ".join([f"{key}: {value}" for key, value in self.memory["personal_info"].items()])

        # Include FULL conversation history
        history = "\n".join([f"User: {conv['user']}\nLia: {conv['lia']}"
                             for conv in self.memory["conversations"]])

        companion_prompt = (
            f"You're Lia, a friendly and supportive AI companion.\n"
            f"You remember these facts about the user: {personal_info}.\n"
            f"Always use past conversations to stay consistent and personal.\n"
            f"Be empathetic, engaging, and keep your tone relaxed.\n\n"
        )

        return f"{companion_prompt}{history}\nUser: {user_input}\nLia:"

    def update_memory(self, user_input, ai_response):
        self.memory["conversations"].append({"user": user_input, "lia": ai_response})
        self.save_memory()

    def run_command(self, command):
        """ Run a system command and return the result. """
        try:
            # Use subprocess to run the command
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return f"Command executed successfully\n{result.stdout}"
            else:
                return f"Error while executing command:\n{result.stderr}"
        except Exception as e:
            return f"An error occurred while trying to execute the command: {str(e)}"

    def install_package(self, package_name):
        """ Install a Python package using pip. """
        try:
            result = subprocess.run(f"pip install {package_name}", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return f"Package {package_name} installed successfully:\n{result.stdout}"
            else:
                return f"Error while installing package {package_name}:\n{result.stderr}"
        except Exception as e:
            return f"An error occurred while installing {package_name}: {str(e)}"

    def open_file(self, file_path):
        """ Open a file and return its contents. """
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"An error occurred while opening the file: {str(e)}"
