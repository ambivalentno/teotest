import json
import redis

from django.conf import settings
from django.http import Http404
from gensim.models import Word2Vec

from rest_framework import routers
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.reverse import reverse


connection = redis.Redis(connection_pool=settings.REDIS_POOL)
word2vec_model = Word2Vec.load(settings.WORD2VEC_FILE)


class WordStatsViewSet(viewsets.ViewSet):

    def retrieve(self, request, pk):
        """
        Return a count of top-10 words (of author specified by slug).
        In case there's "percent" url argument, it returns frequencies.
        """
        data = self.get_data(request, per_author=True)
        if pk not in data:
            raise Http404
        return Response(data[pk])

    def list(self, request):
        """
        Returns a count of top-10 most used words (of all blogposts).
        In case there's "percent" url argument, it returns frequencies.
        """
        return Response(self.get_data(request))

    def get_data(self, request, per_author=False):
        # Todo: we should have an interface to work with data after we have more than 5-8
        # logical entities in storage.
        query = ['top_10']
        if per_author:
            query.append('per_author')
        if 'percent' in request.query_params:
            query.append('percentage')
        query_str = "_".join(query)
        return json.loads(connection.get(query_str))


class SimilaritiesViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk):
        """pk is a word here"""
        similarities = word2vec_model.similar_by_word(pk)
        return Response({
            word: {
                'similarity': similarity,
                'link': reverse('similarity-detail', args=[word], request=request)
            }
            for word, similarity in similarities
        })


router = routers.DefaultRouter()
router.register(r'stats', WordStatsViewSet, base_name='stats')
router.register(r'similarity', SimilaritiesViewSet, base_name='similarity')