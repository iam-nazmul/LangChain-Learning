import os
import requests


class LangChainAssistant:
    def __init__(self, model_name="gemma3:4b", ollama_url="http://localhost:11434"):
        self.markdown_content = ""
        self.file_path = None
        self.model_name = model_name
        self.ollama_url = ollama_url

    def generate_markdown(self, prompt):
        """Generates Markdown content using a local Ollama model."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )
            response.raise_for_status()
            data = response.json()
            self.markdown_content = data.get("response", "")
            return self
        except requests.exceptions.ConnectionError:
            print(
                "Error: Could not connect to Ollama. "
                "Make sure Ollama is running (try `ollama serve` or just open the Ollama app)."
            )
            return self
        except Exception as e:
            print(f"Error during text generation: {e}")
            return self

    def set_file_path(self, path):
        self.file_path = path
        return self

    def write_to_file(self):
        if not self.markdown_content:
            print("No content to write. Did generation succeed?")
            return False
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.markdown_content)
            print(f"Markdown content written to: {self.file_path}")
            return True
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False


# Example Usage
if __name__ == "__main__":
    assistant = LangChainAssistant(model_name="gemma3:4b")

    prompt = "Write a short guide on LangChain for beginners, focusing on key concepts. in bangla language. with proper code snippets and examples. make it engaging and informative."

    assistant.generate_markdown(prompt)
    assistant.set_file_path("LangChainGuide.md")

    if assistant.write_to_file():
        print("Operation successful!")
    else:
        print("Operation failed.")