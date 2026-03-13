from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ShareModel")


@_attrs_define
class ShareModel:
    """
    Attributes:
        deprecated (bool):
        unix_seconds (list[int] | None | Unset):
        data (list[float | None] | None | Unset):
        forecast (list[float | None] | None | Unset):
    """

    deprecated: bool
    unix_seconds: list[int] | None | Unset = UNSET
    data: list[float | None] | None | Unset = UNSET
    forecast: list[float | None] | None | Unset = UNSET
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

        data: list[float | None] | None | Unset
        if isinstance(self.data, Unset):
            data = UNSET
        elif isinstance(self.data, list):
            data = []
            for data_type_0_item_data in self.data:
                data_type_0_item: float | None
                data_type_0_item = data_type_0_item_data
                data.append(data_type_0_item)

        else:
            data = self.data

        forecast: list[float | None] | None | Unset
        if isinstance(self.forecast, Unset):
            forecast = UNSET
        elif isinstance(self.forecast, list):
            forecast = []
            for forecast_type_0_item_data in self.forecast:
                forecast_type_0_item: float | None
                forecast_type_0_item = forecast_type_0_item_data
                forecast.append(forecast_type_0_item)

        else:
            forecast = self.forecast

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "deprecated": deprecated,
            }
        )
        if unix_seconds is not UNSET:
            field_dict["unix_seconds"] = unix_seconds
        if data is not UNSET:
            field_dict["data"] = data
        if forecast is not UNSET:
            field_dict["forecast"] = forecast

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
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

        def _parse_data(data: object) -> list[float | None] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                data_type_0 = []
                _data_type_0 = data
                for data_type_0_item_data in _data_type_0:

                    def _parse_data_type_0_item(data: object) -> float | None:
                        if data is None:
                            return data
                        return cast(float | None, data)

                    data_type_0_item = _parse_data_type_0_item(data_type_0_item_data)

                    data_type_0.append(data_type_0_item)

                return data_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float | None] | None | Unset, data)

        data = _parse_data(d.pop("data", UNSET))

        def _parse_forecast(data: object) -> list[float | None] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                forecast_type_0 = []
                _forecast_type_0 = data
                for forecast_type_0_item_data in _forecast_type_0:

                    def _parse_forecast_type_0_item(data: object) -> float | None:
                        if data is None:
                            return data
                        return cast(float | None, data)

                    forecast_type_0_item = _parse_forecast_type_0_item(forecast_type_0_item_data)

                    forecast_type_0.append(forecast_type_0_item)

                return forecast_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float | None] | None | Unset, data)

        forecast = _parse_forecast(d.pop("forecast", UNSET))

        share_model = cls(
            deprecated=deprecated,
            unix_seconds=unix_seconds,
            data=data,
            forecast=forecast,
        )

        share_model.additional_properties = d
        return share_model

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
