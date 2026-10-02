"""Login and logout tests."""
from __future__ import annotations

import pytest

from pages import HomePage
from utils.data_loader import get_user


@pytest.mark.smoke
@pytest.mark.login
def test_login_page_is_displayed(home_page: HomePage) -> None:
    home_page.expect_logged_out()


@pytest.mark.smoke
@pytest.mark.login
def test_valid_login_shows_welcome(home_page: HomePage, valid_user: dict) -> None:
    home_page.login(valid_user["username"], valid_user["password"])
    home_page.expect_logged_in_as(valid_user["username"])


@pytest.mark.regression
@pytest.mark.login
def test_sign_off_returns_to_login(logged_in: HomePage) -> None:
    logged_in.sign_off()
    logged_in.expect_logged_out()


@pytest.mark.regression
@pytest.mark.login
@pytest.mark.negative
@pytest.mark.parametrize(
    "user_key",
    ["invalid_password", "unknown_user"],
    ids=["wrong-password", "unknown-user"],
)
def test_invalid_credentials_are_rejected(home_page: HomePage, user_key: str) -> None:
    user = get_user(user_key)
    home_page.login(user["username"], user["password"])
    home_page.expect_login_error()


@pytest.mark.regression
@pytest.mark.login
@pytest.mark.negative
def test_empty_credentials_do_not_log_in(home_page: HomePage) -> None:
    user = get_user("empty")
    home_page.login(user["username"], user["password"])
    home_page.expect_logged_out()
