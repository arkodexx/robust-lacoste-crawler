import json
from urllib.parse import urlencode
import scrapy
from scrapy.http import JsonRequest
from scrapy.exceptions import CloseSpider

class CrawlerSpider(scrapy.Spider):
    name = "crawler"
    allowed_domains = ["www.lacoste.com", "algolia.net", "cu0iyshi42-dsn.algolia.net"]

    QUERIES = ["Polo", "Sneakers", "T-Shirts"] # you can add or remove what you want
    LANGUAGE = "products_de_de" # Or you can enter products_en_us for example if you have proxies or live in US

    headers = {
        "Accept": "application/json",
        "Accept-Language": "de,en-US;q=0.9,en;q=0.8",
        "Acept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Origin": "https://www.lacoste.com",
        "Referer": "https://www.lacoste.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Host": "cu0iyshi42-dsn.algolia.net",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    url = (
        "https://cu0iyshi42-dsn.algolia.net/1/indexes/*/queries?"
        "x-algolia-agent=Algolia%20for%20vanilla%20JavaScript%20(lite)%203.30.0;JS%20Helper%202.19.0"
        "&x-algolia-application-id=CU0IYSHI42"
        "&x-algolia-api-key=7e20c005d05fe8f113d8b7e079bf34a1"
    )

    params_dict = {
        "query": QUERIES[0],
        "hitsPerPage": 32,
        "page": 0,
        "analyticsTags": "desktop",
        "attributesToRetrieve": '["pid","name","colors","imagesHttp","imagesHttps","price","badges","urlMaster","urlSwatchPattern","urlSwatchImg","priceBookId","isCustomizable","categoryLabel","genderLabel","productId","manufacturer","colorId","colorLabel","categoryName","productRestrictions"]',
        "distinct": "true",
        "responseFields": '["hits","facets","page","nbPages","query","nbHits","userData"]',
        "clickAnalytics": "true",
        "filters": "(priceBookId: lacoste-de-sales OR priceBookId: lacoste-de) AND (price.onlineFrom <= 1768932055458 AND price.onlineTo >= 1768932055458)",
        "facets": '["categoryLabel","universeLabel","genderLabel","searchColorName","sizes","sleeve"]',
        "tagFilters": ""
    }

    def build_json_request(self):
        payload = {
            "requests": [
                {
                    "indexName": self.LANGUAGE,
                    "params": urlencode(self.params_dict)
                }
            ]
        }
        return JsonRequest(url=self.url,  method="POST", data=payload, headers=self.headers,callback=self.parse)

    async def start(self):
        yield self.build_json_request()

    def parse(self, response):
        current_query = 0
        info = json.loads(response.body)
        items = info["results"][0]["hits"]
        if not info.get('results')[0].get('hits'):
            current_query += 1
            if current_query >= len(self.QUERIES):
                raise CloseSpider('End.')
            self.params_dict["query"]= self.QUERIES[current_query]
            self.params_dict["page"] = 0


        for item in items:
            try:
                price = item["price"]["minDisplayValue"]
            except:
                price = "N/A"
            yield {
                "title": item["name"],
                "category": item["categoryLabel"],
                "price": price,
                "link": item["urlMaster"],
            }
        self.params_dict["page"] = int(self.params_dict.get("page", 0)) + 1
        yield self.build_json_request()
