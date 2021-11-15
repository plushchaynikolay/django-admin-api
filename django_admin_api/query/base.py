import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Collection,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Sequence,
    TypeVar,
    Union,
)

from django.db.models.manager import BaseManager

if TYPE_CHECKING:
    from ..models import ApiModel

_Self = TypeVar("_Self")
_Model = TypeVar("_Model", bound="ApiModel")


class Actions(Enum):
    list = "list"
    count = "count"
    create = "create"
    update = "update"
    delete = "delete"


class AbstractSerializer(abc.ABC, Generic[_Model]):
    @abc.abstractmethod
    def serialize(self, model: _Model) -> Dict[str, Any]:
        raise NotImplementedError

    @abc.abstractmethod
    def deserialize(self, raw: Dict[str, Any]) -> _Model:
        raise NotImplementedError


@dataclass
class Query:
    order_by: Sequence[str] = field(default_factory=list)
    filters: dict = field(default_factory=dict)
    select_related: List[str] = field(default_factory=list)
    data: List[Dict[str, Any]] = field(default_factory=list)
    update: Dict[str, Any] = field(default_factory=dict)
    limit: Optional[int] = None
    offset: Optional[int] = None

    def set_limits(self, start: int, stop: int):
        self.offset = start
        self.limit = start + stop


class AbstractQueryset(abc.ABC, Collection[_Model]):
    """Minimal list of properties and methods for Queryset, to provide admin-site support."""

    query: Query = NotImplemented
    model: _Model
    verbose_name = NotImplemented
    verbose_name_plural = NotImplemented

    @abc.abstractmethod
    def filter(self: _Self, **kwargs) -> _Self:
        raise NotImplementedError

    @abc.abstractmethod
    def get(self: _Self, **kwargs) -> _Model:
        raise NotImplementedError

    @abc.abstractmethod
    def count(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def order_by(self: _Self, *ordering: Iterable[str]) -> _Self:
        raise NotImplementedError

    @abc.abstractmethod
    def _clone(self: _Self) -> _Self:
        raise NotImplementedError


class BaseApiQuerySet(AbstractQueryset):
    serializer: AbstractSerializer = NotImplemented
    url: str = NotImplemented
    list_url: str = None
    count_url: str = None
    update_url: str = None
    create_url: str = None
    delete_url: str = None

    def __init__(self, model: Optional[_Model] = None, **kwargs) -> None:
        self.model = model
        self.verbose_name = model._meta.verbose_name
        self.verbose_name_plural = model._meta.verbose_name_plural

        self.serializer = getattr(model, "_serializer", self.serializer)

        self.url = getattr(model, "_url", self.url)

        self.list_url = getattr(model, "_list_url", self.list_url or self.url)
        self.count_url = getattr(model, "_count_url", self.count_url or self.url)
        self.update_url = getattr(model, "_update_url", self.update_url or self.url)
        self.create_url = getattr(model, "_create_url", self.create_url or self.url)
        self.delete_url = getattr(model, "_delete_url", self.delete_url or self.url)

        self.query = Query()
        self._result_cache: Optional[Sequence[_Model]] = None

    # MAGIC METHODS

    def __len__(self) -> int:
        return len(self._fetch_all())

    def __contains__(self, x: _Model) -> bool:
        return x in self._fetch_all()

    def __iter__(self):
        return iter(self._fetch_all())

    def __getitem__(self, k):
        """Retrieve an item or slice from the set of results."""
        if not isinstance(k, (int, slice)):
            raise TypeError(
                "QuerySet indices must be integers or slices, not %s."
                % type(k).__name__
            )
        assert (not isinstance(k, slice) and (k >= 0)) or (
            isinstance(k, slice)
            and (k.start is None or k.start >= 0)
            and (k.stop is None or k.stop >= 0)
        ), "Negative indexing is not supported."

        if self._result_cache is not None:
            return self._result_cache[k]

        if isinstance(k, slice):
            qs = self._clone()
            if k.start is not None:
                start = int(k.start)
            else:
                start = None
            if k.stop is not None:
                stop = int(k.stop)
            else:
                stop = None
            qs.query.set_limits(start, stop)
            return list(qs)[:: k.step] if k.step else qs

        qs = self._clone()
        qs.query.set_limits(k, k + 1)
        qs._fetch_all()
        return qs._result_cache[0]

    # DJANGO METHODS

    def filter(self, **kwargs):
        clone = self._clone()
        clone.query.filters.update(kwargs)
        return clone

    def get(self, **kwargs):
        # TODO: raise DoesNotExist and TooManyValues
        return next(iter(self.filter(**kwargs)))

    def order_by(self, *ordering):
        self.query.order_by = ordering
        return self

    def count(self):
        return self.extract(self.request(Actions.count), Actions.count)

    def _clone(self):
        """Clone without cache"""
        clone = self.__class__(model=self.model)
        clone.query = self.query
        return clone

    @classmethod
    def as_manager(cls):
        manager = BaseManager.from_queryset(cls)
        return manager

    def create(self, **kwargs) -> _Model:
        self.query.data.append(kwargs)
        return self.extract(self.request(Actions.create), Actions.create)

    def update(self, **kwargs) -> None:
        self.query.update.update(kwargs)
        self.request(Actions.update)

    def delete(self) -> None:
        self.request(Actions.delete)

    def _fetch_all(self) -> Sequence[_Model]:
        if self._result_cache is None:
            self._result_cache = self.extract(self.request(Actions.list), Actions.list)
        return self._result_cache

    def _chain(self):
        return self._clone()

    # API METHODS

    def _get_url(self, action: Actions):
        return getattr(self, f"{action.value}_url", None) or self.url

    @abc.abstractmethod
    def request(self, action: Actions) -> Union[Dict, List]:
        raise NotImplementedError

    @abc.abstractmethod
    def extract(
        self, raw: Union[Dict, List], action: Actions
    ) -> Union[int, List[_Model]]:
        raise NotImplementedError
