from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.cross_border_model import CrossBorderModel
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    country: str | Unset = "de",
    start: str | Unset = "",
    end: str | Unset = "",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["country"] = country

    params["start"] = start

    params["end"] = end

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/cbet",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> CrossBorderModel | HTTPValidationError | None:
    if response.status_code == 200:
        response_200 = CrossBorderModel.from_dict(response.json())

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
) -> Response[CrossBorderModel | HTTPValidationError]:
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
    start: str | Unset = "",
    end: str | Unset = "",
) -> Response[CrossBorderModel | HTTPValidationError]:
    r"""Cross Border Electricity Trading

     Returns the cross-border electricity trading (cbet) in GW between a specified country and its
    neighbors.


    Positive values indicate an import of electricity, whereas negative values show electricity exports.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"countries\": [
            {
            \"name\": str,
            \"data\": [float]
            }
        ],
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CrossBorderModel | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        country=country,
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
    start: str | Unset = "",
    end: str | Unset = "",
) -> CrossBorderModel | HTTPValidationError | None:
    r"""Cross Border Electricity Trading

     Returns the cross-border electricity trading (cbet) in GW between a specified country and its
    neighbors.


    Positive values indicate an import of electricity, whereas negative values show electricity exports.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"countries\": [
            {
            \"name\": str,
            \"data\": [float]
            }
        ],
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CrossBorderModel | HTTPValidationError
    """

    return sync_detailed(
        client=client,
        country=country,
        start=start,
        end=end,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    start: str | Unset = "",
    end: str | Unset = "",
) -> Response[CrossBorderModel | HTTPValidationError]:
    r"""Cross Border Electricity Trading

     Returns the cross-border electricity trading (cbet) in GW between a specified country and its
    neighbors.


    Positive values indicate an import of electricity, whereas negative values show electricity exports.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"countries\": [
            {
            \"name\": str,
            \"data\": [float]
            }
        ],
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CrossBorderModel | HTTPValidationError]
    """

    kwargs = _get_kwargs(
        country=country,
        start=start,
        end=end,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    start: str | Unset = "",
    end: str | Unset = "",
) -> CrossBorderModel | HTTPValidationError | None:
    r"""Cross Border Electricity Trading

     Returns the cross-border electricity trading (cbet) in GW between a specified country and its
    neighbors.


    Positive values indicate an import of electricity, whereas negative values show electricity exports.





    Response schema:


    ```json
    {
        \"unix_seconds\": [int],
        \"countries\": [
            {
            \"name\": str,
            \"data\": [float]
            }
        ],
        \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CrossBorderModel | HTTPValidationError
    """

    return (
        await asyncio_detailed(
            client=client,
            country=country,
            start=start,
            end=end,
        )
    ).parsed
