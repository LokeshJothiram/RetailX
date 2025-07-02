# RetailX Inventory & Billing System

A modern, browser-based inventory, billing, and analytics system for small to medium retail businesses. Built with Python Flask, HTML/CSS, Chart.js, and Excel for data storage.

---

## 🚀 Features

- **Homepage Dashboard:**
  - Store name/logo, welcome message, and quick navigation
  - Overview cards for categories, products, stock, and total sales
  - Recent sales and product categories list

- **Categories Module:**
  - Add, edit, and delete product categories (e.g., Grocery, Electronics, Clothing)
  - Lucide icon buttons for actions
  - Categories filter inventory and billing views

- **Inventory Management:**
  - Add, edit, and delete products (SKU, Name, Category, Price, Stock, Image)
  - Search and filter by name/category
  - Low stock alerts (highlighted and toast)
  - Product images upload and display

- **Billing Page:**
  - Select category and product, input quantity
  - Auto-calculate subtotal, tax (5%), discount, and total
  - Generate printable invoice
  - Inventory auto-updates after checkout
  - Sales are logged in Excel

- **Insights & Reports:**
  - Sales by category, product, and date (charts)
  - Best-selling and low-stock items
  - Visual reports with Chart.js

- **Modern UI:**
  - Responsive, card-based design
  - Sticky navigation with icons
  - Toast notifications for all actions

---

## 🛠️ Tech Stack
- **Backend:** Python Flask
- **Frontend:** HTML, CSS (Domine font, Lucide & Font Awesome icons)
- **Charts:** Chart.js
- **Database:** Excel files (`pandas`, `openpyxl`)

---

## ⚡ Setup & Usage

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <project-folder>
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app:**
   ```bash
   python app.py
   ```
4. **Open in your browser:**
   - Go to [http://localhost:5000](http://localhost:5000)

5. **Data files:**
   - All data is stored in `data/inventory.xlsx`, `data/categories.xlsx`, and `data/sales.xlsx`.
   - To migrate data, copy these files to the new system's `data/` folder.

---

## 📦 Folder Structure
```
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── inventory.xlsx
│   ├── categories.xlsx
│   └── sales.xlsx
├── static/
│   ├── style.css
│   └── images/
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── categories.html
│   ├── inventory.html
│   ├── billing.html
│   └── insights.html
```

---

## ✨ Credits
- [Flask](https://flask.palletsprojects.com/)
- [Chart.js](https://www.chartjs.org/)
- [Lucide Icons](https://lucide.dev/)
- [Font Awesome](https://fontawesome.com/)
- [Domine Font](https://fonts.google.com/specimen/Domine)

---

