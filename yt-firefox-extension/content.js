// content.js - Content script for YouTube sentiment analysis
// This script runs on YouTube watch pages and adds sentiment indicators to comments

(function() {
  'use strict';
  
  const API_KEY = 'AIzaSyD_2XJ1sZFnvLYfJDF5MgFSty6CRK2QcOE';
  const API_URL = 'http://localhost:5000/';
  
  let processedComments = new Set();
  let isProcessing = false;
  
  // Sentiment cache to avoid re-analyzing the same comments
  let sentimentCache = new Map();
  
  // Initialize the extension
  function init() {
    console.log('YouTube Sentiment Insights: Content script loaded');
    
    // Wait for comments to load and start processing
    waitForComments();
    
    // Set up observer for dynamically loaded comments
    setupCommentObserver();
  }
  
  function waitForComments() {
    const checkInterval = setInterval(() => {
      const comments = document.querySelectorAll('#content-text');
      if (comments.length > 0) {
        clearInterval(checkInterval);
        processVisibleComments();
      }
    }, 1000);
    
    // Stop checking after 30 seconds
    setTimeout(() => clearInterval(checkInterval), 30000);
  }
  
  function setupCommentObserver() {
    const observer = new MutationObserver((mutations) => {
      let hasNewComments = false;
      
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if new comments were added
            if (node.querySelector && node.querySelector('#content-text')) {
              hasNewComments = true;
            }
          }
        });
      });
      
      if (hasNewComments && !isProcessing) {
        setTimeout(processVisibleComments, 1000);
      }
    });
    
    // Observe the comments section
    const commentsSection = document.querySelector('#comments');
    if (commentsSection) {
      observer.observe(commentsSection, {
        childList: true,
        subtree: true
      });
    }
  }
  
  async function processVisibleComments() {
    if (isProcessing) return;
    isProcessing = true;
    
    try {
      const commentElements = document.querySelectorAll('#content-text');
      const newComments = [];
      const commentMap = new Map();
      
      // Collect new comments that haven't been processed
      commentElements.forEach((element, index) => {
        const commentText = element.textContent.trim();
        const commentId = `comment_${index}_${commentText.substring(0, 50)}`;
        
        if (!processedComments.has(commentId) && commentText.length > 0) {
          newComments.push({
            text: commentText,
            timestamp: new Date().toISOString(),
            authorId: `user_${index}`
          });
          commentMap.set(commentText, element);
          processedComments.add(commentId);
        }
      });
      
      if (newComments.length === 0) {
        isProcessing = false;
        return;
      }
      
      console.log(`Processing ${newComments.length} new comments...`);
      
      // Get sentiment predictions
      const predictions = await getSentimentPredictions(newComments);
      
      if (predictions && predictions.length > 0) {
        // Add sentiment indicators to comments
        predictions.forEach((prediction) => {
          const element = commentMap.get(prediction.comment);
          if (element) {
            addSentimentIndicator(element, prediction.sentiment);
          }
        });
      }
      
    } catch (error) {
      console.error('Error processing comments:', error);
    } finally {
      isProcessing = false;
    }
  }
  
  function addSentimentIndicator(commentElement, sentiment) {
    // Check if sentiment indicator already exists
    if (commentElement.querySelector('.sentiment-indicator')) {
      return;
    }
    
    const indicator = document.createElement('span');
    indicator.className = 'sentiment-indicator';
    
    let emoji, color, label;
    switch (sentiment) {
      case "1":
        emoji = '😊';
        color = '#4CAF50';
        label = 'Positive';
        break;
      case "0":
        emoji = '😐';
        color = '#FF9800';
        label = 'Neutral';
        break;
      case "-1":
        emoji = '😞';
        color = '#F44336';
        label = 'Negative';
        break;
      default:
        emoji = '❓';
        color = '#9E9E9E';
        label = 'Unknown';
    }
    
    indicator.innerHTML = `
      <span class="sentiment-emoji">${emoji}</span>
      <span class="sentiment-label">${label}</span>
    `;
    
    indicator.style.cssText = `
      display: inline-flex;
      align-items: center;
      gap: 4px;
      margin-left: 8px;
      padding: 2px 6px;
      background-color: ${color}20;
      border: 1px solid ${color};
      border-radius: 12px;
      font-size: 11px;
      font-weight: 500;
      color: ${color};
      vertical-align: middle;
    `;
    
    // Add the indicator after the comment text
    commentElement.appendChild(indicator);
  }
  
  async function getSentimentPredictions(comments) {
    try {
      const response = await fetch(`${API_URL}/predict_with_timestamps`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ comments })
      });
      
      const result = await response.json();
      if (response.ok) {
        return result;
      } else {
        throw new Error(result.error || 'Error fetching predictions');
      }
    } catch (error) {
      console.error("Error fetching sentiment predictions:", error);
      return null;
    }
  }
  
  // Start the extension when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
  // Also restart when navigating to a new video (YouTube SPA)
  let currentUrl = location.href;
  const urlObserver = new MutationObserver(() => {
    if (location.href !== currentUrl) {
      currentUrl = location.href;
      // Reset processed comments for new video
      processedComments.clear();
      sentimentCache.clear();
      setTimeout(init, 2000); // Wait for new page to load
    }
  });
  
  urlObserver.observe(document, { subtree: true, childList: true });
  
})();
