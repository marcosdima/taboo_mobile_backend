# Backend Flask + PostgreSQL

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno en `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/taboo_db
SECRET_KEY=your-secret-key
```

4. Inicializar la base de datos:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Ejecución

### Desarrollo
```bash
python run.py
```

### Producción
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## Estructura

```
backend/
├── app/
│   ├── __init__.py          # Factory de la aplicación
│   ├── config.py            # Configuración
│   ├── extensions.py        # Extensiones (db, migrate)
│   ├── models/              # Modelos de base de datos
│   │   └── user.py
│   ├── routes/              # Rutas/Endpoints
│   │   └── health.py
│   └── services/            # Lógica de negocio
├── migrations/              # Migraciones de base de datos
├── run.py                   # Punto de entrada desarrollo
└── wsgi.py                  # Punto de entrada producción
```

## Endpoints

- `GET /api/health` - Health check
