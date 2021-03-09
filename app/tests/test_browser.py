"""Test UI functionality in the app through the browser (using Selenium)"""

# Standard library imports
import subprocess

# Third party imports
import pytest
from selenium import webdriver


@pytest.fixture
def run_app():
    """Start the app in a separate process"""
    running_app = subprocess.Popen(["panel", "serve", "app"])
    yield running_app
    running_app.terminate()


@pytest.fixture
def app(run_app):
    opts = webdriver.ChromeOptions()
    opts.add_argument("headless")
    app = webdriver.Chrome(executable_path=r"C:\appl\chromedriver.exe", options=opts)
    app.get("http://localhost:5006/")
    return app


@pytest.mark.selenium
def test_app_alive(app):
    """Test that the app responds"""
    assert app.page_source


@pytest.mark.selenium
def test_menu_buttons_available(app):
    """Test that the buttons in the menu can be found"""

    # Find buttons
    buttons = app.find_elements_by_tag_name("button")
    assert buttons


@pytest.mark.selenium
def test_menu_collapsible(app):
    """Test that clicking on a different app changes visible buttons"""

    # Find current buttons
    buttons = app.find_elements_by_tag_name("button")
    labels = [b.text for b in buttons]

    # Click other app
    app_label = "Shallow Marine"
    app_button, *_ = [b for b in buttons if b.text.lower() == app_label.lower()]
    app_button.click()

    # Compare labels
    new_buttons = app.find_elements_by_tag_name("button")
    new_labels = [b.text for b in new_buttons]
    assert new_labels != labels
