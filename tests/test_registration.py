"""Customer registration tests."""
from __future__ import annotations

import pytest

from pages import HomePage, NewCustomer, RegistrationPage
from utils.helpers import unique_username


@pytest.fixture
def on_registration_page(
    home_page: HomePage, registration_page: RegistrationPage
) -> RegistrationPage:
    home_page.go_to_sign_up()
    return registration_page.wait_until_loaded()


@pytest.mark.regression
def test_register_new_customer_and_log_in(
    on_registration_page: RegistrationPage, home_page: HomePage
) -> None:
    customer = NewCustomer(
        username=unique_username(),
        password="Passw0rd",
        password_confirm="Passw0rd",
        first_name="Test",
        last_name="User",
        street="1 Main Street",
        city="Denver",
    )
    on_registration_page.register(customer)
    on_registration_page.expect_registered(customer.username)

    home_page.load().login(customer.username, customer.password)
    home_page.expect_logged_in_as(customer.username)


@pytest.mark.regression
@pytest.mark.negative
def test_mismatched_passwords_are_rejected(on_registration_page: RegistrationPage) -> None:
    on_registration_page.register(
        NewCustomer(username=unique_username(), password="abc123",
                    password_confirm="different")
    )
    on_registration_page.expect_rejected()


@pytest.mark.regression
@pytest.mark.negative
def test_existing_username_is_rejected(
    on_registration_page: RegistrationPage, valid_user: dict
) -> None:
    on_registration_page.register(
        NewCustomer(username=valid_user["username"], password="abc123",
                    password_confirm="abc123")
    )
    on_registration_page.expect_rejected()


@pytest.mark.regression
@pytest.mark.negative
def test_empty_registration_form_is_rejected(on_registration_page: RegistrationPage) -> None:
    on_registration_page.register(NewCustomer(username="", password="", password_confirm=""))
    on_registration_page.expect_rejected()
