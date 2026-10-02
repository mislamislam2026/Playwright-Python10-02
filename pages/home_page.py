"""Home page: login form, welcome message and the main menu."""
from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class HomePage(BasePage):
    """Landing page of Web Tours (login lives in the navbar frame)."""

    ERROR_PATTERN = re.compile(r"error|incorrect|invalid", re.IGNORECASE)

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ------------------------------------------------------------------ #
    # Locators — login form (navbar frame)
    # The inputs carry no <label>, so the name attribute is the most
    # stable hook; the image buttons expose their alt text as a role name.
    # ------------------------------------------------------------------ #
    @property
    def username_input(self) -> Locator:
        return self.navbar.locator('input[name="username"]')

    @property
    def password_input(self) -> Locator:
        return self.navbar.locator('input[name="password"]')

    @property
    def login_button(self) -> Locator:
        return self.navbar.get_by_role("button", name="Login")

    # ------------------------------------------------------------------ #
    # Locators — main menu (navbar frame, shown after login)
    # ------------------------------------------------------------------ #
    @property
    def flights_menu(self) -> Locator:
        return self.navbar.get_by_role("link", name=re.compile("Search Flights", re.I))

    @property
    def itinerary_menu(self) -> Locator:
        return self.navbar.get_by_role("link", name=re.compile("Itinerary", re.I))

    @property
    def sign_off_menu(self) -> Locator:
        return self.navbar.get_by_role("link", name=re.compile("Sign ?Off", re.I))

    # ------------------------------------------------------------------ #
    # Locators — content frame
    # ------------------------------------------------------------------ #
    @property
    def welcome_message(self) -> Locator:
        return self.info.get_by_text(re.compile(r"Welcome,", re.I))

    @property
    def sign_up_link(self) -> Locator:
        return self.info.get_by_role("link", name=re.compile("sign up now", re.I))

    @property
    def error_message(self) -> Locator:
        return self.info.get_by_text(self.ERROR_PATTERN).first

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def load(self) -> "HomePage":
        """Open the application and wait for the login form."""
        self.open()
        expect(self.username_input).to_be_visible()
        return self

    def login(self, username: str, password: str) -> None:
        """Submit the login form (no assertion on the outcome)."""
        self.fill_field(self.username_input, username)
        self.fill_field(self.password_input, password)
        self.login_button.click()

    def login_successfully(self, username: str, password: str) -> "HomePage":
        """Log in and wait for the welcome message."""
        self.login(username, password)
        expect(self.welcome_message).to_be_visible()
        return self

    def go_to_flights(self) -> None:
        self.flights_menu.click()

    def go_to_itinerary(self) -> None:
        self.itinerary_menu.click()

    def go_to_sign_up(self) -> None:
        self.sign_up_link.click()

    def sign_off(self) -> None:
        self.sign_off_menu.click()
        expect(self.username_input).to_be_visible()

    # ------------------------------------------------------------------ #
    # Assertions
    # ------------------------------------------------------------------ #
    def expect_logged_in_as(self, username: str) -> None:
        expect(self.welcome_message).to_contain_text(username)
        expect(self.sign_off_menu).to_be_visible()

    def expect_logged_out(self) -> None:
        expect(self.username_input).to_be_visible()
        expect(self.sign_off_menu).to_have_count(0)

    def expect_login_error(self) -> None:
        expect(self.error_message).to_be_visible()
        expect(self.sign_off_menu).to_have_count(0)
