"""Base page shared by every Web Tours page object.

Web Tours is a frameset application:

    index.htm
    ├── frame "header"            (logo)
    └── frame "body"
        ├── frame "navbar"        (login form / menu buttons)
        └── frame "info"          (main content area)

Playwright's ``frame_locator`` re-resolves the frame on every action, so
the page objects keep working when a frame reloads after a click.
"""
from __future__ import annotations

from playwright.sync_api import FrameLocator, Locator, Page, expect

from config.settings import settings


class BasePage:
    """Common helpers and frame accessors."""

    # Frame selectors: CSS is required here because frames have no role.
    BODY_FRAME = 'frame[name="body"]'
    NAVBAR_FRAME = 'frame[name="navbar"]'
    INFO_FRAME = 'frame[name="info"]'

    def __init__(self, page: Page) -> None:
        self.page = page

    # ------------------------------------------------------------------ #
    # Frames
    # ------------------------------------------------------------------ #
    @property
    def body_frame(self) -> FrameLocator:
        return self.page.frame_locator(self.BODY_FRAME)

    @property
    def navbar(self) -> FrameLocator:
        """Left-hand frame with the login form and menu buttons."""
        return self.body_frame.frame_locator(self.NAVBAR_FRAME)

    @property
    def info(self) -> FrameLocator:
        """Right-hand content frame."""
        return self.body_frame.frame_locator(self.INFO_FRAME)

    # ------------------------------------------------------------------ #
    # Navigation
    # ------------------------------------------------------------------ #
    def open(self, path: str = "") -> None:
        """Open ``settings.base_url`` (plus an optional relative path)."""
        self.page.goto(settings.base_url + path, wait_until="domcontentloaded")

    # ------------------------------------------------------------------ #
    # Generic helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def fill_field(locator: Locator, value: str) -> None:
        """Clear a field and type a value (auto-waits for visibility)."""
        locator.fill(value)

    @staticmethod
    def select_option(locator: Locator, value: str) -> None:
        """Pick a <select> option by its visible label or value."""
        locator.select_option(value)

    def info_text(self) -> str:
        """Whole visible text of the content frame."""
        return self.info.locator("body").inner_text()

    def expect_info_contains(self, text: str) -> None:
        """Assert the content frame shows ``text`` (auto-retrying)."""
        expect(self.info.locator("body")).to_contain_text(text)
