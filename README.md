Day Of Backend
Overview
The Day Of Backend is the server-side component of the Day Of application, built with FastAPI in Python and Docker for containerization. It handles data storage, retrieval, and processing for event management.

Features
Event Management: Create, update, and delete events.
User Authentication: Secure user authentication and authorization.
Data Persistence: Store event and user data reliably.
API Endpoints: Exposes RESTful API endpoints for client communication.
Technologies Used
FastAPI: FastAPI is a modern, fast (high-performance) web framework for building APIs with Python.
Docker: Docker is used for containerization, making it easy to package the application and its dependencies into a standardized unit.
MongoDB: MongoDB is a document-oriented NoSQL database used for data storage.
PyMongo: PyMongo is the Python driver for MongoDB, used for interacting with the MongoDB database.
JWT (JSON Web Tokens): JWT is used for user authentication and token-based access control.
Getting Started
Clone the repository: git clone <repository-url>
Install Docker and Docker Compose: Follow the instructions on the Docker website to install Docker and Docker Compose for your operating system.
Set up environment variables: Create a .env file and add necessary environment variables like MONGO_URI, JWT_SECRET, etc.
Build and run the Docker containers: Run docker-compose up --build to build the Docker containers and start the application.
API Documentation
The API documentation will be available at http://0.0.0.0:8000/docs after the application is running.
