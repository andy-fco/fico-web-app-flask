# FiCo - Sistema de Gestión de Finanzas Personales

FiCo es una aplicación web desarrollada en Flask para la gestión de finanzas personales. El sistema permite registrar ingresos y gastos, administrar presupuestos, definir objetivos de ahorro, consultar reportes financieros, realizar simulaciones de independencia financiera y utilizar un asistente virtual integrado con Gemini.

## Tecnologías utilizadas

### Backend

* Python
* Flask
* SQLAlchemy
* PostgreSQL
* python-dotenv

### Frontend

* HTML
* Jinja2
* Tailwind CSS
* JavaScript

### Servicio externo

* Google Gemini API

## Requisitos previos

Para ejecutar el proyecto desde cero es necesario tener instalado:

* Python 3
* PostgreSQL
* Git
* pip

## Instalación del proyecto

### 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
cd FiCo
```

### 2. Crear y activar un entorno virtual

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

En Linux / WSL:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear la base de datos PostgreSQL

Ingresar a PostgreSQL y crear una base de datos para el proyecto:

```sql
CREATE DATABASE fico_db;
```

### 5. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto, tomando como referencia el archivo `.env.example`.

Ejemplo:

```env
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/fico_db
SECRET_KEY=clave_secreta_para_flask
GEMINI_API_KEY=clave_api_de_gemini
```

Importante: el archivo `.env` no debe subirse al repositorio.

### 6. Importar la base de datos

Si se entrega un archivo SQL con la estructura y datos del sistema, importarlo con:

```bash
psql -U usuario -d fico_db -f fico_db.sql
```

En caso de usar el usuario `postgres`:

```bash
psql -U postgres -d fico_db -f fico_db.sql
```

### 7. Ejecutar la aplicación

```bash
python app.py
```

Luego abrir en el navegador:

```text
http://127.0.0.1:5000
```

## Funcionalidades principales

* Registro e inicio de sesión de usuarios.
* Registro, edición y eliminación de ingresos y gastos.
* Clasificación de movimientos por categoría.
* Gestión de presupuestos por categoría.
* Definición y seguimiento de objetivos de ahorro.
* Visualización de reportes financieros.
* Simulación de independencia financiera.
* Guardado de simulaciones para usuarios autenticados.
* Asistente virtual financiero integrado con Gemini.

## Estructura general del proyecto

```text
FiCo/
├── app.py
├── extensions.py
├── requirements.txt
├── README.md
├── .env.example
├── controllers/
├── models/
├── services/
├── templates/
├── static/
└── archivo SQL de importación (incluido en la entrega)
```

## Patrones y arquitectura

El sistema utiliza una arquitectura basada en el patrón Modelo-Vista-Controlador.

* Modelos: entidades implementadas con SQLAlchemy.
* Vistas: plantillas Jinja con estilos Tailwind CSS.
* Controladores: módulos Flask encargados de recibir solicitudes, validar datos y coordinar la lógica del sistema.

También se implementan patrones de diseño como Singleton y Strategy en componentes específicos del sistema.

## Notas importantes

* El sistema requiere una base de datos PostgreSQL activa.
* El asistente virtual requiere una API Key válida de Gemini.
* Sin configurar correctamente el archivo `.env`, la aplicación no podrá conectarse a la base de datos ni utilizar el chatbot.
* El archivo `.env` debe mantenerse fuera del repositorio por contener información sensible.

## Autores

* Andrés Fernandez
* Felipe Molinari
