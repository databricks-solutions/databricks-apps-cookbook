import reflex_enterprise as rxe
import reflex as rx

# Minimal config — adjust app_name and other settings as needed.
config = rxe.Config(
    app_name="app",
    use_single_port=True,
    show_built_with_reflex=True,
    plugins=[rx.plugins.TailwindV4Plugin()]
    # output_dir="out",  # optional
)
