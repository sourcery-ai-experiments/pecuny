import pytest
from jose import jwt

from app import models
from app import repository as repo
from app import schemas
from app.config import settings
from app.utils.dataclasses_utils import ClientSessionWrapper
from app.utils.enums import RequestMethod
from tests.helpers import make_http_request

SUCCESS_LOGIN_STATUS_CODE = 204
ENDPOINT = "/api/auth"


@pytest.mark.parametrize(
    "username, displayname, password",
    [
        ("john@pytest.de", "John", "password123"),
        ("random-name@pytest.de", "", "password123"),
    ],
)
async def test_create_user(
    client_session_wrapper: ClientSessionWrapper,
    username,
    displayname,
    password,
):
    """
    Tests the create user functionality.

    Args:
        session: The session fixture.
        client: The async client fixture.
        username (str): The username of the user to create.
        displayname (str): The display name of the user to create.
        password (str): The password of the user to create.

    Returns:
        None
    """
    res = await make_http_request(
        client_session_wrapper.session,
        client_session_wrapper.client,
        f"{ENDPOINT}/register",
        json={
            "email": username,
            "password": password,
            "displayname": displayname,
        },
    )
    assert res.status_code == 201

    new_user = schemas.UserRead(**res.json())

    assert new_user.email == username
    assert new_user.displayname != ""
    assert new_user.is_active is True
    assert new_user.is_superuser is False
    assert new_user.is_verified is False


async def test_invalid_create_user(
    client_session_wrapper: ClientSessionWrapper, test_user: models.User
):
    """
    Tests the invalid user creation.

    Args:
        session: The session fixture.
        client: The async client fixture.
        username (str): The username of the user to create.
        displayname (str): The display name of the user to create.
        password (str): The password of the user to create.

    Returns:
        None
    """
    email = test_user.email
    res = await make_http_request(
        client_session_wrapper.session,
        client_session_wrapper.client,
        f"{ENDPOINT}/register",
        json={"email": email, "password": "testpassword", "displayname": "John"},
    )

    assert res.status_code == 400


@pytest.mark.parametrize(
    "username, password",
    [
        ("hello123@pytest.de", "password123"),
        ("hellO123@pytest.de", "password123"),
        ("HELLO123@pytest.de", "password123"),
        ("hello123@PyTeSt.De", "password123"),
        ("hELLO123@pytest.de", "password123"),
    ],
)
async def test_login(
    client_session_wrapper: ClientSessionWrapper,
    test_user,
    username,
    password,
):
    """
    Tests successful user login

    Args:
        authorized_client: The authorized client fixture.
        session: The session fixture.

    Returns:
        None
    """

    res = await make_http_request(
        client_session_wrapper.session,
        client_session_wrapper.client,
        f"{ENDPOINT}/login",
        {
            "username": username,
            "password": password,
        },
    )

    cookie = res.cookies.get("fastapiusersauth")
    payload = jwt.decode(
        cookie,
        settings.secret_key,
        algorithms=settings.algorithm,
        audience="fastapi-users:auth",
    )
    user_id = payload["sub"]

    assert user_id == str(test_user.id)
    assert res.status_code == SUCCESS_LOGIN_STATUS_CODE


@pytest.mark.parametrize(
    "username, password, status_code",
    [
        ("wrongemail@gmail.com", "password123", 400),
        ("hello123@pytest.de", "wrongPassword", 400),
        ("aaaa", "wrongPassword", 400),
        ("*39goa", "wrongPassword", 400),
        (None, "wrongPassword", 422),
        ("wrongemail@gmail.com", None, 422),
    ],
)
@pytest.mark.usefixtures("test_user")
async def test_invalid_login(
    client_session_wrapper: ClientSessionWrapper,
    username,
    password,
    status_code,
):
    """
    Tests failed user login.

    Args:
        authorized_client: The authorized client fixture.
        session: The session fixture.

    Returns:
        None
    """

    res = await make_http_request(
        client_session_wrapper.session,
        client_session_wrapper.client,
        f"{ENDPOINT}/login",
        {"username": username, "password": password},
    )

    assert res.status_code == status_code


@pytest.mark.parametrize(
    "values",
    [
        ({"email": "mew@mew.de"}),
        ({"email": "another@mail.com"}),
        ({"displayname": "Agent Smith"}),
        ({"password": "lancelot"}),
    ],
)
@pytest.mark.usefixtures("test_user")
async def test_updated_user(client_session_wrapper: ClientSessionWrapper, values):
    """
    Tests successful update user parameter.

    Args:
        session: The session fixture.
        client: The async client fixture.
        username (str): The username of the user to create.
        displayname (str): The display name of the user to create.
        password (str): The password of the user to create.

    Returns:
        None
    """

    res = await make_http_request(
        client_session_wrapper.session,
        client_session_wrapper.authorized_client,
        "/api/users/me",
        json=values,
        method=RequestMethod.PATCH,
    )

    assert res.status_code == 200
    user = schemas.UserRead(**res.json())

    for key, value in values.items():
        if key == "password":
            login_res = await make_http_request(
                client_session_wrapper.session,
                client_session_wrapper.client,
                f"{ENDPOINT}/login",
                {"username": user.email, "password": value},
            )
            assert login_res.status_code == SUCCESS_LOGIN_STATUS_CODE
            continue

        assert getattr(user, key) == value


@pytest.mark.parametrize(
    "values",
    [
        ({"email": "mewmew.de"}),
        ({"password": ""}),
        ({"is_superuser": True}),
        ({"email": "anothermail.com"}),
    ],
)
async def test_invalid_updated_user(
    client_session_wrapper: ClientSessionWrapper, test_user, values
):
    """
    Tests tests invalid update user functionality.

    Args:
        authorized_client: The authorized client fixture.
        session: The session fixture.

    Returns:
        None
    """

    user_id = str(test_user.id)
    res = await make_http_request(
        client_session_wrapper.session,
        client_session_wrapper.authorized_client,
        f"/api/users/{user_id}",
        json=values,
        method=RequestMethod.PATCH,
    )

    assert res.status_code == 403


async def test_delete_user(
    client_session_wrapper: ClientSessionWrapper,
    test_user,
):
    """
    Tests the create user functionality.

    Args:
        session: The session fixture.
        client: The async client fixture.
        username (str): The username of the user to create.
        displayname (str): The display name of the user to create.
        password (str): The password of the user to create.

    Returns:
        None
    """

    user = await repo.get(models.User, test_user.id)
    assert user.email == test_user.email

    res = await make_http_request(
        client_session_wrapper.session,
        client_session_wrapper.authorized_client,
        "/api/users/me",
        method=RequestMethod.DELETE,
    )

    user = await repo.get(models.User, test_user.id)
    assert user is None

    assert res.status_code == 204


async def test_invalid_delete_user(
    client_session_wrapper: ClientSessionWrapper,
):
    """
    Tests invalid user deletion.

    Args:
        session: The session fixture.
        client: The async client fixture.
        username (str): The username of the user to create.
        displayname (str): The display name of the user to create.
        password (str): The password of the user to create.

    Returns:
        None
    """

    res = await make_http_request(
        client_session_wrapper.session,
        client_session_wrapper.authorized_client,
        url="/api/users/2",
        method=RequestMethod.DELETE,
    )

    assert res.status_code == 403
