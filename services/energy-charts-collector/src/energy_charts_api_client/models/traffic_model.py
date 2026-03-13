from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TrafficModel")


@_attrs_define
class TrafficModel:
    """
    Attributes:
        unix_seconds (list[int]):
        share (list[float | None]):
        substitute (bool):
        deprecated (bool):
        signal (list[int | None] | Unset):
                0: Red (low renewable share)
                1: Yellow (average renewable share)
                2: Green (high renewable share)

    """

    unix_seconds: list[int]
    share: list[float | None]
    substitute: bool
    deprecated: bool
    signal: list[int | None] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        unix_seconds = self.unix_seconds

        share = []
        for share_item_data in self.share:
            share_item: float | None
            share_item = share_item_data
            share.append(share_item)

        substitute = self.substitute

        deprecated = self.deprecated

        signal: list[int | None] | Unset = UNSET
        if not isinstance(self.signal, Unset):
            signal = []
            for signal_item_data in self.signal:
                signal_item: int | None
                signal_item = signal_item_data
                signal.append(signal_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "unix_seconds": unix_seconds,
                "share": share,
                "substitute": substitute,
                "deprecated": deprecated,
            }
        )
        if signal is not UNSET:
            field_dict["signal"] = signal

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        unix_seconds = cast(list[int], d.pop("unix_seconds"))

        share = []
        _share = d.pop("share")
        for share_item_data in _share:

            def _parse_share_item(data: object) -> float | None:
                if data is None:
                    return data
                return cast(float | None, data)

            share_item = _parse_share_item(share_item_data)

            share.append(share_item)

        substitute = d.pop("substitute")

        deprecated = d.pop("deprecated")

        _signal = d.pop("signal", UNSET)
        signal: list[int | None] | Unset = UNSET
        if _signal is not UNSET:
            signal = []
            for signal_item_data in _signal:

                def _parse_signal_item(data: object) -> int | None:
                    if data is None:
                        return data
                    return cast(int | None, data)

                signal_item = _parse_signal_item(signal_item_data)

                signal.append(signal_item)

        traffic_model = cls(
            unix_seconds=unix_seconds,
            share=share,
            substitute=substitute,
            deprecated=deprecated,
            signal=signal,
        )

        traffic_model.additional_properties = d
        return traffic_model

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
