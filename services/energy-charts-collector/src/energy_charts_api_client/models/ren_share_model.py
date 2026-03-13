from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RenShareModel")


@_attrs_define
class RenShareModel:
    """
    Attributes:
        unix_seconds (list[int]):
        ren_share (list[float | None]):
        substitute (bool):
        deprecated (bool):
        solar_share (list[float] | None | Unset):
        wind_onshore_share (list[float] | None | Unset):
        wind_offshore_share (list[float] | None | Unset):
    """

    unix_seconds: list[int]
    ren_share: list[float | None]
    substitute: bool
    deprecated: bool
    solar_share: list[float] | None | Unset = UNSET
    wind_onshore_share: list[float] | None | Unset = UNSET
    wind_offshore_share: list[float] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        unix_seconds = self.unix_seconds

        ren_share = []
        for ren_share_item_data in self.ren_share:
            ren_share_item: float | None
            ren_share_item = ren_share_item_data
            ren_share.append(ren_share_item)

        substitute = self.substitute

        deprecated = self.deprecated

        solar_share: list[float] | None | Unset
        if isinstance(self.solar_share, Unset):
            solar_share = UNSET
        elif isinstance(self.solar_share, list):
            solar_share = self.solar_share

        else:
            solar_share = self.solar_share

        wind_onshore_share: list[float] | None | Unset
        if isinstance(self.wind_onshore_share, Unset):
            wind_onshore_share = UNSET
        elif isinstance(self.wind_onshore_share, list):
            wind_onshore_share = self.wind_onshore_share

        else:
            wind_onshore_share = self.wind_onshore_share

        wind_offshore_share: list[float] | None | Unset
        if isinstance(self.wind_offshore_share, Unset):
            wind_offshore_share = UNSET
        elif isinstance(self.wind_offshore_share, list):
            wind_offshore_share = self.wind_offshore_share

        else:
            wind_offshore_share = self.wind_offshore_share

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "unix_seconds": unix_seconds,
                "ren_share": ren_share,
                "substitute": substitute,
                "deprecated": deprecated,
            }
        )
        if solar_share is not UNSET:
            field_dict["solar_share"] = solar_share
        if wind_onshore_share is not UNSET:
            field_dict["wind_onshore_share"] = wind_onshore_share
        if wind_offshore_share is not UNSET:
            field_dict["wind_offshore_share"] = wind_offshore_share

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        unix_seconds = cast(list[int], d.pop("unix_seconds"))

        ren_share = []
        _ren_share = d.pop("ren_share")
        for ren_share_item_data in _ren_share:

            def _parse_ren_share_item(data: object) -> float | None:
                if data is None:
                    return data
                return cast(float | None, data)

            ren_share_item = _parse_ren_share_item(ren_share_item_data)

            ren_share.append(ren_share_item)

        substitute = d.pop("substitute")

        deprecated = d.pop("deprecated")

        def _parse_solar_share(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                solar_share_type_0 = cast(list[float], data)

                return solar_share_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        solar_share = _parse_solar_share(d.pop("solar_share", UNSET))

        def _parse_wind_onshore_share(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                wind_onshore_share_type_0 = cast(list[float], data)

                return wind_onshore_share_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        wind_onshore_share = _parse_wind_onshore_share(d.pop("wind_onshore_share", UNSET))

        def _parse_wind_offshore_share(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                wind_offshore_share_type_0 = cast(list[float], data)

                return wind_offshore_share_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        wind_offshore_share = _parse_wind_offshore_share(d.pop("wind_offshore_share", UNSET))

        ren_share_model = cls(
            unix_seconds=unix_seconds,
            ren_share=ren_share,
            substitute=substitute,
            deprecated=deprecated,
            solar_share=solar_share,
            wind_onshore_share=wind_onshore_share,
            wind_offshore_share=wind_offshore_share,
        )

        ren_share_model.additional_properties = d
        return ren_share_model

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
