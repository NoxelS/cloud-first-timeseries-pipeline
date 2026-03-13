from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.named_data import NamedData


T = TypeVar("T", bound="InstalledModel")


@_attrs_define
class InstalledModel:
    """
    Attributes:
        time (list[str]):
        last_update (int | None):
        deprecated (bool):
        production_types (list[NamedData] | None | Unset):
    """

    time: list[str]
    last_update: int | None
    deprecated: bool
    production_types: list[NamedData] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        time = self.time

        last_update: int | None
        last_update = self.last_update

        deprecated = self.deprecated

        production_types: list[dict[str, Any]] | None | Unset
        if isinstance(self.production_types, Unset):
            production_types = UNSET
        elif isinstance(self.production_types, list):
            production_types = []
            for production_types_type_0_item_data in self.production_types:
                production_types_type_0_item = production_types_type_0_item_data.to_dict()
                production_types.append(production_types_type_0_item)

        else:
            production_types = self.production_types

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "time": time,
                "last_update": last_update,
                "deprecated": deprecated,
            }
        )
        if production_types is not UNSET:
            field_dict["production_types"] = production_types

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.named_data import NamedData

        d = dict(src_dict)
        time = cast(list[str], d.pop("time"))

        def _parse_last_update(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        last_update = _parse_last_update(d.pop("last_update"))

        deprecated = d.pop("deprecated")

        def _parse_production_types(data: object) -> list[NamedData] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                production_types_type_0 = []
                _production_types_type_0 = data
                for production_types_type_0_item_data in _production_types_type_0:
                    production_types_type_0_item = NamedData.from_dict(production_types_type_0_item_data)

                    production_types_type_0.append(production_types_type_0_item)

                return production_types_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[NamedData] | None | Unset, data)

        production_types = _parse_production_types(d.pop("production_types", UNSET))

        installed_model = cls(
            time=time,
            last_update=last_update,
            deprecated=deprecated,
            production_types=production_types,
        )

        installed_model.additional_properties = d
        return installed_model

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
