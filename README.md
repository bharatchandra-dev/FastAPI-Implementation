# FastAPI Starter Kit

This is a starter kit for building web APIs using FastAPI, MongoDB, and JWT authentication.

## Features

- FastAPI framework for building high-performance web APIs
- MongoDB integration using Motor
- JWT authentication for securing API routes
- IP-based access control for specific API routes
- Environment variables configuration using python-dotenv
- Dockerfile for containerization (Not available for now)
- Swagger documentation for API endpoints

## Prerequisites

- Python 3.7 or later
- MongoDB installed and running
- Docker (optional) For Now I am not going to implement it.

## Getting Started

1. Clone the repository:
2. Install the dependencies:
3. Set up the environment variables:
    - Create a `.setting_env` file in the project root directory.
    - Add the necessary environment variables to the file (e.g., MongoDB URL, JWT configurations, allowed IP addresses).
    ```
    ALLOWED_IPS=["127.0.0.1", "192.168.0.1"]
    SECRET_KEY="your-secret-key"
    ALGORITHM="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    PROD_DB_URL="mongodb://localhost:27017"
    ```
4. Start the FastAPI server:
5. Access the API documentation:
    - Open your web browser and go to `http://localhost:8000/docs` to view the Swagger documentation. You can change this link in your code.
    - Explore the available endpoints and test them.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

