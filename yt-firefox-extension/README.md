# YouTube Sentiment Insights - Firefox Extension

This Firefox extension analyzes YouTube video comments for sentiment using machine learning. It fetches comments from the current YouTube video page and displays sentiment analysis results including charts, word clouds, and detailed metrics.

## Features

- **Real-time Sentiment Analysis**: Analyzes all available comments from any YouTube video (up to API limits)
- **Inline Comment Sentiment**: Shows sentiment indicators (😊 Positive, 😐 Neutral, 😞 Negative) directly on YouTube comments
- **Visual Analytics**: 
  - Sentiment distribution pie chart
  - Sentiment trend over time graph
  - Word cloud of most common words
- **Detailed Metrics**: 
  - Total comments and unique commenters
  - Average comment length
  - Average sentiment score (0-10 scale)
- **Top Comments Display**: Shows the top 25 comments with their sentiment labels

## Installation

### Quick Start (Without Icons)

If you want to test the extension immediately without creating icons:

1. Rename `manifest-no-icons.json` to `manifest.json` (backup the original first)
2. Follow the installation steps below

### Option 1: Temporary Installation (For Development/Testing)

1. Open Firefox and navigate to `about:debugging`
2. Click on "This Firefox" in the left sidebar
3. Click "Load Temporary Add-on..."
4. Navigate to the `yt-firefox-extension` folder and select the `manifest.json` file
5. The extension should now appear in your Firefox toolbar

### Option 2: Permanent Installation (Requires Signing)

For permanent installation, the extension needs to be signed by Mozilla. You can:
1. Submit it to Mozilla Add-ons store, or
2. Use the AMO (addons.mozilla.org) signing process

## Usage

### Popup Analysis
1. Navigate to any YouTube video page
2. Click on the extension icon in the Firefox toolbar
3. The extension will automatically:
   - Extract the video ID
   - Fetch comments using the YouTube Data API
   - Send comments to the sentiment analysis service
   - Display comprehensive results

### Inline Comment Sentiment
1. Navigate to any YouTube video page
2. Scroll down to the comments section
3. The extension will automatically:
   - Analyze visible comments in real-time
   - Add sentiment indicators next to each comment
   - Update indicators as you scroll and new comments load

## Configuration

The extension uses:
- **YouTube Data API Key**: Configured in the code (from your .env file)
- **Sentiment Analysis API**: Currently pointing to `http://23.20.221.231:8080/`

To modify the API endpoints, edit the `API_URL` variable in `popup.js`.

## API Endpoints Used

The extension communicates with the following endpoints:
- `/predict_with_timestamps` - For sentiment predictions
- `/generate_chart` - For sentiment distribution charts
- `/generate_wordcloud` - For word cloud generation
- `/generate_trend_graph` - For sentiment trend graphs

## Permissions

The extension requests the following permissions:
- `tabs` - To access the current tab's URL
- `activeTab` - To work with the currently active tab
- `storage` - To cache sentiment analysis results
- `http://localhost/*` - For local development API access
- `https://www.googleapis.com/*` - For YouTube Data API access
- `*://www.youtube.com/*` - To inject sentiment indicators on YouTube pages

## Files Structure

```
yt-firefox-extension/
├── manifest.json     # Extension manifest (Firefox Manifest V2)
├── popup.html       # Extension popup UI
├── popup.js         # Main extension logic for popup
├── content.js       # Content script for inline sentiment analysis
├── content.css      # Styles for sentiment indicators
└── README.md        # This file
```

## Differences from Chrome Version

- Uses Manifest V2 (more stable in Firefox)
- Uses `browser.tabs.query()` instead of `chrome.tabs.query()`
- Uses `browser_action` instead of `action` in manifest
- Enhanced error handling and user feedback
- Improved visual indicators for loading states
- **Content script injection** for inline sentiment display on YouTube pages

## Troubleshooting

### Extension doesn't work on YouTube
- Make sure you're on a YouTube video page (`https://www.youtube.com/watch?v=...`)
- Check that the video has comments enabled
- Verify the YouTube API key is valid

### Sentiment indicators not showing on comments
- Make sure you're on a YouTube video page with comments enabled
- Check that the sentiment analysis service is running and accessible
- Scroll down to load more comments - indicators appear as comments are processed
- Check browser console (F12) for any error messages

### Performance issues
- The extension processes comments in batches to avoid overwhelming the API
- Sentiment indicators are cached to avoid re-analyzing the same comments
- If the page feels slow, try refreshing the YouTube page

### Temporary Extension Disappears
- Temporary extensions are removed when Firefox restarts
- You'll need to reload it via `about:debugging` after each restart

## Development

To modify the extension:
1. Edit the relevant files
2. Go to `about:debugging` in Firefox
3. Click "Reload" next to your extension
4. Test the changes

## Support

If you encounter issues:
1. Check the browser console (F12) for error messages
2. Verify all API endpoints are accessible
3. Ensure you're using a valid YouTube video URL
