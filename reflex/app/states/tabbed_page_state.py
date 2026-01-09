import reflex as rx


class TabbedPageState(rx.State):
    """State to manage the active tab in the tabbed page template."""

    active_tab: str = "try_it"

    @rx.event
    def set_active_tab(self, tab_name: str):
        """Set the currently active tab."""
        self.active_tab = tab_name