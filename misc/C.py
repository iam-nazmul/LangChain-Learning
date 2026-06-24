import os
import io
from transformers import pipeline

class LangChainAssistant:
    def __init__(self):
        self.markdown_content = ""
        self.file_path = None
        self.model_name = "google/gemma-3b-it"
        self.generator = None

    def generate_markdown(self, prompt):
        """Generates Markdown content using the Gemma model."""
        try:
            self.generator = pipeline("text-generation", model=self.model_name)
            results = self.generator(prompt, max_length=200, num_return_sequences=1)
            self.markdown_content = results[0]['generated_text']
            return self
        except Exception as e:
            print(f"Error during text generation: {e}")
            return self

    def set_file_path(self, path):
        self.file_path = path
        return self

    def write_to_file(self):
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)  # Handle nested directories
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.markdown_content)
            print(f"Markdown content written to: {self.file_path}")
            return True
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False

# Example Usage (Simulated Interaction)
assistant = LangChainAssistant()

# Prompt for Gemma
prompt = "Write a short guide on LangChain for beginners, focusing on key concepts."

# Generate Markdown content
assistant.generate_markdown(prompt)

# Set file path
assistant.set_file_path("~/Desktop/LangChainGuide.md")

# Write to file
if assistant.write_to_file():
    print("Operation successful!")
else:
    print("Operation failed.")
