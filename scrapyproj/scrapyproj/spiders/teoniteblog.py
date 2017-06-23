# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urljoin, urlsplit
from scrapyproj.items import BlogPostItem


def absolutize(x):
    return urljoin('http://build.sh/', x.extract())

class TeoniteblogSpider(scrapy.Spider):
    name = 'teoniteblog'
    allowed_domains = ['build.sh']
    start_urls = ['http://build.sh/']

    def parse(self, response):
        # get next pages
        older_postst_selectors = response.xpath('//a[@class="older-posts"]/@href')
        older_links = set([absolutize(x) for x in older_postst_selectors])
        for link in older_links:
            yield response.follow(link, self.parse)
        post_links = response.xpath('//h2[@class="post-title"]/node()/@href')
        for link in post_links:
            yield response.follow(absolutize(link), self.parse_article)

    def parse_article(self, response):
        slug = urlsplit(response.url).path.strip('/')
        # Most of the time I prefer to use xpath, but I've tried this for brewity.
        title = response.css('.post-title::text').extract_first()
        text_untreated = response.xpath(
            '//section[@class="post-content"]/descendant-or-self::*/text()'
        ).extract()
        text = ' '.join(chunk.strip() for chunk in text_untreated).strip()
        author = response.xpath(
            '//span[@class="author-content"]/h4/text()'
        ).extract_first()
        return BlogPostItem(
            slug=slug,
            title=title,
            text=text,
            author=author
        )
