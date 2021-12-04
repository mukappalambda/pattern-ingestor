import concurrent.futures
import json
import sys
from collections import Counter
from itertools import chain

import requests
from bs4 import BeautifulSoup
from gensim import corpora, models, similarities
from gensim.parsing.preprocessing import STOPWORDS
from newsapi import NewsApiClient


def get_lsi_model(corpus, id2word, num_topics: int):
  return models.LsiModel(corpus=corpus, id2word=id2word, num_topics=num_topics)

def get_article_urls(q: str, page: int=1) -> list:

  with open("app.json") as f:
    API_KEY = json.load(f).get("API_KEY")

  api = NewsApiClient(api_key=API_KEY)
  # sources = "abc-news,bbc-news,cnn"
  sources = "cnn"
  response = api.get_everything(q=q,
                                sources=sources,
                                language="en",
                                sort_by="relevancy",
                                page=page)

  articles = response.get("articles")

  return [x.get("url") for x in articles]

def get_one_content(url: str):
  return requests.get(url).content

def get_contents(urls: list[str]):
  with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(get_one_content, url) for url in urls]
  return [f.result() for f in futures]

def extract_texts(contents: list) -> list[str]:
  extracted = []

  for c in contents:
    soup = BeautifulSoup(c, features="html.parser")
    for data in soup.find("body").find_all("div", class_="zn-body__paragraph"):
      extracted.append(data.get_text())

  return [ex for ex in extracted if ex != ""]

if __name__ == "__main__":

  query = sys.argv[1]
  article_urls = get_article_urls(q=query)

  if len(article_urls) == 0:
    print(f"There is no article given the query: {query}. Choose another one.")
    sys.exit(0)

  contents = get_contents(urls=article_urls)
  docs = extract_texts(contents=contents)

  texts = [
    [w for w in doc.lower().split() if w not in STOPWORDS]
    for doc in docs
  ]

  freq = dict(Counter(chain(*texts)))

  texts = [
    [token for token in text if freq[token] > 1]
    for text in texts
  ]

  dictionary = corpora.Dictionary(texts)
  corpus = [dictionary.doc2bow(text) for text in texts]

  lsi = get_lsi_model(corpus=corpus, id2word=dictionary, num_topics=5)

  index = similarities.MatrixSimilarity(lsi[corpus])

  vec_bow = dictionary.doc2bow(query.lower().split())
  vec_lsi = lsi[vec_bow]
  sims = list(set(index[vec_lsi]))

  topN = 10
  sims = sorted(enumerate(sims), key=lambda x: -x[1])
  sims = sims[:topN]

  print(f"\n\n*****\nQuery: {query}\n*****\n\n")
  for doc_pos, doc_score in sims:
    print(f"Score: {doc_score}; sentence: {docs[doc_pos]}")
