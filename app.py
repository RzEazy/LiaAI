# app.py
import threading
import time
from lia_ai import Lia  

# Initialize the assistant with your API key and memory file location
# Head to cohere's official website and sign-in to get your own api key.

lia = Lia(api_key='Provide your own cohere api key', memory_file='lia_memory.json')

def chat():
    print("Lia: Hey there!  I'm here to assist and chat with you. What’s on your mind?")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Lia: See you later! Have a great day!")
            break

        # Generate response using Lia and display it
        response = lia.generate_response(user_input)
        print(f"Lia: {response}")

if __name__ == "__main__":
    try:
        chat()
    except KeyboardInterrupt:
        print("\n: Oops, you’re leaving already? Catch you next time!")
    except Exception as e:
        print(f": Something went wrong. Error: {str(e)}")
