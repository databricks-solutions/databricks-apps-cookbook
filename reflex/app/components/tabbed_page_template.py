import reflex as rx
from typing import Callable, Union
from app.states.tabbed_page_state import TabbedPageState
from app import theme


def placeholder_requirements() -> rx.Component:
    return rx.vstack(
        rx.heading("Requirements", size="4", class_name="font-semibold text-gray-800"),
        rx.text("This component requires the following:", class_name="text-gray-600"),
        rx.el.ul(
            rx.el.li("A configured Databricks workspace."),
            rx.el.li("Appropriate permissions to access the specified resources."),
            rx.el.li("The Reflex library installed and configured."),
            class_name="list-disc list-inside text-gray-600 pl-4",
        ),
        align="start",
        spacing="3",
    )


def _tab_button(name: str, tab_name: str) -> rx.Component:
    """A helper to create a tab button."""
    is_active = TabbedPageState.active_tab == tab_name
    return rx.button(
        name,
        on_click=lambda: TabbedPageState.set_active_tab(tab_name),
        class_name="px-4 py-2 text-sm font-semibold",
        color=rx.cond(is_active, theme.PRIMARY_COLOR, "#6B7280"),
        border_bottom=rx.cond(
            is_active, f"2px solid {theme.PRIMARY_COLOR}", "2px solid transparent"
        ),
        _hover={"background_color": "transparent", "color": theme.PRIMARY_COLOR},
        bg="transparent",
        border="none",
        border_radius="0",
    )


def tabbed_page_template(
    page_title: str,
    page_description: str,
    try_it_content: Callable[[], rx.Component],
    code_snippet_content: Union[str, Callable[[], rx.Component]],
    requirements_content: Callable[[], rx.Component] = placeholder_requirements,
) -> rx.Component:
    """A reusable template for pages with tabs."""
    if isinstance(code_snippet_content, str):
        code_content = rx.code_block(code_snippet_content, language="python")
    else:
        code_content = code_snippet_content()
    return rx.vstack(
        rx.vstack(
            rx.heading(page_title, size="5", class_name="font-bold text-gray-800"),
            rx.text(page_description, class_name="text-gray-600"),
            align="start",
            class_name="mb-6",
        ),
        rx.vstack(
            rx.hstack(
                _tab_button("Try It", "try_it"),
                _tab_button("Code Snippet", "code"),
                _tab_button("Requirements/Details", "requirements"),
                class_name="border-b border-gray-200 w-full",
            ),
            rx.box(
                rx.match(
                    TabbedPageState.active_tab,
                    ("try_it", try_it_content()),
                    ("code", code_content),
                    ("requirements", requirements_content()),
                ),
                class_name="p-4 w-full",
            ),
            align="start",
            class_name="bg-white border border-gray-200 rounded-lg shadow-sm w-full",
        ),
        align="start",
        width="100%",
        spacing="4",
    )