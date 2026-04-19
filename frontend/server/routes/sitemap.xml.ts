export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig(event);
  const apiBase = (config.public.apiBase as string).replace(/\/$/, "");
  const siteUrl = ((config.public.siteUrl as string) || apiBase).replace(/\/$/, "");

  // Tüm yayınlanmış blog postlarını çek (sayfalama olmadan max 500)
  let posts: Array<{ slug: string; slug_tr?: string; updated_at?: string }> = [];
  try {
    let page = 1;
    while (true) {
      const res = await $fetch<{
        items: Array<{ slug: string; slug_tr?: string; updated_at?: string }>;
        total: number;
        page: number;
        page_size: number;
      }>(`${apiBase}/api/v1/blog?page=${page}&page_size=50`);
      posts = posts.concat(res.items);
      if (posts.length >= res.total || res.items.length === 0) break;
      page++;
    }
  } catch {
    // API erişilemiyorsa sadece statik sayfalarla devam et
  }

  const staticUrls = [
    { loc: `${siteUrl}/`, changefreq: "weekly", priority: "1.0" },
    { loc: `${siteUrl}/en/blog`, changefreq: "daily", priority: "0.9" },
    { loc: `${siteUrl}/tr/blog`, changefreq: "daily", priority: "0.9" },
    { loc: `${siteUrl}/stories`, changefreq: "daily", priority: "0.8" },
    { loc: `${siteUrl}/story`, changefreq: "monthly", priority: "0.5" },
  ];

  const urlTags: string[] = [];

  for (const entry of staticUrls) {
    urlTags.push(
      `  <url>\n    <loc>${entry.loc}</loc>\n    <changefreq>${entry.changefreq}</changefreq>\n    <priority>${entry.priority}</priority>\n  </url>`
    );
  }

  for (const post of posts) {
    const lastmod = post.updated_at
      ? `\n    <lastmod>${post.updated_at.slice(0, 10)}</lastmod>`
      : "";

    urlTags.push(
      `  <url>\n    <loc>${siteUrl}/en/blog/${post.slug}</loc>${lastmod}\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>`
    );

    if (post.slug_tr) {
      urlTags.push(
        `  <url>\n    <loc>${siteUrl}/tr/blog/${post.slug_tr}</loc>${lastmod}\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>`
      );
    }
  }

  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...urlTags,
    "</urlset>",
  ].join("\n");

  setHeader(event, "Content-Type", "application/xml");
  return xml;
});
