import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin();

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: process.env.NEXT_OUTPUT === "export" ? "export" : "standalone",
  images: process.env.NEXT_OUTPUT === "export" ? { unoptimized: true } : undefined,
};

export default withNextIntl(nextConfig);
