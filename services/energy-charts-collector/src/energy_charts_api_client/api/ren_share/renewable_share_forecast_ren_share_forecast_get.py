from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.ren_share_model import RenShareModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    country: str | Unset = "de",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["country"] = country

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/ren_share_forecast",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | RenShareModel | None:
    if response.status_code == 200:
        response_200 = RenShareModel.from_dict(response.json())

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
) -> Response[HTTPValidationError | RenShareModel]:
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
) -> Response[HTTPValidationError | RenShareModel]:
    r"""Renewable Share Forecast

     <b>Renewable share forecast</b>





    Returns the renewable share of load forecast in percent from today until prediction is currently
    available. It also includes the forecast for solar, wind on- and offshore share of load.





    If no data is available from the primary data providers, a best guess is made from historic data.
    This is indicated by \"substitute\" set to True.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"ren_share\": [float],
        \"solar_share\": [float],
        \"wind_onshore_share\": [float],
        \"wind_offshore_share\": [float],
        \"substitute\": bool,
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RenShareModel]
    """

    kwargs = _get_kwargs(
        country=country,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
) -> HTTPValidationError | RenShareModel | None:
    r"""Renewable Share Forecast

     <b>Renewable share forecast</b>





    Returns the renewable share of load forecast in percent from today until prediction is currently
    available. It also includes the forecast for solar, wind on- and offshore share of load.





    If no data is available from the primary data providers, a best guess is made from historic data.
    This is indicated by \"substitute\" set to True.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"ren_share\": [float],
        \"solar_share\": [float],
        \"wind_onshore_share\": [float],
        \"wind_offshore_share\": [float],
        \"substitute\": bool,
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RenShareModel
    """

    return sync_detailed(
        client=client,
        country=country,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
) -> Response[HTTPValidationError | RenShareModel]:
    r"""Renewable Share Forecast

     <b>Renewable share forecast</b>





    Returns the renewable share of load forecast in percent from today until prediction is currently
    available. It also includes the forecast for solar, wind on- and offshore share of load.





    If no data is available from the primary data providers, a best guess is made from historic data.
    This is indicated by \"substitute\" set to True.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"ren_share\": [float],
        \"solar_share\": [float],
        \"wind_onshore_share\": [float],
        \"wind_offshore_share\": [float],
        \"substitute\": bool,
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | RenShareModel]
    """

    kwargs = _get_kwargs(
        country=country,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
) -> HTTPValidationError | RenShareModel | None:
    r"""Renewable Share Forecast

     <b>Renewable share forecast</b>





    Returns the renewable share of load forecast in percent from today until prediction is currently
    available. It also includes the forecast for solar, wind on- and offshore share of load.





    If no data is available from the primary data providers, a best guess is made from historic data.
    This is indicated by \"substitute\" set to True.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"ren_share\": [float],
        \"solar_share\": [float],
        \"wind_onshore_share\": [float],
        \"wind_offshore_share\": [float],
        \"substitute\": bool,
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | RenShareModel
    """

    return (
        await asyncio_detailed(
            client=client,
            country=country,
        )
    ).parsed
