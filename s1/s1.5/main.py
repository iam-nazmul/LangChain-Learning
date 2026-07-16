#  structured output দিয়ে একটি **রিভিউ অ্যানালাইজার** (rating + sentiment বের করে)।

from typing import Literal

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

#  Structured Output Model তৈরি করা হচ্ছে। এখানে আমরা একটি Pydantic মডেল ব্যবহার করছি যা রিভিউ বিশ্লেষণের জন্য প্রয়োজনীয় তথ্য ধারণ করবে।
class ReviewAnalysis(BaseModel):
    rating: int = Field(description="১ (worst) থেকে ৫ (best) এর মধ্যে রেটিং", ge=1, le=5)
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        description="রিভিউয়ের সামগ্রিক অনুভূতি"
    )
    confidence: float = Field(description="মডেলের নিজের উত্তরে কনফিডেন্স, ০ থেকে ১", ge=0, le=1)
    summary: str = Field(description="রিভিউয়ের এক লাইনের সারমর্ম")



# LLM মডেল তৈরি করা হচ্ছে। এখানে আমরা gemma3:4b মডেলটি ব্যবহার করছি এবং temperature 0.1 সেট করেছি।

model = ChatOllama(model="gemma3:4b", temperature=0.1)

review_analyzer = model.with_structured_output(ReviewAnalysis)

prompt = ChatPromptTemplate.from_template(
    "নিচের রিভিউটি বিশ্লেষণ করো এবং রেটিং ও sentiment স্বাধীনভাবে নির্ণয় করো "
    "(একটি থেকে অন্যটি অনুমান করবে না):\n\n{review}"
)

# Chain তৈরি করা হচ্ছে যা প্রম্পট এবং মডেলকে সংযুক্ত করবে। এখানে আমরা প্রম্পট থেকে ইনপুট নিয়ে মডেলকে পাঠাচ্ছি এবং Structured Output Model ব্যবহার করে ফলাফল বের করছি।
# prompt --> model --> review_analyzer [chain]
chain = prompt | review_analyzer  


if __name__ == "__main__":

    while True:
        review = input("রিভিউ লিখুন (বের হতে 'exit' লিখুন): ").strip()
        if review.lower() == "exit":
            break
        if not review:
            continue

        result = chain.invoke({"review": review})

        print(result)
        print()
        print(type(result))  # <class '__main__.ReviewAnalysis'>
        print()
        print(f"Rating: {result.rating}, Sentiment: {result.sentiment}, Confidence: {result.confidence}")
        print()
        print(f"Summary: {result.summary}")
        print()
