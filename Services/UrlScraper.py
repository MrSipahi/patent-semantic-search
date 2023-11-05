from scrapy.crawler import CrawlerProcess
from scrapy.http.response.html import HtmlResponse
from twisted.python.failure import Failure
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError

import scrapy
import json
from rich import print

import os
from dotenv import load_dotenv
from Library.VectorDB import VectorDatabaseProvider
from Library.VectorEmbedding import VectorEmbeddingProvider

import numpy as np


class Crawler(scrapy.Spider):
    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.callback_handler = PatentDataExtractor()
        self.TIMEOUT = 30
        

    name = "crawler"
    start_urls = []
    url_info={}

    def start_requests(self):
        for u in self.start_urls:

            yield scrapy.Request(u, callback=self.callback_handler.parse,
                                 errback=self.errback_httpbin,
                                 dont_filter=True, meta={
                                     'download_timeout': self.TIMEOUT,
                                     'dont_retry': True,
                                     'url_info': self.url_info[u],
                                     }
                                 )
        
    def errback_httpbin(self, failure: Failure):
        id = failure.request.meta["url_info"]["id"]
        if failure.check(DNSLookupError,TimeoutError, TCPTimedOutError):
            self.callback_handler.errback(id, "Timeout Error")

        elif failure.value.response and failure.value.response.status == 404 :
            self.callback_handler.errback(id, "404 Page Not Found")

        elif failure.value.response and (failure.value.response.status == 401 or failure.value.response.status == 403):
            
            if failure.request.meta.get("re-scraped"):
                self.callback_handler.errback(id, "401/403 Status Code")
            else:
                meta = failure.request.meta
                meta["re-scraped"] = True
                yield scrapy.Request(failure.request.url,
                                        callback=self.parse,
                                        errback=self.errback_httpbin,
                                        dont_filter=True,
                                        meta=failure.request.meta,
                                        headers={
                                            'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
                                        }
                                        )
        else:
            self.callback_handler.errback(id, str(failure))

    def closed(self, reason):
        self.callback_handler.finish()

class UrlScraper:
    def __init__(self) -> None:
        self.BASE_URL = "https://patents.justia.com/patent/"

    def start(self):
        
        with open("ids_for_case.json") as f:
            patent_ids = json.load(f)
        url_info_list = self.getUrlInfoList(patent_ids)
        self.scrapeUrl(url_info_list)

    

    def scrapeUrl(self, url_info:dict):
        process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'})

        cr = Crawler
        cr.start_urls = list(url_info.keys())
        cr.url_info = url_info
        process.crawl(cr)
        process.start()

    def getUrlInfoList(self,patent_ids:list) -> dict:

        url_info={}
        for patent_id in patent_ids:
            url = self.BASE_URL + str(patent_id)

            url_info[url] = {
                        "id": patent_id,
                        "title_xpath": '//*[@id="main-content"]/div/div[1]/div/div/div[1]/h1/text()',
                        "abstract_xpath": '//*[@id="abstract"]/p/text()',
                        "paragraph_xpath": '//strong[@class="heading-4" and (contains(., "BACKGROUND") or contains(., "SUMMARY"))]/following-sibling::p[following-sibling::strong[@class="heading-4" and (contains(., "BACKGROUND") or contains(., "SUMMARY"))]]',
                        "paragraph_xpath_alternative": '//strong[@class="heading-4" and (contains(., "BACKGROUND") or contains(., "DESCRIPTION"))]/following-sibling::p[following-sibling::strong[@class="heading-4" and (contains(., "BACKGROUND") or contains(., "DESCRIPTION"))]]',
                        }
            
        return url_info



class PatentDataExtractor:

    def __init__(self) -> None:
        load_dotenv(".env")
        self.vector_model = os.getenv("VECTOR_MODEL", "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb")
        self.vector_embedding = VectorEmbeddingProvider(self.vector_model)

        self.vectorDB = VectorDatabaseProvider()
        self.collection_name = os.getenv("MILVUS_COLLECTION", "bio_patent")
        self.result_data = []


    def parse(self, response: HtmlResponse):
        url_info = response.meta["url_info"]
        id = url_info["id"]
        title = response.xpath(url_info["title_xpath"]).get()
        abstract = response.xpath(url_info["abstract_xpath"]).get()
        p_selector = response.selector.xpath(url_info["paragraph_xpath"]) if len(response.selector.xpath(url_info["paragraph_xpath"])) > 0 else response.selector.xpath(url_info["paragraph_xpath_alternative"])
        paragraph_list = []

        for paragraph in p_selector:
            text = paragraph.xpath("text()").getall()
            paragraph_list.append(" ".join(text))

        if len(paragraph_list) > 0:
            data = {
                "id": id,
                "title": title,
                "abstract": abstract,
                "paragraph": paragraph_list
            }
            paragraph = " ".join(paragraph_list)
            print(paragraph)

            paragraph_vec = self.vector_embedding.encode([paragraph])
            
            entities = [
                [id],
                list(paragraph_vec), 
                [paragraph],  
                [title],
                [abstract],
                [self.vector_model],
            ]

            self.vectorDB.insert(self.collection_name, entities)
            self.result_data.append(data)
            '''
            with open("result.json", "a") as f:
                json.dump(data, f) 
                f.write("\n")
            '''
        else:
            self.errback(id, "Paragraph Not Found")


    def errback(self,id:int, error_description: str):

        data = {
            "id": id,
            "status": "failed",
            "error_description": error_description,
        }

        with open("result.json", "a") as f:
            json.dump(data, f)
            f.write("\n")
    
    def finish(self):
        print("Finish")
        with open("result.json", "a") as f:
            json.dump(self.result_data, f)
            f.write("\n")
