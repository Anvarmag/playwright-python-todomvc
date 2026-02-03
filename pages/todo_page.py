import re
from playwright.sync_api import Page, expect


class TodoPage:
    """
    Page Object для TodoMVC.
    POM (Page Object Model) - выносим селекторы и действия на страницу в отдельный класс,
    чтобы тесты читались как сценарии.
    """

    URL = "https://demo.playwright.dev/todomvc/"

    # Селекторы
    NEW_TODO_INPUT = "input.new-todo"
    TODO_ITEMS = "ul.todo-list li"
    FILTER_ALL = "a:has-text('All')"
    FILTER_ACTIVE = "a:has-text('Active')"
    FILTER_COMPLETED = "a:has-text('Completed')"

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self) -> None:
        self.page.goto(self.URL)
        expect(self.page).to_have_url(re.compile(r"^https://demo\.playwright\.dev/todomvc/.*$"))
       
    def add_todo(self, text: str) -> None:
        self.page.fill(self.NEW_TODO_INPUT, text)
        self.page.press(self.NEW_TODO_INPUT, "Enter")

    def should_have_todo(self, text: str) -> None:
        item = self.page.locator(self.TODO_ITEMS).filter(has_text=text)
        expect(item).to_have_count(1)

    def todos_count(self) -> int:
        return self.page.locator(self.TODO_ITEMS).count()
