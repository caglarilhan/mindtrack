/**
 * Bundle optimization utilities
 * Helps identify and optimize bundle size
 */

/**
 * Check if a package is actually used in the codebase
 */
export function isPackageUsed(packageName: string): boolean {
  // This would be used with a tool like depcheck
  // For now, it's a placeholder
  return true;
}

/**
 * Get bundle size recommendations
 */
export const BUNDLE_RECOMMENDATIONS = {
  // Target bundle sizes (gzipped)
  initial: 200 * 1024, // 200KB
  route: 100 * 1024, // 100KB per route
  chunk: 50 * 1024, // 50KB per chunk
  
  // Optimization strategies
  strategies: [
    "Use dynamic imports for heavy libraries",
    "Tree-shake unused exports",
    "Optimize images (use next/image)",
    "Use font subsetting",
    "Remove unused dependencies",
    "Code split by route",
    "Lazy load components",
  ],
} as const;

/**
 * Common heavy packages that should be lazy loaded
 */
export const HEAVY_PACKAGES = [
  "recharts",
  "jspdf",
  "docx",
  "file-saver",
  "@google/generative-ai",
  "openai",
] as const;





