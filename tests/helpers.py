import datetime
from typing import List

from fastapi import Response
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.utils.enums import RequestMethod


async def make_http_request(
    session: AsyncSession,
    client: AsyncClient,
    url: str,
    data: dict = None,
    json: dict = None,
    method: RequestMethod = RequestMethod.POST,
) -> Response:
    """
    Makes an HTTP request to the specified URL using the given method and JSON data.

    Args:
        client_session_wrapper: The client session wrapper object.
        method: The HTTP method to use for the request.
        url: The URL to make the request to.
        json_data: The JSON data to include in the request body. Defaults to None.

    Returns:
        Response: The response object.

    Raises:
        ValueError: If an invalid method is provided.
    """

    async with session:
        if method == RequestMethod.POST:
            response = await client.post(url, json=json, data=data)
        elif method == RequestMethod.PATCH:
            response = await client.patch(url, json=json, data=data)
        elif method == RequestMethod.GET:
            response = await client.get(url)
        elif method == RequestMethod.DELETE:
            response = await client.delete(url)
        else:
            raise ValueError(
                f"Invalid method: {method}. Expected one of: get, post, patch, delete."
            )

    return response


def get_user_offset_account(
    account: models.Account, account_list: List[models.Account]
) -> models.Account:

    for account_element in account_list:
        if (
            account_element.user_id == account.user_id
            and account.id != account_element.id
        ):
            return account_element


def get_date_range(date_start, days=5):
    """
    Returns a list of dates in a range starting from a given date.

    Args:
        date_start: The starting date.
        days: The number of days in the range (default is 5).

    Returns:
        List[datetime.date]: A list of dates in the range.
    """

    return [(date_start - datetime.timedelta(days=idx)) for idx in range(days)]
