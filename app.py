from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
import os
import re
import math
import tldextract
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('SECRET_KEY')


PALABRAS_RIESGO = ["login", "verify", "secure", "account", "aduana", "tracking", "pago", "factura"]
TLDS_RIESGO = {"xyz", "top", "tk", "ml", "ga", "cf", "gq"}
ACORTADORES = {"bit.ly", "tinyurl.com", "goo.gl", "ow.ly", "t.co"}

def calcular_entropia(texto):
    if not texto: return 0
    freq = {c: texto.count(c)/len(texto) for c in set(texto)}
    return -sum(p * math.log2(p) for p in freq.values())

def analizar_url(url):
    senales = []
    puntos = 0
    
    if not url.startswith('http'):
        url = 'http://' + url 
        
    parsed = urlparse(url)
    host = parsed.hostname or ""
    ext = tldextract.extract(url)
    dominio_registrable = f"{ext.domain}.{ext.suffix}"

    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
        senales.append("URL usa dirección IP directa")
        puntos += 30

    if ext.suffix in TLDS_RIESGO:
        senales.append(f"Dominio de nivel superior (TLD) sospechoso: .{ext.suffix}")
        puntos += 25

    if dominio_registrable in ACORTADORES:
        senales.append("URL acortada (oculta el destino real)")
        puntos += 15

    if len(ext.subdomain.split(".")) >= 3:
        senales.append("Exceso de subdominios")
        puntos += 15

    texto_bajo = url.lower()
    for p in PALABRAS_RIESGO:
        if p in texto_bajo:
            senales.append(f"Palabra clave de engaño: '{p}'")
            puntos += 10
            break

    if parsed.scheme != "https":
        senales.append("El enlace no utiliza HTTPS")
        puntos += 20

    if calcular_entropia(ext.domain) > 3.5:
        senales.append("Dominio con alta entropía (posible aleatorio)")
        puntos += 15

    puntos = min(puntos, 100)
    
    if puntos >= 60:
        clasificacion = "malicioso"
    elif puntos >= 30:
        clasificacion = "sospechoso"
    else:
        clasificacion = "seguro"

    return {
        "url": url,
        "dominio_registrable": dominio_registrable,
        "puntuacion": puntos,
        "clasificacion": clasificacion,
        "senales": senales
    }


def obtener_conexion():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        return conn
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analizar', methods=['POST'])
def api_analizar():
    datos = request.get_json()
    texto_correo = datos.get('texto', '')
    
    if not texto_correo:
        return jsonify({"error": "No se proporcionó texto"}), 400

    patron = r'https?:\/\/[^\s<>"\']+'
    urls_encontradas = list(set(re.findall(patron, texto_correo)))

    if not urls_encontradas:
        return jsonify({"mensaje": "No se encontraron enlaces en el texto", "resultados": []})

    resultados = []
    riesgo_maximo_puntos = 0
    riesgo_global = "seguro"

    for url in urls_encontradas:
        analisis = analizar_url(url)
        resultados.append(analisis)
        if analisis["puntuacion"] > riesgo_maximo_puntos:
            riesgo_maximo_puntos = analisis["puntuacion"]
            riesgo_global = analisis["clasificacion"]

    conn = obtener_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO correos_analizados (asunto, riesgo_global) VALUES (%s, %s)",
                ("Análisis desde panel web", riesgo_global)
            )
            correo_id = cursor.lastrowid
            
            for res in resultados:
                cursor.execute(
                    "INSERT INTO enlaces (correo_id, url_original, dominio_registrable, puntuacion_riesgo, clasificacion, detalles_json) VALUES (%s, %s, %s, %s, %s, %s)",
                    (correo_id, res['url'], res['dominio_registrable'], res['puntuacion'], res['clasificacion'], str(res['senales']))
                )
            conn.commit()
        except Error as e:
            print(f"Error guardando en BD: {e}")
        finally:
            conn.close()

    return jsonify({
        "riesgo_global": riesgo_global,
        "resultados": resultados
    })

if __name__ == '__main__':
    app.run(debug=True)