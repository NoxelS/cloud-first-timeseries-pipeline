from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.public_power_forecast_model import PublicPowerForecastModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    country: str | Unset = "de",
    production_type: str | Unset = "solar",
    forecast_type: str | Unset = "current",
    start: str | Unset = "",
    end: str | Unset = "",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["country"] = country

    params["production_type"] = production_type

    params["forecast_type"] = forecast_type

    params["start"] = start

    params["end"] = end

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/public_power_forecast",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PublicPowerForecastModel | None:
    if response.status_code == 200:
        response_200 = PublicPowerForecastModel.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | PublicPowerForecastModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    production_type: str | Unset = "solar",
    forecast_type: str | Unset = "current",
    start: str | Unset = "",
    end: str | Unset = "",
) -> Response[HTTPValidationError | PublicPowerForecastModel]:
    r"""Public Power Forecast

     Returns the forecast of the public net electricity production for a given country for each
    production type.





    <b>production_type:</b> Can be solar, wind_onshore, wind_offshore or load
        <br><b>forecast_type:</b> Can be current, intraday or day-ahead





    If no dates are provided, values for today until forecast is available are returned. For load only
    the forecast type \"day-ahead\" is available.





    Response schema:


     ```json
    {
      \"unix_seconds\": list[int],
      \"forecast_values\": list[float],
      \"production_type\": str,
      \"forecast_type\": str,
      \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        production_type (str | Unset):  Default: 'solar'.
        forecast_type (str | Unset):  Default: 'current'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PublicPowerForecastModel]
    """

    kwargs = _get_kwargs(
        country=country,
        production_type=production_type,
        forecast_type=forecast_type,
        start=start,
        end=end,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    production_type: str | Unset = "solar",
    forecast_type: str | Unset = "current",
    start: str | Unset = "",
    end: str | Unset = "",
) -> HTTPValidationError | PublicPowerForecastModel | None:
    r"""Public Power Forecast

     Returns the forecast of the public net electricity production for a given country for each
    production type.





    <b>production_type:</b> Can be solar, wind_onshore, wind_offshore or load
        <br><b>forecast_type:</b> Can be current, intraday or day-ahead





    If no dates are provided, values for today until forecast is available are returned. For load only
    the forecast type \"day-ahead\" is available.





    Response schema:


     ```json
    {
      \"unix_seconds\": list[int],
      \"forecast_values\": list[float],
      \"production_type\": str,
      \"forecast_type\": str,
      \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        production_type (str | Unset):  Default: 'solar'.
        forecast_type (str | Unset):  Default: 'current'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PublicPowerForecastModel
    """

    return sync_detailed(
        client=client,
        country=country,
        production_type=production_type,
        forecast_type=forecast_type,
        start=start,
        end=end,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    production_type: str | Unset = "solar",
    forecast_type: str | Unset = "current",
    start: str | Unset = "",
    end: str | Unset = "",
) -> Response[HTTPValidationError | PublicPowerForecastModel]:
    r"""Public Power Forecast

     Returns the forecast of the public net electricity production for a given country for each
    production type.





    <b>production_type:</b> Can be solar, wind_onshore, wind_offshore or load
        <br><b>forecast_type:</b> Can be current, intraday or day-ahead





    If no dates are provided, values for today until forecast is available are returned. For load only
    the forecast type \"day-ahead\" is available.





    Response schema:


     ```json
    {
      \"unix_seconds\": list[int],
      \"forecast_values\": list[float],
      \"production_type\": str,
      \"forecast_type\": str,
      \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        production_type (str | Unset):  Default: 'solar'.
        forecast_type (str | Unset):  Default: 'current'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PublicPowerForecastModel]
    """

    kwargs = _get_kwargs(
        country=country,
        production_type=production_type,
        forecast_type=forecast_type,
        start=start,
        end=end,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    production_type: str | Unset = "solar",
    forecast_type: str | Unset = "current",
    start: str | Unset = "",
    end: str | Unset = "",
) -> HTTPValidationError | PublicPowerForecastModel | None:
    r"""Public Power Forecast

     Returns the forecast of the public net electricity production for a given country for each
    production type.





    <b>production_type:</b> Can be solar, wind_onshore, wind_offshore or load
        <br><b>forecast_type:</b> Can be current, intraday or day-ahead





    If no dates are provided, values for today until forecast is available are returned. For load only
    the forecast type \"day-ahead\" is available.





    Response schema:


     ```json
    {
      \"unix_seconds\": list[int],
      \"forecast_values\": list[float],
      \"production_type\": str,
      \"forecast_type\": str,
      \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        production_type (str | Unset):  Default: 'solar'.
        forecast_type (str | Unset):  Default: 'current'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PublicPowerForecastModel
    """

    return (
        await asyncio_detailed(
            client=client,
            country=country,
            production_type=production_type,
            forecast_type=forecast_type,
            start=start,
            end=end,
        )
    ).parsed
