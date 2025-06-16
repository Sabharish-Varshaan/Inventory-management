# Inventory Management System

A comprehensive desktop inventory management system built with PySide6 and SQLite database.

## Features

### Two Operator Login Types
- **Goods Receiving Operator**
  - Username: `goods_operator`
  - Password: `password123`
  - Access: Goods receiving, product master list, inventory tracking

- **Sales Operator**
  - Username: `sales_operator`
  - Password: `password123`
  - Access: Sales processing, product master list, inventory tracking

### Core Functionality
- **Goods Receiving Module**: Complete product receiving with supplier details, quantity, pricing, and tax calculations
- **Sales Processing Module**: Customer sales with stock validation and automatic calculations
- **Product Master List**: Comprehensive product database with barcode, SKU, categories, pricing, and stock tracking
- **Real-time Inventory**: Live stock updates with receiving and sales transactions

## System Requirements
- Python 3.8 or higher
- Windows 10+, Linux, or macOS
- 512MB RAM minimum
- 100MB storage space

## Quick Start

### Installation
1. Clone or download the project files
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python main.py`

### First Login
Use the provided operator credentials:
- Goods Receiving: `goods_operator` / `password123`
- Sales Processing: `sales_operator` / `password123`

## Database
The system uses SQLite for local data storage with automatic database initialization and sample data creation on first run.

## Technical Details
- **Framework**: PySide6 (Qt6 for Python)
- **Database**: SQLite with comprehensive relational schema
- **Security**: bcrypt password hashing and role-based access control
- **UI**: Professional tab-based interface with real-time calculations
