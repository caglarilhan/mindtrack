import type { NextConfig } from "next";
import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin('./i18n.ts');

const nextConfig: NextConfig = {
  eslint: {
    // Build sırasında lint hatalarını engellemeyin
    ignoreDuringBuilds: false,
  },
  typescript: {
    // Build sırasında TS hatalarını engellemeyin
    ignoreBuildErrors: false,
  },
  // Production optimizations
  swcMinify: true,
  compress: true,
  
  // Image optimization
  images: {
    formats: ['image/avif', 'image/webp'],
  },
  
  // Experimental features
  experimental: {
    optimizeCss: true,
  },
  
  // Webpack configuration for bundle optimization
  webpack: (config, { isServer }) => {
    // Tree shaking optimization
    config.optimization = {
      ...config.optimization,
      usedExports: true,
      sideEffects: false,
    };
    
    return config;
  },
};

// Bundle analyzer (only in development when ANALYZE=true)
let finalConfig = withNextIntl(nextConfig);

if (process.env.ANALYZE === 'true') {
  const withBundleAnalyzer = require('@next/bundle-analyzer')({
    enabled: true,
  });
  finalConfig = withBundleAnalyzer(finalConfig);
}

export default finalConfig;
