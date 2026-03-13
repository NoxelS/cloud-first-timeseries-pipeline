from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.share_model import ShareModel
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
        "url": "/solar_share",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | ShareModel | None:
    if response.status_code == 200:
        response_200 = ShareModel.from_dict(response.json())

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
) -> Response[HTTPValidationError | ShareModel]:
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
) -> Response[HTTPValidationError | ShareModel]:
    r"""Solar Share

     <b>Solar Share of Load</b>





    Returns the solar share of load from today until prediction is currently available





    Response schema:


    ```json
    {
        \"unix_seconds\": list[int],
        \"data\": list[float],
        \"forecast\": list[float],
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ShareModel]
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
) -> HTTPValidationError | ShareModel | None:
    r"""Solar Share

     <b>Solar Share of Load</b>





    Returns the solar share of load from today until prediction is currently available





    Response schema:


    ```json
    {
        \"unix_seconds\": list[int],
        \"data\": list[float],
        \"forecast\": list[float],
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ShareModel
    """

    return sync_detailed(
        client=client,
        country=country,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
) -> Response[HTTPValidationError | ShareModel]:
    r"""Solar Share

     <b>Solar Share of Load</b>





    Returns the solar share of load from today until prediction is currently available





    Response schema:


    ```json
    {
        \"unix_seconds\": list[int],
        \"data\": list[float],
        \"forecast\": list[float],
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | ShareModel]
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
) -> HTTPValidationError | ShareModel | None:
    r"""Solar Share

     <b>Solar Share of Load</b>





    Returns the solar share of load from today until prediction is currently available





    Response schema:


    ```json
    {
        \"unix_seconds\": list[int],
        \"data\": list[float],
        \"forecast\": list[float],
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | ShareModel
    """

    return (
        await asyncio_detailed(
            client=client,
            country=country,
        )
    ).parsed
