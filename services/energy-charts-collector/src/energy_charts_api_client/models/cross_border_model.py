from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.named_data import NamedData


T = TypeVar("T", bound="CrossBorderModel")


@_attrs_define
class CrossBorderModel:
    """
    Attributes:
        deprecated (bool):
        unix_seconds (list[int] | None | Unset):
        countries (list[NamedData] | None | Unset):
    """

    deprecated: bool
    unix_seconds: list[int] | None | Unset = UNSET
    countries: list[NamedData] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        deprecated = self.deprecated

        unix_seconds: list[int] | None | Unset
        if isinstance(self.unix_seconds, Unset):
            unix_seconds = UNSET
        elif isinstance(self.unix_seconds, list):
            unix_seconds = self.unix_seconds

        else:
            unix_seconds = self.unix_seconds

        countries: list[dict[str, Any]] | None | Unset
        if isinstance(self.countries, Unset):
            countries = UNSET
        elif isinstance(self.countries, list):
            countries = []
            for countries_type_0_item_data in self.countries:
                countries_type_0_item = countries_type_0_item_data.to_dict()
                countries.append(countries_type_0_item)

        else:
            countries = self.countries

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "deprecated": deprecated,
            }
        )
        if unix_seconds is not UNSET:
            field_dict["unix_seconds"] = unix_seconds
        if countries is not UNSET:
            field_dict["countries"] = countries

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.named_data import NamedData

        d = dict(src_dict)
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

        def _parse_countries(data: object) -> list[NamedData] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                countries_type_0 = []
                _countries_type_0 = data
                for countries_type_0_item_data in _countries_type_0:
                    countries_type_0_item = NamedData.from_dict(countries_type_0_item_data)

                    countries_type_0.append(countries_type_0_item)

                return countries_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[NamedData] | None | Unset, data)

        countries = _parse_countries(d.pop("countries", UNSET))

        cross_border_model = cls(
            deprecated=deprecated,
            unix_seconds=unix_seconds,
            countries=countries,
        )

        cross_border_model.additional_properties = d
        return cross_border_model

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
