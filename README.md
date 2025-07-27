# 🍽 Restaurant Management System – Modular MVC Framework

A modular, scalable restaurant management system built using the **Model-View-Controller (MVC)** architecture in Python. This project supports both **GUI (via `customtkinter`)** and **Terminal interfaces**, with flexible **JSON** and **Database** backends. Designed with extensibility and clean code principles (OOP + SOLID) in mind.

---

## 📌 Overview

This application simulates a restaurant environment where:
- Owners can manage restaurant operations
- Customers can place and reserve food orders

The system supports **multiple user roles**, **interface types**, and **data storage formats** — all coordinated dynamically through a central controller.

---

## Key Concepts & Architecture

### ✅ MVC Design Pattern

- **Model**: Handles data storage and logic (e.g., customer data, product info).
- **View**: Responsible for UI — either Terminal-based or GUI-based.
- **Controller**: Manages logic between the model and the view.

At the heart of the system is the `MainController`, which acts as a central coordinator:
- Registers all views and models
- Controls the application flow
- Provides models to sub-controllers on demand
- Implements **Observer** and **Strategy** patterns

---

## 🧩 Design Principles Used

| Principle | Description |
|----------|-------------|
| **OCP (Open-Closed Principle)** | You can add new views/models without modifying existing code |
| **SRP (Single Responsibility Principle)** | Each class has a clear, single purpose |
| **Observer Pattern** | Views and sub-controllers register with the `MainController` |
| **Strategy Pattern** | Enables flexible selection of GUI/CLI interfaces and data storage |
| **Singleton Pattern** | Applied to models that must only be instantiated once |
| **Polymorphism** | Interfaces and abstract classes allow interchangeable components |

---

##  Features

- 🖥️ GUI and Terminal interface support
- 💾 Dual storage support: JSON and database
- 🔄 Dynamically register new views and models
- 🧩 Plug-and-play architecture for extensions
- 📐 SOLID-compliant and clean OOP structure
- 🧠 Intelligent model dispatching through the main controller
- ➕ Insert views at any point in the flow

---

##  Project Structure

| File | Description |
|------|-------------|
| `app.py` | Application entry point — select interface and storage type here |
| `main_controller1.py` | Central controller that manages registration, flow, and module loading |
| `abstract.py` | Abstract base classes (interfaces for models, views, controllers) |
| `sign.py` | Handles sign-in / sign-up for customers and owners |
| `owner.py` | Contains views and logic specific to the restaurant owner |
| `customer.py` | Contains views and logic specific to the customer |
| `decorator.py` | Contains Singleton decorator used by shared models |


