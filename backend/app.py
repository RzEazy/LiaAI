from core.lia_main import LiaMain

# Initialize Lia with your Cohere API key
lia = LiaMain(
    api_key="doeM32W2so3ubfYYs673lmiOmUzwN15weKfB68bj",
    memory_file="lia_memory.json"
)

def chat():
    print("LiaAI - Modular Cyber Assistant")
    print("Ask me anything - I can chat, run commands, or query system security!")
    print("Type 'exit', 'quit', 'bye', or 'goodbye' to exit.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
            print("Lia: Peace!")
            break

        response = lia.process_input(user_input)
        print("Lia:", response)
        print()  # Add spacing for readability

if __name__ == "__main__":
    chat()
