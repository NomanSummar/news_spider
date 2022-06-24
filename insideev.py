import datetime
from datetime import date, timedelta
from scrapy.crawler import CrawlerProcess
from scrapy import Spider, Request


class InsideEv(Spider):
    name = 'InsideEv'
    base_url = 'https://insideevs.com'
    start_urls = ['https://insideevs.com/news/?p=1',
                  'https://cleantechnica.com/category/clean-transport-2/electric-vehicles/',
                  'https://electrek.co/2022/04/20/'
                  ]
    electrek_url = 'https://electrek.co/'

    custom_settings = {
        'LOG_FILE': 'last_run.log',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/101.0.4951.67 Mobile Safari/537.36',
        'FEED_EXPORT_ENCODING': 'UTF-8',
        'FEEDS': {
            f"news_spider/posts.xlsx": {"format": "xlsx"}
        },
        "FEED_EXPORTERS": {
            'xlsx': 'scrapy_xlsx.XlsxItemExporter',
        },
    }
    headings = []

    def parse(self, response, **kwargs):
        if 'cleantechnica' in response.url:
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
        elif 'electrek.co' in response.url:
            start_date = date.today()
            end_date = date(2015, 11, 16)
            delta = timedelta(days=1)
            while start_date >= end_date:
                yield Request(
                    url=self.electrek_url + start_date.strftime("%Y/%m/%d") + '/',
                    callback=self.get_article
                )
                # print(start_date.strftime("%Y/%m/%d"))
                start_date -= delta
        elif 'insideevs':
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
        if 'insideevs' in response.url:
            heading = response.css('.m1-article-title::text').get()
            some_text = ''
            text = response.css('.e-content p *::text').extract()
            for tex in text:
                if 'EVANNEX' in tex:
                    continue
                if len(some_text) <= 400:
                    some_text = some_text + tex.strip()
                else:
                    break
            link = response.url
            date = response.css('.date-data::text').get()
            date = datetime.datetime.strptime(date, '%b %d, %Y')
            yield {
                'Date': str(date),
                "Headline": heading,
                'Some text': some_text,
                'URL': link
            }
        elif 'electrek.co' in response.url:
            posts = response.css('.post-content')
            for post in posts:
                if post.css('div h1 a::attr(href)').get():
                    post.css('.post-body p *::text').extract()
                    some_text = ''.join(post.css('.post-body p *::text').extract())
                    if 'Quick Charge is available now on\xa0,\xa0,\xa0\xa0and our\xa0for Overcast and other podcast ' \
                       'players. ' in some_text:
                        some_text = some_text.replace(
                            'Quick Charge is available now on\xa0,\xa0,\xa0\xa0and our\xa0for '
                            'Overcast and other podcast players. ', '')

                    yield {
                        'Date': str(datetime.datetime.strptime(response.url.split('co/')[-1][:-1].strip(), '%Y/%m/%d')),
                        'Headline': post.css('div h1 a::text').get(),
                        'Some text': some_text,
                        'URL': post.css('div h1 a::attr(href)').get(),
                    }
        else:
            url = response.url
            heading = response.css('.post-date::attr(datetime)').get()
            text = response.css('.zox-post-body p *::text').extract()
            some_text = ''
            for index, tex in enumerate(text):
                if len(some_text) <= 400:
                    some_text = some_text + tex.strip() + ' '
                else:
                    break
            date = response.css('.post-date::attr(datetime)').get()
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            yield {
                'Date': str(date),
                "Headline": response.css('.entry-title::text').get(),
                'Some text': some_text,
                'URL': url
            }


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(InsideEv)
    process.start()
