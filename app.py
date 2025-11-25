from lia_ai import Lia

lia = Lia(
    api_key="doeM32W2so3ubfYYs673lmiOmUzwN15weKfB68bj",
    memory_file="lia_memory.json"
)

def chat():
    print()

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye","goodbye"]:
            print("Lia: Peace!")
            break

        response = lia.generate_response(user_input)
        print("Lia:", response)

if __name__ == "__main__":
    chat()
