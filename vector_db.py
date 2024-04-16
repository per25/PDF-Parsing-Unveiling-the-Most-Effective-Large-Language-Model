import os
from dotenv import load_dotenv

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()
DB_PERSISTENCE_PATH = os.getenv("DB_PERSISTENCE_PATH")

embedding_function = OpenAIEmbeddings()

db = Chroma(persist_directory=DB_PERSISTENCE_PATH, embedding_function=embedding_function)

query = "A nice query"

docs = db.similarity_search(query)

print(docs[0].page_content)

