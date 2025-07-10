// Configuration file for the Firefox extension
// DO NOT commit this file to version control if it contains sensitive data

const CONFIG = {
  // YouTube Data API key - replace with your actual key
  YOUTUBE_API_KEY: 'YOUR_API_KEY_HERE',
  
  // Sentiment analysis API endpoint
  API_URL: 'http://23.20.221.231:8080/',
  
  // Alternative endpoints for development
  // API_URL: 'http://localhost:5000/',
  
  // Maximum number of comments to fetch
  MAX_COMMENTS: 500,
  
  // Comments per API request
  COMMENTS_PER_REQUEST: 100
};
