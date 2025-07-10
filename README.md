# YouTube Viewer Sentiment Analysis

A machine learning project that analyzes YouTube video comments to determine sentiment (positive, negative, or neutral). This project includes a Flask web API and a Firefox browser extension for real-time sentiment analysis of YouTube comments.

The project features complete MLOps implementation with CI/CD pipeline, Docker containerization, and AWS cloud deployment using ECR for container management, S3 for data storage, and EC2 for hosting.

## Overview

This project was built following a tutorial with some personal modifications. It uses machine learning to classify YouTube comments into different sentiment categories and provides both a web API and browser extension interface. The project demonstrates end-to-end ML deployment with modern DevOps practices including automated testing, containerization, and cloud infrastructure.

## Features

- **Sentiment Analysis**: Classifies YouTube comments into positive, negative, or neutral sentiments
- **Flask Web API**: RESTful API for comment sentiment prediction
- **Firefox Extension**: Browser extension for real-time YouTube comment analysis
- **Data Visualization**: Word clouds and sentiment distribution charts
- **Machine Learning Pipeline**: Complete ML pipeline with preprocessing, training, and evaluation

## Tech Stack

- **Backend**: Flask, Python
- **Machine Learning**: LightGBM, scikit-learn, TF-IDF vectorization
- **Data Processing**: pandas, NumPy, NLTK
- **Visualization**: matplotlib, seaborn, WordCloud
- **MLOps**: MLflow, DVC
- **Frontend**: HTML, CSS, JavaScript (Firefox Extension)
- **Deployment**: CI/CD, Docker, AWS

## Screenshots

### Extension Interface
![Extension Interface](https://raw.githubusercontent.com/arifesat/YoutubeViewerSentiment/refs/heads/main/screenshots/1.png)

### Sentiment Analysis Results
![Sentiment Analysis Results](https://raw.githubusercontent.com/arifesat/YoutubeViewerSentiment/refs/heads/main/screenshots/2.png)

![Word Cloud](https://raw.githubusercontent.com/arifesat/YoutubeViewerSentiment/refs/heads/main/screenshots/3.png)

### Sentiments On Comment Section
![Comment Section](https://raw.githubusercontent.com/arifesat/YoutubeViewerSentiment/refs/heads/main/screenshots/4.png)

## Deployment

### Docker
The project includes Docker containerization for easy deployment and consistent environments across different platforms. The `Dockerfile` provides a complete setup for running the application in a containerized environment.

### CI/CD Pipeline
Continuous Integration and Continuous Deployment pipeline is implemented using GitHub Actions, enabling automated testing, building, and deployment of the application.

### AWS Integration
The project is configured for AWS deployment with:
- **S3**: For storing model artifacts and data files
- **EC2**: For hosting the Flask application
- **ECR**: For storing and managing Docker container images

## Model Information

The project uses a LightGBM classifier with TF-IDF vectorization for text processing. The model was trained on Reddit comment data and fine-tuned for YouTube comment analysis.

## Acknowledgments

This project was developed following a tutorial with additional modifications and improvements. Special thanks to Bappy and freeCodeCamp.

**Tutorial Reference**: [YouTube Sentiment Analysis Tutorial](https://youtu.be/gwNPV882tkc)

