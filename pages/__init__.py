"""Page Object Model classes for Web Tours."""
from pages.base_page import BasePage
from pages.flights_page import FlightSearch, FlightsPage, PaymentDetails
from pages.home_page import HomePage
from pages.itinerary_page import ItineraryPage
from pages.registration_page import NewCustomer, RegistrationPage

__all__ = [
    "BasePage",
    "FlightSearch",
    "FlightsPage",
    "HomePage",
    "ItineraryPage",
    "NewCustomer",
    "PaymentDetails",
    "RegistrationPage",
]
