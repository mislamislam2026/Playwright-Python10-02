"""Flight booking flow: find flights → choose flight → payment → invoice."""
from __future__ import annotations

import re
from dataclasses import dataclass

from playwright.sync_api import Locator, Page, expect

from pages.base_page import BasePage


@dataclass
class FlightSearch:
    """Search criteria for the "Find Flight" form."""

    depart: str
    arrive: str
    depart_date: str | None = None
    return_date: str | None = None
    passengers: str = "1"
    seat_preference: str = "None"  # Aisle | Window | None
    seat_type: str = "Coach"  # First | Business | Coach
    round_trip: bool = False


@dataclass
class PaymentDetails:
    first_name: str
    last_name: str
    street: str
    city: str
    passenger_name: str
    credit_card: str
    expiry: str


class FlightsPage(BasePage):
    """All steps of the reservation wizard (content frame)."""

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    # ------------------------------------------------------------------ #
    # Step 1 — Find Flight. Selects/inputs have no labels → name attribute.
    # ------------------------------------------------------------------ #
    @property
    def depart_city_select(self) -> Locator:
        return self.info.locator('select[name="depart"]')

    @property
    def arrive_city_select(self) -> Locator:
        return self.info.locator('select[name="arrive"]')

    @property
    def depart_date_input(self) -> Locator:
        return self.info.locator('input[name="departDate"]')

    @property
    def return_date_input(self) -> Locator:
        return self.info.locator('input[name="returnDate"]')

    @property
    def round_trip_checkbox(self) -> Locator:
        return self.info.locator('input[name="roundtrip"]')

    @property
    def passengers_input(self) -> Locator:
        return self.info.locator('input[name="numPassengers"]')

    def seat_preference_radio(self, preference: str) -> Locator:
        return self.info.locator(f'input[name="seatPref"][value="{preference}"]')

    def seat_type_radio(self, seat_type: str) -> Locator:
        return self.info.locator(f'input[name="seatType"][value="{seat_type}"]')

    @property
    def find_flights_button(self) -> Locator:
        return self.info.locator('input[name="findFlights"]')

    # ------------------------------------------------------------------ #
    # Step 2 — Select Flight
    # ------------------------------------------------------------------ #
    @property
    def outbound_flight_options(self) -> Locator:
        return self.info.locator('input[name="outboundFlight"]')

    @property
    def reserve_flights_button(self) -> Locator:
        return self.info.locator('input[name="reserveFlights"]')

    # ------------------------------------------------------------------ #
    # Step 3 — Payment Details
    # ------------------------------------------------------------------ #
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
    def passenger_name_input(self) -> Locator:
        return self.info.locator('input[name="pass1"]')

    @property
    def credit_card_input(self) -> Locator:
        return self.info.locator('input[name="creditCard"]')

    @property
    def expiry_input(self) -> Locator:
        return self.info.locator('input[name="expDate"]')

    @property
    def buy_flights_button(self) -> Locator:
        return self.info.locator('input[name="buyFlights"]')

    # ------------------------------------------------------------------ #
    # Step 4 — Invoice
    # ------------------------------------------------------------------ #
    @property
    def invoice_message(self) -> Locator:
        return self.info.get_by_text(re.compile(r"Thank you for booking", re.I))

    # ------------------------------------------------------------------ #
    # Actions
    # ------------------------------------------------------------------ #
    def wait_until_loaded(self) -> "FlightsPage":
        expect(self.depart_city_select).to_be_visible()
        return self

    def search(self, criteria: FlightSearch) -> None:
        """Fill in and submit the Find Flight form."""
        self.select_option(self.depart_city_select, criteria.depart)
        self.select_option(self.arrive_city_select, criteria.arrive)
        if criteria.depart_date:
            self.fill_field(self.depart_date_input, criteria.depart_date)
        if criteria.round_trip:
            self.round_trip_checkbox.check()
            if criteria.return_date:
                self.fill_field(self.return_date_input, criteria.return_date)
        self.fill_field(self.passengers_input, criteria.passengers)
        self.seat_preference_radio(criteria.seat_preference).check()
        self.seat_type_radio(criteria.seat_type).check()
        self.find_flights_button.click()

    def select_outbound_flight(self, index: int = 0) -> None:
        """Choose one of the listed outbound flights and continue."""
        expect(self.outbound_flight_options.first).to_be_visible()
        self.outbound_flight_options.nth(index).check()
        self.reserve_flights_button.click()

    def pay(self, payment: PaymentDetails) -> None:
        """Fill in payment details and confirm the purchase."""
        expect(self.credit_card_input).to_be_visible()
        self.fill_field(self.first_name_input, payment.first_name)
        self.fill_field(self.last_name_input, payment.last_name)
        self.fill_field(self.street_input, payment.street)
        self.fill_field(self.city_input, payment.city)
        self.fill_field(self.passenger_name_input, payment.passenger_name)
        self.fill_field(self.credit_card_input, payment.credit_card)
        self.fill_field(self.expiry_input, payment.expiry)
        self.buy_flights_button.click()

    def book_flight(self, criteria: FlightSearch, payment: PaymentDetails) -> None:
        """Run the whole wizard end to end."""
        self.search(criteria)
        self.select_outbound_flight()
        self.pay(payment)

    # ------------------------------------------------------------------ #
    # Assertions
    # ------------------------------------------------------------------ #
    def expect_search_form_visible(self) -> None:
        expect(self.depart_city_select).to_be_visible()
        expect(self.arrive_city_select).to_be_visible()
        expect(self.find_flights_button).to_be_visible()

    def expect_flights_listed(self) -> None:
        expect(self.outbound_flight_options.first).to_be_visible()
        expect(self.reserve_flights_button).to_be_visible()

    def expect_booking_confirmed(self) -> None:
        expect(self.invoice_message).to_be_visible()

    def expect_still_on_search_form(self) -> None:
        """Validation failed: the wizard did not move to flight selection."""
        expect(self.outbound_flight_options).to_have_count(0)
