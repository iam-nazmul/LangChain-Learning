import os
import json
import requests


class LangChainAssistant:
    def __init__(
        self,
        model_name="gemma3:4b",
        ollama_url="http://localhost:11434",
        sd_model_id="runwayml/stable-diffusion-v1-5",
        image_dir="images",
    ):
        self.markdown_content = ""
        self.file_path = None
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.sd_model_id = sd_model_id
        self.image_dir = image_dir
        self.sd_pipe = None  # Lazy-loaded on first image request
        os.makedirs(self.image_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # TEXT GENERATION (Ollama)
    # ------------------------------------------------------------------
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

            header = f"\n\n---\n\n## Prompt: {prompt}\n\n"

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
                self.markdown_content += "\n\n---\n\n"

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

    # ------------------------------------------------------------------
    # IMAGE GENERATION (local Stable Diffusion 1.5 via diffusers, CPU)
    # ------------------------------------------------------------------
    def _load_sd_pipeline(self):
        """Lazily loads the SD1.5 pipeline only once, on first use."""
        if self.sd_pipe is not None:
            return

        print("Loading Stable Diffusion 1.5 (first run downloads ~2GB, then cached)...")
        import torch
        from diffusers import StableDiffusionPipeline

        self.sd_pipe = StableDiffusionPipeline.from_pretrained(
            self.sd_model_id,
            torch_dtype=torch.float32,  # CPU doesn't benefit from fp16
            safety_checker=None,        # skip extra model load to save RAM
        )
        self.sd_pipe.to("cpu")

        # Lower memory footprint at the cost of some speed -- helpful
        # on machines with under 8GB RAM.
        self.sd_pipe.enable_attention_slicing()

        print("Stable Diffusion pipeline ready.\n")

    def generate_image(self, prompt, index=0, steps=20, size=512):
        """
        Generates an image locally using Stable Diffusion 1.5 on CPU,
        saves it to self.image_dir, and appends a markdown image link
        to self.file_path. Slow on CPU (expect ~1-5 min per image on
        low-RAM machines) but fully offline, no server required.
        """
        if not self.file_path:
            print("Error: No file path set. Call set_file_path() first.")
            return self

        try:
            self._load_sd_pipeline()

            print(f"Generating image for: '{prompt}' (this may take a few minutes on CPU)...")
            result = self.sd_pipe(
                prompt,
                num_inference_steps=steps,
                width=size,
                height=size,
            )
            image = result.images[0]

            filename = f"image_{index}.png"
            image_path = os.path.join(self.image_dir, filename)
            image.save(image_path)

            print(f"Image saved to: {image_path}")

            md_image_link = f"\n![{prompt[:60]}]({image_path})\n"
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(md_image_link)
            self.markdown_content += md_image_link

            return self

        except Exception as e:
            print(f"Error during image generation: {e}")
            return self

    # ------------------------------------------------------------------
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


QUIT_WORDS = {"q", "quit", "exit", ":q", "ctrl+q"}


def main():
    assistant = LangChainAssistant(model_name="gemma3:4b")
    assistant.set_file_path("Output.md")

    print("Type your prompt and press Enter.")
    print(f"Type one of {sorted(QUIT_WORDS)} (then Enter) to quit.\n")
    print("Note: image generation runs on CPU and can take 1-5 minutes per image.\n")

    round_index = 0

    while True:
        try:
            P1 = input("Enter your prompt for the LangChain assistant: ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        p1 = P1.strip()

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

        # Use the original (untranslated) prompt for image generation --
        # SD1.5 was trained mostly on English captions and works best with
        # plain descriptive English-style prompts.
        assistant.generate_image(p1, index=round_index)

        assistant.markdown_content = ""
        round_index += 1
        print()

    print("Operation complete! All responses are in Output.md")


if __name__ == "__main__":
    main()
