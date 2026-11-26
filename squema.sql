CREATE DATABASE IF NOT EXISTS detector_enlaces_chacao;
USE detector_enlaces_chacao;

CREATE TABLE correos_analizados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    remitente VARCHAR(255),
    asunto TEXT,
    fecha_analisis DATETIME DEFAULT CURRENT_TIMESTAMP,
    riesgo_global ENUM('seguro','sospechoso','malicioso')
);

CREATE TABLE enlaces (
    id INT AUTO_INCREMENT PRIMARY KEY,
    correo_id INT,
    url_original TEXT NOT NULL,
    dominio_registrable VARCHAR(255),
    puntuacion_riesgo DECIMAL(5,2),
    clasificacion ENUM('seguro','sospechoso','malicioso'),
    detalles_json JSON,
    FOREIGN KEY (correo_id) REFERENCES correos_analizados(id) ON DELETE CASCADE
);