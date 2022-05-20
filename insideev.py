from scrapy.crawler import CrawlerProcess
from scrapy import Spider, Request


class InsideEv(Spider):
    name = 'InsideEv'
    base_url = 'https://insideevs.com'
    start_urls = ['https://insideevs.com/news/?p=1']

    custom_settings = {
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/101.0.4951.67 Mobile Safari/537.36',
        'FEED_EXPORT_ENCODING': 'UTF-8',
        'FEEDS': {
            f"{name}.xlsx": {"format": "xlsx"}
        },
        "FEED_EXPORTERS": {
            'xlsx': 'scrapy_xlsx.XlsxItemExporter',
        },
    }

    def parse(self, response, **kwargs):
        if '<h1>404 Page not found</h1>' in response.text:
            return
        links = response.css('.browseBox-half h3 a::attr(href)').extract()
        for link in links:
            yield Request(
                url=self.base_url + link,
                callback=self.get_article
            )

        else:
            url = 'https://insideevs.com/news/?p={}'
            next_page = int(response.request.url.split('=')[-1].strip())
            yield Request(
                url=url.format(str(next_page + 1)),
                callback=self.parse
            )

    def get_article(self, response):
        heading = response.css('.m1-article-title::text').get()
        some_text = response.css('p::text').get()
        link = response.url
        date = response.css('.date-data::text').get()
        yield {
            'Date': date,
            "Headline": heading,
            'Some text': some_text,
            'URL': link
        }


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(InsideEv)
    process.start()
