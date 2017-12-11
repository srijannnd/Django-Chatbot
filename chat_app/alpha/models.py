from django.db import models

# Create your models here.


class Memory(models.Model):
    key = models.TextField()
    value = models.TextField()


class Conversation(models.Model):
    query = models.TextField()
    response = models.TextField()

    def __unicode__(self):
        return self.query
