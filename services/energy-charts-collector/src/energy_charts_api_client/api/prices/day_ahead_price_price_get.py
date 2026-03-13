from http import HTTPStatus
from typing import Any, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.price_model import PriceModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    bzn: str | Unset = "DE-LU",
    start: str | Unset = "",
    end: str | Unset = "",
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["bzn"] = bzn

    params["start"] = start

    params["end"] = end

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/price",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Any | HTTPValidationError | PriceModel | None:
    if response.status_code == 200:
        response_200 = PriceModel.from_dict(response.json())

        return response_200

    if response.status_code == 404:
        response_404 = cast(Any, None)
        return response_404

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[Any | HTTPValidationError | PriceModel]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    bzn: str | Unset = "DE-LU",
    start: str | Unset = "",
    end: str | Unset = "",
) -> Response[Any | HTTPValidationError | PriceModel]:
    r"""Day Ahead Price

     Returns the day-ahead spot market price for a specified bidding zone in EUR/MWh.





    Available bidding zones (bzn) are shown above.





    <b>The data for the following bidding zones is licensed as <a
    href=\"https://creativecommons.org/licenses/by/4.0/\" target=\"_blank\">CC BY 4.0</a> from
    Bundesnetzagentur | SMARD.de and is published without changes:
        <ul>
            <li>AT (Austria)</li>
            <li>BE (Belgium)</li>
            <li>CH (Switzerland)</li>
            <li>CZ (Czech Republic)</li>
            <li>DE-LU (Germany, Luxembourg)</li>
            <li>DE-AT-LU (Germany, Austria, Luxembourg)</li>
            <li>DK1 (Denmark 1)</li>
            <li>DK2 (Denmark 2)</li>
            <li>FR (France)</li>
            <li>HU (Hungary)</li>
            <li>IT-North (Italy North)</li>
            <li>NL (Netherlands)</li>
            <li>NO2 (Norway 2)</li>
            <li>PL (Poland)</li>
            <li>SE4 (Sweden 4)</li>
            <li>SI (Slovenia)
        </ul></b>





    <b>The data for the other bidding zones is for private and internal use only. The utilization of any
    data</li>
    whether in its raw or derived form, for external or commercial purposes is expressly prohibited.
    Should you require licensing for market-related data, please direct your inquiries to the original
    data providers, including but not limited to EPEX SPOT SE.</b>


    Response schema:


    ```json
    {
        \"license_info\": str,
        \"unix_seconds\": [int],
        \"price\": [float],
        \"unit\": str,
        \"deprecated\": bool
    }
    ```

    Args:
        bzn (str | Unset):  Default: 'DE-LU'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | PriceModel]
    """

    kwargs = _get_kwargs(
        bzn=bzn,
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
    bzn: str | Unset = "DE-LU",
    start: str | Unset = "",
    end: str | Unset = "",
) -> Any | HTTPValidationError | PriceModel | None:
    r"""Day Ahead Price

     Returns the day-ahead spot market price for a specified bidding zone in EUR/MWh.





    Available bidding zones (bzn) are shown above.





    <b>The data for the following bidding zones is licensed as <a
    href=\"https://creativecommons.org/licenses/by/4.0/\" target=\"_blank\">CC BY 4.0</a> from
    Bundesnetzagentur | SMARD.de and is published without changes:
        <ul>
            <li>AT (Austria)</li>
            <li>BE (Belgium)</li>
            <li>CH (Switzerland)</li>
            <li>CZ (Czech Republic)</li>
            <li>DE-LU (Germany, Luxembourg)</li>
            <li>DE-AT-LU (Germany, Austria, Luxembourg)</li>
            <li>DK1 (Denmark 1)</li>
            <li>DK2 (Denmark 2)</li>
            <li>FR (France)</li>
            <li>HU (Hungary)</li>
            <li>IT-North (Italy North)</li>
            <li>NL (Netherlands)</li>
            <li>NO2 (Norway 2)</li>
            <li>PL (Poland)</li>
            <li>SE4 (Sweden 4)</li>
            <li>SI (Slovenia)
        </ul></b>





    <b>The data for the other bidding zones is for private and internal use only. The utilization of any
    data</li>
    whether in its raw or derived form, for external or commercial purposes is expressly prohibited.
    Should you require licensing for market-related data, please direct your inquiries to the original
    data providers, including but not limited to EPEX SPOT SE.</b>


    Response schema:


    ```json
    {
        \"license_info\": str,
        \"unix_seconds\": [int],
        \"price\": [float],
        \"unit\": str,
        \"deprecated\": bool
    }
    ```

    Args:
        bzn (str | Unset):  Default: 'DE-LU'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | PriceModel
    """

    return sync_detailed(
        client=client,
        bzn=bzn,
        start=start,
        end=end,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    bzn: str | Unset = "DE-LU",
    start: str | Unset = "",
    end: str | Unset = "",
) -> Response[Any | HTTPValidationError | PriceModel]:
    r"""Day Ahead Price

     Returns the day-ahead spot market price for a specified bidding zone in EUR/MWh.





    Available bidding zones (bzn) are shown above.





    <b>The data for the following bidding zones is licensed as <a
    href=\"https://creativecommons.org/licenses/by/4.0/\" target=\"_blank\">CC BY 4.0</a> from
    Bundesnetzagentur | SMARD.de and is published without changes:
        <ul>
            <li>AT (Austria)</li>
            <li>BE (Belgium)</li>
            <li>CH (Switzerland)</li>
            <li>CZ (Czech Republic)</li>
            <li>DE-LU (Germany, Luxembourg)</li>
            <li>DE-AT-LU (Germany, Austria, Luxembourg)</li>
            <li>DK1 (Denmark 1)</li>
            <li>DK2 (Denmark 2)</li>
            <li>FR (France)</li>
            <li>HU (Hungary)</li>
            <li>IT-North (Italy North)</li>
            <li>NL (Netherlands)</li>
            <li>NO2 (Norway 2)</li>
            <li>PL (Poland)</li>
            <li>SE4 (Sweden 4)</li>
            <li>SI (Slovenia)
        </ul></b>





    <b>The data for the other bidding zones is for private and internal use only. The utilization of any
    data</li>
    whether in its raw or derived form, for external or commercial purposes is expressly prohibited.
    Should you require licensing for market-related data, please direct your inquiries to the original
    data providers, including but not limited to EPEX SPOT SE.</b>


    Response schema:


    ```json
    {
        \"license_info\": str,
        \"unix_seconds\": [int],
        \"price\": [float],
        \"unit\": str,
        \"deprecated\": bool
    }
    ```

    Args:
        bzn (str | Unset):  Default: 'DE-LU'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | HTTPValidationError | PriceModel]
    """

    kwargs = _get_kwargs(
        bzn=bzn,
        start=start,
        end=end,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    bzn: str | Unset = "DE-LU",
    start: str | Unset = "",
    end: str | Unset = "",
) -> Any | HTTPValidationError | PriceModel | None:
    r"""Day Ahead Price

     Returns the day-ahead spot market price for a specified bidding zone in EUR/MWh.





    Available bidding zones (bzn) are shown above.





    <b>The data for the following bidding zones is licensed as <a
    href=\"https://creativecommons.org/licenses/by/4.0/\" target=\"_blank\">CC BY 4.0</a> from
    Bundesnetzagentur | SMARD.de and is published without changes:
        <ul>
            <li>AT (Austria)</li>
            <li>BE (Belgium)</li>
            <li>CH (Switzerland)</li>
            <li>CZ (Czech Republic)</li>
            <li>DE-LU (Germany, Luxembourg)</li>
            <li>DE-AT-LU (Germany, Austria, Luxembourg)</li>
            <li>DK1 (Denmark 1)</li>
            <li>DK2 (Denmark 2)</li>
            <li>FR (France)</li>
            <li>HU (Hungary)</li>
            <li>IT-North (Italy North)</li>
            <li>NL (Netherlands)</li>
            <li>NO2 (Norway 2)</li>
            <li>PL (Poland)</li>
            <li>SE4 (Sweden 4)</li>
            <li>SI (Slovenia)
        </ul></b>





    <b>The data for the other bidding zones is for private and internal use only. The utilization of any
    data</li>
    whether in its raw or derived form, for external or commercial purposes is expressly prohibited.
    Should you require licensing for market-related data, please direct your inquiries to the original
    data providers, including but not limited to EPEX SPOT SE.</b>


    Response schema:


    ```json
    {
        \"license_info\": str,
        \"unix_seconds\": [int],
        \"price\": [float],
        \"unit\": str,
        \"deprecated\": bool
    }
    ```

    Args:
        bzn (str | Unset):  Default: 'DE-LU'.
        start (str | Unset):  Default: ''.
        end (str | Unset):  Default: ''.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | HTTPValidationError | PriceModel
    """

    return (
        await asyncio_detailed(
            client=client,
            bzn=bzn,
            start=start,
            end=end,
        )
    ).parsed
