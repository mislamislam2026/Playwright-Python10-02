"""Customer registration ("sign up now") page."""
from __future__ import annotations

import re
from dataclasses import dataclass

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


@dataclass
class NewCustomer:
    username: str
    password: str
    password_confirm: str
    first_name: str = ""
    last_name: str = ""
    street: str = ""
    city: str = ""


class RegistrationPage(BasePage):
    """Customer Profile form in the content frame."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ------------------------------------------------------------------ #
    # Locators (unlabeled inputs → name attribute)
    # ------------------------------------------------------------------ #
    @property
    def username_input(self) -> Locator:
        return self.info.locator('input[name="username"]')

    @property
    def password_input(self) -> Locator:
        return self.info.locator('input[name="password"]')

    @property
    def confirm_password_input(self) -> Locator:
        return self.info.locator('input[name="passwordConfirm"]')

    @property
    def first_name_input(self) -> Locator:
        return self.info.locator('input[name="firstName"]')

    @property
    def last_name_input(self) -> Locator:
        return self.info.locator('input[name="lastName"]')

    @property
    def street_input(self) -> Locator:
        return self.info.locator('input[name="address1"]')

    @property
    def city_input(self) -> Locator:
        return self.info.locator('input[name="address2"]')

    @property
    def continue_button(self) -> Locator:
        return self.info.locator('input[name="register"]')

    @property
    def success_message(self) -> Locator:
        return self.info.get_by_text(re.compile(r"Thank you", re.I)).first

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def wait_until_loaded(self) -> "RegistrationPage":
        expect(self.confirm_password_input).to_be_visible()
        return self

    def register(self, customer: NewCustomer) -> None:
        self.fill_field(self.username_input, customer.username)
        self.fill_field(self.password_input, customer.password)
        self.fill_field(self.confirm_password_input, customer.password_confirm)
        self.fill_field(self.first_name_input, customer.first_name)
        self.fill_field(self.last_name_input, customer.last_name)
        self.fill_field(self.street_input, customer.street)
        self.fill_field(self.city_input, customer.city)
        self.continue_button.click()

    # ------------------------------------------------------------------ #
    # Assertions
    # ------------------------------------------------------------------ #
    def expect_registered(self, username: str) -> None:
        expect(self.success_message).to_be_visible()
        expect(self.success_message).to_contain_text(username)

    def expect_rejected(self) -> None:
        """Registration failed: no thank-you message is shown."""
        expect(self.info.locator("body")).not_to_contain_text(
            re.compile(r"Thank you", re.I)
        )
