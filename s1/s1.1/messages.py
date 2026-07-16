from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o")

messages = [
    SystemMessage(content="তুমি একজন সংক্ষিপ্ত উত্তরদাতা। এক লাইনে উত্তর দাও।"),
    HumanMessage(content="পানির রাসায়নিক সংকেত কী?"),
]

response = model.invoke(messages)
print(response)  # এটা একটা AIMessage অবজেক্ট রিটার্ন করবে


messages.append(response)  # AIMessage যোগ হলো
messages.append(HumanMessage(content="তাহলে অক্সিজেনের সংকেত কী?"))

response2 = model.invoke(messages)
print(response2)