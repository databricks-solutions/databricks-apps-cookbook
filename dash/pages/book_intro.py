from dash import html, dcc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import dash

# pages/book_intro.py
dash.register_page(__name__, path="/", title="Introduction", name="Introduction")


def create_group_cards():
    category_metadata = {
        "Tables": {
            "icon": "material-symbols:table",
            "views": ["Read a table", "Edit a table"],
        },
        "Volumes": {
            "icon": "material-symbols:folder",
            "views": ["Upload a file", "Download a file"],
        },
        "AI / ML": {
            "icon": "material-symbols:science",
            "views": ["Invoke a model", "Run vector search", "Connect an MCP server", "Invoke a multi-modal LLM"],
        },
        "Business Intelligence": {
            "icon": "material-symbols:analytics",
            "views": ["AI/BI Dashboard", "Genie"],
        },
        "Workflows": {
            "icon": "material-symbols:workflow",
            "views": ["Trigger a job", "Retrieve job results"],
        },
        "Compute": {"icon": "material-symbols:computer", "views": ["Connect"]},
        "Authentication": {
            "icon": "material-symbols:lock",
            "views": ["Get current user"],
        },
        "External services": {
            "icon": "material-symbols:link",
            "views": ["External connections", "Retrieve a secret"],
        },
    }

    cards = []
    for category, metadata in category_metadata.items():
        category_pages = [
            page
            for page in dash.page_registry.values()
            if page.get("category") == category
        ]

        if category_pages:  # Only create card if there are pages in this category
            # Sort pages according to the specified view order
            ordered_pages = sorted(
                category_pages,
                key=lambda x: metadata["views"].index(x["name"])
                if x["name"] in metadata["views"]
                else len(metadata["views"]),
            )

            cards.append(
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            [
                                                DashIconify(
                                                    icon=metadata["icon"],
                                                    className="me-2",
                                                ),
                                                category,
                                            ],
                                            className="h5 mb-3",
                                        ),
                                        html.Ul(
                                            [
                                                html.Li(
                                                    dcc.Link(
                                                        page["name"],
                                                        href=page["relative_path"],
                                                        className="recipe-link",
                                                        style={
                                                            "display": "block",
                                                            "padding": "8px 12px",
                                                            "borderRadius": "4px",
                                                            "color": "#1b3139",
                                                            "textDecoration": "none",
                                                        },
                                                    )
                                                )
                                                for page in ordered_pages
                                            ],
                                            className="list-unstyled mb-0",
                                        ),
                                    ]
                                )
                            ],
                            className="h-100 bg-light",
                        )
                    ],
                    md=6,
                    lg=4,
                    className="mb-3",
                )
            )

    return cards


def layout():
    return dbc.Container([
        # Header section matching Streamlit style
        dbc.Row([
            dbc.Col([
                html.H1("📖 Databricks Apps Cookbook 🍳", className="mb-3"),
                html.P([
                    "Welcome to the Databricks Apps Cookbook!",
                    html.Br(),
                    html.Br(),
                        "Are you ready to serve some tasty apps to your users? You're in the right place!",
                    html.Br(),
                    html.Br(),
                            "Explore the recipes via the sidebar to quickly build flexible and engaging data apps directly on Databricks.",
                    html.Br(),
                            html.Br(),
                            "Have a great recipe to share? Raise a pull request on the ",
                    html.A("GitHub repository", 
                          href="https://github.com/pbv0/databricks-apps-cookbook",
                                target="_blank",
                          className="text-primary"),
                    "!"
                ], className="mb-4")
            ])
        ]),
        
        # Recipes section
        dbc.Row([
            dbc.Col([
                html.H2("Recipes", className="mb-3"),
                html.Hr(className="mb-4")
            ])
        ]),
        
        # Recipe cards
        dbc.Row(create_group_cards()),
        
        # Links section
        dbc.Row([
            dbc.Col([
                html.H2("Links", className="mb-3 mt-4"),
                html.Hr(className="mb-4")
            ])
        ]),
        
        dbc.Row([
            dbc.Col(md=4, children=[
                html.H4("Official documentation", className="mb-3"),
                html.Ul([
                    html.Li(html.A("AWS", href="https://docs.databricks.com/en/dev-tools/databricks-apps/index.html", target="_blank")),
                    html.Li(html.A("Azure", href="https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/", target="_blank")),
                    html.Li(html.A("Python SDK", href="https://databricks-sdk-py.readthedocs.io/en/latest/", target="_blank"))
                ])
            ]),
            dbc.Col(md=4, children=[
                html.H4("Code samples", className="mb-3"),
                html.Ul([
                    html.Li(html.A("Databricks Apps Templates", href="https://github.com/databricks/app-templates", target="_blank"))
                ])
            ]),
            dbc.Col(md=4, children=[
                html.H4("Blog posts", className="mb-3"),
                html.Ul([
                    html.Li(html.A("End-to-end RAG application with source retrieval on Databricks Platform", 
                                            href="https://www.linkedin.com/pulse/end-to-end-rag-application-source-retriveal-platform-ivan-trusov-znvqf/",
                                  target="_blank")),
                    html.Li(html.A("Building data applications with Databricks Apps", 
                                            href="https://www.linkedin.com/pulse/building-data-applications-databricks-apps-ivan-trusov-6pjwf/",
                                  target="_blank"))
                ])
            ])
        ])
    ], fluid=True)


# Make layout available at module level
__all__ = ["layout"]
