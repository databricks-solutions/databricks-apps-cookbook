import React, { useEffect, useState } from "react";
import Layout from "@theme/Layout";

interface Author {
  name: string;
  url?: string;
}

interface Resource {
  title: string;
  date: string;
  authors?: Author[];
  type: string;
  category: string;
  url: string;
  summary?: string;
  repo_org?: string;
  repo_name?: string;
}

function ResourcesPage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [categories, setCategories] = useState<string[]>([]);
  const [types, setTypes] = useState<string[]>([]);
  const [years, setYears] = useState<string[]>([]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [selectedYears, setSelectedYears] = useState<string[]>([]);

  const handleFilterChange = (setter, value) => {
    setter((prev) =>
      prev.includes(value)
        ? prev.filter((item) => item !== value)
        : [...prev, value],
    );
  };

  const filteredResources = resources.filter((resource) => {
    const authorString = resource.authors
      ? resource.authors.map((a) => a.name).join(" ")
      : "";
    const repoString =
      resource.repo_org && resource.repo_name
        ? `${resource.repo_org} ${resource.repo_name}`
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
    fetch("/resources.json")
      .then((response) => response.json())
      .then((data: Resource[]) => {
        const sortedData = data.sort(
          (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime(),
        );
        setResources(sortedData);
        const allCategories = [...new Set(data.map((r) => r.category))];
        const allTypes = [...new Set(data.map((r) => r.type))];
        const allYears = [
          ...new Set(
            data.map((r) => new Date(r.date).getFullYear().toString()),
          ),
        ];
        setCategories(allCategories.sort());
        setTypes(allTypes.sort());
        setYears(allYears.sort().reverse());
      });
  }, []);

  return (
    <Layout title="Resources">
      <div className="px-4 py-8">
        <div className="container mx-auto">
          <h1 className="mb-4 text-4xl font-bold">Databricks Apps Resources</h1>
          <p className="mb-8">
            A collection of resources for building data and AI applications
            using Databricks Apps. Submit a resource by{" "}
            <a
              href="https://github.com/databricks-solutions/databricks-apps-cookbook/pulls"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline"
            >
              raising a PR
            </a>{" "}
            or using{" "}
            <a
              href="https://docs.google.com/forms/d/e/1FAIpQLSe8rW3XUbCDMK2OsgPVVqfKYuVgw4FlnoWHkAksMJTNwKhibQ/viewform?usp=dialog"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:underline"
            >
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
                {categories.map((category) => (
                  <div key={category}>
                    <input
                      type="checkbox"
                      id={category}
                      value={category}
                      onChange={() =>
                        handleFilterChange(setSelectedCategories, category)
                      }
                    />
                    <label htmlFor={category} className="ml-2">
                      {category}
                    </label>
                  </div>
                ))}
              </div>

              <div className="mt-4">
                <h3 className="mb-2 font-semibold">Type</h3>
                {types.map((type) => (
                  <div key={type}>
                    <input
                      type="checkbox"
                      id={type}
                      value={type}
                      onChange={() =>
                        handleFilterChange(setSelectedTypes, type)
                      }
                    />
                    <label htmlFor={type} className="ml-2">
                      {type}
                    </label>
                  </div>
                ))}
              </div>

              <div className="mt-4">
                <h3 className="mb-2 font-semibold">Year</h3>
                {years.map((year) => (
                  <div key={year}>
                    <input
                      type="checkbox"
                      id={year}
                      value={year}
                      onChange={() =>
                        handleFilterChange(setSelectedYears, year)
                      }
                    />
                    <label htmlFor={year} className="ml-2">
                      {year}
                    </label>
                  </div>
                ))}
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
                        resource.repo_org &&
                        resource.repo_name ? (
                          <a
                            href={resource.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:underline"
                          >
                            {resource.repo_org}/{resource.repo_name}
                          </a>
                        ) : (
                          resource.authors?.map((author, index) => (
                            <React.Fragment key={author.name}>
                              {author.url ? (
                                <a
                                  href={author.url}
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
