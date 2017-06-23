from blog.models import BlogPost
import factory


class BlogPostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BlogPost

    @classmethod
    def _generate(cls, create, attrs):
        if 'author' in attrs and isinstance('author', str):
            attrs['author_slug'] = attrs['author']
        return super()._generate(create, attrs)
