from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# মডেল নাম এবং Ollama URL
model_name = "gemma3:4b"
ollama_url = "http://localhost:11434"

# Ollama-এর মাধ্যমে Gemma মডেলটিকে ইনিশিয়ালাইজ করা হচ্ছে
llm = OllamaLLM(model=model_name, base_url=ollama_url)

# একটি প্রম্পট টেমপ্লেট তৈরি করা হচ্ছে
template = """প্রশ্ন: {question}
উত্তর: """
prompt = PromptTemplate(template=template, input_variables=["question"])

# নতুন LangChain pipe-style chain তৈরি করা হচ্ছে (LLMChain এখন deprecated)
chain = prompt | llm

# প্রশ্ন জিজ্ঞাসা করা হচ্ছে
question = "How to create a LangChain agent that can use tools? Provide a step-by-step guide with code snippets and examples. Write in Bangla language."
answer = chain.invoke({"question": question})

print(answer)