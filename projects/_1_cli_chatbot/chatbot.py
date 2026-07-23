from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


def main():
    model = ChatOllama(model="gemma3:4b")
    history = [SystemMessage(content="You are a helpful assistant.")]

    print("CLI Chatbot (gemma3:4b via Ollama)")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        history.append(HumanMessage(content=user_input))

        print("Bot: ", end="", flush=True)
        full_response = ""
        for chunk in model.stream(history):
            print(chunk.content, end="", flush=True)
            full_response += chunk.content
        print("\n")

        history.append(AIMessage(content=full_response))


if __name__ == "__main__":
    main()
