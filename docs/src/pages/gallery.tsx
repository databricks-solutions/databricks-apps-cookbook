import React, { useEffect, useState } from "react";
import Layout from "@theme/Layout";
import { Github } from "lucide-react";
import { useHistory, useLocation } from "@docusaurus/router";
import FilterPills from "../components/FilterPills";
import { createClient } from "@sanity/client";
import GalleryAppPage from "./GalleryApp";

interface Tag {
  name: string;
  slug: string;
  description?: string;
  borderColor?: string;
  darkBorderColor?: string;
  frameColor?: string;
}

interface Author {
  name: string;
  linkedinUrl?: string;
}

interface ImageAsset {
  asset: {
    _id: string;
    url: string;
  };
  alt?: string;
}

interface App {
  _id: string;
  _createdAt: string;
  title: string;
  slug: string;
  summary: string;
  useCase: Tag;
  industries: Tag[];
  technologies: Tag[];
  githubUrl: string;
  authors: Author[];
  previewImage: ImageAsset;
}

const client = createClient({
  projectId: "5f7a73bz",
  dataset: "production",
  useCdn: false,
  apiVersion: "2025-02-06",
});

function GalleryPage() {
  const history = useHistory();
  const location = useLocation();
  const [apps, setApps] = useState<App[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [useCases, setUseCases] = useState<string[]>([]);
  const [industries, setIndustries] = useState<string[]>([]);
  const [technologies, setTechnologies] = useState<string[]>([]);
  const [selectedUseCases, setSelectedUseCases] = useState<string[]>([]);
  const [selectedIndustries, setSelectedIndustries] = useState<string[]>([]);
  const [selectedTechnologies, setSelectedTechnologies] = useState<string[]>(
    [],
  );

  // Check if we're on a detail page (e.g., /gallery/pixels)
  const pathParts = location.pathname.split("/").filter(Boolean);
  const isDetailPage = pathParts.length > 1 && pathParts[0] === "gallery";

  // If we're on a detail page, render the GalleryApp component
  if (isDetailPage) {
    return <GalleryAppPage />;
  }

  const filteredApps = apps.filter((app) => {
    const authorString = app.authors.map((a) => a.name).join(" ");
    const industriesString = app.industries.map((i) => i.name).join(" ");
    const technologiesString = app.technologies.map((t) => t.name).join(" ");
    const searchString =
      `${app.title} ${app.summary} ${authorString} ${app.useCase.name} ${industriesString} ${technologiesString}`.toLowerCase();

    const useCaseMatch =
      selectedUseCases.length === 0 ||
      selectedUseCases.includes(app.useCase.name);

    const industryMatch =
      selectedIndustries.length === 0 ||
      app.industries.some((ind) => selectedIndustries.includes(ind.name));

    const technologyMatch =
      selectedTechnologies.length === 0 ||
      app.technologies.some((tech) => selectedTechnologies.includes(tech.name));

    return (
      searchString.includes(searchTerm.toLowerCase()) &&
      useCaseMatch &&
      industryMatch &&
      technologyMatch
    );
  });

  useEffect(() => {
    const fetchApps = async () => {
      try {
        setLoading(true);
        const data: App[] = await client.fetch(`
          *[_type == "galleryApp"] | order(_createdAt desc) {
            _id,
            _createdAt,
            title,
            "slug": slug.current,
            summary,
            previewImage {
              asset->{
                _id,
                url
              },
              alt
            },
            "useCase": useCase->{
              name,
              "slug": slug.current,
              description,
              borderColor,
              darkBorderColor,
              frameColor
            },
            "industries": industries[]->{
              name,
              "slug": slug.current,
              description,
              borderColor,
              darkBorderColor
            },
            "technologies": technologies[]->{
              name,
              "slug": slug.current,
              description,
              borderColor,
              darkBorderColor
            },
            githubUrl,
            "authors": authors[]->{
              name,
              linkedinUrl
            }
          }
        `);

        setApps(data);

        const allUseCases = [
          ...new Set(data.map((app) => app.useCase.name)),
        ].filter((name): name is string => typeof name === "string");
        const allIndustries = [
          ...new Set(data.flatMap((app) => app.industries.map((i) => i.name))),
        ].filter((name): name is string => typeof name === "string");
        const allTechnologies = [
          ...new Set(
            data.flatMap((app) => app.technologies.map((t) => t.name)),
          ),
        ].filter((name): name is string => typeof name === "string");

        setUseCases(allUseCases.sort());
        setIndustries(allIndustries.sort());
        setTechnologies(allTechnologies.sort());
      } catch (error) {
        console.error("Error fetching apps:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchApps();
  }, []);

  return (
    <Layout title="Gallery">
      <div className="px-4 py-8">
        <div className="container mx-auto">
          <h1 className="mb-4 text-4xl font-bold">Databricks Apps Gallery</h1>
          <p className="mb-8">
            Explore applications built with Databricks Apps.
          </p>
          <div className="flex">
            <aside className="hidden w-1/5 pr-8 md:block">
              <input
                type="text"
                placeholder={`Search ${apps.length} apps...`}
                className="mb-4 w-full border border-gray-800 bg-transparent px-4 py-2 text-gray-900 dark:border-gray-400 dark:text-gray-200"
                onChange={(e) => setSearchTerm(e.target.value)}
              />

              <div>
                <h3 className="mb-2 border-l-4 border-lava-600 pl-2 font-semibold dark:border-lava-500">
                  Use Case
                </h3>
                <FilterPills
                  options={useCases}
                  selected={selectedUseCases}
                  onChange={setSelectedUseCases}
                  className="mb-4"
                />
              </div>

              <div className="mt-2">
                <h3 className="mb-2 border-l-4 border-[#095A35] pl-2 font-semibold dark:border-[#10B981]">
                  Industry
                </h3>
                <FilterPills
                  options={industries}
                  selected={selectedIndustries}
                  onChange={setSelectedIndustries}
                  className="mb-4"
                />
              </div>

              <div className="mt-2">
                <h3 className="mb-2 border-l-4 border-[#04355D] pl-2 font-semibold dark:border-[#3B82F6]">
                  Technologies
                </h3>
                <FilterPills
                  options={technologies}
                  selected={selectedTechnologies}
                  onChange={setSelectedTechnologies}
                  className="mb-4"
                />
              </div>
            </aside>
            <main className="w-full md:w-4/5">
              {loading ? (
                <div className="grid grid-cols-1 gap-8 md:grid-cols-2 xl:grid-cols-3">
                  {[...Array(6)].map((_, i) => (
                    <div
                      key={i}
                      className="flex animate-pulse flex-col border bg-[#F9F7F4] shadow-lg dark:border-gray-700 dark:bg-[#242526]"
                    >
                      {/* Preview Image Skeleton */}
                      <div className="w-full overflow-hidden bg-gray-300 p-8 pb-0 dark:bg-gray-600">
                        <div className="mx-auto w-full overflow-hidden rounded-t-md border-t border-r border-l border-gray-300 bg-white dark:border-gray-600 dark:bg-gray-800">
                          <div className="h-40 w-full bg-gray-200 dark:bg-gray-700"></div>
                        </div>
                      </div>

                      {/* Card Content Skeleton */}
                      <div className="flex flex-1 flex-col p-6">
                        {/* Title Skeleton */}
                        <div className="mb-2 h-7 w-3/4 rounded bg-gray-300 dark:bg-gray-600"></div>

                        {/* Summary Skeleton */}
                        <div className="mb-4 flex-1 space-y-2">
                          <div className="h-4 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
                          <div className="h-4 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
                          <div className="h-4 w-2/3 rounded bg-gray-200 dark:bg-gray-700"></div>
                        </div>

                        {/* Badges Skeleton */}
                        <div className="mb-4 flex flex-wrap gap-2">
                          <div className="h-6 w-20 rounded bg-gray-200 dark:bg-gray-700"></div>
                          <div className="h-6 w-24 rounded bg-gray-200 dark:bg-gray-700"></div>
                          <div className="h-6 w-16 rounded bg-gray-200 dark:bg-gray-700"></div>
                        </div>

                        {/* Footer Skeleton */}
                        <div className="border-t border-gray-300 pt-4 dark:border-gray-600">
                          <div className="mb-3 h-4 w-32 rounded bg-gray-200 dark:bg-gray-700"></div>
                          <div className="h-10 w-full rounded bg-gray-200 dark:bg-gray-700"></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-1 gap-8 md:grid-cols-2 xl:grid-cols-3">
                  {filteredApps.map((app) => (
                    <div
                      key={app._id}
                      className="flex cursor-pointer flex-col border bg-[#F9F7F4] shadow-lg transition-shadow hover:shadow-xl dark:border-gray-700 dark:bg-[#242526]"
                      onClick={() => history.push(`/gallery/${app.slug}`)}
                    >
                      {/* Preview Image with Frame */}
                      <div
                        className="w-full overflow-hidden p-8 pb-0"
                        style={{
                          backgroundColor:
                            app.useCase.frameColor ||
                            ["#FF5F47", "#01A770", "#2373B4", "#FFAB00"][
                              Math.abs(
                                app._id
                                  .split("")
                                  .reduce(
                                    (acc, char) => acc + char.charCodeAt(0),
                                    0,
                                  ),
                              ) % 4
                            ],
                        }}
                      >
                        <div className="mx-auto w-full overflow-hidden rounded-t-md border-t border-r border-l border-gray-300 bg-white shadow-sm dark:border-gray-600 dark:bg-gray-800">
                          {/* Browser Bar */}
                          <div className="flex h-4 items-center gap-1 bg-gray-100 px-2 dark:bg-gray-700">
                            <div className="h-1.5 w-1.5 rounded-full bg-gray-300 dark:bg-gray-500"></div>
                            <div className="h-1.5 w-1.5 rounded-full bg-gray-300 dark:bg-gray-500"></div>
                            <div className="h-1.5 w-1.5 rounded-full bg-gray-300 dark:bg-gray-500"></div>
                          </div>
                          {/* Screenshot */}
                          <div className="h-40 w-full overflow-hidden">
                            <img
                              src={app.previewImage.asset.url}
                              alt={
                                app.previewImage.alt || `${app.title} preview`
                              }
                              className="h-full w-full object-cover object-top"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Card Content */}
                      <div className="flex flex-1 flex-col p-6">
                        {/* Title */}
                        <h2 className="mb-2 text-xl font-bold">{app.title}</h2>

                        {/* Summary */}
                        <p className="mb-4 flex-1 text-sm text-gray-700 dark:text-gray-400">
                          {app.summary}
                        </p>

                        {/* Badges */}
                        <div className="mb-4 flex flex-wrap gap-2">
                          <span
                            className="inline-block border bg-transparent px-2 py-1 text-xs font-semibold"
                            style={{
                              borderColor: app.useCase.borderColor || "#FF3621",
                              color: app.useCase.borderColor || "#FF3621",
                            }}
                          >
                            {app.useCase.name}
                          </span>
                          {app.industries.map((industry) => (
                            <span
                              key={industry.slug}
                              className="inline-block border [border-color:var(--industry-light)!important] bg-transparent px-2 py-1 text-xs font-medium [color:var(--industry-light)!important] dark:[border-color:var(--industry-dark)!important] dark:[color:var(--industry-dark)!important]"
                              style={
                                {
                                  "--industry-light":
                                    industry.borderColor || "#095A35",
                                  "--industry-dark":
                                    industry.darkBorderColor || "#10B981",
                                } as React.CSSProperties
                              }
                            >
                              {industry.name}
                            </span>
                          ))}
                          {app.technologies.map((tech) => (
                            <span
                              key={tech.slug}
                              className="inline-block border [border-color:var(--tech-light)!important] bg-transparent px-2 py-1 text-xs font-medium [color:var(--tech-light)!important] dark:[border-color:var(--tech-dark)!important] dark:[color:var(--tech-dark)!important]"
                              style={
                                {
                                  "--tech-light": tech.borderColor || "#04355D",
                                  "--tech-dark":
                                    tech.darkBorderColor || "#3B82F6",
                                } as React.CSSProperties
                              }
                            >
                              {tech.name}
                            </span>
                          ))}
                        </div>

                        {/* Footer: Author and GitHub link */}
                        <div className="border-t border-gray-300 pt-4 dark:border-gray-600">
                          <span className="mb-3 block text-sm text-gray-600 dark:text-gray-400">
                            {app.authors.map((a) => a.name).join(", ")}
                          </span>
                          <a
                            href={app.githubUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="hover:bg-lava-50 dark:hover:bg-lava-950 flex items-center justify-center gap-2 border border-lava-600 px-4 py-2 text-sm font-semibold whitespace-nowrap text-lava-600 transition-colors dark:border-lava-500 dark:text-lava-500"
                            title="View source"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <Github size={18} />
                            Source code
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </main>
          </div>
        </div>
      </div>
    </Layout>
  );
}

export default GalleryPage;
