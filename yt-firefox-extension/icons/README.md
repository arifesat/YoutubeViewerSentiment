# Icon Creation Instructions

This directory should contain icon files for the Firefox extension. You'll need to create PNG files with the following dimensions:

- `icon-16.png` - 16x16 pixels
- `icon-32.png` - 32x32 pixels  
- `icon-48.png` - 48x48 pixels
- `icon-96.png` - 96x96 pixels

## Creating Icons

You can create these icons using any image editor (GIMP, Photoshop, Canva, etc.) or use online icon generators.

### Design Suggestions:
- Use a YouTube-related theme (play button, speech bubble, sentiment face)
- Include sentiment analysis elements (charts, graphs, emoji)
- Use colors that contrast well with Firefox's interface
- Keep the design simple and recognizable at small sizes

### Quick Option:
1. Create a simple design with a red play button (YouTube theme) and a small chart/graph icon
2. Use a transparent background
3. Export as PNG files in the required sizes

### Alternative:
You can temporarily remove the icon references from manifest.json if you want to test the extension without icons first. Just remove the "icons" section and the "default_icon" from "browser_action".
