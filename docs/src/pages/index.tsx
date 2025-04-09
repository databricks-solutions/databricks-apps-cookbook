import type { ReactNode } from "react";
import Link from "@docusaurus/Link";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import Layout from "@theme/Layout";
import Heading from "@theme/Heading";
import HeaderAnimation from "../components/HeaderAnimation";
import { useColorMode } from "@docusaurus/theme-common";

function HomepageHeader() {
  const { siteConfig } = useDocusaurusContext();
  const { colorMode } = useColorMode();
  const isDarkTheme = colorMode === "dark";

  return (
    <div className="relative flex h-full w-full flex-1 items-center justify-center overflow-hidden">
      <HeaderAnimation isDarkMode={isDarkTheme} />
      <div className="absolute z-10 flex w-full flex-col items-center justify-center px-6 text-center text-white">
        <Heading
          as="h1"
          className="font-bold text-gray-800 xs:text-5xl sm:text-6xl md:text-7xl dark:text-white"
        >
          {siteConfig.title}
        </Heading>
        <p className="mt-2 max-w-3xl text-gray-800 xs:text-xl md:mt-4 md:text-3xl md:leading-10 dark:text-white">
          {siteConfig.tagline}
        </p>
        <div className="mt-2 flex w-full flex-row items-center justify-center space-x-4 sm:w-auto">
          <Link
            to="/docs/category/streamlit"
            className="landing-button-horizontal"
          >
            <button className="w-full border-2 border-lava-600 bg-lava-600 px-8 py-2.5 align-middle font-semibold text-white hover:cursor-pointer hover:border-lava-700 hover:bg-lava-700 hover:underline xs:text-lg">
              Streamlit
            </button>
          </Link>
          <Link to="/docs/category/dash" className="landing-button-horizontal">
            <button className="w-full border-2 border-lava-600 bg-lava-600 px-8 py-2.5 align-middle font-semibold text-white hover:cursor-pointer hover:border-lava-700 hover:bg-lava-700 hover:underline xs:text-lg">
              Dash
            </button>
          </Link>
          <Link to="/docs/intro" className="landing-button-horizontal">
            <button className="w-full border-2 border-gray-800 bg-transparent px-8 py-2.5 align-middle font-semibold text-gray-800 hover:cursor-pointer hover:underline xs:text-lg dark:border-white dark:text-white">
              Learn more
            </button>
          </Link>
        </div>
        <div className="mt-2 flex w-full flex-col items-center justify-center space-y-4 sm:w-auto">
          <Link
            to="/docs/category/streamlit"
            className="landing-button-vertical w-full"
          >
            <button className="w-full border-2 border-lava-600 bg-lava-600 px-8 py-2.5 align-middle font-semibold text-white hover:cursor-pointer hover:border-lava-700 hover:bg-lava-700 hover:underline xs:text-lg">
              Streamlit
            </button>
          </Link>
          <Link
            to="/docs/category/dash"
            className="landing-button-vertical w-full"
          >
            <button className="w-full border-2 border-lava-600 bg-lava-600 px-8 py-2.5 align-middle font-semibold text-white hover:cursor-pointer hover:border-lava-700 hover:bg-lava-700 hover:underline xs:text-lg">
              Dash
            </button>
          </Link>
          <Link to="/docs/intro" className="landing-button-vertical w-full">
            <button className="w-full border-2 border-gray-800 bg-transparent px-8 py-2.5 align-middle font-semibold text-gray-800 hover:cursor-pointer hover:underline xs:text-lg dark:border-white dark:text-white">
              Learn more
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function Home(): ReactNode {
  const { siteConfig } = useDocusaurusContext();
  return (
    <Layout description={`${siteConfig.tagline}`}>
      <HomepageHeader />
    </Layout>
  );
}
