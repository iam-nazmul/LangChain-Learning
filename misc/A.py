import os
import io

class LangChainAssistant:
    def __init__(self):
        self.markdown_content = ""  # Store the Markdown content
        self.file_path = None

    def generate_markdown(self, content):
        """Generates the Markdown content."""
        self.markdown_content = content
        return self

    def set_file_path(self, path):
        """Sets the destination file path."""
        self.file_path = path
        return self

    def write_to_file(self):
        """Writes the Markdown content to the specified file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.markdown_content)
            print(f"Markdown content written to: {self.file_path}")
            return True
        except Exception as e:
            print(f"Error writing to file: {e}")
            return False

# Example Usage (Simulated Interaction)
assistant = LangChainAssistant()

# Simulate generating Markdown content (Replace this with your code)
assistant.generate_markdown("# LangChain-এর জন্য নতুনদের গাইড (Professional-এর পথে)\n...") #  Example Markdown content

# Set the file path (Replace this with your desired path)
assistant.set_file_path("LangChainGuide.md")

# Instruct the assistant to write to the file
if assistant.write_to_file():
    print("Operation successful!")
else:
    print("Operation failed.")
