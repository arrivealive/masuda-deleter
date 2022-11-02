import factory

from masudaapi import models

class HatenaUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.HatenaUser

    hatena_id = 'masuda'


class PostFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Post
        # django_get_or_create = ('name',)

    # masuda_id = '20220123045607'
    # body = '記を書く' 
    # posted_at = '2022-01-23 04:56:07'


class ProgressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Progress

class StopCommandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.StopCommand

class DeletePostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Delete_Post

class DeleteLaterCheckFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Delete_Later_Check