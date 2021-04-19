"""Test basic functionality of the app"""

# Third party imports
import panel as pn
import pytest

# Geo:N:G imports
from app import apps
from app import config


@pytest.fixture
def app():
    """The app object"""
    return apps.view()


@pytest.fixture
def header(app):
    """The header strip"""
    return app.header.objects[0]


@pytest.fixture
def sidebar(app):
    """The sidebar menu"""
    return app.sidebar.objects[0]


@pytest.fixture
def main(app):
    """The main canvas"""
    return app.main.objects[0]


def test_app_alive(app):
    """Test that the app can be rendered"""
    assert app


def test_header_shows_app(header):
    """Test that the header shows name of active app"""
    # Expected title of primary app
    expected = "Deep Marine"

    # Remove Markdown markup
    actual = header.object.strip("# ")

    assert actual == expected


def test_apps_in_sidebar(sidebar):
    """Test that sidebar menu contains links to all apps"""
    expected = [config.app.apps[app].label for app in config.app.apps.apps]
    actual = sidebar._names

    assert actual == expected


def test_apps_on_splash_screen(main):
    """Test that splash screen contains links to all apps"""
    expected = {config.app.apps[app].label for app in config.app.apps.apps}
    buttons = {b.name for b in main.select(pn.widgets.Button)}
    actual = buttons & expected

    assert actual == expected


def test_click_in_sidebar_updates_header(sidebar, header):
    """Test that clicking in the sidebar updates the header"""
    expected = "Instructions"

    # Confirm that header starts with a different text
    actual = header.object.strip("# ")
    assert actual != expected

    # Get Instructions button for Shallow Marine and click it
    button, *_ = [
        button
        for name, menu in zip(sidebar._names, sidebar)
        if name == "Instructions"
        for button in menu
        if button.name == "Shallow Marine"
    ]
    button.clicks += 1

    # Confirm that header has been updated with correct text
    actual = header.object.strip("# ")
    assert actual == expected


def test_click_in_sidebar_updates_main(sidebar, main):
    """Test that clicking in the sidebar updates the main canvas"""

    # Record state of main view at startup
    initial_objects = main.objects.copy()

    # Get the first Deep Marine button and click it
    button, *_ = [
        b for b in sidebar.select(pn.widgets.Button) if b.name == "Deep Marine"
    ]
    button.clicks += 1

    # Confirm that main area has been updated
    assert main.objects != initial_objects


def test_click_in_splash_updates_sidebar(sidebar, main):
    """Test that initiating an app from splash activates app in sidebar"""

    # Record active app in the sidebar
    initial_active = sidebar.active

    # Click the Shallow Marine button on the splash screen
    button, *_ = [
        b for b in main.select(pn.widgets.Button) if b.name == "Shallow Marine"
    ]
    button.clicks += 1

    # Confirm that the active app in the sidebar has been updated
    assert sidebar.active != initial_active
