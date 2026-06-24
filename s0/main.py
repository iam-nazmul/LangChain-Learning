# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI

# load_dotenv()
# model = ChatOpenAI(model="gpt-4o-mini")
# print(model.invoke("এক বাক্যে বলো LangChain কী?").content)


from langchain_ollama import ChatOllama

model = ChatOllama(model="gemma3:4b", temperature=0.7)

prompt ="বাংলায় বলো LangChain কী?"


print(model.invoke(prompt).content)
