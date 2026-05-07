import json
import re
import sqlite3
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from email.header import decode_header
import os
import feedparser


def conectar_db(db_path: str) -> sqlite3.Connection:
    """
    Crea una conexión a SQLite con foreign keys activadas.
    
    Args:
        db_path: Ruta del archivo SQLite.
    
    Returns:
        sqlite3.Connection: Conexión con foreign keys activadas.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ==================== FUNCIONES DE LAS TOOLS ====================

def obtener_clima(ciudad: str) -> str:
    """
    Obtiene el clima actual de una ciudad usando OpenWeatherMap API.
    
    Args:
        ciudad: Nombre de la ciudad (ej: "Buenos Aires", "Madrid")
    
    Returns:
        str: Información del clima en formato JSON
    """
    WEATHER_API_KEY = "dbc2fbf999aad5500160256e1bd5d8c1"
    if not WEATHER_API_KEY:
        return json.dumps({"error": "WEATHER_API_KEY no configurada en el archivo .env"})
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={WEATHER_API_KEY}&units=metric&lang=es"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            resultado = {
                "ciudad": data["name"],
                "pais": data["sys"]["country"],
                "temperatura": data["main"]["temp"],
                "sensacion_termica": data["main"]["feels_like"],
                "humedad": data["main"]["humidity"],
                "descripcion": data["weather"][0]["description"],
                "viento": data["wind"]["speed"]
            }
            return json.dumps(resultado, ensure_ascii=False)
        else:
            return json.dumps({"error": f"Ciudad no encontrada o error en la API (código: {response.status_code})"})
    
    except Exception as e:
        return json.dumps({"error": f"Error al obtener el clima: {str(e)}"})


def calcular_descuento(precio: float, porcentaje: float) -> str:
    """
    Calcula el precio final de un producto aplicando un porcentaje de descuento.

    Args:
        precio: Precio original del producto.
        porcentaje: Porcentaje de descuento a aplicar (ej: 15 para 15%).

    Returns:
        str: Precio final con descuento en formato JSON.
    """
    resultado = float(precio) * (1 - float(porcentaje) / 100)
    return json.dumps({"precio_final": round(resultado, 2)})


def acceder_pagina_web(url: str) -> str:
    """
    Accede a una página web y extrae su contenido principal.
    
    Args:
        url: La URL de la página web (ej: "https://www.ejemplo.com")
    
    Returns:
        str: El contenido de la página en formato JSON
    """
    try:
        # Agregar protocolo si no lo tiene
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remover scripts y styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extraer texto limpio
        texto = soup.get_text(separator='\n', strip=True)
        
        # Limitar longitud
        if len(texto) > 2000:
            texto = texto[:2000] + "...\n[Contenido truncado]"
        
        # Extraer título
        titulo = soup.title.string if soup.title else "Sin título"
        
        return json.dumps({
            "url": url,
            "titulo": titulo,
            "contenido": texto,
            "estado": "éxito"
        }, ensure_ascii=False)
    
    except requests.exceptions.Timeout:
        return json.dumps({"error": "Timeout: La página tardó demasiado en responder"})
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Error al acceder a la URL: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error procesando la página: {str(e)}"})


def convertir_unidades(valor: float, de: str, a: str) -> str:
    """
    Convierte unidades de medida entre diferentes sistemas.
    
    Args:
        valor: El valor numérico a convertir
        de: Unidad de origen (ej: 'celsius', 'fahrenheit', 'metros', 'kilometros', 'gramos', 'kilogramos', 'litros', 'mililitros')
        a: Unidad de destino
    
    Returns:
        str: Resultado de la conversión en formato JSON
    """
    try:
        # Definir factores de conversión
        conversiones = {
            # Temperatura
            ('celsius', 'fahrenheit'): lambda x: (x * 9/5) + 32,
            ('fahrenheit', 'celsius'): lambda x: (x - 32) * 5/9,
            ('celsius', 'kelvin'): lambda x: x + 273.15,
            ('kelvin', 'celsius'): lambda x: x - 273.15,
            ('fahrenheit', 'kelvin'): lambda x: (x - 32) * 5/9 + 273.15,
            ('kelvin', 'fahrenheit'): lambda x: (x - 273.15) * 9/5 + 32,
            
            # Longitud
            ('metros', 'kilometros'): lambda x: x / 1000,
            ('kilometros', 'metros'): lambda x: x * 1000,
            ('metros', 'centimetros'): lambda x: x * 100,
            ('centimetros', 'metros'): lambda x: x / 100,
            ('metros', 'milimetros'): lambda x: x * 1000,
            ('milimetros', 'metros'): lambda x: x / 1000,
            ('kilometros', 'millas'): lambda x: x * 0.621371,
            ('millas', 'kilometros'): lambda x: x / 0.621371,
            ('metros', 'pies'): lambda x: x * 3.28084,
            ('pies', 'metros'): lambda x: x / 3.28084,
            ('metros', 'pulgadas'): lambda x: x * 39.3701,
            ('pulgadas', 'metros'): lambda x: x / 39.3701,
            
            # Masa
            ('gramos', 'kilogramos'): lambda x: x / 1000,
            ('kilogramos', 'gramos'): lambda x: x * 1000,
            ('gramos', 'libras'): lambda x: x * 0.00220462,
            ('libras', 'gramos'): lambda x: x / 0.00220462,
            ('kilogramos', 'libras'): lambda x: x * 2.20462,
            ('libras', 'kilogramos'): lambda x: x / 2.20462,
            ('gramos', 'onzas'): lambda x: x * 0.035274,
            ('onzas', 'gramos'): lambda x: x / 0.035274,
            
            # Volumen
            ('litros', 'mililitros'): lambda x: x * 1000,
            ('mililitros', 'litros'): lambda x: x / 1000,
            ('litros', 'galones'): lambda x: x * 0.264172,
            ('galones', 'litros'): lambda x: x / 0.264172,
            ('litros', 'onzas_liquidas'): lambda x: x * 33.814,
            ('onzas_liquidas', 'litros'): lambda x: x / 33.814,
            
            # Tiempo
            ('segundos', 'minutos'): lambda x: x / 60,
            ('minutos', 'segundos'): lambda x: x * 60,
            ('minutos', 'horas'): lambda x: x / 60,
            ('horas', 'minutos'): lambda x: x * 60,
            ('horas', 'dias'): lambda x: x / 24,
            ('dias', 'horas'): lambda x: x * 24,
            ('dias', 'semanas'): lambda x: x / 7,
            ('semanas', 'dias'): lambda x: x * 7,
        }
        
        # Normalizar unidades
        de = de.lower().strip()
        a = a.lower().strip()
        
        # Buscar conversión directa
        if (de, a) in conversiones:
            resultado = conversiones[(de, a)](valor)
            return json.dumps({
                "valor_original": valor,
                "unidad_origen": de,
                "valor_convertido": round(resultado, 4),
                "unidad_destino": a,
                "estado": "éxito"
            }, ensure_ascii=False)
        
        # Buscar conversión inversa
        elif (a, de) in conversiones:
            # Para la inversa, necesitamos calcular el inverso
            factor = conversiones[(a, de)](1)  # Obtener factor para 1 unidad
            if factor != 0:
                resultado = valor / factor
                return json.dumps({
                    "valor_original": valor,
                    "unidad_origen": de,
                    "valor_convertido": round(resultado, 4),
                    "unidad_destino": a,
                    "estado": "éxito"
                }, ensure_ascii=False)
        
        return json.dumps({"error": f"Conversión de '{de}' a '{a}' no soportada"})
    
    except Exception as e:
        return json.dumps({"error": f"Error en la conversión: {str(e)}"})


def traducir_texto(texto: str, idioma_origen: str, idioma_destino: str) -> str:
    """
    Traduce texto entre diferentes idiomas usando MyMemory API.
    
    Args:
        texto: El texto a traducir
        idioma_origen: Código del idioma de origen (ej: 'es', 'en', 'fr', 'de', 'it', 'pt')
        idioma_destino: Código del idioma de destino (ej: 'en', 'es', 'fr', 'de', 'it', 'pt')
    
    Returns:
        str: Texto traducido en formato JSON
    """
    try:
        # Usar MyMemory API (gratuita y confiable)
        url = "https://api.mymemory.translated.net/get"
        
        params = {
            "q": texto,
            "langpair": f"{idioma_origen.lower()}|{idioma_destino.lower()}"
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("responseStatus") == 200:
            return json.dumps({
                "texto_original": texto,
                "idioma_origen": idioma_origen,
                "texto_traducido": data.get("responseData", {}).get("translatedText", ""),
                "idioma_destino": idioma_destino,
                "estado": "éxito"
            }, ensure_ascii=False)
        else:
            return json.dumps({"error": f"Error en la traducción: {data.get('responseDetails', 'Error desconocido')}"})
    
    except requests.exceptions.Timeout:
        return json.dumps({"error": "Timeout: El servicio de traducción tardó demasiado en responder"})
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Error al conectar con el servicio de traducción: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error en la traducción: {str(e)}"})


def enviar_email(destinatario: str, asunto: str, mensaje: str, tipo: str = "plain") -> str:
    """
    Envía un email usando SMTP.
    
    Args:
        destinatario: Email del destinatario
        asunto: Asunto del email
        mensaje: Contenido del mensaje
        tipo: Tipo de contenido del mensaje ('plain' o 'html')
    
    Returns:
        str: Resultado del envío en formato JSON
    """
    try:
        # Configuración desde variables de entorno
        EMAIL_USER = os.getenv("EMAIL_USER")
        EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
        SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        
        if not EMAIL_USER or not EMAIL_PASSWORD:
            return json.dumps({"error": "Configuración de email incompleta. Necesitas EMAIL_USER y EMAIL_PASSWORD en .env"})
        
        tipo = tipo.lower().strip()
        if tipo not in ("plain", "html", "text/plain", "text/html"):
            return json.dumps({"error": f"Tipo de mensaje no válido: {tipo}. Use 'plain' o 'html'."})
        
        subtype = "html" if tipo in ("html", "text/html") else "plain"
        
        # Crear mensaje
        if subtype == "html":
            msg = MIMEMultipart("alternative")
            plain_text = re.sub(r"<[^>]+>", "", mensaje)
            plain_part = MIMEText(plain_text, "plain", "utf-8")
            html_part = MIMEText(mensaje, "html", "utf-8")
            msg.attach(plain_part)
            msg.attach(html_part)
        else:
            msg = MIMEMultipart("mixed")
            body_part = MIMEText(mensaje, "plain", "utf-8")
            msg.attach(body_part)
        
        msg['From'] = EMAIL_USER
        msg['To'] = destinatario
        msg['Subject'] = asunto
        msg['MIME-Version'] = '1.0'
        msg.add_header('Content-Type', msg.get_content_type())
        
        # Conectar al servidor SMTP
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Iniciar TLS
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        
        # Enviar email
        server.sendmail(EMAIL_USER, destinatario, msg.as_string())
        server.quit()
        
        return json.dumps({
            "destinatario": destinatario,
            "asunto": asunto,
            "tipo": subtype,
            "estado": "enviado",
            "mensaje": "Email enviado exitosamente"
        }, ensure_ascii=False)
    
    except smtplib.SMTPAuthenticationError:
        return json.dumps({"error": "Error de autenticación. Verifica tu email y contraseña/app password"})
    except smtplib.SMTPConnectError:
        return json.dumps({"error": "Error de conexión al servidor SMTP"})
    except Exception as e:
        return json.dumps({"error": f"Error al enviar email: {str(e)}"})


def leer_emails(cantidad: int = 5) -> str:
    """
    Lee los emails más recientes usando IMAP.
    
    Args:
        cantidad: Número de emails a leer (máximo 10)
    
    Returns:
        str: Lista de emails en formato JSON
    """
    try:
        # Configuración desde variables de entorno
        EMAIL_USER = os.getenv("EMAIL_USER")
        EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
        IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
        
        if not EMAIL_USER or not EMAIL_PASSWORD:
            return json.dumps({"error": "Configuración de email incompleta. Necesitas EMAIL_USER y EMAIL_PASSWORD en .env"})
        
        # Limitar cantidad
        cantidad = min(max(1, cantidad), 10)
        
        # Conectar al servidor IMAP
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select('inbox')
        
        # Buscar emails recientes
        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()
        
        # Tomar los más recientes
        recent_ids = email_ids[-cantidad:] if len(email_ids) >= cantidad else email_ids
        recent_ids.reverse()  # Más reciente primero
        
        emails = []
        
        for email_id in recent_ids:
            # Obtener email
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)
            
            # Extraer información
            subject = decode_header(email_message["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()
            
            sender = email_message["From"]
            date = email_message["Date"]
            
            # Extraer cuerpo del mensaje
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = email_message.get_payload(decode=True).decode()
            
            # Limitar longitud del cuerpo
            if len(body) > 200:
                body = body[:200] + "..."
            
            emails.append({
                "id": email_id.decode(),
                "remitente": sender,
                "asunto": subject,
                "fecha": date,
                "cuerpo_preview": body
            })
        
        mail.logout()
        
        return json.dumps({
            "cantidad_leida": len(emails),
            "emails": emails,
            "estado": "éxito"
        }, ensure_ascii=False)
    
    except imaplib.IMAP4.error as e:
        return json.dumps({"error": f"Error de IMAP: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error al leer emails: {str(e)}"})


def leer_noticias(fuente: str = "bbc", cantidad: int = 5) -> str:
    """
    Lee las noticias más recientes desde feeds RSS gratuitos.
    
    Args:
        fuente: Fuente de noticias ('bbc', 'reuters', 'cnn', 'nytimes', 'elpais', 'clarin')
        cantidad: Número de noticias a obtener (1-10)
    
    Returns:
        str: Lista de noticias en formato JSON
    """
    try:
        # Fuentes RSS disponibles (gratuitas)
        feeds = {
            "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
            "reuters": "https://feeds.reuters.com/Reuters/worldNews",
            "cnn": "http://rss.cnn.com/rss/edition.rss",
            "nytimes": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
            "elpais": "https://feeds.elpais.com/mrss-feeds/elpais/portada.xml",
            "clarin": "https://www.clarin.com/rss/lo-ultimo/",
            "guardian": "https://www.theguardian.com/world/rss",
            "washingtonpost": "http://feeds.washingtonpost.com/rss/world",
            "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
            "ap": "https://feeds.apnews.com/rss/apf-topnews",
            "npr": "https://feeds.npr.org/1001/rss.xml",
            "theverge": "https://www.theverge.com/rss/index.xml",
            "techcrunch": "https://techcrunch.com/feed/",
            "arstechnica": "https://feeds.arstechnica.com/arstechnica/index",
            "wired": "https://www.wired.com/feed/rss",
            "abc": "https://abcnews.go.com/abcnews/topstories",
            "cbs": "https://www.cbsnews.com/latest/rss/main",
            "nbc": "http://feeds.nbcnews.com/nbcnews/public/news",
            "fox": "http://feeds.foxnews.com/foxnews/latest",
            "huffpost": "https://www.huffpost.com/section/front-page/feed",
            "politico": "https://rss.politico.com/politics-news.xml",
            "axios": "https://api.axios.com/feed/",
            "vice": "https://www.vice.com/en/rss",
            "mashable": "https://mashable.com/feeds/rss/all"
        }
        
        fuente = fuente.lower().strip()
        if fuente not in feeds:
            fuentes_disponibles = ['bbc', 'reuters', 'cnn', 'nytimes', 'elpais', 'clarin', 'guardian', 'washingtonpost', 'aljazeera', 'ap', 'npr', 'theverge', 'techcrunch', 'arstechnica', 'wired', 'abc', 'cbs', 'nbc', 'fox', 'huffpost', 'politico', 'axios', 'vice', 'mashable']
            return json.dumps({"error": f"Fuente '{fuente}' no disponible. Fuentes disponibles: {', '.join(fuentes_disponibles)}"})
        
        # Limitar cantidad
        cantidad = min(max(1, cantidad), 10)
        
        # Parsear el feed RSS
        feed_url = feeds[fuente]
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:  # Error al parsear
            return json.dumps({"error": f"Error al parsear el feed RSS de {fuente}"})
        
        noticias = []
        for entry in feed.entries[:cantidad]:
            # Extraer información de la noticia
            titulo = entry.title if hasattr(entry, 'title') else "Sin título"
            descripcion = ""
            if hasattr(entry, 'description'):
                # Limpiar HTML de la descripción
                soup = BeautifulSoup(entry.description, 'html.parser')
                descripcion = soup.get_text().strip()
            elif hasattr(entry, 'summary'):
                soup = BeautifulSoup(entry.summary, 'html.parser')
                descripcion = soup.get_text().strip()
            
            # Limitar longitud de la descripción
            if len(descripcion) > 300:
                descripcion = descripcion[:300] + "..."
            
            link = entry.link if hasattr(entry, 'link') else ""
            fecha = ""
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                from time import strftime
                fecha = strftime('%Y-%m-%d %H:%M:%S', entry.published_parsed)
            
            noticias.append({
                "titulo": titulo,
                "descripcion": descripcion,
                "link": link,
                "fecha": fecha,
                "fuente": fuente.upper()
            })
        
        return json.dumps({
            "fuente": fuente.upper(),
            "cantidad_obtenida": len(noticias),
            "titulo_feed": feed.feed.title if hasattr(feed.feed, 'title') else f"Noticias {fuente.upper()}",
            "noticias": noticias,
            "estado": "éxito"
        }, ensure_ascii=False)
    
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Error al conectar con el feed RSS: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error al leer noticias: {str(e)}"})


def ejecutar_sql(db_path: str = "agente.db", query: str = "", parametros: list = None) -> str:
    """
    Ejecuta una consulta SQL en una base de datos SQLite local.

    Args:
        db_path: Ruta del archivo SQLite (por defecto agente.db).
        query: Consulta SQL a ejecutar.
        parametros: Lista de parámetros para consultas preparadas.

    Returns:
        str: Resultado en formato JSON.
    """
    try:
        if not query:
            return json.dumps({"error": "Debes proporcionar una consulta SQL en el parámetro 'query'."})

        parametros = parametros or []
        conn = conectar_db(db_path)
        cursor = conn.cursor()
        cursor.execute(query, tuple(parametros))

        if query.strip().lower().startswith("select"):
            columnas = [col[0] for col in cursor.description] if cursor.description else []
            filas = cursor.fetchall()
            resultados = [dict(zip(columnas, fila)) for fila in filas]
            conn.close()
            return json.dumps({
                "db_path": db_path,
                "query": query,
                "resultados": resultados,
                "cantidad": len(resultados),
                "estado": "éxito"
            }, ensure_ascii=False)

        conn.commit()
        filas_afectadas = cursor.rowcount
        conn.close()
        return json.dumps({
            "db_path": db_path,
            "query": query,
            "filas_afectadas": filas_afectadas,
            "estado": "éxito"
        }, ensure_ascii=False)
    except sqlite3.Error as e:
        return json.dumps({"error": f"Error SQLite: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error al ejecutar SQL: {str(e)}"})


def listar_tablas(db_path: str = "agente.db") -> str:
    """
    Lista las tablas existentes en una base de datos SQLite local.

    Args:
        db_path: Ruta del archivo SQLite (por defecto agente.db).

    Returns:
        str: Lista de tablas en formato JSON.
    """
    try:
        conn = conectar_db(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tablas = [fila[0] for fila in cursor.fetchall()]
        conn.close()
        return json.dumps({
            "db_path": db_path,
            "tablas": tablas,
            "cantidad": len(tablas),
            "estado": "éxito"
        }, ensure_ascii=False)
    except sqlite3.Error as e:
        return json.dumps({"error": f"Error SQLite: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error al listar tablas: {str(e)}"})


def info_tabla(db_path: str = "agente.db", tabla: str = "") -> str:
    """
    Obtiene información detallada sobre las columnas de una tabla.
    
    Args:
        db_path: Ruta del archivo SQLite (por defecto agente.db).
        tabla: Nombre de la tabla.
    
    Returns:
        str: Información sobre las columnas en formato JSON.
    """
    try:
        if not tabla:
            return json.dumps({"error": "Debes proporcionar el nombre de la tabla."})
        
        conn = conectar_db(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = cursor.fetchall()
        conn.close()
        
        if not columnas:
            return json.dumps({"error": f"La tabla '{tabla}' no existe o está vacía."})
        
        info_columnas = []
        for col in columnas:
            info_columnas.append({
                "id": col[0],
                "nombre": col[1],
                "tipo": col[2],
                "no_null": col[3],
                "default": col[4],
                "primary_key": col[5]
            })
        
        return json.dumps({
            "tabla": tabla,
            "db_path": db_path,
            "columnas": info_columnas,
            "cantidad_columnas": len(info_columnas),
            "estado": "éxito"
        }, ensure_ascii=False)
    except sqlite3.Error as e:
        return json.dumps({"error": f"Error SQLite: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error al obtener info de tabla: {str(e)}"})


def contar_registros(db_path: str = "agente.db", tabla: str = "") -> str:
    """
    Cuenta el número de registros en una tabla.
    
    Args:
        db_path: Ruta del archivo SQLite (por defecto agente.db).
        tabla: Nombre de la tabla.
    
    Returns:
        str: Cantidad de registros en formato JSON.
    """
    try:
        if not tabla:
            return json.dumps({"error": "Debes proporcionar el nombre de la tabla."})
        
        conn = conectar_db(db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        cantidad = cursor.fetchone()[0]
        conn.close()
        
        return json.dumps({
            "tabla": tabla,
            "db_path": db_path,
            "cantidad": cantidad,
            "estado": "éxito"
        }, ensure_ascii=False)
    except sqlite3.Error as e:
        return json.dumps({"error": f"Error SQLite: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error al contar registros: {str(e)}"})


def buscar_en_tabla(db_path: str = "agente.db", tabla: str = "", columna: str = "", valor: str = "") -> str:
    """
    Busca registros en una tabla por una columna específica.
    
    Args:
        db_path: Ruta del archivo SQLite (por defecto agente.db).
        tabla: Nombre de la tabla.
        columna: Nombre de la columna a buscar.
        valor: Valor a buscar (búsqueda parcial si contiene caracteres especiales).
    
    Returns:
        str: Registros encontrados en formato JSON.
    """
    try:
        if not tabla or not columna or not valor:
            return json.dumps({"error": "Debes proporcionar tabla, columna y valor."})
        
        conn = conectar_db(db_path)
        cursor = conn.cursor()
        
        # Búsqueda con LIKE para coincidencias parciales
        cursor.execute(f"SELECT * FROM {tabla} WHERE {columna} LIKE ?", (f"%{valor}%",))
        columnas_info = [col[0] for col in cursor.description]
        filas = cursor.fetchall()
        resultados = [dict(zip(columnas_info, fila)) for fila in filas]
        conn.close()
        
        return json.dumps({
            "tabla": tabla,
            "columna": columna,
            "valor_buscado": valor,
            "db_path": db_path,
            "resultados": resultados,
            "cantidad": len(resultados),
            "estado": "éxito"
        }, ensure_ascii=False)
    except sqlite3.Error as e:
        return json.dumps({"error": f"Error SQLite: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error al buscar en tabla: {str(e)}"})


def backup_db(db_path: str = "agente.db", backup_path: str = "") -> str:
    """
    Realiza un backup de la base de datos SQLite.
    
    Args:
        db_path: Ruta del archivo SQLite original.
        backup_path: Ruta donde guardar el backup (por defecto agente_backup_TIMESTAMP.db).
    
    Returns:
        str: Confirmación del backup en formato JSON.
    """
    try:
        if not backup_path:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"agente_backup_{timestamp}.db"
        
        import shutil
        shutil.copy2(db_path, backup_path)
        
        return json.dumps({
            "db_path": db_path,
            "backup_path": backup_path,
            "estado": "éxito",
            "mensaje": f"Backup creado correctamente en {backup_path}"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Error al hacer backup: {str(e)}"})


def limpiar_tabla(db_path: str = "agente.db", tabla: str = "") -> str:
    """
    Elimina todos los registros de una tabla (la deja vacía).
    
    Args:
        db_path: Ruta del archivo SQLite (por defecto agente.db).
        tabla: Nombre de la tabla a limpiar.
    
    Returns:
        str: Confirmación de la limpieza en formato JSON.
    """
    try:
        if not tabla:
            return json.dumps({"error": "Debes proporcionar el nombre de la tabla."})
        
        conn = conectar_db(db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {tabla}")
        filas_eliminadas = cursor.rowcount
        conn.commit()
        conn.close()
        
        return json.dumps({
            "tabla": tabla,
            "db_path": db_path,
            "registros_eliminados": filas_eliminadas,
            "estado": "éxito"
        }, ensure_ascii=False)
    except sqlite3.Error as e:
        return json.dumps({"error": f"Error SQLite: {str(e)}"})
    except Exception as e:
        return json.dumps({"error": f"Error al limpiar tabla: {str(e)}"})

def buscar_en_web(consulta: str, num_resultados: int = 5) -> str:
    """Busca en Google usando Serper y devuelve los resultados orgánicos."""
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")
    if not SERPER_API_KEY:
        return json.dumps({"error": "SERPER_API_KEY no configurada en el archivo .env"})
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": consulta, "num": num_resultados, "hl": "es"},
            timeout=10
        )
        if response.status_code == 200:
            items = response.json().get("organic", [])
            resultados = [
                {"titulo": i.get("title", ""), "enlace": i.get("link", ""), "fragmento": i.get("snippet", "")}
                for i in items
            ]
            return json.dumps({"consulta": consulta, "resultados": resultados}, ensure_ascii=False)
        return json.dumps({"error": f"Error Serper (código: {response.status_code}): {response.text}"})
    except Exception as e:
        return json.dumps({"error": str(e)})

# ==================== SCHEMA DE TOOLS PARA OPENAI ====================

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "obtener_clima",
            "description": "Obtiene el clima actual de una ciudad específica. Usa esta función cuando el usuario pregunte por el clima, temperatura o condiciones meteorológicas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {
                        "type": "string",
                        "description": "El nombre de la ciudad (ej: 'Buenos Aires', 'Madrid', 'New York')"
                    }
                },
                "required": ["ciudad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calcular_descuento",
            "description": "Calcula el precio final aplicando un porcentaje.",
            "parameters": {
                "type": "object",
                "properties": {
                    "precio": {"type": "number"},
                    "porcentaje": {"type": "number"}
                },
                "required": ["precio", "porcentaje"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "acceder_pagina_web",
            "description": "Accede a una página web y extrae su contenido. Úsalo cuando el usuario pida información de una página específica o quiera que verifiques contenido web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "La URL completa de la página (ej: 'https://www.wikipedia.org' o 'google.com')"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convertir_unidades",
            "description": "Convierte unidades de medida entre diferentes sistemas. Soporta temperatura (celsius, fahrenheit, kelvin), longitud (metros, kilometros, millas, pies, pulgadas), masa (gramos, kilogramos, libras, onzas), volumen (litros, mililitros, galones, onzas líquidas) y tiempo (segundos, minutos, horas, días, semanas).",
            "parameters": {
                "type": "object",
                "properties": {
                    "valor": {
                        "type": "number",
                        "description": "El valor numérico a convertir"
                    },
                    "de": {
                        "type": "string",
                        "description": "Unidad de origen (ej: 'celsius', 'metros', 'kilogramos', 'litros', 'horas')"
                    },
                    "a": {
                        "type": "string",
                        "description": "Unidad de destino (ej: 'fahrenheit', 'kilometros', 'libras', 'galones', 'dias')"
                    }
                },
                "required": ["valor", "de", "a"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "traducir_texto",
            "description": "Traduce texto entre diferentes idiomas. Soporta español (es), inglés (en), francés (fr), alemán (de), italiano (it), portugués (pt) y muchos más. Usa esta función cuando el usuario pida traducir texto o necesite comunicación en diferentes idiomas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "texto": {
                        "type": "string",
                        "description": "El texto que quieres traducir"
                    },
                    "idioma_origen": {
                        "type": "string",
                        "description": "Código del idioma de origen (ej: 'es' para español, 'en' para inglés, 'fr' para francés)"
                    },
                    "idioma_destino": {
                        "type": "string",
                        "description": "Código del idioma de destino (ej: 'en' para inglés, 'es' para español, 'fr' para francés)"
                    }
                },
                "required": ["texto", "idioma_origen", "idioma_destino"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "enviar_email",
            "description": "Envía un email a un destinatario. Requiere configuración de EMAIL_USER, EMAIL_PASSWORD, SMTP_SERVER y SMTP_PORT en el archivo .env. Para Gmail, usa app password en lugar de tu contraseña normal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "destinatario": {
                        "type": "string",
                        "description": "Email del destinatario (ej: 'usuario@gmail.com')"
                    },
                    "asunto": {
                        "type": "string",
                        "description": "Asunto del email"
                    },
                    "mensaje": {
                        "type": "string",
                        "description": "Contenido del mensaje a enviar"
                    },
                    "tipo": {
                        "type": "string",
                        "description": "Tipo de contenido del mensaje: 'plain' para texto o 'html' para HTML",
                        "default": "plain"
                    }
                },
                "required": ["destinatario", "asunto", "mensaje"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "leer_emails",
            "description": "Lee los emails más recientes de la bandeja de entrada. Requiere configuración de EMAIL_USER, EMAIL_PASSWORD e IMAP_SERVER en el archivo .env. Para Gmail, usa app password.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cantidad": {
                        "type": "integer",
                        "description": "Número de emails a leer (1-10, por defecto 5)",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "leer_noticias",
            "description": "Lee las noticias más recientes desde feeds RSS gratuitos de fuentes confiables como BBC, Reuters, CNN, New York Times, El País, Clarín, The Guardian, Washington Post, Al Jazeera, AP, NPR, The Verge, TechCrunch, Ars Technica, Wired, ABC, CBS, NBC, Fox News, HuffPost, Politico, Axios, Vice y Mashable.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fuente": {
                        "type": "string",
                        "description": "Fuente de noticias: 'bbc', 'reuters', 'cnn', 'nytimes', 'elpais', 'clarin'",
                        "default": "bbc"
                    },
                    "cantidad": {
                        "type": "integer",
                        "description": "Número de noticias a obtener (1-10)",
                        "minimum": 1,
                        "maximum": 10,
                        "default": 5
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "ejecutar_sql",
            "description": "Ejecuta una consulta SQL en una base de datos SQLite local. Úsalo para crear, insertar, actualizar o consultar datos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "description": "Ruta del archivo SQLite local (por defecto 'agente.db')",
                        "default": "agente.db"
                    },
                    "query": {
                        "type": "string",
                        "description": "Consulta SQL a ejecutar"
                    },
                    "parametros": {
                        "type": "array",
                        "items": {"type": ["string", "number", "boolean", "null"]},
                        "description": "Lista de parámetros para la consulta preparada"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_tablas",
            "description": "Lista las tablas existentes en una base de datos SQLite local.",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "description": "Ruta del archivo SQLite local (por defecto 'agente.db')",
                        "default": "agente.db"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "info_tabla",
            "description": "Obtiene información detallada sobre las columnas, tipos y estructura de una tabla.",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "description": "Ruta del archivo SQLite local (por defecto 'agente.db')",
                        "default": "agente.db"
                    },
                    "tabla": {
                        "type": "string",
                        "description": "Nombre de la tabla"
                    }
                },
                "required": ["tabla"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "contar_registros",
            "description": "Cuenta el número total de registros en una tabla.",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "description": "Ruta del archivo SQLite local (por defecto 'agente.db')",
                        "default": "agente.db"
                    },
                    "tabla": {
                        "type": "string",
                        "description": "Nombre de la tabla"
                    }
                },
                "required": ["tabla"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_en_tabla",
            "description": "Busca registros en una tabla por un valor en una columna específica (búsqueda parcial).",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "description": "Ruta del archivo SQLite local (por defecto 'agente.db')",
                        "default": "agente.db"
                    },
                    "tabla": {
                        "type": "string",
                        "description": "Nombre de la tabla donde buscar"
                    },
                    "columna": {
                        "type": "string",
                        "description": "Nombre de la columna donde buscar"
                    },
                    "valor": {
                        "type": "string",
                        "description": "Valor a buscar (búsqueda parcial con LIKE)"
                    }
                },
                "required": ["tabla", "columna", "valor"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "backup_db",
            "description": "Realiza un backup completo de la base de datos SQLite. Si no especificas ruta, crea backup_TIMESTAMP.db",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "description": "Ruta del archivo SQLite original (por defecto 'agente.db')",
                        "default": "agente.db"
                    },
                    "backup_path": {
                        "type": "string",
                        "description": "Ruta donde guardar el backup (opcional, genera automáticamente si no se especifica)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "limpiar_tabla",
            "description": "Elimina todos los registros de una tabla, dejándola vacía. ¡CUIDADO! Esta acción es irreversible.",
            "parameters": {
                "type": "object",
                "properties": {
                    "db_path": {
                        "type": "string",
                        "description": "Ruta del archivo SQLite local (por defecto 'agente.db')",
                        "default": "agente.db"
                    },
                    "tabla": {
                        "type": "string",
                        "description": "Nombre de la tabla a limpiar"
                    }
                },
                "required": ["tabla"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_en_web",
            "description": (
                "Busca información actualizada en Google. Úsala para noticias recientes, "
                "eventos actuales o cualquier dato que pueda haber cambiado después del "
                "entrenamiento del modelo."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "consulta": {
                        "type": "string",
                        "description": "Consulta a buscar en Google (ej: 'últimas noticias sobre IA')"
                    },
                    "num_resultados": {
                        "type": "integer",
                        "description": "Cantidad de resultados (por defecto 5, máximo 10)",
                        "default": 5
                    }
                },
                "required": ["consulta"]
            }
        }
    }
]

# ==================== DICCIONARIO DE FUNCIONES DISPONIBLES ====================

AVAILABLE_FUNCTIONS = {
    "obtener_clima": obtener_clima,
    "calcular_descuento": calcular_descuento,
    "acceder_pagina_web": acceder_pagina_web,
    "convertir_unidades": convertir_unidades,
    "traducir_texto": traducir_texto,
    "enviar_email": enviar_email,
    "leer_emails": leer_emails,
    "leer_noticias": leer_noticias,
    "ejecutar_sql": ejecutar_sql,
    "listar_tablas": listar_tablas,
    "info_tabla": info_tabla,
    "contar_registros": contar_registros,
    "buscar_en_tabla": buscar_en_tabla,
    "backup_db": backup_db,
    "limpiar_tabla": limpiar_tabla,
    "buscar_en_web": buscar_en_web
}
