
# 🏥 Complaint Management System API

[![Django CI](https://github.com/your-username/your-repo/actions/workflows/django.yml/badge.svg)](https://github.com/your-username/your-repo/actions/workflows/django.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

An advanced API for a hospital complaint management system, built with Django and Django REST Framework. This system allows for efficient tracking and resolution of complaints, with features like QR code integration for easy complaint submission, role-based access control, and detailed reporting.

## ✨ Features

*   **Complaint Management:** Create, track, and manage complaints from submission to resolution.
*   **QR Code Integration:** Generate unique QR codes for rooms to simplify complaint submission.
*   **Role-Based Access Control:** Different user roles (Master Admin, Department Admin, Staff) with specific permissions.
*   **Department and Issue Management:** Organize complaints by department and issue category.
*   **File Uploads:** Attach images to complaints for better context.
*   **Advanced Filtering and Searching:** Easily find complaints based on various criteria.
*   **Reporting and Analytics:** Generate reports to analyze complaint data and track resolution times.
*   **JWT Authentication:** Secure API endpoints with JSON Web Token authentication.

## 🛠️ Tech Stack

*   **Backend:** Django, Django REST Framework
*   **Database:** PostgreSQL
*   **Authentication:** Simple JWT (JSON Web Token)
*   **Image Processing:** Pillow
*   **QR Code Generation:** qrcode
*   **Deployment:** Gunicorn

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

*   Python 3.10+
*   PostgreSQL
*   Poetry (optional, for dependency management)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/complaint-system-backend.git
    cd complaint-system-backend
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up the database:**
    *   Create a PostgreSQL database.
    *   Create a `.env` file in the project root and add the following environment variables:
        ```
        SECRET_KEY=your-secret-key
        QR_CODE_SECRET_KEY=your-qr-code-secret-key
        DEBUG=True
        ALLOWED_HOSTS=127.0.0.1,localhost
        DATABASE_URL=postgres://user:password@host:port/database_name
        CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
        ACCESS_TOKEN_LIFETIME_MINUTES=60
        REFRESH_TOKEN_LIFETIME_DAYS=1
        ```

4.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser:**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The API will be available at `http://127.0.0.1:8000/api/`.

##  API Endpoints

The base URL for all API endpoints is `/api/`.

| Method | Endpoint                       | Description                               |
| :----- | :----------------------------- | :---------------------------------------- |
| `POST` | `/auth/login/`                 | Obtain JWT access and refresh tokens.     |
| `POST` | `/auth/refresh/`               | Refresh JWT access token.                 |
| `GET`  | `/auth/user/`                  | Get details of the authenticated user.    |
| `POST` | `/auth/logout/`                | Logout the user.                          |
| `GET`  | `/rooms/`                      | List all rooms.                           |
| `POST` | `/rooms/`                      | Create a new room.                        |
| `GET`  | `/rooms/{id}/`                 | Retrieve a single room.                   |
| `PUT`  | `/rooms/{id}/`                 | Update a room.                            |
| `PATCH`| `/rooms/{id}/`                 | Partially update a room.                  |
| `DELETE`| `/rooms/{id}/`                | Delete a room.                            |
| `GET`  | `/complaints/`                 | List all complaints.                      |
| `POST` | `/complaints/`                 | Create a new complaint.                   |
| `GET`  | `/complaints/{ticket_id}/`     | Retrieve a single complaint.              |
| `PUT`  | `/complaints/{ticket_id}/`     | Update a complaint.                       |
| `PATCH`| `/complaints/{ticket_id}/`     | Partially update a complaint.             |
| `DELETE`| `/complaints/{ticket_id}/`    | Delete a complaint.                       |
| `GET`  | `/departments/`                | List all departments.                     |
| `POST` | `/departments/`                | Create a new department.                  |
| `GET`  | `/issue-category/`             | List all issue categories.                |
| `POST` | `/issue-category/`             | Create a new issue category.              |
| `GET`  | `/report/`                     | Get complaint reports.                    |
| `GET`  | `/TATView/`                    | Get Turnaround Time (TAT) for complaints. |

## 🔐 Authentication

This API uses JWT for authentication. To access protected endpoints, you need to include the access token in the `Authorization` header as a Bearer token:

```
Authorization: Bearer <your_access_token>
```

Alternatively, you can use the secure cookie-based authentication provided by the `CookieTokenObtainPairView`.

## 📦 Data Models

The main data models in this project are:

*   **`CustomUser`**: Extends the default Django User model with roles (`master_admin`, `dept_admin`, `staff`).
*   **`Room`**: Represents a room in the hospital with details like room number, bed number, and a generated QR code.
*   **`Complaint`**: The core model for storing complaint details, including status, priority, and assigned department/staff.
*   **`ComplaintImage`**: Stores images associated with a complaint.
*   **`Department`**: Represents a hospital department.
*   **`Issue_Category`**: Defines categories for complaints, linked to departments.

## 🧪 Testing

Currently, there are no automated tests in this project. It is recommended to add unit and integration tests to ensure the reliability of the API. You can use Django's built-in `TestCase` or other testing frameworks like `pytest`.

To run tests, you would typically use the following command:
```bash
python manage.py test
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or find any bugs.

## 📜 License

This project is licensed under the GPLv3 License. See the [LICENSE](LICENSE) file for details.
