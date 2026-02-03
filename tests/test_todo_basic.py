from playwright.sync_api import Page
from pages.todo_page import TodoPage


def test_add_todo_item(page: Page) -> None:
    """
    E2E (End-to-End) тест: пользователь добавляет задачу и видит её в списке.
    """
    todo = TodoPage(page)
    todo.open()
    todo.add_todo("Buy milk")
    todo.should_have_todo("Buy milk")

