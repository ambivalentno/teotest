import os
import sys

import redis
from django.conf import settings
from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from blog.calc import recalculate_stats, to_processed_sentences, calc_wor2vec, \
    reset_stats
from blog.models import BlogPost


connection = redis.Redis(connection_pool=settings.REDIS_POOL)


class Command(BaseCommand):
    help = "Scrape build.sh site."

    def handle(self, *args, **options):
        # Set environment for scrapy to be able to launch.
        sys.path.insert(0, os.path.join(settings.PROJECT_DIR, 'scrapyproj'))
        os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapyproj.settings'

        # Perform crawling. Blocking process.
        process = CrawlerProcess(get_project_settings())
        process.crawl('teoniteblog')
        process.start()

        # Update stats
        reset_stats(
            recalculate_stats(),
            connection
        )

        # Calculate word2vec
        calc_wor2vec(
            to_processed_sentences(
                BlogPost.objects.values_list('text', flat=True)
            ),
            filepath=settings.WORD2VEC_FILE
        )
