---
sidebar_position: 1
---

import Link from "@docusaurus/Link";

# Introduction

Welcome to the Databricks Apps Cookbook!

The Databricks Apps Cookbook contains ready-to-use code snippets for building interactive data and AI applications using [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html).

These code snippets cover common use cases such as reading and writing to and from **tables** and **volumes**, invoking traditional **ML models** and GenAI, or triggering **workflows**.

For each snippet, you will find the **source code**, required **permissions**, list of **dependencies**, and any other information needed to implement it.

Currently, we offer snippets for [Streamlit](/docs/category/streamlit), [Dash](/docs/category/dash), [FastAPI](/docs/category/fastapi), and [Reflex](/docs/category/reflex) and they can be easily adapted to other Python frameworks.

<div className="mt-6 flex w-full flex-col items-center justify-center gap-4 sm:flex-row">
    <Link to="/docs/category/streamlit" className="w-full sm:w-auto">
        <button className="inline-flex h-14 w-full items-center justify-center gap-3 border-2 border-lava-600 bg-transparent px-6 py-2.5 text-lg font-semibold text-lava-600 transition-colors hover:border-lava-700 hover:bg-lava-600 hover:text-white">
            <img 
                src="/img/logo_streamlit.svg" 
                alt="Streamlit logo"
                className="h-6 w-6 object-contain" 
            />
            <span>Build with Streamlit</span>
        </button>
    </Link>
    <Link to="/docs/category/dash" className="w-full sm:w-auto">
        <button className="inline-flex h-14 w-full items-center justify-center gap-3 border-2 border-lava-600 bg-transparent px-6 py-2.5 text-lg font-semibold text-lava-600 transition-colors hover:border-lava-700 hover:bg-lava-600 hover:text-white">
            <img 
                src="/img/logo_dash.png" 
                alt="Dash logo"
                className="h-6 w-6 object-contain" 
            />
            <span>Build with Dash</span>
        </button>
    </Link>
    <Link to="/docs/category/fastapi" className="w-full sm:w-auto">
        <button className="inline-flex h-14 w-full items-center justify-center gap-3 border-2 border-lava-600 bg-transparent px-6 py-2.5 text-lg font-semibold text-lava-600 transition-colors hover:border-lava-700 hover:bg-lava-600 hover:text-white">
            <img 
                src="/img/logo_fastapi.svg" 
                alt="FastAPI logo"
                className="h-6 w-6 object-contain" 
            />
            <span>Build with FastAPI</span>
        </button>
    </Link>
    <Link to="/docs/category/reflex" className="w-full sm:w-auto">
        <button className="inline-flex h-14 w-full items-center justify-center gap-3 border-2 border-lava-600 bg-transparent px-6 py-2.5 text-lg font-semibold text-lava-600 transition-colors hover:border-lava-700 hover:bg-lava-600 hover:text-white">
            <img 
                src="/img/logo_reflex.svg" 
                alt="Reflex logo"
                className="h-6 w-6 object-contain" 
            />
            <span>Build with Reflex</span>
        </button>
    </Link>
</div>

## Interactive samples

You can find **interactive sample implementations** for each snippet in the [databricks-apps-cookbook](https://github.com/pbv0/databricks-apps-cookbook) GitHub repository. Take a look at the [deployment instructions](/docs/deploy) to **run them locally** or **deploy to your Databricks workspace**.

![Example banner](./assets/demo.gif)

## Contributing

We welcome contributions! Submit a [pull request](https://github.com/pbv0/databricks-apps-cookbook/pulls) to add or improve recipes. Raise an [issue](https://github.com/pbv0/databricks-apps-cookbook/issues) to report a bug or raise a feature request.
