"""Itinerary tests."""
from __future__ import annotations

import pytest

from pages import FlightSearch, FlightsPage, HomePage, ItineraryPage, PaymentDetails
from utils.data_loader import load_json
from utils.helpers import future_date

PAYMENT = load_json("flights.json")["payment"]


def _book(home: HomePage, flights: FlightsPage, depart: str, arrive: str) -> None:
    home.go_to_flights()
    flights.wait_until_loaded().book_flight(
        FlightSearch(depart=depart, arrive=arrive, depart_date=future_date(14)),
        PaymentDetails(**PAYMENT),
    )
    flights.expect_booking_confirmed()


@pytest.mark.smoke
def test_itinerary_page_opens(logged_in: HomePage, itinerary_page: ItineraryPage) -> None:
    logged_in.go_to_itinerary()
    itinerary_page.wait_until_loaded()


@pytest.mark.regression
def test_empty_itinerary_shows_message(
    empty_itinerary: HomePage, itinerary_page: ItineraryPage
) -> None:
    empty_itinerary.go_to_itinerary()
    itinerary_page.wait_until_loaded().expect_empty()


@pytest.mark.regression
def test_cancel_single_flight(
    empty_itinerary: HomePage,
    flights_page: FlightsPage,
    itinerary_page: ItineraryPage,
) -> None:
    _book(empty_itinerary, flights_page, "Denver", "London")
    _book(empty_itinerary, flights_page, "Paris", "Seattle")

    empty_itinerary.go_to_itinerary()
    itinerary_page.wait_until_loaded().expect_flight_count(2)

    itinerary_page.cancel_flight(0)
    itinerary_page.expect_flight_count(1)


@pytest.mark.regression
def test_cancel_all_flights(
    empty_itinerary: HomePage,
    flights_page: FlightsPage,
    itinerary_page: ItineraryPage,
) -> None:
    _book(empty_itinerary, flights_page, "Frankfurt", "Sydney")

    empty_itinerary.go_to_itinerary()
    itinerary_page.cancel_all_flights()
    itinerary_page.expect_empty()
