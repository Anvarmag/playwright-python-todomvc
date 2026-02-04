from __future__ import annotations

import os
from pathlib import Path

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

ARTIFACTS_DIR = Path("test-results")


@pytest.fixture(scope="session")
def browser() -> Browser:
    """
    CI/CD (Continuous Integration / Continuous Delivery) будет запускать headless=true.
    Локально можно включить headless=false через env var PW_HEADLESS=0.
    env var (environment variable) = переменная окружения.
    """
    headless = os.getenv("PW_HEADLESS", "1") == "1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        yield browser
        browser.close()


@pytest.fixture()
def context(request: pytest.FixtureRequest, browser: Browser) -> BrowserContext:
    """
    На каждый тест - новый контекст (чистая сессия).
    Включаем trace, чтобы при падении сохранить запись.
    """
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)

    yield context

    # after test (teardown)
    test_failed = (
        request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    )

    if test_failed:
        trace_path = ARTIFACTS_DIR / f"{request.node.name}-trace.zip"
        context.tracing.stop(path=str(trace_path))
    else:
        context.tracing.stop()

    context.close()


@pytest.fixture()
def page(request: pytest.FixtureRequest, context: BrowserContext) -> Page:
    """
    Если тест упал - делаем screenshot.
    """
    page = context.new_page()
    yield page

    test_failed = (
        request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    )
    if test_failed:
        screenshot_path = ARTIFACTS_DIR / f"{request.node.name}-screenshot.png"
        page.screenshot(path=str(screenshot_path), full_page=True)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """
    Хук pytest: сохраняем результат выполнения теста (passed/failed) в item.
    Это нужно, чтобы фикстуры понимали - упал тест или нет.
    hook = "крючок", точка расширения pytest.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
