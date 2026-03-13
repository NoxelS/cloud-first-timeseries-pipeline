from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PriceModel")


@_attrs_define
class PriceModel:
    """
    Attributes:
        license_info (str):
        unit (str):
        deprecated (bool):
        unix_seconds (list[int] | None | Unset):
        price (list[float | None] | None | Unset):
    """

    license_info: str
    unit: str
    deprecated: bool
    unix_seconds: list[int] | None | Unset = UNSET
    price: list[float | None] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        license_info = self.license_info

        unit = self.unit

        deprecated = self.deprecated

        unix_seconds: list[int] | None | Unset
        if isinstance(self.unix_seconds, Unset):
            unix_seconds = UNSET
        elif isinstance(self.unix_seconds, list):
            unix_seconds = self.unix_seconds

        else:
            unix_seconds = self.unix_seconds

        price: list[float | None] | None | Unset
        if isinstance(self.price, Unset):
            price = UNSET
        elif isinstance(self.price, list):
            price = []
            for price_type_0_item_data in self.price:
                price_type_0_item: float | None
                price_type_0_item = price_type_0_item_data
                price.append(price_type_0_item)

        else:
            price = self.price

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "license_info": license_info,
                "unit": unit,
                "deprecated": deprecated,
            }
        )
        if unix_seconds is not UNSET:
            field_dict["unix_seconds"] = unix_seconds
        if price is not UNSET:
            field_dict["price"] = price

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        license_info = d.pop("license_info")

        unit = d.pop("unit")

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

        def _parse_price(data: object) -> list[float | None] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                price_type_0 = []
                _price_type_0 = data
                for price_type_0_item_data in _price_type_0:

                    def _parse_price_type_0_item(data: object) -> float | None:
                        if data is None:
                            return data
                        return cast(float | None, data)

                    price_type_0_item = _parse_price_type_0_item(price_type_0_item_data)

                    price_type_0.append(price_type_0_item)

                return price_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float | None] | None | Unset, data)

        price = _parse_price(d.pop("price", UNSET))

        price_model = cls(
            license_info=license_info,
            unit=unit,
            deprecated=deprecated,
            unix_seconds=unix_seconds,
            price=price,
        )

        price_model.additional_properties = d
        return price_model

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
