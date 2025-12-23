#!/bin/bash

# Bundle analyzer script
# Usage: ./scripts/analyze-bundle.sh

echo "🔍 Analyzing bundle size..."
echo ""

# Build with analyzer
ANALYZE=true npm run build

echo ""
echo "✅ Bundle analysis complete!"
echo "📊 Check .next/analyze/ directory for detailed reports"





