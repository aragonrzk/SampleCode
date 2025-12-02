📦 ERP API — Flask + PostgreSQL
- Mudah diintegrasikan dengan tool API mana pun


### **Authentication (JWT)**
- Login endpoint
- Token 12 jam
- Decorator `require_auth` untuk proteksi route


### **Frontend (Tabulator.js minimal)**
- Tabel dinamis untuk menampilkan data inventory
- Auto-fetch dari API
- Layout simple dan lightweight


### **CI/CD (GitHub Actions)**
- Workflow otomatis menjalankan pytest setiap push
- Meningkatkan credibility & code quality


---


## 📁 Struktur Direktori
```
project/
├── app/
│ ├── __init__.py
│ ├── config.py
│ ├── models.py
│ ├── routes/
│ │ ├── inventory_routes.py
│ │ └── swagger_routes.py
│ ├── services/
│ │ └── inventory_service.py
├── public/
│ └── index.html
├── tests/
│ ├── test_inventory.py
│ └── conftest.py
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── run.py
