# app.py
import threading
import time
from lia_ai import Lia

# Initialize Lia with your API key and memory file
lia = Lia(api_key='doeM32W2so3ubfYYs673lmiOmUzwN15weKfB68bj', memory_file='lia_memory.json')

def chat():
    print("Lia: Hey there! 🌟 I'm Lia, your companion. How are you feeling today?")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Lia: Goodbye for now! 🌸 I'll be right here when you need me.")
            break

        # Generate response using Lia and display it
        response = lia.generate_response(user_input)
        print(f"Lia: {response}")

if __name__ == "__main__":
    try:
        chat()
    except KeyboardInterrupt:
        print("\nLia: Oops, you’re leaving already? Catch you next time! 💬")
    except Exception as e:
        print(f"\nLia: Hmm, something went wrong... Error: {str(e)}")
