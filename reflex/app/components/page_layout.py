import reflex as rx
from app.components.sidebar import sidebar
from app import theme


def main_layout(page_content: rx.Component) -> rx.Component:
    """The main layout for all pages, including sidebar and header."""
    return rx.hstack(
        sidebar(),
        rx.box(
            rx.box(
                rx.heading("Databricks Apps Cookbook", size="6"),
                rx.spacer(),
                class_name="flex items-center h-16 px-6 border-b shadow-sm",
                bg=theme.HEADER_BG,
                border_bottom=f"1px solid {theme.BORDER_COLOR}",
            ),
            rx.box(page_content, class_name="p-6"),
            class_name="flex-1 overflow-y-auto",
        ),
        bg=theme.CONTENT_AREA_BG,
        class_name="h-screen w-full",
        spacing="0",
        align="start",
    )