import os
import json
import base64
import requests


class LangChainAssistant:
    def __init__(
        self,
        model_name="gemma3:4b",
        ollama_url="http://localhost:11434",
        sd_url="http://127.0.0.1:7860",
        image_dir="images",
    ):
        self.markdown_content = ""
        self.file_path = None
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.sd_url = sd_url
        self.image_dir = image_dir
        os.makedirs(self.image_dir, exist_ok=True)

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
                self.markdown_content += "\n\n---\n\n"  # Closing separator for clarity

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

    def generate_image(self, prompt, index=0):
        """
        Generates an image using a local Stable Diffusion WebUI (AUTOMATIC1111)
        instance, saves it to self.image_dir, and appends a markdown image
        link to self.file_path.
        Requires the WebUI to be launched with the --api flag.
        """
        if not self.file_path:
            print("Error: No file path set. Call set_file_path() first.")
            return self

        try:
            payload = {
                "prompt": prompt,
                "steps": 25,
                "width": 512,
                "height": 512,
            }
            response = requests.post(
                f"{self.sd_url}/sdapi/v1/txt2img",
                json=payload,
                timeout=300,
            )
            response.raise_for_status()
            data = response.json()

            images = data.get("images", [])
            if not images:
                print("No image returned by Stable Diffusion.")
                return self

            # Save the first returned image
            image_b64 = images[0]
            image_bytes = base64.b64decode(image_b64)

            filename = f"image_{index}.png"
            image_path = os.path.join(self.image_dir, filename)
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)

            print(f"Image saved to: {image_path}")

            # Append a markdown image link right after the text section
            md_image_link = f"\n![{prompt[:60]}]({image_path})\n"
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(md_image_link)
            self.markdown_content += md_image_link

            return self

        except requests.exceptions.ConnectionError:
            print(
                "Error: Could not connect to Stable Diffusion WebUI. "
                "Make sure it's running with the --api flag "
                "(e.g. `./webui.sh --api`)."
            )
            return self
        except Exception as e:
            print(f"Error during image generation: {e}")
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


# Words that quit the loop (case-insensitive). A literal Ctrl+Q key
# combo can't be read by input() in a normal terminal -- typing one
# of these and pressing Enter is the practical equivalent.
QUIT_WORDS = {"q", "quit", "exit", ":q", "ctrl+q"}


def main():
    assistant = LangChainAssistant(model_name="gemma3:4b")
    assistant.set_file_path("Output.md")

    print("Type your prompt and press Enter.")
    print(f"Type one of {sorted(QUIT_WORDS)} (then Enter) to quit.\n")

    round_index = 0

    while True:
        try:
            P1 = input("Enter your prompt for the LangChain assistant: ")
        except (EOFError, KeyboardInterrupt):
            # Ctrl+C / Ctrl+D also exit cleanly
            print("\nExiting...")
            break

        p1 = P1.strip()  # Remove leading/trailing whitespace

        if not p1:
            print("Empty prompt, try again.\n")
            continue

        if p1.lower() in QUIT_WORDS:
            print("Quit signal received. Exiting...")
            break

        text_prompt = (
            f"{p1} and attach helping questions section at "
            "the end. write in bangla language."
        )

        assistant.generate_markdown(text_prompt)

        # Generate an accompanying image using the original (untranslated)
        # user prompt, since Stable Diffusion works best with plain
        # descriptive English-style prompts.
        assistant.generate_image(p1, index=round_index)

        # Reset in-memory buffer between runs so it doesn't keep
        # growing unbounded across many prompts in one session.
        assistant.markdown_content = ""

        round_index += 1
        print()  # spacing before next prompt

    print("Operation complete! All responses are in Output.md")


if __name__ == "__main__":
    main()
