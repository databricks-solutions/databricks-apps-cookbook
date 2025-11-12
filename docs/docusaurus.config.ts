import { themes as prismThemes } from "prism-react-renderer";
import type { Config } from "@docusaurus/types";
import type * as Preset from "@docusaurus/preset-classic";

const config: Config = {
  title: "Databricks Apps Cookbook",
  tagline:
    "Ready-to-use code snippets for building data and AI applications using Databricks Apps",
  favicon: "img/favicon.ico",

  url: "https://apps-cookbook.dev",
  baseUrl: "/",

  organizationName: "databricks-solutions",
  projectName: "databricks-apps-cookbook",

  onBrokenLinks: "throw",
  onBrokenMarkdownLinks: "warn",

  i18n: {
    defaultLocale: "en",
    locales: ["en"],
  },

  scripts: [
    {
      src: "https://analytics.pascal-vogel.com/js/script.js",
      defer: true,
      "data-domain": "apps-cookbook.dev",
    },
  ],

  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: "./sidebars.ts",
          editUrl:
            "https://github.com/databricks-solutions/databricks-apps-cookbook/edit/main/docs/",
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ["rss", "atom"],
            xslt: true,
          },
          onInlineTags: "warn",
          onInlineAuthors: "warn",
          onUntruncatedBlogPosts: "warn",
        },
        theme: {
          customCss: "./src/css/custom.css",
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    "./src/plugins/tailwind-config.js",
    require.resolve("docusaurus-lunr-search"),
  ],

  themeConfig: {
    image: "img/og-image.png",
    metadata: [
      {
        name: "keywords",
        content: "databricks, databricks apps, streamlit, dash, fastapi",
      },
    ],
    navbar: {
      title: "Databricks Apps Cookbook",
      items: [
        {
          to: "docs/intro",
          label: "Introduction",
          position: "left",
          activeBasePath: "docs/intro",
        },
        {
          to: "docs/category/streamlit",
          label: "Streamlit",
          position: "left",
          activeBasePath: "docs/category/streamlit",
        },
        {
          to: "docs/category/dash",
          label: "Dash",
          position: "left",
          activeBasePath: "docs/category/dash",
        },
        {
          to: "docs/category/fastapi",
          label: "FastAPI",
          position: "left",
          activeBasePath: "docs/category/fastapi",
        },
        { to: "resources", label: "Resources", position: "left" },
        {
          href: "https://github.com/pbv0/databricks-apps-cookbook/",
          label: "GitHub",
          position: "right",
        },
      ],
    },
    footer: {
      copyright: `Copyright © ${new Date().getFullYear()} Databricks Apps Cookbook`,
    },
    prism: {
      theme: prismThemes.vsLight,
      darkTheme: prismThemes.vsDark,
      additionalLanguages: ["bash"],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
