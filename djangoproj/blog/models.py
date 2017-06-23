from dirtyfields import DirtyFieldsMixin
from django.db import models


class BlogPost(DirtyFieldsMixin, models.Model):
    slug = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255, null=True)
    text = models.TextField(null=True)
    # I don't think there's any point to have a ForeignKey here.
    # Also, there's no link to some author profile in the html, therefore we will have dublicated
    # author instances in case of edition.
    author_name = models.CharField(max_length=255, null=True)
    author_slug = models.CharField(max_length=255, null=True)
    lang = models.CharField(max_length=2, null=True)
