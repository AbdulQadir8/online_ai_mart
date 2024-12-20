# Online Mart API

## Overview
The Online Mart API is a comprehensive suite of microservices designed to manage an e-commerce platform. It includes multiple services that handle different aspects of the platform, such as products, inventory, orders, users, payments, and notifications. These services communicate with each other using Apache Kafka to ensure scalability and reliability.

## Features
- **User Management:** Register, log in, and manage user accounts.
- **Product Management:** Add, update, delete, and list products.
- **Inventory Management:** Track and manage inventory levels.
- **Order Management:** Create and manage customer orders.
- **Payment Processing:** Handle payment transactions.
- **Notification Service:** Send notifications to users.

## Technologies Used
- **Backend Framework:** FastAPI
- **ORM:** SQLModel
- **Database:** PostgreSQL
- **Containerization:** Docker, Docker Compose
- **Development Environment:** DevContainers
- **Messaging Queue:** Apache Kafka
- **Serialization:** Protobuf
- **API Gateway:** Kong
- **Deployment:** Azure Apps
- **Testing:** Pytest

## Installation

### Prerequisites
- Docker and Docker Compose installed
- Azure account for deployment

### Steps
1. **Clone the repository:**
    ```bash
    git clone https://github.com/AbdulQadir8/online-mart-api.git
    cd online-mart-api
    ```

2. **Set up environment variables:**
    Create a `.env` file in the root directory and add the following variables:
    ```env
    DATABASE_URL=postgresql://username:password@db:5432/onlinemart
    SECRET_KEY=your_secret_key
    KAFKA_BROKER=kafka_broker_url
    ```

3. **Build and run the Docker containers:**
    ```bash
    docker-compose up --build
    ```

4. **Access the API:**
    The API should now be running and accessible at `http://localhost:8000`.

## API Services

### Product Service
- **GET /api/products:** Get a list of all products.
- **POST /api/products:** Add a new product (admin only).
- **GET /api/products/:id:** Get details of a specific product.
- **PUT /api/products/:id:** Update a product (admin only).
- **DELETE /api/products/:id:** Delete a product (admin only).

### Inventory Service
- **GET /api/inventory:** Get inventory levels.
- **POST /api/inventory:** Update inventory levels (admin only).

### Order Service
- **GET /api/orders:** Get a list of all orders (admin only).
- **POST /api/orders:** Create a new order.
- **GET /api/orders/:id:** Get details of a specific order.
- **PUT /api/orders/:id:** Update an order (admin only).
- **DELETE /api/orders/:id:** Delete an order (admin only).

### User Service
- **POST /api/register:** Register a new user.
- **POST /api/login:** Log in a user and receive a JWT token.
- **GET /api/users:** Get a list of all users (admin only).

### Payment Service
- **POST /api/payments:** Process a payment.
- **GET /api/payments/:id:** Get details of a specific payment.

### Notification Service
- **POST /api/notifications:** Send a notification to a user.
- **GET /api/notifications:** Get a list of notifications sent.

## Communication Between Services
The above services communicate with each other using Apache Kafka. This ensures that the system is decoupled and scalable. Kafka topics are used to publish and subscribe to events between services.

## Testing
- **Run tests:**
    ```bash
    docker-compose exec web pytest
    ```

## Deployment
- **Azure Deployment:**
    - Set up your Azure Web App and configure the necessary environment variables.
    - Deploy the Docker container to Azure using the Azure CLI or Azure portal.

## Contributing
Contributions are welcome! Please create a pull request or open an issue to discuss your changes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
- **Email:** [your.email@example.com](mailto:your.email@example.com)
- **GitHub:** [AbdulQadir8](https://github.com/AbdulQadir8)

Thank you for using the Online Mart API! If you have any questions or need further assistance, feel free to reach out.
