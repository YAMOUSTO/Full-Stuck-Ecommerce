# E-commerce Platform (Full-Stack Application)

This is a complete e-commerce application built from scratch, featuring a modern, decoupled architecture with a Python FastAPI backend and a Vue.js frontend.

## Features

*   **Product Management:** Full CRUD (Create, Read, Update, Delete) operations for products.
*   **Image Uploads:** Support for uploading and displaying product images.
*   **Category System:** Products can be assigned to categories.
*   **Client-Side Filtering & Searching:** Filter products by category and search by name/description on the frontend.
*   **User Authentication:** Secure user registration and login using JWT (JSON Web Tokens).
*   **Protected Routes:** Backend API routes for CUD operations are protected, requiring authentication.
*   **Frontend Route Guards:** Prevents unauthenticated users from accessing protected pages.
*   **Shopping Cart:** Client-side cart functionality using Pinia for state management.
*   **Order & Checkout:** Users can place orders which are saved to the database.
*   **Order History:** Authenticated users can view their past orders.

---

## Tech Stack

*   **Backend:**
    *   **Framework:** Python 3 with FastAPI
    *   **Database:** MySQL
    *   **ORM:** SQLAlchemy
    *   **Authentication:** JWT with Passlib for password hashing
    *   **API Documentation:** Automatic interactive docs via Swagger UI and ReDoc.

*   **Frontend:**
    *   **Framework:** Vue.js 3 (Composition API) with Vite
    *   **Routing:** Vue Router
    *   **State Management:** Pinia
    *   **Styling:** Tailwind CSS
    *   **API Communication:** Axios

---

## Setup and Installation

### Prerequisites

*   Python 3.8+
*   Node.js & npm
*   MySQL Server
*   Composer (if you were using the Laravel version)

### Backend Setup

1.  Navigate to the project root: `cd ecommerce-platform`
2.  Create a Python virtual environment: `python3 -m venv venv`
3.  Activate the virtual environment: `source venv/bin/activate`
4.  Install Python dependencies: `pip install -r requirements.txt` *(Note: You should create this file)*
5.  Set up your `.env` file with database credentials and a `SECRET_KEY`.
6.  Start the server: `python -m uvicorn main:app --reload`

### Frontend Setup

1.  Navigate to the frontend directory: `cd frontend`
2.  Install Node.js dependencies: `npm install`
3.  Start the development server: `npm run dev`

---

*This project was built with the guidance of an AI assistant.*