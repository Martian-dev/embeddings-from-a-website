# # import os
# import pickle
#
# # from custom_crawl import crawl_urls
#
# # import time
#
# # from firecrawl import FirecrawlApp, ScrapeOptions
#
# # FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
#
# # app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)
#
#
# # sources = [
# #     "https://www.airtel.in/broadband-faq/",
# #     "https://www.airtel.in/dth-faqs/",
# #     "https://www.airtel.in/airtel-xstream-faqs/",
# #     "https://www.airtel.in/postpaid-faqs/",
# # ]
#
#
# def main():
#     # resulting_markdown = []
#     # for source in sources:
#     #     resulting_markdown.append(
#     #         app.crawl_url(
#     #             source, limit=2, scrape_options=ScrapeOptions(formats=["markdown"])
#     #         )
#     #     )
#     #     time.sleep(6)
#     # url_list = ["https://example.com", "https://another.com/page"]
#     # markdown_pages = crawl_urls(sources, max_depth=2)
#
#     # # Save to files or process further
#     # for i, md in enumerate(markdown_pages):
#     #     with open(f"page_{i+1}.md", "w", encoding="utf-8") as f:
#     #         f.write(md)
#     #
#     file_path = "data.pkl"
#
#     with open(file_path, "rb") as f:
#         result = pickle.load(f)
#         # print(len(result))
#         i = 0
#         for r in result:
#             with open(
#                 f"/home/vaibhav/Files/dev/projects/rag-chatbot/dataPrep/documents/page_{i+1}.md",
#                 "w",
#                 encoding="utf-8",
#             ) as a:
#                 a.write(r)
#             i += 1
#
#     print("donee")
#
#
# if __name__ == "__main__":
#     main()

import csv
import glob
import json
import os
from uuid import uuid4

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tqdm import tqdm

# Constants
SOURCE_DIR = "./documents/"
OUTPUT_CSV = "database.csv"
DIMENSIONS = 768

# Embedding model
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",  # Maps to text-embedding-004
    google_api_key=os.environ["GOOGLE_API_KEY"],
)

# Chunker
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n## ", "\n### ", "\n", ". "],
)


def process_markdown_files(directory: str, output_csv: str):
    files = glob.glob(os.path.join(directory, "*.md"))
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id", "resourceURL", "content", "embedding"]
        )
        writer.writeheader()

        for file_path in tqdm(files, desc="Processing files"):
            loader = TextLoader(file_path)
            docs = loader.load()
            content = docs[0].page_content

            lines = content.strip().split("\n")
            if not lines:
                continue

            resource_url = lines[0].strip()
            content_body = "\n".join(lines[1:]).strip()
            chunks = text_splitter.split_text(content_body)

            embed_and_write_chunks(chunks, resource_url, writer)


def embed_and_write_chunks(chunks, resource_url, writer):
    embeddings = embedding_model.embed_documents(chunks)

    for chunk, vector in zip(chunks, embeddings):
        writer.writerow(
            {
                "id": str(uuid4()),
                "resourceURL": resource_url,
                "content": chunk,
                "embedding": json.dumps(vector),
            }
        )


if __name__ == "__main__":
    process_markdown_files(SOURCE_DIR, OUTPUT_CSV)
