import os
import json
import requests


class LangChainAssistant:
    def __init__(self, model_name="gemma3:4b", ollama_url="http://localhost:11434"):
        self.markdown_content = ""
        self.file_path = None
        self.model_name = model_name
        self.ollama_url = ollama_url

    def generate_markdown(self, prompt):
        """
        Generates Markdown content using a local Ollama model,
        streaming chunks and writing each one to file as it arrives.
        """
        if not self.file_path:
            print("Error: No file path set. Call set_file_path() first.")
            return self

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True,
                },
                timeout=120,
                stream=True,
            )
            response.raise_for_status()

            # Open the file once, write each chunk as it streams in
            with open(self.file_path, "w", encoding="utf-8") as f:
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                    except json.JSONDecodeError:
                        continue

                    text_piece = chunk.get("response", "")
                    if text_piece:
                        # Print to console so you can watch it generate live
                        print(text_piece, end="", flush=True)
                        # Write chunk to file immediately
                        f.write(text_piece)
                        f.flush()
                        # Keep a full copy in memory too
                        self.markdown_content += text_piece

                    if chunk.get("done", False):
                        break

            print(f"\n\nFinished streaming. Markdown written to: {self.file_path}")
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
        """
        Kept for compatibility / re-saving the full accumulated content
        (not needed for the normal streaming flow, since chunks are
        already written live in generate_markdown()).
        """
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

    # prompt = "Write a short guide on LangChain for beginners, focusing on key concepts."
    # prompt = "Write a short guide on LangChain for beginners, focusing on key concepts. in bangla language. with proper code snippets and examples. make it engaging and informative."
    prompt = "Create a diagram to illustrate the LangChain architecture."

    # assistant.set_file_path("LangChainGuide.md")
    assistant.set_file_path("Output.md")
    assistant.generate_markdown(prompt)

    print("Operation complete!")
