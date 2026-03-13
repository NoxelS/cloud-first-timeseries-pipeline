from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="DailyAvgDict")


@_attrs_define
class DailyAvgDict:
    """
    Attributes:
        days (list[str]): List of days in the format dd.mm.yyyy
        data (list[float | None]): List of average daily values
        deprecated (bool):
    """

    days: list[str]
    data: list[float | None]
    deprecated: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        days = self.days

        data = []
        for data_item_data in self.data:
            data_item: float | None
            data_item = data_item_data
            data.append(data_item)

        deprecated = self.deprecated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "days": days,
                "data": data,
                "deprecated": deprecated,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        days = cast(list[str], d.pop("days"))

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

        daily_avg_dict = cls(
            days=days,
            data=data,
            deprecated=deprecated,
        )

        daily_avg_dict.additional_properties = d
        return daily_avg_dict

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
