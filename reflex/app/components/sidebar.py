import reflex as rx
from app.states.cookbook_state import CookbookState
from app import theme


def nav_link(item: dict) -> rx.Component:
    """A navigation link component."""
    is_active = CookbookState.current_page_path == item["path"]
    return rx.link(
        rx.text(item["name"], class_name="truncate"),
        href=item["path"],
        class_name="flex items-center w-full px-4 py-2 text-sm font-semibold rounded-lg",
        bg=rx.cond(is_active, theme.ACTIVE_ITEM_BG, "transparent"),
        color=rx.cond(is_active, theme.ACTIVE_ITEM_TEXT, theme.SIDEBAR_TEXT),
        _hover={"background_color": theme.ACTIVE_ITEM_BG, "opacity": 0.8},
    )


def nav_section(section: dict) -> rx.Component:
    """A navigation section component with a collapsible header."""
    return rx.vstack(
        rx.button(
            rx.hstack(
                rx.icon(
                    tag=section["icon"],
                    class_name="h-5 w-5 mr-3",
                    color=theme.SIDEBAR_TEXT,
                ),
                rx.text(
                    section["section_name"],
                    class_name="font-semibold",
                    color=theme.SIDEBAR_TEXT,
                ),
                justify="start",
            ),
            rx.icon(
                tag=rx.cond(
                    CookbookState.collapsed_sections[section["section_name"]],
                    "chevron-right",
                    "chevron-down",
                ),
                class_name="h-5 w-5",
                color=theme.SIDEBAR_TEXT,
            ),
            on_click=lambda: CookbookState.toggle_section(section["section_name"]),
            class_name="flex items-center justify-between w-full p-2 rounded-lg",
            style={
                "_hover": {"background_color": theme.ACTIVE_ITEM_BG, "opacity": 0.8}
            },
            width="100%",
        ),
        rx.vstack(
            rx.foreach(section["items"], nav_link),
            class_name=rx.cond(
                CookbookState.collapsed_sections[section["section_name"]],
                "hidden",
                "flex flex-col gap-1 mt-2 pl-6 ml-2.5",
            ),
            style={"border_left_color": theme.BORDER_COLOR},
        ),
        class_name="w-full",
        align="start",
    )


def sidebar() -> rx.Component:
    """The sidebar component for navigation."""
    return rx.box(
        rx.vstack(
            rx.box(
                rx.link(rx.image(src="/logo.svg", class_name="h-12 w-auto"), href="/"),
                class_name="flex items-center justify-start h-16 border-b px-8",
                border_bottom=f"1px solid {theme.BORDER_COLOR}",
            ),
            rx.vstack(
                nav_link({"name": "Introduction", "path": "/introduction"}),
                rx.foreach(CookbookState.navigation_items, nav_section),
                class_name="flex flex-col gap-2 p-4",
            ),
            class_name="flex-1 overflow-y-auto",
            align="start",
        ),
        class_name="hidden md:flex flex-col w-72 h-screen shrink-0",
        bg=theme.SIDEBAR_BG,
    )