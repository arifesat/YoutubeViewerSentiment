# PowerShell script to generate config.js from .env file
# Run this script to automatically update the extension configuration

Write-Host "🔄 Generating config.js from .env file..." -ForegroundColor Cyan

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$envPath = Join-Path (Split-Path -Parent $scriptDir) ".env"
$configPath = Join-Path $scriptDir "config.js"

Write-Host "📁 Reading .env from: $envPath" -ForegroundColor Yellow
Write-Host "📝 Writing config.js to: $configPath" -ForegroundColor Yellow

# Check if .env file exists
if (-not (Test-Path $envPath)) {
    Write-Host "❌ Error: .env file not found at $envPath" -ForegroundColor Red
    exit 1
}

# Read .env file
$envVars = @{}
try {
    Get-Content $envPath | ForEach-Object {
        $line = $_.Trim()
        if ($line -and !$line.StartsWith('#') -and $line.Contains('=')) {
            $parts = $line.Split('=', 2)
            $key = $parts[0].Trim()
            $value = $parts[1].Trim().Trim("'", '"')
            $envVars[$key] = $value
        }
    }
} catch {
    Write-Host "❌ Error reading .env file: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Get YouTube API key
$youtubeApiKey = if ($envVars.ContainsKey('YT-API')) { $envVars['YT-API'] } else { 'YOUR_API_KEY_HERE' }

if (-not $envVars.ContainsKey('YT-API')) {
    Write-Host "⚠️  Warning: YT-API not found in .env file" -ForegroundColor Yellow
    Write-Host "Make sure your .env file contains: YT-API=your_api_key_here" -ForegroundColor Yellow
}

# Generate config.js content
$configContent = @"
// Configuration file for the Firefox extension
// This file is auto-generated from .env file
// DO NOT edit manually - run generate_config.ps1 instead

const CONFIG = {
  // YouTube Data API key
  YOUTUBE_API_KEY: '$youtubeApiKey',
  
  // Sentiment analysis API endpoint
  API_URL: 'http://23.20.221.231:8080/',
  
  // Alternative endpoints for development
  // API_URL: 'http://localhost:5000/',
  
  // Maximum number of comments to fetch
  MAX_COMMENTS: 500,
  
  // Comments per API request
  COMMENTS_PER_REQUEST: 100
};
"@

# Write config.js file
try {
    $configContent | Out-File -FilePath $configPath -Encoding utf8
    Write-Host "✅ Successfully generated $configPath" -ForegroundColor Green
    Write-Host "🎉 Configuration updated successfully!" -ForegroundColor Green
    Write-Host "🔧 You can now load the Firefox extension" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Error writing config.js: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
