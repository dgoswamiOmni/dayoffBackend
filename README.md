
# DayOff Backend

## Overview

The DayOff Backend is the serverless component of the DayOff application, leveraging AWS Lambda and S3 for its infrastructure,built with FastAPI in Python and Docker for containerization. It handles data storage, retrieval, and processing for event management.

## Features

- **Event Management**: Create, update, and delete events.
- **User Authentication**: Secure user authentication and authorization.
- **Data Persistence**: Store event and user data reliably.
- **API Endpoints**: Exposes RESTful API endpoints for client communication.
- - **Data Persistence**: Store event and user data reliably using AWS S3.


## Technologies Used

- **FastAPI**: FastAPI is a modern, fast (high-performance) web framework for building APIs with Python.
- **Docker**: Docker is used for containerization, making it easy to package the application and its dependencies into a standardized unit.
- **MongoDB**: MongoDB is a document-oriented NoSQL database used for data storage.
- **PyMongo**: PyMongo is the Python driver for MongoDB, used for interacting with the MongoDB database.
- **JWT (JSON Web Tokens)**: JWT is used for user authentication and token-based access control.
- - **AWS Lambda**: Serverless compute service for running code without provisioning or managing servers.
- **AWS S3**: Object storage service for storing and retrieving data.



## Getting Started

1. **Clone the repository**: `git clone <repository-url>`
2. **Install Docker and Docker Compose**: Follow the instructions on the Docker website to install Docker and Docker Compose for your operating system.
3. **Set up environment variables**: Create a `.env` file and add necessary environment variables like `MONGO_URI`, `JWT_SECRET`, etc.
4. **Build and run the Docker containers**: Run `docker-compose up --build` to build the Docker containers and start the application.

## API Documentation

The API documentation will be available at `http://0.0.0.0:8000/docs` after the application is running.

## Licensing

This project is currently under development and its licensing information will be added soon. Stay tuned!

