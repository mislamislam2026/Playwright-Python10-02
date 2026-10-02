"""Itinerary page: list and cancel booked flights."""
from __future__ import annotations

import re

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


class ItineraryPage(BasePage):
    """Shows the logged-in user's reservations (content frame)."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ------------------------------------------------------------------ #
    # Locators
    # ------------------------------------------------------------------ #
    @property
    def heading(self) -> Locator:
        return self.info.get_by_text(re.compile(r"Itinerary", re.I)).first

    @property
    def flight_checkboxes(self) -> Locator:
        """One checkbox per booked flight (the 'Cancel' column)."""
        return self.info.get_by_role("checkbox")

    @property
    def cancel_checked_button(self) -> Locator:
        return self.info.locator('input[name="removeFlights"]')

    @property
    def cancel_all_button(self) -> Locator:
        return self.info.locator('input[name="removeAllFlights"]')

    @property
    def no_flights_message(self) -> Locator:
        return self.info.get_by_text(re.compile(r"No flights have been reserved", re.I))

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def wait_until_loaded(self) -> "ItineraryPage":
        expect(self.heading).to_be_visible()
        return self

    def booked_flight_count(self) -> int:
        """Number of flights currently in the itinerary."""
        self.wait_until_loaded()
        return self.flight_checkboxes.count()

    def cancel_flight(self, index: int = 0) -> None:
        """Tick one flight and cancel it."""
        self.flight_checkboxes.nth(index).check()
        self.cancel_checked_button.click()

    def cancel_all_flights(self) -> None:
        """Cancel every reservation if any exist."""
        if self.booked_flight_count() > 0:
            self.cancel_all_button.click()
            expect(self.no_flights_message).to_be_visible()

    # ------------------------------------------------------------------ #
    # Assertions
    # ------------------------------------------------------------------ #
    def expect_flight_count(self, count: int) -> None:
        expect(self.flight_checkboxes).to_have_count(count)

    def expect_empty(self) -> None:
        expect(self.no_flights_message).to_be_visible()
