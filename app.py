from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import pandas as pd
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Data file paths
INVENTORY_FILE = 'data/inventory.xlsx'
SALES_FILE = 'data/sales.xlsx'
CATEGORIES_FILE = 'data/categories.xlsx'

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure data directory and files exist
os.makedirs('data', exist_ok=True)
if not os.path.exists(INVENTORY_FILE):
    df = pd.DataFrame(columns=['SKU', 'Name', 'Category', 'Price', 'Stock'])
    df.to_excel(INVENTORY_FILE, index=False)
if not os.path.exists(SALES_FILE):
    df = pd.DataFrame(columns=['InvoiceID', 'Date', 'SKU', 'Name', 'Category', 'Quantity', 'Price', 'Subtotal', 'Tax', 'Discount', 'Total'])
    df.to_excel(SALES_FILE, index=False)
if not os.path.exists(CATEGORIES_FILE):
    df = pd.DataFrame(columns=['Category'])
    df.to_excel(CATEGORIES_FILE, index=False)

# Ensure image upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ensure Image column in inventory Excel
if os.path.exists(INVENTORY_FILE):
    df = pd.read_excel(INVENTORY_FILE)
    if 'Image' not in df.columns:
        df['Image'] = ''
        df.to_excel(INVENTORY_FILE, index=False)

# Helper to check allowed file
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    # Load inventory for overview
    df = pd.read_excel(INVENTORY_FILE)
    total_items = df['Stock'].sum() if not df.empty else 0
    total_products = len(df) if not df.empty else 0
    # Load categories from categories file
    cat_df = pd.read_excel(CATEGORIES_FILE)
    categories = cat_df['Category'].dropna().unique() if not cat_df.empty else []
    total_categories = len(categories)
    # Load sales for stats and recent activity
    sales_df = pd.read_excel(SALES_FILE)
    total_sales = sales_df['Total'].sum() if not sales_df.empty else 0
    recent_sales = sales_df.sort_values('Date', ascending=False).head(3).to_dict('records') if not sales_df.empty else []
    return render_template('home.html', total_items=total_items, categories=categories, total_categories=total_categories, total_products=total_products, total_sales=total_sales, recent_sales=recent_sales, active_page='home')

@app.route('/categories', methods=['GET', 'POST'])
def categories():
    cat_df = pd.read_excel(CATEGORIES_FILE)
    categories = cat_df['Category'].dropna().tolist() if not cat_df.empty else []
    if request.method == 'POST':
        new_cat = request.form.get('category', '').strip()
        edit_cat = request.form.get('edit_category', '').strip()
        delete_cat = request.form.get('delete_category', '').strip()
        # Add new category
        if new_cat:
            if new_cat in categories:
                flash('Category already exists!', 'error')
            else:
                cat_df = pd.concat([cat_df, pd.DataFrame([{'Category': new_cat}])], ignore_index=True)
                cat_df.to_excel(CATEGORIES_FILE, index=False)
                flash('Category added!', 'info')
            return redirect(url_for('categories'))
        # Edit category
        if edit_cat and request.form.get('new_name'):
            new_name = request.form.get('new_name').strip()
            if new_name in categories:
                flash('Category name already exists!', 'error')
            else:
                cat_df.loc[cat_df['Category'] == edit_cat, 'Category'] = new_name
                cat_df.to_excel(CATEGORIES_FILE, index=False)
                # Update inventory to reflect new category name
                inv_df = pd.read_excel(INVENTORY_FILE)
                inv_df.loc[inv_df['Category'] == edit_cat, 'Category'] = new_name
                inv_df.to_excel(INVENTORY_FILE, index=False)
                flash('Category updated!', 'info')
            return redirect(url_for('categories'))
        # Delete category
        if delete_cat:
            cat_df = cat_df[cat_df['Category'] != delete_cat]
            cat_df.to_excel(CATEGORIES_FILE, index=False)
            # Delete all products in this category from inventory
            inv_df = pd.read_excel(INVENTORY_FILE)
            inv_df = inv_df[inv_df['Category'] != delete_cat]
            inv_df.to_excel(INVENTORY_FILE, index=False)
            flash('Category and all its products deleted!', 'info')
            return redirect(url_for('categories'))
    return render_template('categories.html', categories=categories, active_page='categories')

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    df = pd.read_excel(INVENTORY_FILE)
    cat_df = pd.read_excel(CATEGORIES_FILE)
    categories = cat_df['Category'].dropna().tolist() if not cat_df.empty else []
    search = request.args.get('search', '').strip()
    filter_cat = request.args.get('filter_category', '').strip()
    low_stock_threshold = 5
    if request.method == 'POST':
        if 'edit_sku' in request.form:
            # Edit product
            edit_sku = request.form.get('edit_sku')
            name = request.form.get('edit_name', '').strip()
            category = request.form.get('edit_category', '').strip()
            price = request.form.get('edit_price', '').strip()
            stock = request.form.get('edit_stock', '').strip()
            image_file = request.files.get('edit_image')
            image_filename = df.loc[df['SKU'] == edit_sku, 'Image'].values[0] if 'Image' in df.columns else ''
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
            if not name or not category or not price or not stock:
                flash('All fields are required for edit!', 'error')
            else:
                df.loc[df['SKU'] == edit_sku, ['Name', 'Category', 'Price', 'Stock', 'Image']] = [name, category, float(price), int(stock), image_filename]
                df.to_excel(INVENTORY_FILE, index=False)
                flash('Product updated!', 'success')
            return redirect(url_for('inventory'))
        elif 'delete_sku' in request.form:
            # Delete product
            delete_sku = request.form.get('delete_sku')
            df = df[df['SKU'] != delete_sku]
            df.to_excel(INVENTORY_FILE, index=False)
            flash('Product deleted!', 'success')
            return redirect(url_for('inventory'))
        else:
            # Add product
            sku = request.form.get('sku', '').strip()
            name = request.form.get('name', '').strip()
            category = request.form.get('category', '').strip()
            price = request.form.get('price', '').strip()
            stock = request.form.get('stock', '').strip()
            image_file = request.files.get('image')
            image_filename = ''
            if image_file and allowed_file(image_file.filename):
                filename = secure_filename(image_file.filename)
                image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
            if not sku or not name or not category or not price or not stock:
                flash('All fields are required!', 'error')
            else:
                new_row = {'SKU': sku, 'Name': name, 'Category': category, 'Price': float(price), 'Stock': int(stock), 'Image': image_filename}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_excel(INVENTORY_FILE, index=False)
                flash('Product added!', 'success')
            return redirect(url_for('inventory'))
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(search, case=False, na=False)]
    if filter_cat:
        filtered_df = filtered_df[filtered_df['Category'] == filter_cat]
    low_stock_items = filtered_df[filtered_df['Stock'] < low_stock_threshold]
    if not low_stock_items.empty:
        flash(f'Low stock alert: {len(low_stock_items)} item(s) below {low_stock_threshold}', 'warning')
    return render_template('inventory.html', inventory=filtered_df.to_dict('records'), categories=categories, search=search, filter_cat=filter_cat, low_stock_threshold=low_stock_threshold, active_page='inventory')

@app.route('/billing', methods=['GET', 'POST'])
def billing():
    df = pd.read_excel(INVENTORY_FILE)
    cat_df = pd.read_excel(CATEGORIES_FILE)
    categories = cat_df['Category'].dropna().unique() if not cat_df.empty else []
    invoice = None
    if request.method == 'POST':
        category = request.form.get('category', '').strip()
        sku = request.form.get('product', '').strip()
        quantity = request.form.get('quantity', '').strip()
        discount = request.form.get('discount', '').strip()  # optional
        tax_rate = 0.05  # 5% tax for example
        if not category or not sku or not quantity:
            flash('Please select category, product, and quantity.', 'error')
            return redirect(url_for('billing'))
        try:
            quantity = int(quantity)
        except ValueError:
            flash('Invalid quantity.', 'error')
            return redirect(url_for('billing'))
        product_row = df[df['SKU'] == sku]
        if product_row.empty:
            flash('Product not found.', 'error')
            return redirect(url_for('billing'))
        product = product_row.iloc[0]
        if quantity > product['Stock']:
            flash('Not enough stock.', 'error')
            return redirect(url_for('billing'))
        price = product['Price']
        subtotal = price * quantity
        tax = subtotal * tax_rate
        discount_val = float(discount) if discount else 0.0
        total = subtotal + tax - discount_val
        # Update inventory
        df.loc[df['SKU'] == sku, 'Stock'] = product['Stock'] - quantity
        df.to_excel(INVENTORY_FILE, index=False)
        # Log sale
        import uuid
        from datetime import datetime
        sales_df = pd.read_excel(SALES_FILE)
        invoice_id = str(uuid.uuid4())[:8]
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sale_row = {
            'InvoiceID': invoice_id,
            'Date': now,
            'SKU': sku,
            'Name': product['Name'],
            'Category': category,
            'Quantity': quantity,
            'Price': price,
            'Subtotal': subtotal,
            'Tax': tax,
            'Discount': discount_val,
            'Total': total
        }
        sales_df = pd.concat([sales_df, pd.DataFrame([sale_row])], ignore_index=True)
        sales_df.to_excel(SALES_FILE, index=False)
        # Prepare invoice for display
        invoice = sale_row
        flash('Invoice generated and inventory updated!', 'success')
        return render_template('billing.html', categories=categories, inventory=df.to_dict('records'), invoice=invoice, active_page='billing')
    return render_template('billing.html', categories=categories, inventory=df.to_dict('records'), invoice=invoice, active_page='billing')

@app.route('/insights')
def insights():
    sales_df = pd.read_excel(SALES_FILE)
    inv_df = pd.read_excel(INVENTORY_FILE)
    # Sales by category
    sales_by_cat = sales_df.groupby('Category')['Total'].sum().reset_index().to_dict('records') if not sales_df.empty else []
    # Sales by product
    sales_by_prod = sales_df.groupby('Name')['Total'].sum().reset_index().to_dict('records') if not sales_df.empty else []
    # Sales by date (daily)
    if not sales_df.empty:
        sales_df['DateOnly'] = pd.to_datetime(sales_df['Date']).dt.date
        sales_by_date = sales_df.groupby('DateOnly')['Total'].sum().reset_index().to_dict('records')
    else:
        sales_by_date = []
    # Best-selling products (top 5)
    best_sellers = sales_df.groupby('Name')['Quantity'].sum().reset_index().sort_values('Quantity', ascending=False).head(5).to_dict('records') if not sales_df.empty else []
    # Low stock items (stock < 5)
    low_stock = inv_df[inv_df['Stock'] < 5].to_dict('records') if not inv_df.empty else []
    return render_template('insights.html',
        sales_by_cat=sales_by_cat,
        sales_by_prod=sales_by_prod,
        sales_by_date=sales_by_date,
        best_sellers=best_sellers,
        low_stock=low_stock,
        active_page='insights'
    )

if __name__ == '__main__':
    app.run(debug=True) 