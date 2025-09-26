# Complaint System Backend API Documentation

This document provides an overview of the API endpoints for the Complaint System backend.

## Base URL

`http://127.0.0.1:8000/api/`

## Authentication

The API uses SessionAuthentication and BasicAuthentication. For development and testing, `AllowAny` permissions are currently enabled (`rest_framework.permissions.AllowAny`).

## Media and Static Files

*   **Media URL:** `/media/`
*   **Media Root:** `complaintsystem/media/` (where uploaded files like complaint images and QR codes are stored)
*   **Static URL:** `/static/`
*   **Static Root:** `complaintsystem/staticfiles/`

## API Endpoints

### 1. Rooms

Manage room details and QR codes.

*   **List all rooms:**
    *   `GET /api/rooms/`
*   **Create a new room:**
    *   `POST /api/rooms/`
    *   **Body:** JSON object with room details (e.g., `bed_no`, `room_no`, `Block`, `Floor_no`, `ward`, `speciality`, `room_type`, `status`).
    *   **Note:** This will automatically generate a QR code for the room, including an HMAC signature for tamper-proofing the QR data.
*   **Retrieve a single room:**
    *   `GET /api/rooms/{id}/`
    *   **Response includes:** Room details, `qr_code` URL, and `dataenc` (base64 encoded room data).
*   **Update a room (full update):**
    *   `PUT /api/rooms/{id}/`
    *   **Body:** Full JSON object with all room details.
    *   **Note:** This will regenerate `dataenc`, the HMAC signature, and the QR code image for the updated room.
*   **Partially update a room:**
    *   `PATCH /api/rooms/{id}/`
    *   **Body:** JSON object with fields to update.
    *   **Note:** This will also regenerate `dataenc`, the HMAC signature, and the QR code image.
*   **Delete a room:**
    *   `DELETE /api/rooms/{id}/`
*   **Update Room Status (Custom Action):**
    *   `POST /api/rooms/{id}/update_status/`
    *   **Body:** JSON object `{ "status": "<new_status>" }` (e.g., `"active"`, `"inactive"`).

### 2. Departments

Manage department details.

*   **List all departments:**
    *   `GET /api/departments/`
*   **Create a new department:**
    *   `POST /api/departments/`
    *   **Body:** JSON object with department details (e.g., `dept_code`, `department_name`).
*   **Retrieve a single department:**
    *   `GET /api/departments/{dept_code}/`
*   **Update a department (full update):**
    *   `PUT /api/departments/{dept_code}/`
    *   **Body:** Full JSON object with all department details.
*   **Partially update a department:**
    *   `PATCH /api/departments/{dept_code}/`
    *   **Body:** JSON object with fields to update.
*   **Delete a department:**
    *   `DELETE /api/departments/{dept_code}/`

### 3. Issue Categories

Manage issue categories, linked to departments.

*   **List all issue categories:**
    *   `GET /api/issue-category/`
*   **Create a new issue category:**
    *   `POST /api/issue-category/`
    *   **Body:** JSON object with category details (e.g., `issue_category_code`, `department` (dept_code), `issue_category_name`).
*   **Retrieve a single issue category:**
    *   `GET /api/issue-category/{issue_category_code}/`
*   **Update an issue category (full update):**
    *   `PUT /api/issue-category/{issue_category_code}/`
    *   **Body:** Full JSON object with all category details.
*   **Partially update an issue category:**
    *   `PATCH /api/issue-category/{issue_category_code}/`
    *   **Body:** JSON object with fields to update.
*   **Delete an issue category:**
    *   `DELETE /api/issue-category/{issue_category_code}/`

### 4. Complaints

Manage complaint submissions, including image uploads and QR code data validation.

*   **List all complaints:**
    *   `GET /api/complaints/`
    *   **Query Parameters for filtering:** `status`, `priority`, `issue_type`, `ward`, `block`
    *   **Search Parameters:** `ticket_id`, `room_number`, `bed_number`, `description`
    *   **Ordering Parameters:** `submitted_at`, `priority`, `status`
*   **Create a new complaint:**
    *   `POST /api/complaints/`
    *   **Content-Type:** `multipart/form-data`
    *   **Body (Form Data):**
        *   All complaint fields (e.g., `bed_number`, `block`, `room_number`, `issue_type`, `description`, `priority`, etc.).
        *   `images`: (Optional) One or more image files.
        *   `qr_data_from_qr`: (Required if submitted via QR code scan) The `data` query parameter extracted from the QR code URL.
        *   `qr_signature_from_qr`: (Required if submitted via QR code scan) The `signature` query parameter extracted from the QR code URL.
    *   **HMAC Validation:** The backend validates `qr_data_from_qr` against `qr_signature_from_qr` using the `QR_CODE_SECRET_KEY` to prevent data tampering.
*   **Retrieve a single complaint:**
    *   `GET /api/complaints/{ticket_id}/`
    *   **Response includes:** Complaint details and URLs to associated `images`.
*   **Update a complaint (full update):**
    *   `PUT /api/complaints/{ticket_id}/`
    *   **Content-Type:** `multipart/form-data`
    *   **Body (Form Data):** Full set of complaint fields.
    *   **Note:** If `images` are included, they will be **appended** to the existing images.
*   **Partially update a complaint:**
    *   `PATCH /api/complaints/{ticket_id}/`
    *   **Content-Type:** `multipart/form-data`
    *   **Body (Form Data):** Fields to update.
    *   **Note:** If `images` are included, they will be **appended** to the existing images.
*   **Delete a complaint:**
    *   `DELETE /api/complaints/{ticket_id}/`
*   **Update Complaint Status (Custom Action):**
    *   `POST /api/complaints/{ticket_id}/update_status/`
    *   **Body:** JSON object `{ "status": "<new_status>", "remarks": "<optional_remarks>" }` (e.g., `"resolved"`, `"in_progress"`).
*   **Filter Complaints by Status (Custom Action):**
    *   `GET /api/complaints/by_status/`
    *   **Query Parameter:** `status=<status_value>` (e.g., `status=open`, `status=resolved`).
*   **Filter Complaints by Priority (Custom Action):**
    *   `GET /api/complaints/by_priority/`
    *   **Query Parameter:** `priority=<priority_value>` (e.g., `priority=low`, `priority=high`).

---

17. SYSTEM TESTING AND IMPLEMENTATION

System Testing
To comprehensively test a Complaint Management System, you would establish a controlled environment to simulate various user interactions and system loads. This involves utilizing tools to mimic user submissions, data processing, and administrative actions. Implement robust testing logic that identifies correct complaint routing, data integrity, and proper notification mechanisms. To simulate user input and system events, employ automated testing frameworks, allowing you to effectively test the system's functionality and responsiveness. This setup enables you to observe how your system handles complaint submissions, status updates, and resolution workflows, helping to refine its capabilities while ensuring compliance with functional and performance requirements.

7.1.1 Unit Testing
Unit testing a Complaint Management System involves creating specific test cases to validate the functionality of individual components, such as complaint submission forms, data validation logic, and API endpoints. You can mock database interactions and external service calls to isolate and verify that each unit performs its intended function correctly. For instance, you might create tests that assert a complaint form correctly validates input fields, or that a specific API endpoint successfully processes a complaint and stores it in the database. Using frameworks like Jest (for frontend) or Pytest (for backend), you can automate these tests, ensuring that each part of the system remains robust as you refine its implementation. This approach helps maintain high reliability and data integrity standards in your Complaint Management System.

7.1.2 Integration Testing
Integration testing for a Complaint Management System focuses on ensuring that different modules and services work together seamlessly. In this phase, you would deploy the complete system (frontend and backend) in a controlled environment, where user interactions with the frontend trigger appropriate actions in the backend, and data flows correctly between components. You would then simulate user scenarios, such as submitting a complaint, updating its status, or assigning it to an agent, to evaluate how well the integrated system handles these workflows. The goal is to validate that the system can accurately process end-to-end complaint lifecycles, from submission to resolution, responding appropriately in each scenario. Successful integration testing ensures that all components function harmoniously, enhancing the reliability of the overall Complaint Management System.

7.1.3 Functional Testing
Functional testing for a Complaint Management System involves verifying that each feature within the system performs as intended under various conditions. This includes testing the complaint submission process to ensure it accurately captures user inputs, as well as validating the logic for complaint categorization, assignment, and status updates. You would create scenarios to simulate different user roles (e.g., complainant, agent, administrator) and their respective actions, such as submitting a new complaint, adding comments, or changing a complaint's priority. By systematically evaluating these functions, you can ensure that each part of the system works correctly and reliably, contributing to the overall effectiveness of the Complaint Management System.

7.1.4 Performance Testing
Performance testing for a Complaint Management System involves assessing the system's responsiveness and efficiency under varying loads and conditions. This testing aims to determine how well the system handles a high volume of concurrent complaint submissions, status updates, and data retrievals, particularly during peak usage times. By employing load testing tools to simulate extensive user interactions, you can measure the system's latency in processing complaints, its throughput, and its overall resource consumption, including CPU, memory, and database I/O. Additionally, you would evaluate the system's ability to maintain accuracy and stability without significant performance degradation, ensuring that it can operate effectively under stress. This comprehensive performance assessment helps identify any bottlenecks and ensures that the Complaint Management System is robust and reliable under various operating conditions.

7.1.5 Regression Testing
Regression testing for a Complaint Management System focuses on ensuring that recent updates or changes to the system have not introduced new bugs or compromised existing functionality. This involves re-running previously established test cases that cover various aspects of the system, such as complaint submission, data processing, user authentication, and reporting. By using automated test suites to replicate both normal and edge-case scenarios, you can verify that the system continues to function correctly, handling new complaints and existing data without issues, and that all features remain intact.

7.1.6 Test Cases
7.1.6.1 Positive Test Cases
Positive test cases for a Complaint Management System involve scenarios where the system correctly processes valid inputs and performs expected actions. One test case could involve a user successfully submitting a new complaint with all required fields filled out, and verifying that the complaint appears in the system with the correct status and details. Another case might involve an administrator successfully assigning a complaint to an agent and confirming that the agent receives a notification. Additionally, you could create tests that mimic a user updating their complaint details or an agent resolving a complaint, assessing whether the system accurately reflects these changes and triggers appropriate follow-up actions. By ensuring that the system accurately handles these scenarios, you can confirm its effectiveness in managing complaints.

7.1.6.2 Negative Test Cases
Negative test cases for a Complaint Management System focus on scenarios where the system should gracefully handle invalid inputs or unexpected situations without errors. One test case could involve a user attempting to submit a complaint with missing required fields, and verifying that the system displays appropriate validation errors. Another case might include a user trying to access a complaint they do not have permission to view, and ensuring the system denies access and provides an informative message. Additionally, you can test for scenarios like submitting excessively long text in a comment field or attempting to use invalid characters, to ensure the system handles these inputs robustly. By validating these scenarios, you can confirm that the system effectively prevents data corruption and maintains security, thus enhancing its reliability.