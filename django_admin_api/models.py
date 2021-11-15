from typing import Iterable, Optional
from django.db import models

from .query import RestApiQuerySet


class ApiModel(models.Model):
    class Meta:
        abstract = True
        managed = True
        default_manager_name = "objects"

    objects = RestApiQuerySet.as_manager()()

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        qs = self.__class__.objects.all()
        if self.pk or force_update:
            qs = qs.filter(**{self._meta.pk.attname: self.pk})
            qs = qs.update(**self.as_dict(update_fields))
        else:
            d = self.as_dict()
            d.pop(self._meta.pk.attname)
            model = qs.create(**d)
            self.pk = model.pk

    def delete(self, using=None, keep_parents: bool = False) -> None:
        qs = self.__class__.objects.all()
        qs = qs.filter(**{self._meta.pk.attname: self.pk}).delete()

    def as_dict(self, fields=None):
        fields = fields or (f.name for f in self._meta.fields)
        return {name: getattr(self, name) for name in fields}
