---
sidebar_position: 1
---

import Link from "@docusaurus/Link";

# Introduction

Welcome to the Databricks Apps Cookbook!

The Databricks Apps Cookbook contains ready-to-use code snippets for building interactive data and AI applications using [Databricks Apps](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html).

These code snippets cover common use cases such as reading and writing to and from **tables** and **volumes**, invoking traditional **ML models** and GenAI, or triggering **workflows**.

For each snippet, you will find the **source code**, required **permissions**, list of **dependencies**, and any other information needed to implement it.

Currently, we offer snippets for [Streamlit](/docs/category/streamlit), [Dash](/docs/category/dash), and [FastAPI](/docs/category/fastapi) and they can be easily adapted to other Python frameworks.

<div className="mt-4 flex w-full flex-row items-center justify-center space-x-4 sm:w-auto">
    <Link to="/docs/category/streamlit" className="landing-button-horizontal">
        <button className="inline-flex w-full items-center justify-center border-2 border-lava-600 bg-transparent px-8 py-2.5 text-center align-middle text-lg font-semibold text-lava-600 hover:cursor-pointer hover:border-lava-700 hover:underline">
            <div className="flex h-8 items-center">
                <img src="/img/logo_streamlit.svg" className="mr-4 h-6" />
            </div>
            <span className="m-0 p-0">Build with Streamlit</span>
        </button>
    </Link>
    <Link to="/docs/category/dash" className="landing-button-horizontal">
        <button className="inline-flex w-full items-center justify-center border-2 border-lava-600 bg-transparent px-8 py-2.5 text-center align-middle text-lg font-semibold text-lava-600 hover:cursor-pointer hover:border-lava-700 hover:underline">
            <div className="flex h-8 items-center">
                <img src="/img/logo_dash.png" className="mr-4 h-6" />
            </div>
            <span>Build with Dash</span>
        </button>
    </Link>
    <Link to="/docs/category/fastapi" className="landing-button-horizontal">
        <button className="inline-flex w-full items-center justify-center border-2 border-lava-600 bg-transparent px-8 py-2.5 text-center align-middle text-lg font-semibold text-lava-600 hover:cursor-pointer hover:border-lava-700 hover:underline">
            <div className="flex h-8 items-center">
                <img src="/img/logo_fastapi.svg" className="mr-4 h-6" />
            </div>
            <span>Build with FastAPI</span>
        </button>
    </Link>
</div>
<div className="mt-4 flex w-full flex-col items-center justify-center space-y-4 sm:w-auto">
    <Link to="/docs/category/streamlit" className="landing-button-vertical w-full">
        <button className="inline-flex w-full items-center justify-center border-2 border-lava-600 bg-transparent px-8 py-2.5 text-center align-middle text-lg font-semibold text-lava-600 hover:cursor-pointer hover:border-lava-700 hover:underline">
            <div className="flex h-8 items-center">
                <img src="/img/logo_streamlit.svg" className="mr-4 h-6" />
            </div>
            <span className="m-0 p-0">Build with Streamlit</span>
        </button>
    </Link>
    <Link to="/docs/category/dash" className="landing-button-vertical w-full">
        <button className="inline-flex w-full items-center justify-center border-2 border-lava-600 bg-transparent px-8 py-2.5 text-center align-middle text-lg font-semibold text-lava-600 hover:cursor-pointer hover:border-lava-700 hover:underline">
            <div className="flex h-8 items-center">
                <img src="/img/logo_dash.png" className="mr-4 h-6" />
            </div>
            <span>Build with Dash</span>
        </button>
    </Link>
    <Link to="/docs/category/fastapi" className="landing-button-vertical w-full">
        <button className="inline-flex w-full items-center justify-center border-2 border-lava-600 bg-transparent px-8 py-2.5 text-center align-middle text-lg font-semibold text-lava-600 hover:cursor-pointer hover:border-lava-700 hover:underline">
            <div className="flex h-8 items-center">
                <img src="/img/logo_fastapi.svg" className="mr-4 h-6" />
            </div>
            <span>Build with FastAPI</span>
        </button>
    </Link>
</div>

## Interactive samples

You can find **interactive sample implementations** for each snippet in the [databricks-apps-cookbook](https://github.com/pbv0/databricks-apps-cookbook) GitHub repository. Take a look at the [deployment instructions](/docs/deploy) to **run them locally** or **deploy to your Databricks workspace**.

![Example banner](./assets/demo.gif)

## Contributing

We welcome contributions! Submit a [pull request](https://github.com/pbv0/databricks-apps-cookbook/pulls) to add or improve recipes. Raise an [issue](https://github.com/pbv0/databricks-apps-cookbook/issues) to report a bug or raise a feature request.
