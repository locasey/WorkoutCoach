# App Icon

The app icon is located at `frontend/public/icon.svg`.

## Current Icon

A simple, modern running figure icon with a gradient background (purple/blue theme matching the app).

## Using the Icon

The icon is already configured in `frontend/index.html` as:
- Favicon (browser tab icon)
- Apple touch icon (for iOS home screen)

## Generating Additional Formats

If you need different formats or sizes:

### PNG Versions
You can generate PNG versions using:
- Online tools: https://cloudconvert.com/svg-to-png
- ImageMagick: `convert icon.svg -resize 192x192 icon-192.png`
- Or any image editing software

### ICO Format (for Windows)
- Online converter: https://convertio.co/svg-ico/
- Or use: https://favicon.io/favicon-converter/

### Recommended Sizes
- 16x16, 32x32, 48x48 (favicon)
- 192x192, 512x512 (PWA icons)
- 180x180 (Apple touch icon)

## Customizing the Icon

The SVG file (`frontend/public/icon.svg`) can be edited with:
- Any text editor (it's just XML)
- Inkscape (free SVG editor)
- Adobe Illustrator
- Figma
- Online SVG editors

## Alternative: Generate with AI

If you want a different style, you can:
1. Use AI image generators (DALL-E, Midjourney, Stable Diffusion) with prompt: "minimalist running/workout app icon, purple gradient background, white silhouette"
2. Use icon generators like:
   - https://favicon.io/
   - https://www.favicon-generator.org/
   - https://realfavicongenerator.net/

