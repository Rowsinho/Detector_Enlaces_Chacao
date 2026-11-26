# Sistema de Detección de Enlaces Maliciosos en Correos Institucionales – Municipio Chacao, Miranda

Aplicación web para que analistas y personal administrativo de empresas de importación y exportación en Chacao evalúen enlaces contenidos en correos institucionales, obtengan una clasificación de riesgo (seguro, sospechoso o malicioso) mediante reglas heurísticas y registren los resultados en una base de datos para auditorías de seguridad.

## Stack Tecnológico
* **Backend:** Python 3 + Flask
* **Base de Datos:** MySQL 8 / MariaDB (vía `mysql-connector-python`)
* **Frontend:** HTML5 / CSS3 / JavaScript (Vanilla)

## Requisitos Previos
Asegúrate de tener instalado en tu sistema:
* Python (versión 3.10 o superior)
* Git
* Servidor MySQL o MariaDB activo

## Instalación
1. Instalar [XAMPP](https://www.apachefriends.org/) y encender **MySQL** (en Apache solo si se usará phpMyAdmin).
2. Crear la base de datos importando `Proyecto/schema.sql`:
   - Con phpMyAdmin: abrir http://localhost/phpmyadmin, pestaña **Importar**, elegir `schema.sql` y pulsar **Importar**.
   - Con terminal (Linux/Mac o MySQL en el PATH): `mysql -u root -p < Proyecto/schema.sql`
3. Entrar a la carpeta del proyecto: `cd Proyecto`
4. Crear y activar el entorno virtual:
   - Windows: `python -m venv venv` y luego `venv\Scripts\activate`
   - Linux/Mac: `python3 -m venv venv` y luego `source venv/bin/activate`
5. Instalar dependencias: `pip install -r requirements.txt`
6. Copiar el archivo `.env.example` a `.env` y configurar las credenciales de la base de datos (Si MySQL tiene clave, colocarla en el archivo).
7. Ejecutar: `python app.py` y abrir http://127.0.0.1:5000
   
## Funcionalidades
- Extracción automática de URLs a partir de texto plano o del cuerpo de un correo institucional.
- Análisis heurístico de enlaces basado en características de phishing (IPs directas, TLDs de bajo costo, acortadores, exceso de subdominios, palabras clave, ausencia de HTTPS y cálculo de entropía).
- Clasificación con puntuación de riesgo: **Seguro** (0-29 puntos), **Sospechoso** (30-59 puntos), **Malicioso** (60-100 puntos).
- Almacenamiento de historial de correos analizados y resultados detallados en la base de datos MySQL.
- Interfaz web amigable con alertas visuales (colores rojo, amarillo y verde) para identificar rápidamente el nivel de peligro.

## API
`GET /` (Interfaz principal) · `POST /api/analizar` (Recibe el texto del correo y devuelve el análisis de los enlaces en formato JSON)

## Integrantes:
* -Andrés Reyes 
* -Allan González 
* -Diego Herrera 
* -Fernando Reyes 
* -Mitchael Ruíz