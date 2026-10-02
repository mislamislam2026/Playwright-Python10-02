"""Flight search and booking tests."""
from __future__ import annotations

import pytest

from pages import FlightSearch, FlightsPage, HomePage, ItineraryPage, PaymentDetails
from utils.data_loader import load_json
from utils.helpers import future_date

FLIGHT_DATA = load_json("flights.json")
ROUTES = FLIGHT_DATA["routes"]


@pytest.fixture
def payment() -> PaymentDetails:
    return PaymentDetails(**FLIGHT_DATA["payment"])


@pytest.fixture
def on_flights_page(logged_in: HomePage, flights_page: FlightsPage) -> FlightsPage:
    logged_in.go_to_flights()
    return flights_page.wait_until_loaded()


@pytest.mark.smoke
def test_flights_page_opens(on_flights_page: FlightsPage) -> None:
    on_flights_page.expect_search_form_visible()


@pytest.mark.regression
@pytest.mark.parametrize(
    "route", ROUTES, ids=[f"{r['depart']}-{r['arrive']}" for r in ROUTES]
)
def test_search_lists_outbound_flights(on_flights_page: FlightsPage, route: dict) -> None:
    on_flights_page.search(
        FlightSearch(depart=route["depart"], arrive=route["arrive"],
                     depart_date=future_date(7))
    )
    on_flights_page.expect_flights_listed()


@pytest.mark.smoke
@pytest.mark.regression
def test_book_one_way_flight_end_to_end(
    empty_itinerary: HomePage,
    flights_page: FlightsPage,
    itinerary_page: ItineraryPage,
    payment: PaymentDetails,
) -> None:
    empty_itinerary.go_to_flights()
    flights_page.wait_until_loaded().book_flight(
        FlightSearch(depart="Denver", arrive="London", depart_date=future_date(10),
                     seat_preference="Window", seat_type="Business"),
        payment,
    )
    flights_page.expect_booking_confirmed()

    empty_itinerary.go_to_itinerary()
    itinerary_page.wait_until_loaded().expect_flight_count(1)


@pytest.mark.regression
@pytest.mark.negative
def test_same_departure_and_arrival_city_is_rejected(on_flights_page: FlightsPage) -> None:
    on_flights_page.search(
        FlightSearch(depart="Denver", arrive="Denver", depart_date=future_date(7))
    )
    on_flights_page.expect_still_on_search_form()


@pytest.mark.regression
@pytest.mark.negative
def test_past_departure_date_is_rejected(on_flights_page: FlightsPage) -> None:
    on_flights_page.search(
        FlightSearch(depart="Denver", arrive="London", depart_date="01/01/2000")
    )
    on_flights_page.expect_still_on_search_form()
