# 🏠 Household Services Web Application

### 📘 Modern Application Development

---

## 📖 About the Project
This project is a **web-based household services platform** that connects customers with service professionals such as cleaners, plumbers, and electricians.  
It was built as part of the **Modern Application Development – I** course and demonstrates full-stack web development using Flask and SQLAlchemy.

Users can:
- Register as **customers** or **professionals**
- Book or manage household services
- Have all activities monitored and managed by an **admin dashboard**

---

## 💡 Key Features

### 👥 Customer
- Search for services by name or location  
- Book a service with preferred date and time  
- View active and completed bookings  
- Cancel ongoing bookings  

### 🧰 Professional
- View and accept/reject service requests  
- Mark services as completed  
- Track total earnings and completed job history  

### 🧑‍💼 Admin
- Approve or reject professional accounts  
- Add or remove available services  
- View total platform earnings and reports  
- Manage all users, bookings, and permissions  

---

## 🛠️ Technologies Used
| Technology | Purpose |
|-------------|----------|
| **Flask** | Backend web framework |
| **SQLAlchemy** | ORM for database operations |
| **Flask-RESTful** | API development |
| **Bootstrap & CSS** | Frontend design and responsiveness |
| **SQLite** | Database management |

---

## 🧩 Database Schema
- **User Table** – Stores details for admins, customers, and professionals  
- **Services Table** – Contains all service listings  
- **Bookings Table** – Tracks each booking and its status  
- **Roles Table** – Defines user roles (admin, customer, professional)  
- **Relationships** – Connects users and services through bookings  

---

## 🌐 Application Routes Overview

### 🧍 Customer Routes
| Route | Description |
|--------|--------------|
| `/customer/dashboard` | Dashboard with active & completed bookings |
| `/customer/book_service` | Book a new service |
| `/customer/reports` | View spending and service history |
| `/customer/search_services` | Search available services |

### 🧑‍🔧 Professional Routes
| Route | Description |
|--------|--------------|
| `/professional/dashboard` | Dashboard with assigned bookings |
| `/professional/requests` | View pending service requests |
| `/professional/complete_booking/<id>` | Mark booking as completed |
| `/professional/reports` | View earnings and history |

### 👨‍💼 Admin Routes
| Route | Description |
|--------|--------------|
| `/admin/dashboard` | Admin main panel |
| `/admin/user_approvals` | Approve or reject professionals |
| `/admin/manage_services` | Add or remove services |
| `/admin/reports` | Platform-wide reports & analytics |
| `/admin/view_users` | View customers & professionals |

### 🔐 Authentication
| Route | Description |
|--------|--------------|
| `/signup` | Register a new account |
| `/login` | Login for all users |
| `/logout` | Logout and clear session |
| `/` | Home page |

---

## 🔗 RESTful API Routes
| Route | Description |
|--------|--------------|
| `/api/services` | Fetch all available services in JSON format |
| `/search` | Global search API for services |

---

## 🎥 Demo Video
📺 [Watch the Project Demo](https://drive.google.com/file/d/1ggP1dGQTLj51m6qU1KgasHwdjs-iQazD/view?usp=sharing)

---

## 🧭 Project Flow Summary
1. User signs up as a **customer** or **professional**  
2. Admin approves new professional accounts  
3. Customers browse and book services  
4. Professionals manage and complete bookings  
5. Admin oversees the entire platform’s activity and performance  

---

## ✅ Conclusion
This project successfully implements a functional **household service management system** with complete CRUD operations and multi-role control.  
It highlights the use of Flask, SQLAlchemy, and RESTful APIs to build scalable web applications with role-based access control.

---

⭐ **If you like this project, consider giving it a star on GitHub!**

