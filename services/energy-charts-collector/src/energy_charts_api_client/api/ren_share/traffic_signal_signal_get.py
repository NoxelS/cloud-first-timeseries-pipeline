from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.traffic_model import TrafficModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    country: str | Unset = "de",
    postal_code: str | Unset = "",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["country"] = country

    params["postal_code"] = postal_code

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/signal",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | TrafficModel | None:
    if response.status_code == 200:
        response_200 = TrafficModel.from_dict(response.json())

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
) -> Response[HTTPValidationError | TrafficModel]:
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
    postal_code: str | Unset = "",
) -> Response[HTTPValidationError | TrafficModel]:
    r"""Traffic Signal

     <b>Electricity traffic signal</b>





    Returns the renewable share of load in percent from today until prediction is currently available
    and the corresponding traffic light.





    The traffic light \"signal\" is indicated by the following numbers:



        -1: Red (grid congestion),
        0: Red (low renewable share),
        1: Yellow (average renewable share),
        2: Green (high renewable share)





    If no data is available from the primary data providers, a best guess is made from historic data.
    This is indicated by \"substitute\" set to True.





    \"postal_code\" is an optional input parameter, which will consider the local grid state (e.g.
    transmission line overload) in future implementations.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"share\": [float],
        \"signal\": [int],
        \"substitute\": bool,
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        postal_code (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | TrafficModel]
    """

    kwargs = _get_kwargs(
        country=country,
        postal_code=postal_code,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    postal_code: str | Unset = "",
) -> HTTPValidationError | TrafficModel | None:
    r"""Traffic Signal

     <b>Electricity traffic signal</b>





    Returns the renewable share of load in percent from today until prediction is currently available
    and the corresponding traffic light.





    The traffic light \"signal\" is indicated by the following numbers:



        -1: Red (grid congestion),
        0: Red (low renewable share),
        1: Yellow (average renewable share),
        2: Green (high renewable share)





    If no data is available from the primary data providers, a best guess is made from historic data.
    This is indicated by \"substitute\" set to True.





    \"postal_code\" is an optional input parameter, which will consider the local grid state (e.g.
    transmission line overload) in future implementations.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"share\": [float],
        \"signal\": [int],
        \"substitute\": bool,
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        postal_code (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | TrafficModel
    """

    return sync_detailed(
        client=client,
        country=country,
        postal_code=postal_code,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    postal_code: str | Unset = "",
) -> Response[HTTPValidationError | TrafficModel]:
    r"""Traffic Signal

     <b>Electricity traffic signal</b>





    Returns the renewable share of load in percent from today until prediction is currently available
    and the corresponding traffic light.





    The traffic light \"signal\" is indicated by the following numbers:



        -1: Red (grid congestion),
        0: Red (low renewable share),
        1: Yellow (average renewable share),
        2: Green (high renewable share)





    If no data is available from the primary data providers, a best guess is made from historic data.
    This is indicated by \"substitute\" set to True.





    \"postal_code\" is an optional input parameter, which will consider the local grid state (e.g.
    transmission line overload) in future implementations.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"share\": [float],
        \"signal\": [int],
        \"substitute\": bool,
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        postal_code (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | TrafficModel]
    """

    kwargs = _get_kwargs(
        country=country,
        postal_code=postal_code,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    postal_code: str | Unset = "",
) -> HTTPValidationError | TrafficModel | None:
    r"""Traffic Signal

     <b>Electricity traffic signal</b>





    Returns the renewable share of load in percent from today until prediction is currently available
    and the corresponding traffic light.





    The traffic light \"signal\" is indicated by the following numbers:



        -1: Red (grid congestion),
        0: Red (low renewable share),
        1: Yellow (average renewable share),
        2: Green (high renewable share)





    If no data is available from the primary data providers, a best guess is made from historic data.
    This is indicated by \"substitute\" set to True.





    \"postal_code\" is an optional input parameter, which will consider the local grid state (e.g.
    transmission line overload) in future implementations.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"share\": [float],
        \"signal\": [int],
        \"substitute\": bool,
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        postal_code (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | TrafficModel
    """

    return (
        await asyncio_detailed(
            client=client,
            country=country,
            postal_code=postal_code,
        )
    ).parsed
