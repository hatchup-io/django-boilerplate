from django.db import models


class HatchUpBaseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, is_deleted=False)

    def delete(self, instance):
        instance.is_active = False
        instance.is_deleted = True
        instance.save()

    def purge(self, instance):
        instance.delete()
