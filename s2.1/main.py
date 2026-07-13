from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import CSVLoader
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import DirectoryLoader

model = ChatOllama(model="gemma3:4b")


loader = TextLoader("data.txt")
documents = loader.load()


loader = PyPDFLoader("file.pdf")
documents = loader.load()



loader = CSVLoader(file_path="data.csv")
documents = loader.load()



loader = WebBaseLoader("https://www.glascutr.com")
documents = loader.load()



loader = DirectoryLoader("./docs", glob="**/*.pdf")
documents = loader.load()



# UnstructuredFileLoader: auto-detects the file type (PDF, DOCX, PPTX, HTML, EML...)
# Requires: pip install "unstructured[all-docs]"
from langchain_community.document_loaders import UnstructuredFileLoader

loader = UnstructuredFileLoader("file.pdf")
documents = loader.load()

# mode="elements" splits the file into pieces (Title, NarrativeText, Table...)
loader = UnstructuredFileLoader("file.pdf", mode="elements")
documents = loader.load()





# NotionDirectoryLoader: loads a Notion workspace export (Settings > Export content > Markdown & CSV)
# Unzip the export and point the loader at the folder
from langchain_community.document_loaders import NotionDirectoryLoader

loader = NotionDirectoryLoader("notion_export/")
documents = loader.load()

# NotionDBLoader: loads pages live from a Notion database via the API
# Requires a Notion integration token (https://www.notion.so/my-integrations)
# and sharing the database with the integration
from langchain_community.document_loaders import NotionDBLoader

loader = NotionDBLoader(
    integration_token="secret_xxx",
    database_id="your-database-id",
    request_timeout_sec=30,
)
documents = loader.load()



# GoogleDriveLoader: loads Google Docs/Sheets/files from Drive
# Requires: pip install langchain-google-community google-api-python-client google-auth-oauthlib
# Needs OAuth credentials.json (Google Cloud Console) — token is cached after first login
from langchain_google_community import GoogleDriveLoader

loader = GoogleDriveLoader(
    folder_id="your-folder-id",              # load everything in a folder
    # document_ids=["doc-id-1", "doc-id-2"], # or specific Google Docs
    # file_ids=["file-id"],                  # or specific files (PDF etc.)
    credentials_path="credentials.json",
    token_path="token.json",
    recursive=False,
)
documents = loader.load()



# SlackDirectoryLoader: loads a Slack workspace export
# (Workspace Settings > Import/Export Data > Export) — point it at the zip file
from langchain_community.document_loaders import SlackDirectoryLoader

loader = SlackDirectoryLoader(
    zip_path="slack_export.zip",
    workspace_url="https://your-workspace.slack.com",  # optional: adds message URLs to metadata
)
documents = loader.load()