from scrapy.crawler import CrawlerProcess
from scrapy import Spider, Request


class Clean(Spider):
    name = 'clean'
    start_urls = ['https://cleantechnica.com/category/clean-transport-2/electric-vehicles/', ]
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
        articles = response.css('.zox-art-title a::attr(href)').extract()
        for link in articles:
            yield Request(
                url=link,
                callback=self.get_article
            )
            # 1775
        if "exist" not in response.meta:
            last_page = response.css('.pagination span::text').get()
            if last_page:
                try:
                    last_page = int(last_page.split('of')[-1].strip())
                except:
                    last_page = 1775
            else:
                last_page = 1775
            for page in range(2, last_page + 1):
                url = 'https://cleantechnica.com/category/clean-transport-2/electric-vehicles/page/{}/'.format(page)
                yield Request(
                    url=url,
                    callback=self.parse,
                    meta={"exist": True}
                )

    def get_article(self, response):
        url = response.url
        some_text = response.css('.zox-post-body p::text').get()
        if not some_text or len(some_text) < 150:
            some_text = response.css('p:nth-child(2)::text').get()

        yield {
            'Date': response.css('.post-date::attr(datetime)').get(),
            "Headline": response.css('.entry-title::text').get(),
            'Some text': some_text,
            'URL': url
        }


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(Clean)
    process.start()
