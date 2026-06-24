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
        streaming chunks and APPENDING each one to the file as it arrives
        (existing file content is preserved, not overwritten).
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

            # Add a separator + the prompt as a heading, so each run
            # is clearly delimited in the merged file.
            header = f"\n\n---\n\n## Prompt: {prompt}\n\n"

            # "a" = append mode. Creates the file if it doesn't exist yet,
            # and adds to the end if it does -- never truncates.
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(header)
                f.flush()
                self.markdown_content += header
                

                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                    except json.JSONDecodeError:
                        continue

                    text_piece = chunk.get("response", "")
                    if text_piece:
                        print(text_piece, end="", flush=True)
                        f.write(text_piece)
                        f.flush()
                        self.markdown_content += text_piece

                    if chunk.get("done", False):
                        break
                self.markdown_content += "\n\n---\n\n"  # Add a closing separator for clarity
            print(f"\n\nFinished streaming. Content appended to: {self.file_path}")
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
        """Kept for compatibility; appends in-memory content to file."""
        if not self.markdown_content:
            print("No content to write. Did generation succeed?")
            return False
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(self.markdown_content)
            print(f"Markdown content appended to: {self.file_path}")
            return True
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False


# Example Usage
if __name__ == "__main__":
    assistant = LangChainAssistant(model_name="gemma3:4b")

    # prompt1 = "Write a a tutorial on LangChain for beginners, focusing on key concepts. in bangla language. with proper code snippets and examples. make it engaging and informative."

    # p1 = "How to get/ create YOUR_OPENAI_API_KEY?\n\n"
    # p1 = 'I want to learn LangChain with  model_name="gemma3:4b", ollama_url="http://localhost:11434" \n\n'
    P1 = input("Enter your prompt for the LangChain assistant: ")
    p1 = P1.strip()  # Remove leading/trailing whitespace
    prompt = f"{p1} provide step by step instructions with screenshots and examples. make it engaging and informative. attach proper code snippets where relevant. attach helping questions section at the end. write in bangla language." 

    assistant.set_file_path("Output.md")
    assistant.generate_markdown(prompt)

    print("Operation complete!")