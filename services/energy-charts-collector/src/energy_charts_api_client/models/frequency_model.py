from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FrequencyModel")


@_attrs_define
class FrequencyModel:
    """
    Attributes:
        data (list[float | None]):
        deprecated (bool):
        unix_seconds (list[int] | None | Unset):
    """

    data: list[float | None]
    deprecated: bool
    unix_seconds: list[int] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item: float | None
            data_item = data_item_data
            data.append(data_item)

        deprecated = self.deprecated

        unix_seconds: list[int] | None | Unset
        if isinstance(self.unix_seconds, Unset):
            unix_seconds = UNSET
        elif isinstance(self.unix_seconds, list):
            unix_seconds = self.unix_seconds

        else:
            unix_seconds = self.unix_seconds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "deprecated": deprecated,
            }
        )
        if unix_seconds is not UNSET:
            field_dict["unix_seconds"] = unix_seconds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:

            def _parse_data_item(data: object) -> float | None:
                if data is None:
                    return data
                return cast(float | None, data)

            data_item = _parse_data_item(data_item_data)

            data.append(data_item)

        deprecated = d.pop("deprecated")

        def _parse_unix_seconds(data: object) -> list[int] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                unix_seconds_type_0 = cast(list[int], data)

                return unix_seconds_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[int] | None | Unset, data)

        unix_seconds = _parse_unix_seconds(d.pop("unix_seconds", UNSET))

        frequency_model = cls(
            data=data,
            deprecated=deprecated,
            unix_seconds=unix_seconds,
        )

        frequency_model.additional_properties = d
        return frequency_model

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
