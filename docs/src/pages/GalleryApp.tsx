import React, { useEffect, useState } from "react";
import Layout from "@theme/Layout";
import { useLocation, useHistory } from "@docusaurus/router";
import { ArrowLeft, Github } from "lucide-react";
import { PortableText } from "@portabletext/react";
import { createClient } from "@sanity/client";
import { Swiper, SwiperSlide } from "swiper/react";
import { Navigation, Pagination } from "swiper/modules";

interface Tag {
  name: string;
  slug: string;
  description?: string;
  borderColor?: string;
  darkBorderColor?: string;
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
  caption?: string;
}

interface App {
  _id: string;
  _createdAt: string;
  title: string;
  slug: string;
  summary: string;
  description?: any; // Portable Text blocks
  useCase: Tag;
  industries: Tag[];
  technologies: Tag[];
  githubUrl: string;
  authors: Author[];
  previewImage: ImageAsset;
  previewImages?: ImageAsset[];
}

const client = createClient({
  projectId: "5f7a73bz",
  dataset: "production",
  useCdn: false,
  apiVersion: "2025-02-06",
});

function GalleryAppPage() {
  const location = useLocation();
  const history = useHistory();
  const [app, setApp] = useState<App | null>(null);
  const [relatedApps, setRelatedApps] = useState<App[]>([]);
  const [loading, setLoading] = useState(true);

  const slug = location.pathname.split("/").filter(Boolean).pop() || "";

  useEffect(() => {
    const fetchApp = async () => {
      try {
        const data: App[] = await client.fetch(
          `
          *[_type == "galleryApp" && slug.current == $slug] {
            _id,
            _createdAt,
            title,
            "slug": slug.current,
            summary,
            description,
            previewImage {
              asset->{
                _id,
                url
              },
              alt
            },
            previewImages[] {
              asset->{
                _id,
                url
              },
              alt,
              caption
            },
            "useCase": useCase->{
              name,
              "slug": slug.current,
              description,
              borderColor,
              darkBorderColor
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
        `,
          { slug },
        );

        const foundApp = data[0] || null;
        setApp(foundApp);

        if (foundApp) {
          const allApps: App[] = await client.fetch(
            `
            *[_type == "galleryApp" && _id != $appId] | order(_createdAt desc) {
              _id,
              _createdAt,
              title,
              "slug": slug.current,
              summary,
              description,
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
                darkBorderColor
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
          `,
            { appId: foundApp._id },
          );

          const scoredApps = allApps
            .map((a) => {
              let score = 0;

              if (a.useCase?.slug === foundApp.useCase?.slug) {
                score += 1;
              }

              const matchingTechnologies = a.technologies.filter((tech) =>
                foundApp.technologies.some((t) => t.slug === tech.slug),
              ).length;
              score += matchingTechnologies;

              const matchingIndustries = a.industries.filter((ind) =>
                foundApp.industries.some((i) => i.slug === ind.slug),
              ).length;
              score += matchingIndustries;

              return { app: a, score };
            })
            .filter(({ score }) => score > 0)
            .sort((a, b) => b.score - a.score)
            .slice(0, 3)
            .map(({ app }) => app);

          setRelatedApps(scoredApps);
        }
      } catch (error) {
        console.error("Error fetching app:", error);
        setApp(null);
      } finally {
        setLoading(false);
      }
    };

    fetchApp();
  }, [slug]);

  if (loading) {
    return (
      <Layout title="Loading...">
        <div className="container mx-auto px-4 py-16">
          <p className="text-center">Loading app details...</p>
        </div>
      </Layout>
    );
  }

  if (!app) {
    return (
      <Layout title="App Not Found">
        <div className="mx-auto max-w-3xl px-4 py-8 md:py-16">
          <h1 className="mb-4 text-2xl font-bold md:text-4xl">App Not Found</h1>
          <p className="mb-6 md:mb-8">
            The app with slug "{slug}" could not be found in the gallery.
          </p>
          <div
            onClick={() => history.push("/gallery")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                history.push("/gallery");
              }
            }}
            className="flex cursor-pointer items-center gap-2 border border-lava-600 bg-lava-600 px-4 py-2 font-semibold text-white transition-colors hover:bg-lava-700 md:px-6 md:py-3"
          >
            <ArrowLeft size={20} />
            Back to Gallery
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout title={app.title}>
      <div className="px-4 py-4 md:py-8">
        <div className="mx-auto max-w-4xl">
          <div
            onClick={() => history.push("/gallery")}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                history.push("/gallery");
              }
            }}
            className="mt-2 mb-6 flex cursor-pointer items-center gap-2 border-0 text-sm text-gray-600 transition-colors hover:text-gray-900 hover:underline md:mt-4 md:mb-8 dark:text-gray-400 dark:hover:text-gray-200"
          >
            <ArrowLeft size={16} />
            Back to Gallery
          </div>
          <div className="mb-6 flex flex-col items-start justify-between gap-4 md:mb-2 md:flex-row md:items-start md:gap-6">
            <div className="min-w-0 flex-1">
              {/* Title */}
              <h1 className="mb-2 text-2xl leading-tight font-bold md:mb-3 md:text-3xl lg:text-4xl">
                {app.title}
              </h1>
              <p className="mb-4 text-sm leading-relaxed text-gray-700 md:mb-6 dark:text-gray-300">
                {app.summary}
              </p>
            </div>
            <a
              href={app.githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex w-full flex-shrink-0 items-center justify-center gap-2 bg-lava-600 px-4 py-2 text-sm font-semibold whitespace-nowrap text-white! transition-colors hover:bg-lava-700 md:w-auto"
            >
              <Github size={16} />
              View Source
            </a>
          </div>

          {/* Preview Image Carousel */}
          <div className="mb-6 overflow-hidden border border-gray-200 bg-gray-100 shadow-lg md:mb-8 dark:border-gray-700 dark:bg-gray-800">
            <Swiper
              modules={[Navigation, Pagination]}
              navigation
              pagination={{ clickable: true }}
              spaceBetween={0}
              slidesPerView={1}
              loop={false}
              className="h-[250px] md:h-[350px] lg:h-[400px]"
            >
              {/* Main preview image as first slide */}
              <SwiperSlide>
                <img
                  src={app.previewImage.asset.url}
                  alt={app.previewImage.alt || `${app.title} preview`}
                  className="h-full w-full object-cover"
                />
              </SwiperSlide>

              {/* Additional preview images */}
              {app.previewImages?.map((image, index) => (
                <SwiperSlide key={image.asset._id || index}>
                  <img
                    src={image.asset.url}
                    alt={image.alt || `${app.title} preview ${index + 2}`}
                    className="h-full w-full object-cover"
                  />
                </SwiperSlide>
              ))}
            </Swiper>
          </div>

          {/* Two column layout for description and metadata */}
          <div className="mb-8 grid grid-cols-1 gap-6 md:mb-12 md:grid-cols-3 md:gap-8">
            {/* Left: Description */}
            <div className="order-2 md:order-1 md:col-span-2">
              {app.description && (
                <div className="prose prose-sm prose-gray dark:prose-invert md:prose-base max-w-none">
                  <PortableText value={app.description} />
                </div>
              )}
            </div>

            {/* Right: Metadata */}
            <div className="order-1 space-y-4 border border-gray-200 bg-gray-50 p-4 md:order-2 md:space-y-6 md:p-6 dark:border-gray-700 dark:bg-gray-800">
              {/* GitHub Repo */}
              <div>
                <h3 className="mb-2 text-sm font-semibold tracking-wide text-gray-600 dark:text-gray-400">
                  GitHub
                </h3>
                <a
                  href={app.githubUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-sm text-gray-700 hover:text-lava-600 dark:text-gray-300 dark:hover:text-lava-500"
                >
                  {app.githubUrl.replace("https://github.com/", "")}
                </a>
              </div>

              {/* Use Case */}
              <div>
                <h3 className="mb-2 text-sm font-semibold tracking-wide text-gray-600 dark:text-gray-400">
                  Use Case
                </h3>
                <span
                  className="inline-block border bg-transparent px-2 py-1 text-xs font-semibold"
                  style={{
                    borderColor: app.useCase.borderColor || "#1B3139",
                    color: app.useCase.borderColor || "#1B3139",
                  }}
                >
                  {app.useCase.name}
                </span>
              </div>

              {/* Industry */}
              <div>
                <h3 className="mb-2 text-sm font-semibold tracking-wide text-gray-600 dark:text-gray-400">
                  Industry
                </h3>
                <div className="flex flex-wrap gap-2">
                  {app.industries.map((industry) => (
                    <span
                      key={industry.slug}
                      className="inline-block border bg-transparent px-2 py-1 text-xs font-medium"
                      style={{
                        borderColor: industry.borderColor || "#095A35",
                        color: industry.borderColor || "#095A35",
                      }}
                    >
                      {industry.name}
                    </span>
                  ))}
                </div>
              </div>

              {/* Technologies */}
              <div>
                <h3 className="mb-2 text-sm font-semibold tracking-wide text-gray-600 dark:text-gray-400">
                  Technologies
                </h3>
                <div className="flex flex-wrap gap-2">
                  {app.technologies.map((tech) => (
                    <span
                      key={tech.slug}
                      className="inline-block border bg-transparent px-2 py-1 text-xs font-medium"
                      style={{
                        borderColor: tech.borderColor || "#04355D",
                        color: tech.borderColor || "#04355D",
                      }}
                    >
                      {tech.name}
                    </span>
                  ))}
                </div>
              </div>

              {/* Authors */}
              <div>
                <h3 className="mb-2 text-sm font-semibold tracking-wide text-gray-600 dark:text-gray-400">
                  {app.authors.length > 1 ? "Authors" : "Author"}
                </h3>
                <div className="space-y-1">
                  {app.authors.map((author, index) => (
                    <div key={index}>
                      {author.linkedinUrl ? (
                        <a
                          href={author.linkedinUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-gray-700 hover:text-lava-600 hover:underline dark:text-gray-300 dark:hover:text-lava-500"
                        >
                          {author.name}
                        </a>
                      ) : (
                        <p className="text-sm text-gray-700 dark:text-gray-300">
                          {author.name}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Related Templates */}
          {relatedApps.length > 0 && (
            <div className="border-t border-gray-300 pt-8 md:pt-12 dark:border-gray-700">
              <h2 className="mb-4 text-xl font-bold md:mb-6 md:text-2xl">
                Related apps
              </h2>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:gap-6 lg:grid-cols-3">
                {relatedApps.map((relatedApp) => (
                  <div
                    key={relatedApp._id}
                    onClick={() => history.push(`/gallery/${relatedApp.slug}`)}
                    className="group cursor-pointer overflow-hidden border border-gray-200 bg-white transition-all hover:shadow-lg dark:border-gray-700 dark:bg-gray-800"
                  >
                    <div className="h-40 w-full overflow-hidden">
                      <img
                        src={relatedApp.previewImage.asset.url}
                        alt={relatedApp.previewImage.alt || relatedApp.title}
                        className="h-full w-full object-cover transition-transform group-hover:scale-105"
                      />
                    </div>
                    <div className="p-4">
                      <h3 className="mb-2 leading-tight font-semibold">
                        {relatedApp.title}
                      </h3>
                      <p className="line-clamp-2 text-sm text-gray-600 dark:text-gray-400">
                        {relatedApp.summary}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

export default GalleryAppPage;
