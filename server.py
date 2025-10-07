from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'nevlis_secret_key'

PRODUCTS_FILE = 'products.json'
ADMIN_PASSWORD = 'pyexw'

# Хранилище сессий (в реальном приложении используйте базу данных)
sessions = {}

def load_products():
    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_products(products):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def is_authenticated(request):
    token = request.cookies.get('admin_token')
    return token in sessions and sessions[token] == 'authenticated'

# Главная страница магазина - КАТАЛОГ
@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>NevlisShop</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Arial', sans-serif; }
            body { background: linear-gradient(135deg, #0c0c0c 0%, #1a237e 100%); color: #fff; min-height: 100vh; }
            .main-shop { padding: 20px; }
            .shop-header { text-align: center; padding: 40px 0; background: rgba(13, 19, 33, 0.8); margin-bottom: 40px; border-bottom: 2px solid #2962ff; }
            .shop-title { font-size: 48px; color: #2962ff; text-shadow: 0 0 20px rgba(41, 98, 255, 0.7); margin-bottom: 10px; }
            .shop-subtitle { color: #b3e5fc; font-size: 18px; }
            .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; padding: 0 20px; }
            .product-card { background: rgba(13, 19, 33, 0.8); border: 1px solid #2962ff; border-radius: 15px; padding: 20px; transition: all 0.3s ease; text-align: center; }
            .product-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(41, 98, 255, 0.3); }
            .product-image { width: 100%; height: 180px; object-fit: cover; border-radius: 8px; margin-bottom: 15px; }
            .product-name { font-size: 20px; margin-bottom: 10px; color: #fff; }
            .product-price { color: #64dd17; font-size: 24px; font-weight: bold; margin: 15px 0; }
            .product-description { color: #b3e5fc; line-height: 1.5; margin-bottom: 15px; }
            .buy-btn { background: linear-gradient(45deg, #4CAF50, #66BB6A); border: none; padding: 12px 30px; border-radius: 8px; color: white; font-size: 16px; cursor: pointer; transition: all 0.3s ease; width: 100%; }
            .buy-btn:hover { background: linear-gradient(45deg, #66BB6A, #4CAF50); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4); }
        </style>
    </head>
    <body>
        <div class="main-shop">
            <div class="shop-header">
                <h1 class="shop-title">NevlisShop</h1>
                <p class="shop-subtitle">оплата через @send</p>
            </div>
            <div class="products-grid" id="productsGrid"></div>
        </div>
        <script>
            const SELLER_TELEGRAM = "t.me/seller";
            async function loadProducts() {
                try {
                    const response = await fetch('/api/products');
                    const products = await response.json();
                    renderProducts(products);
                } catch (error) {
                    console.error('Ошибка загрузки товаров:', error);
                    renderProducts([]);
                }
            }
            function renderProducts(products) {
                const container = document.getElementById('productsGrid');
                container.innerHTML = '';
                if (products.length === 0) {
                    container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #b3e5fc; font-size: 18px;">Товаров пока нет в каталоге</p>';
                    return;
                }
                products.forEach((product, index) => {
                    const productHTML = `
                        <div class="product-card">
                            <img src="${product.image}" alt="${product.name}" class="product-image">
                            <h3 class="product-name">${product.name}</h3>
                            <div class="product-price">$${product.price}</div>
                            <p class="product-description">${product.description}</p>
                            <button class="buy-btn" onclick="buyProduct(${index})">Купить сейчас</button>
                        </div>
                    `;
                    container.innerHTML += productHTML;
                });
            }
            function buyProduct(index) {
                fetch('/api/products').then(response => response.json()).then(products => {
                    const product = products[index];
                    const message = `сап хочу купить товар: ${product.name} за $${product.price}.`;
                    const url = `https://t.me/Vexece?text=${encodeURIComponent(message)}`;
                    window.open(url, '_blank');
                });
            }
            document.addEventListener('DOMContentLoaded', loadProducts);
        </script>
    </body>
    </html>
    """

# Страница входа в админку
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            import uuid
            token = str(uuid.uuid4())
            sessions[token] = 'authenticated'
            response = redirect(url_for('admin_panel'))
            response.set_cookie('admin_token', token, max_age=3600)  # 1 час
            return response
        else:
            return """
            <!DOCTYPE html>
            <html lang="ru">
            <head>
                <meta charset="UTF-8">
                <title>Вход в админку - NevlisShop</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Arial', sans-serif; }
                    body { background: linear-gradient(135deg, #0c0c0c 0%, #1a237e 100%); color: #fff; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
                    .login-container { background: rgba(13, 19, 33, 0.95); padding: 40px; border-radius: 15px; border: 1px solid #2962ff; box-shadow: 0 0 30px rgba(41, 98, 255, 0.3); width: 100%; max-width: 400px; }
                    .login-title { text-align: center; margin-bottom: 30px; color: #2962ff; font-size: 28px; }
                    .error-message { background: rgba(255, 0, 0, 0.2); border: 1px solid #ff5252; padding: 10px; border-radius: 8px; margin-bottom: 20px; text-align: center; color: #ff5252; }
                    .form-group { margin-bottom: 20px; }
                    .form-group label { display: block; margin-bottom: 8px; color: #b3e5fc; }
                    .form-group input { width: 100%; padding: 12px; border: 1px solid #2962ff; border-radius: 8px; background: rgba(255, 255, 255, 0.1); color: #fff; font-size: 16px; }
                    .login-btn { width: 100%; padding: 12px; background: linear-gradient(45deg, #2962ff, #304ffe); border: none; border-radius: 8px; color: white; font-size: 16px; cursor: pointer; transition: all 0.3s ease; }
                    .login-btn:hover { background: linear-gradient(45deg, #304ffe, #2962ff); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(41, 98, 255, 0.4); }
                    .back-link { display: block; text-align: center; margin-top: 20px; color: #b3e5fc; text-decoration: none; }
                </style>
            </head>
            <body>
                <div class="login-container">
                    <h2 class="login-title">Вход в админку</h2>
                    <div class="error-message">❌ Неверный пароль! Попробуйте снова.</div>
                    <form method="POST">
                        <div class="form-group">
                            <label>Пароль:</label>
                            <input type="password" name="password" placeholder="Введите пароль" required>
                        </div>
                        <button type="submit" class="login-btn">Войти</button>
                    </form>
                    <a href="/" class="back-link">← Вернуться в магазин</a>
                </div>
            </body>
            </html>
            """
    
    # GET запрос - показать форму входа
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Вход в админку - NevlisShop</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Arial', sans-serif; }
            body { background: linear-gradient(135deg, #0c0c0c 0%, #1a237e 100%); color: #fff; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
            .login-container { background: rgba(13, 19, 33, 0.95); padding: 40px; border-radius: 15px; border: 1px solid #2962ff; box-shadow: 0 0 30px rgba(41, 98, 255, 0.3); width: 100%; max-width: 400px; }
            .login-title { text-align: center; margin-bottom: 30px; color: #2962ff; font-size: 28px; }
            .form-group { margin-bottom: 20px; }
            .form-group label { display: block; margin-bottom: 8px; color: #b3e5fc; }
            .form-group input { width: 100%; padding: 12px; border: 1px solid #2962ff; border-radius: 8px; background: rgba(255, 255, 255, 0.1); color: #fff; font-size: 16px; }
            .login-btn { width: 100%; padding: 12px; background: linear-gradient(45deg, #2962ff, #304ffe); border: none; border-radius: 8px; color: white; font-size: 16px; cursor: pointer; transition: all 0.3s ease; }
            .login-btn:hover { background: linear-gradient(45deg, #304ffe, #2962ff); transform: translateY(-2px); box-shadow: 0 5px 15px rgba(41, 98, 255, 0.4); }
            .back-link { display: block; text-align: center; margin-top: 20px; color: #b3e5fc; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="login-container">
            <h2 class="login-title">Вход в админку</h2>
            <form method="POST">
                <div class="form-group">
                    <label>Пароль:</label>
                    <input type="password" name="password" placeholder="Введите пароль" required>
                </div>
                <button type="submit" class="login-btn">Войти</button>
            </form>
            <a href="/" class="back-link">← Вернуться в магазин</a>
        </div>
    </body>
    </html>
    """

# Админ панель (только для авторизованных)
@app.route('/admin-panel')
def admin_panel():
    if not is_authenticated(request):
        return redirect(url_for('admin_login'))
    
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Админ панель - NevlisShop</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Arial', sans-serif; }
            body { background: linear-gradient(135deg, #0c0c0c 0%, #1a237e 100%); color: #fff; min-height: 100vh; padding: 30px; }
            .admin-header { text-align: center; margin-bottom: 40px; }
            .admin-header h1 { color: #2962ff; font-size: 36px; margin-bottom: 10px; }
            .admin-subtitle { color: #b3e5fc; font-size: 16px; }
            .logout-btn { position: fixed; top: 20px; right: 20px; background: rgba(255, 82, 82, 0.2); padding: 10px 15px; border-radius: 8px; color: #ff5252; text-decoration: none; border: 1px solid #ff5252; transition: all 0.3s ease; font-size: 14px; }
            .logout-btn:hover { background: rgba(255, 82, 82, 0.4); }
            .product-form { background: rgba(13, 19, 33, 0.8); padding: 30px; border-radius: 15px; border: 1px solid #2962ff; margin-bottom: 30px; max-width: 800px; margin-left: auto; margin-right: auto; }
            .form-row { display: flex; gap: 20px; margin-bottom: 20px; }
            .form-field { flex: 1; }
            .form-field label { display: block; margin-bottom: 8px; color: #b3e5fc; font-weight: bold; }
            .form-field input, .form-field textarea { width: 100%; padding: 12px; border: 1px solid #2962ff; border-radius: 8px; background: rgba(255, 255, 255, 0.1); color: #fff; font-size: 16px; }
            .form-field textarea { height: 100px; resize: vertical; }
            .add-product-btn { background: linear-gradient(45deg, #00c853, #64dd17); border: none; padding: 15px 30px; border-radius: 8px; color: white; font-size: 18px; cursor: pointer; transition: all 0.3s ease; display: block; margin: 20px auto 0; }
            .add-product-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(100, 221, 23, 0.4); }
            .products-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; margin-top: 30px; }
            .product-card { background: rgba(13, 19, 33, 0.8); border: 1px solid #2962ff; border-radius: 15px; padding: 20px; transition: all 0.3s ease; text-align: center; }
            .product-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(41, 98, 255, 0.3); }
            .product-image { width: 100%; height: 180px; object-fit: cover; border-radius: 8px; margin-bottom: 15px; }
            .product-name { font-size: 20px; margin-bottom: 10px; color: #fff; }
            .product-price { color: #64dd17; font-size: 24px; font-weight: bold; margin: 15px 0; }
            .product-description { color: #b3e5fc; line-height: 1.5; margin-bottom: 15px; }
            .delete-btn { background: linear-gradient(45deg, #ff5252, #d32f2f); border: none; padding: 10px 20px; border-radius: 6px; color: white; cursor: pointer; margin-top: 10px; width: 100%; font-size: 14px; }
            .delete-btn:hover { background: linear-gradient(45deg, #d32f2f, #ff5252); }
            .back-to-shop { display: block; text-align: center; margin-top: 30px; color: #b3e5fc; text-decoration: none; font-size: 16px; padding: 10px 20px; border: 1px solid #2962ff; border-radius: 8px; width: 200px; margin-left: auto; margin-right: auto; }
            .back-to-shop:hover { background: rgba(41, 98, 255, 0.2); }
            .stats { text-align: center; margin-bottom: 20px; color: #b3e5fc; font-size: 16px; }
        </style>
    </head>
    <body>
        <a href="/admin-logout" class="logout-btn">🚪 Выйти</a>
        <div class="admin-panel">
            <div class="admin-header">
                <h1>NevlisShop</h1>
                <p class="admin-subtitle"></p>
            </div>
            <div class="stats" id="statsInfo"></div>
            <div class="product-form">
                <div class="form-row">
                    <div class="form-field">
                        <label>Название товара:</label>
                        <input type="text" id="productName" placeholder="Введите название товара">
                    </div>
                    <div class="form-field">
                        <label>Цена ($):</label>
                        <input type="number" id="productPrice" placeholder="Введите цену в долларах">
                    </div>
                </div>
                <div class="form-field">
                    <label>Описание товара:</label>
                    <textarea id="productDescription" placeholder="Введите подробное описание товара"></textarea>
                </div>
                <button class="add-product-btn" onclick="addProduct()">Добавить товар в каталог</button>
            </div>
            <div class="products-grid" id="adminProductsContainer"></div>
            <a href="/" class="back-to-shop">← Вернуться в каталог</a>
        </div>
        <script>
            const DEFAULT_IMAGE = "https://avatars.mds.yandex.net/i?id=2d08106efa07b019e812ad861d5a2977_l-5185690-images-thumbs&n=13";
            document.addEventListener('DOMContentLoaded', loadAdminProducts);
            async function loadAdminProducts() {
                try {
                    const response = await fetch('/api/products');
                    const products = await response.json();
                    renderAdminProducts(products);
                    updateStats(products);
                } catch (error) {
                    console.error('Ошибка загрузки товаров:', error);
                }
            }
            function updateStats(products) {
                const statsElement = document.getElementById('statsInfo');
                statsElement.innerHTML = `В каталоге: <strong>${products.length}</strong> товаров | Общая стоимость: <strong>$${products.reduce((sum, product) => sum + parseFloat(product.price), 0).toFixed(2)}</strong>`;
            }
            async function addProduct() {
                const name = document.getElementById('productName').value;
                const price = document.getElementById('productPrice').value;
                const description = document.getElementById('productDescription').value;
                if (name && price && description) {
                    try {
                        const response = await fetch('/api/products', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ name, price: parseFloat(price), description, image: DEFAULT_IMAGE })
                        });
                        if (response.ok) {
                            document.getElementById('productName').value = '';
                            document.getElementById('productPrice').value = '';
                            document.getElementById('productDescription').value = '';
                            loadAdminProducts();
                            alert('✅ Товар успешно добавлен в каталог!');
                        }
                    } catch (error) {
                        alert('❌ Ошибка при добавлении товара');
                    }
                } else {
                    alert('⚠️ Заполните все поля!');
                }
            }
            async function deleteProduct(index) {
                if (confirm('❓ Вы уверены, что хотите удалить этот товар из каталога?')) {
                    try {
                        const response = await fetch(`/api/products/${index}`, { method: 'DELETE' });
                        if (response.ok) {
                            loadAdminProducts();
                            alert('✅ Товар удален из каталога');
                        }
                    } catch (error) {
                        alert('❌ Ошибка при удалении товара');
                    }
                }
            }
            function renderAdminProducts(products) {
                const container = document.getElementById('adminProductsContainer');
                container.innerHTML = '';
                if (products.length === 0) {
                    container.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #b3e5fc; font-size: 18px;">В каталоге пока нет товаров</p>';
                    return;
                }
                products.forEach((product, index) => {
                    const productHTML = `
                        <div class="product-card">
                            <img src="${product.image}" alt="${product.name}" class="product-image">
                            <h3 class="product-name">${product.name}</h3>
                            <div class="product-price">$${product.price}</div>
                            <p class="product-description">${product.description}</p>
                            <button class="delete-btn" onclick="deleteProduct(${index})">🗑️ Удалить товар</button>
                        </div>
                    `;
                    container.innerHTML += productHTML;
                });
            }
        </script>
    </body>
    </html>
    """

# Выход из админки
@app.route('/admin-logout')
def admin_logout():
    token = request.cookies.get('admin_token')
    if token in sessions:
        del sessions[token]
    response = redirect(url_for('admin_login'))
    response.set_cookie('admin_token', '', expires=0)
    return response

# API для получения товаров
@app.route('/api/products', methods=['GET'])
def get_products():
    products = load_products()
    return jsonify(products)

# API для добавления товара
@app.route('/api/products', methods=['POST'])
def add_product():
    products = load_products()
    new_product = request.get_json()
    products.append(new_product)
    save_products(products)
    return jsonify({'success': True})

# API для удаления товара
@app.route('/api/products/<int:index>', methods=['DELETE'])
def delete_product(index):
    products = load_products()
    if 0 <= index < len(products):
        products.pop(index)
        save_products(products)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Invalid index'}), 400

if __name__ == '__main__':
    if not os.path.exists(PRODUCTS_FILE):
        save_products([])
    
    print("🚀 NevlisShop запущен!")
    print("📱 Каталог товаров: http://localhost:5000")
    print("🔐 Админ панель: http://localhost:5000/admin")
    print("🔑 Пароль админки: pyexw")
    
    app.run(host='0.0.0.0', port=5000, debug=True)