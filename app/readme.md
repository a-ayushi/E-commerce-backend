Project Overview
This project is a RESTful backend API for an e-commerce platform built with FastAPI. It supports admin product management, user authentication, product browsing, cart operations, and dummy checkout functionality.

Features

- Admin CRUD for products
- User authentication (Signup, Signin, Forgot/Reset Password)
- Product browsing and search
- Cart and Checkout
- Order history
- Role-based access control (RBAC)
- JWT authentication
- Swagger/OpenAPI documentation

Tech Stack

- Python
- FastAPI
- PostgreSQL or SQLite
- SQLAlchemy or Tortoise ORM
- JWT (PyJWT)
- Pydantic
- Alembic for DB migrations

Project Structure
app/
├── main.py
├── auth/
│ ├── routes.py
│ ├── models.py
│ ├── utils.py
├── products/
├── cart/
├── checkout/
├── orders/
├── core/
├── middlewares/
├── utils/
├── tests/

Setup Instructions
Follow these commands to set up the project environment step by step:

1.  Clone the repository:
    git clone https://github.com/a-ayushi/E-commerce-backend.git
    cd <repo-folder>

2.  Create and activate a virtual environment:
    python -m venv myenv
    `myenv\Scripts\activate`

3.  Install the dependencies:
    pip install -r requirements.txt

4.  Set up the `.env` file for environment variables (e.g., DB URL, JWT secret, email credentials).

5.  Run the development server:
    uvicorn app.main:app --reload

API Documentation
Once the server is running, you can access the API documentation at:

- Swagger UI: http://127.0.0.1:8000/docs
