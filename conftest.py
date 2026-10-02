"""Pytest fixtures: Playwright lifecycle, page objects, failure screenshots.

Fixture scopes
--------------
playwright_instance  session   one Playwright driver per run
browser              session   one browser process per run
context              function  fresh, isolated context (cookies/storage) per test
page                 function  new tab per test; screenshot on failure; closed after
"""
from __future__ import annotations

from typing import Generator

import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from config.settings import settings
from pages import FlightsPage, HomePage, ItineraryPage, RegistrationPage
from utils.data_loader import get_user
from utils.helpers import safe_file_name
from utils.logger import get_logger

log = get_logger()


# ---------------------------------------------------------------------- #
# Command-line options
# ---------------------------------------------------------------------- #
def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("webtours", "Web Tours UI options")
    group.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run the browser with a visible window.",
    )
    group.addoption(
        "--browser-name",
        action="store",
        default=settings.browser,
        choices=("chromium", "firefox", "webkit"),
        help="Browser engine to use (default: chromium).",
    )
    group.addoption(
        "--base-url",
        action="store",
        default=settings.base_url,
        help="Web Tours URL, e.g. http://192.168.1.183:1080/webtours/",
    )
    group.addoption(
        "--slowmo",
        action="store",
        type=int,
        default=settings.slow_mo,
        help="Slow down every Playwright action by N milliseconds.",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Apply CLI overrides to the shared settings object."""
    base_url = config.getoption("--base-url")
    settings.base_url = base_url if base_url.endswith("/") else base_url + "/"
    settings.browser = config.getoption("--browser-name")
    settings.slow_mo = config.getoption("--slowmo")
    if config.getoption("--headed"):
        settings.headless = False
    settings.screenshots_dir.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------- #
# Make each phase's result available to fixtures (for screenshots)
# ---------------------------------------------------------------------- #
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def _test_failed(request: pytest.FixtureRequest) -> bool:
    for phase in ("setup", "call"):
        report = getattr(request.node, f"rep_{phase}", None)
        if report is not None and report.failed:
            return True
    return False


# ---------------------------------------------------------------------- #
# Playwright lifecycle
# ---------------------------------------------------------------------- #
@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    browser_type = getattr(playwright_instance, settings.browser)
    log.info("Launching %s (headless=%s)", settings.browser, settings.headless)
    browser = browser_type.launch(
        headless=settings.headless, slow_mo=settings.slow_mo
    )
    yield browser
    browser.close()


@pytest.fixture
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    context = browser.new_context(
        viewport=settings.viewport, ignore_https_errors=True
    )
    context.set_default_timeout(settings.default_timeout)
    context.set_default_navigation_timeout(settings.navigation_timeout)
    yield context
    context.close()


@pytest.fixture
def page(
    context: BrowserContext, request: pytest.FixtureRequest
) -> Generator[Page, None, None]:
    page = context.new_page()
    yield page

    if _test_failed(request):
        path = settings.screenshots_dir / f"{safe_file_name(request.node.nodeid)}.png"
        try:
            page.screenshot(path=str(path), full_page=True)
            log.error("Test failed - screenshot saved to %s", path)
            _attach_to_html_report(request, path)
        except Exception as exc:  # noqa: BLE001 - never mask the real failure
            log.warning("Could not capture screenshot: %s", exc)
    page.close()


def _attach_to_html_report(request: pytest.FixtureRequest, path) -> None:
    """Embed the screenshot in pytest-html's report when it is installed."""
    plugin = request.config.pluginmanager.getplugin("html")
    report = getattr(request.node, "rep_call", None)
    if plugin is None or report is None:
        return
    extras = getattr(report, "extras", [])
    extras.append(plugin.extras.png(str(path.resolve())))
    report.extras = extras


# ---------------------------------------------------------------------- #
# Page objects
# ---------------------------------------------------------------------- #
@pytest.fixture
def home_page(page: Page) -> HomePage:
    """Home page already opened in the browser."""
    return HomePage(page).load()


@pytest.fixture
def flights_page(page: Page) -> FlightsPage:
    return FlightsPage(page)


@pytest.fixture
def itinerary_page(page: Page) -> ItineraryPage:
    return ItineraryPage(page)


@pytest.fixture
def registration_page(page: Page) -> RegistrationPage:
    return RegistrationPage(page)


# ---------------------------------------------------------------------- #
# State fixtures
# ---------------------------------------------------------------------- #
@pytest.fixture
def valid_user() -> dict[str, str]:
    return get_user("valid")


@pytest.fixture
def logged_in(home_page: HomePage, valid_user: dict[str, str]) -> HomePage:
    """Home page with the default user logged in."""
    return home_page.login_successfully(valid_user["username"], valid_user["password"])


@pytest.fixture
def empty_itinerary(
    logged_in: HomePage, itinerary_page: ItineraryPage
) -> Generator[HomePage, None, None]:
    """Logged-in user whose itinerary is empty before and after the test."""
    logged_in.go_to_itinerary()
    itinerary_page.cancel_all_flights()
    yield logged_in
    try:
        logged_in.go_to_itinerary()
        itinerary_page.cancel_all_flights()
    except Exception as exc:  # noqa: BLE001 - cleanup must not fail the test
        log.warning("Itinerary cleanup failed: %s", exc)
