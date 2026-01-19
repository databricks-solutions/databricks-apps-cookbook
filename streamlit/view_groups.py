groups = [
    {
        "views": [
            {
                "label": "Introduction",
                "help": "",
                "page": "views/book_intro.py",
                "icon": ":material/skillet_cooktop:",
            },
        ],
    },
    {
        "title": "Tables",
        "views": [
            {
                "label": "Read a Lakebase table",
                "help": "Query a Lakebase OLTP database instance table.",
                "page": "views/lakebase_read.py",
                "icon": ":material/database:",
            },
            {
                "label": "Read a Databricks table",
                "help": "Read a Databricks table.",
                "page": "views/tables_read.py",
                "icon": ":material/table_view:",
            },
            {
                "label": "Edit a Databricks table",
                "help": "Interactively edit a Databricks table in the UI.",
                "page": "views/tables_edit.py",
                "icon": ":material/edit_document:",
            },
        ],
    },
    {
        "title": "Volumes",
        "views": [
            {
                "label": "Upload a file",
                "help": "Upload a file into a Unity Catalog Volume.",
                "page": "views/volumes_upload.py",
                "icon": ":material/publish:",
            },
            {
                "label": "Download a file",
                "help": "Download a Volume file.",
                "page": "views/volumes_download.py",
                "icon": ":material/download:",
            },
        ],
    },
    {
        "title": "AI / ML",
        "views": [
            {
                "label": "Invoke a model",
                "help": "Invoke a model across classical ML and Large Language with UI inputs.",
                "page": "views/ml_serving_invoke.py",
                "icon": ":material/experiment:",
            },
            {
                "label": "Invoke amulti-modal LLM",
                "help": "Send text and images for visual-language LLM tasks.",
                "page": "views/ml_serving_invoke_mllm.py",
                "icon": ":material/sensors:",
            },
            {
                "label": "Run vector search",
                "help": "Use Mosaic AI to generate embeddings for textual data and perform vector search.",
                "page": "views/ml_vector_search.py",
                "icon": ":material/search:",
            },
            {
                "label": "Connect to an MCP server",
                "help": "Connect to an MCP server.",
                "page": "views/mcp_connect.py",
                "icon": ":material/modeling:",
            },
        ],
    },
    {
        "title": "Business Intelligence",
        "views": [
            {
                "label": "AI/BI Dashboard",
                "help": "Embed an AI/BI dashboard.",
                "page": "views/embed_dashboard.py",
                "icon": ":material/dashboard:",
            },
            {
                "label": "Genie",
                "help": "Embed a Genie space.",
                "page": "views/genie_api.py",
                "icon": ":material/chat:",
            },
        ],
    },
    {
        "title": "Workflows",
        "views": [
            {
                "label": "Trigger a job",
                "help": "Trigger a job with job parameters.",
                "page": "views/workflows_run.py",
                "icon": ":material/valve:",
            },
            {
                "label": "Retrieve job results",
                "help": "Retrieve results for a Workflow Job run.",
                "page": "views/workflows_get_results.py",
                "icon": ":material/account_tree:",
            },
        ],
    },
    {
        "title": "Compute",
        "views": [
            {
                "label": "Connect to shared cluster",
                "help": "Transform data at scale with UI inputs.",
                "page": "views/compute_connect.py",
                "icon": ":material/lan:",
            },
            {
                "label": "Connect to serverless cluster",
                "help": "Transform data at scale with UI inputs.",
                "page": "views/compute_connect_serverless.py",
                "icon": ":material/lan:",
            },
        ],
    },
    {
        "title": "Unity Catalog",
        "views": [
            {
                "label": "List catalogs and schemas",
                "help": "Get metadata.",
                "page": "views/unity_catalog_get.py",
                "icon": ":material/library_books:",
            },
        ],
    },
    {
        "title": "Authentication",
        "views": [
            {
                "label": "Get current user",
                "help": "Get current App user information.",
                "page": "views/users_get_current.py",
                "icon": ":material/fingerprint:",
            },
            {
                "label": "On-behalf-of-user",
                "help": "Run commands on behalf of a user instead of the app's service principal.",
                "page": "views/users_obo.py",
                "icon": ":material/key:",
            },
        ],
    },
    {
        "title": "Visualizations",
        "views": [
            {
                "label": "Charts",
                "help": "Visualize data using Streamlit's built-in chart components.",
                "page": "views/visualizations_charts.py",
                "icon": ":material/bar_chart:",
            },
            {
                "label": "Map display and interaction",
                "help": "Display geo information on a map and allow users to draw on the map.",
                "page": "views/visualizations_map.py",
                "icon": ":material/globe:",
            },
        ],
    },
    {
        "title": "External services",
        "views": [
            {
                "label": "Use external connections",
                "help": "Use a Unity Catalog-governed HTTP endpoint.",
                "page": "views/external_connections.py",
                "icon": ":material/link:",
            },
            {
                "label": "Retrieve a secret",
                "help": "Get a sensitive API key without hard-coding it.",
                "page": "views/secrets_retrieve.py",
                "icon": ":material/lock:",
            },
        ],
    },
]
