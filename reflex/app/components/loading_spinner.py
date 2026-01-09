import reflex as rx

def loading_spinner(loading_text: str = "Loading...") -> rx.Component:
    return rx.vstack(
        rx.spinner(size="3", class_name="mb-2"),
        rx.text(loading_text, class_name="text-gray-500 font-medium"),
        align="center",
        justify="center",
        class_name="w-full h-48 bg-gray-50 rounded-lg border border-gray-100",
    )
