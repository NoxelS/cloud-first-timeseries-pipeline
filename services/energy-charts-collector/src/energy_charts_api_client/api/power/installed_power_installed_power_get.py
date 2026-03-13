from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.installed_model import InstalledModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    country: str | Unset = "de",
    time_step: str | Unset = "yearly",
    installation_decommission: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["country"] = country

    params["time_step"] = time_step

    params["installation_decommission"] = installation_decommission

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/installed_power",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | InstalledModel | None:
    if response.status_code == 200:
        response_200 = InstalledModel.from_dict(response.json())

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
) -> Response[HTTPValidationError | InstalledModel]:
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
    time_step: str | Unset = "yearly",
    installation_decommission: bool | Unset = False,
) -> Response[HTTPValidationError | InstalledModel]:
    r"""Installed Power

     Returns the installed power for a specified country in GW except for battery storage capacity, which
    is given in GWh. Monthly installation / decommission numbers are returned in MW instead of GW.
    \"last_update\" is the time of the last data update, expressed as seconds since the Unix epoch
    (UTC).





    <b>time_step:</b> Time step can be either \"yearly\" or \"monthly\" (only for Germany)
        <br><b>installation_decommission:</b> If true, the net installation / decommission numbers are
    returned instead of total installed power





    Response schema:


     ```json
    {
      \"time\": list[str],
      \"production_types\": [
        {
            \"name\": str,
            \"data\": list[float]
        }
      ],
      \"last_update\": int,
      \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        time_step (str | Unset):  Default: 'yearly'.
        installation_decommission (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | InstalledModel]
    """

    kwargs = _get_kwargs(
        country=country,
        time_step=time_step,
        installation_decommission=installation_decommission,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    time_step: str | Unset = "yearly",
    installation_decommission: bool | Unset = False,
) -> HTTPValidationError | InstalledModel | None:
    r"""Installed Power

     Returns the installed power for a specified country in GW except for battery storage capacity, which
    is given in GWh. Monthly installation / decommission numbers are returned in MW instead of GW.
    \"last_update\" is the time of the last data update, expressed as seconds since the Unix epoch
    (UTC).





    <b>time_step:</b> Time step can be either \"yearly\" or \"monthly\" (only for Germany)
        <br><b>installation_decommission:</b> If true, the net installation / decommission numbers are
    returned instead of total installed power





    Response schema:


     ```json
    {
      \"time\": list[str],
      \"production_types\": [
        {
            \"name\": str,
            \"data\": list[float]
        }
      ],
      \"last_update\": int,
      \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        time_step (str | Unset):  Default: 'yearly'.
        installation_decommission (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | InstalledModel
    """

    return sync_detailed(
        client=client,
        country=country,
        time_step=time_step,
        installation_decommission=installation_decommission,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    time_step: str | Unset = "yearly",
    installation_decommission: bool | Unset = False,
) -> Response[HTTPValidationError | InstalledModel]:
    r"""Installed Power

     Returns the installed power for a specified country in GW except for battery storage capacity, which
    is given in GWh. Monthly installation / decommission numbers are returned in MW instead of GW.
    \"last_update\" is the time of the last data update, expressed as seconds since the Unix epoch
    (UTC).





    <b>time_step:</b> Time step can be either \"yearly\" or \"monthly\" (only for Germany)
        <br><b>installation_decommission:</b> If true, the net installation / decommission numbers are
    returned instead of total installed power





    Response schema:


     ```json
    {
      \"time\": list[str],
      \"production_types\": [
        {
            \"name\": str,
            \"data\": list[float]
        }
      ],
      \"last_update\": int,
      \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        time_step (str | Unset):  Default: 'yearly'.
        installation_decommission (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | InstalledModel]
    """

    kwargs = _get_kwargs(
        country=country,
        time_step=time_step,
        installation_decommission=installation_decommission,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    country: str | Unset = "de",
    time_step: str | Unset = "yearly",
    installation_decommission: bool | Unset = False,
) -> HTTPValidationError | InstalledModel | None:
    r"""Installed Power

     Returns the installed power for a specified country in GW except for battery storage capacity, which
    is given in GWh. Monthly installation / decommission numbers are returned in MW instead of GW.
    \"last_update\" is the time of the last data update, expressed as seconds since the Unix epoch
    (UTC).





    <b>time_step:</b> Time step can be either \"yearly\" or \"monthly\" (only for Germany)
        <br><b>installation_decommission:</b> If true, the net installation / decommission numbers are
    returned instead of total installed power





    Response schema:


     ```json
    {
      \"time\": list[str],
      \"production_types\": [
        {
            \"name\": str,
            \"data\": list[float]
        }
      ],
      \"last_update\": int,
      \"deprecated\": bool
    }
    ```

    Args:
        country (str | Unset):  Default: 'de'.
        time_step (str | Unset):  Default: 'yearly'.
        installation_decommission (bool | Unset):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | InstalledModel
    """

    return (
        await asyncio_detailed(
            client=client,
            country=country,
            time_step=time_step,
            installation_decommission=installation_decommission,
        )
    ).parsed
