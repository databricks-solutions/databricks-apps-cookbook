import React, { useEffect, useState } from "react";
import Layout from "@theme/Layout";
import { createClient } from "@sanity/client";
import FilterPills from "../components/FilterPills";

interface Author {
  name: string;
  linkedinUrl?: string;
}

interface Resource {
  title: string;
  date: string;
  authors?: Author[];
  type: string;
  category: string;
  url: string;
  summary?: string;
  repoOrg?: string;
  repoName?: string;
}

const client = createClient({
  projectId: "5f7a73bz",
  dataset: "production",
  useCdn: false,
  apiVersion: "2025-02-06",
});

function ResourcesPage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [categories, setCategories] = useState<string[]>([]);
  const [types, setTypes] = useState<string[]>([]);
  const [years, setYears] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [selectedYears, setSelectedYears] = useState<string[]>([]);

  // no-op helper removed; selection handled inside FilterPills

  const filteredResources = resources.filter((resource) => {
    const authorString = resource.authors
      ? resource.authors.map((a) => a.name).join(" ")
      : "";
    const repoString =
      resource.repoOrg && resource.repoName
        ? `${resource.repoOrg} ${resource.repoName}`
        : "";
    const searchString =
      `${resource.title} ${resource.summary} ${authorString} ${repoString} ${resource.type} ${resource.category}`.toLowerCase();
    const year = new Date(resource.date).getFullYear().toString();

    return (
      searchString.includes(searchTerm.toLowerCase()) &&
      (selectedCategories.length === 0 ||
        selectedCategories.includes(resource.category)) &&
      (selectedTypes.length === 0 || selectedTypes.includes(resource.type)) &&
      (selectedYears.length === 0 || selectedYears.includes(year))
    );
  });

  useEffect(() => {
    const fetchResources = async () => {
      try {
        const data: Resource[] = await client.fetch(`
          *[_type == "resource"] | order(date desc) {
            ...,
            "authors": authors[]->{ name, linkedinUrl },
            "category": category->title,
            "type": type->title
          }
        `);

        setResources(data);
        const allCategories = [...new Set(data.map((r) => r.category))].filter(
          (cat): cat is string => typeof cat === "string",
        );
        const allTypes = [...new Set(data.map((r) => r.type))].filter(
          (type): type is string => typeof type === "string",
        );
        const allYears = [
          ...new Set(
            data.map((r) => new Date(r.date).getFullYear().toString()),
          ),
        ].filter((year): year is string => typeof year === "string");
        const sortedCategories = allCategories.sort();
        const sortedTypes = allTypes.sort();
        const sortedYears = allYears.sort().reverse();
        setCategories(sortedCategories);
        setTypes(sortedTypes);
        setYears(sortedYears);
        // Keep selections empty so empty means "show all"
        setSelectedCategories([]);
        setSelectedTypes([]);
        setSelectedYears([]);
      } catch (error) {
        console.error("Error fetching resources:", error);
      }
    };

    fetchResources();
  }, []);

  return (
    <Layout title="Resources">
      <div className="px-4 py-8">
        <div className="container mx-auto">
          <h1 className="mb-4 text-4xl font-bold">Databricks Apps Resources</h1>
          <p className="mb-8">
            A collection of resources for building data and AI applications
            using Databricks Apps. Submit a resource using
            <a
              href="https://docs.google.com/forms/d/e/1FAIpQLSe8rW3XUbCDMK2OsgPVVqfKYuVgw4FlnoWHkAksMJTNwKhibQ/viewform?usp=dialog"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline"
            >
              {" "}
              this form
            </a>
            .
          </p>
          <div className="flex">
            <aside className="hidden w-1/5 pr-8 md:block">
              <input
                type="text"
                placeholder={`Search ${resources.length} resources...`}
                className="mb-4 w-full border border-gray-800 bg-transparent px-4 py-2 text-gray-900 dark:border-gray-400 dark:text-gray-200"
                onChange={(e) => setSearchTerm(e.target.value)}
              />

              <div>
                <h3 className="mb-2 font-semibold">Category</h3>
                <FilterPills
                  options={categories}
                  selected={selectedCategories}
                  onChange={setSelectedCategories}
                  className="mb-4"
                />
              </div>

              <div className="mt-2">
                <h3 className="mb-2 font-semibold">Type</h3>
                <FilterPills
                  options={types}
                  selected={selectedTypes}
                  onChange={setSelectedTypes}
                  className="mb-4"
                />
              </div>

              <div className="mt-2">
                <h3 className="mb-2 font-semibold">Year</h3>
                <FilterPills
                  options={years}
                  selected={selectedYears}
                  onChange={setSelectedYears}
                />
              </div>
            </aside>
            <main className="w-full md:w-4/5">
              <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
                {filteredResources.map((resource, index) => (
                  <div
                    key={index}
                    className="border bg-[#F9F7F4] p-6 shadow-lg transition-shadow hover:shadow-xl dark:border-gray-700 dark:bg-[#242526]"
                  >
                    <h2 className="mb-2 text-xl font-bold">
                      <a
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-lava-600 hover:underline dark:text-lava-500"
                      >
                        {resource.title}
                      </a>
                    </h2>
                    <div className="mb-4 text-sm text-gray-400">
                      <span>
                        {new Date(resource.date).toLocaleDateString()}
                      </span>{" "}
                      |{" "}
                      <span className="font-bold">
                        {resource.type === "Code sample" &&
                        resource.repoOrg &&
                        resource.repoName ? (
                          <a
                            href={resource.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:underline"
                          >
                            {resource.repoOrg}/{resource.repoName}
                          </a>
                        ) : (
                          resource.authors?.map((author, index) => (
                            <React.Fragment key={author.name}>
                              {author.linkedinUrl ? (
                                <a
                                  href={author.linkedinUrl}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="hover:underline"
                                >
                                  {author.name}
                                </a>
                              ) : (
                                author.name
                              )}
                              {index < resource.authors.length - 1 && ", "}
                            </React.Fragment>
                          ))
                        )}
                      </span>
                    </div>
                    {resource.summary && (
                      <p className="group text-sm text-gray-700 dark:text-gray-400">
                        <span className="group-hover:hidden">
                          {resource.summary.substring(0, 100)}...
                        </span>
                        <span className="hidden group-hover:inline">
                          {resource.summary}
                        </span>
                      </p>
                    )}
                    <div className="mt-4 text-sm font-medium">
                      <span className="mr-2 mb-2 inline-block border border-lava-600 bg-transparent px-3 py-1 text-sm font-semibold text-lava-600 dark:border-lava-500 dark:text-lava-500">
                        {resource.type}
                      </span>
                      <span className="mr-2 mb-2 inline-block border border-[#1B3139] bg-transparent px-3 py-1 text-sm font-semibold text-[#1B3139] dark:border-gray-500 dark:text-gray-400">
                        {resource.category}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </main>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default ResourcesPage;
