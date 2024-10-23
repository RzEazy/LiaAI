# app.py
import threading
import time
from lia_ai import Lia  # Your assistant class

# Initialize the assistant with your API key and memory file location
lia = Lia(api_key='T1Bc1ugk1s3scjMkgKCqXDk6l8utMuBcHABskBoR', memory_file='lia_memory.json')

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
