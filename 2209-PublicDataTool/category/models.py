from django.db import models

# Create your models here.
# class Index(models.Model):
#     name = models.CharField(max_length=200, db_index=True)
#
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ['-created', '-updated']
#         index_together = [['id', 'name']]