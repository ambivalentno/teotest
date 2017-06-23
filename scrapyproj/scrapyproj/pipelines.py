# -*- coding: utf-8 -*-
from langdetect import detect as detect_lang
from slugify import slugify
from blog.models import BlogPost


class TeonitePipeline(object):
    def process_item(self, item, spider):
        blogpost, created = BlogPost.objects.get_or_create(slug=item['slug'])
        blogpost.title = item['title']
        blogpost.text = item['text']
        blogpost.author_name = item['author']
        blogpost.author_slug = slugify(item['author'])
        blogpost.lang = detect_lang(item['text'])
        blogpost.save_dirty_fields()
