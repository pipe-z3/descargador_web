# app.py mejorado con opciones de formato y calidad
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import yt_dlp
import os
import uuid
ffmpeg_path = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")
app = Flask(__name__)
app.secret_key = "clave_secreta_segura"

DESCARGAS = os.path.join(os.path.dirname(__file__), "videos")
os.makedirs(DESCARGAS, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        formato = request.form.get("formato")  # mp4 o mp3
        calidad = request.form.get("calidad")   # best, 720p, 1080p

        if not url:
            flash("Por favor, ingresa un enlace.")
            return redirect(url_for("index"))

        # Nombre temporal único
        nombre_temp = str(uuid.uuid4())
        salida = os.path.join(DESCARGAS, nombre_temp + ".%(ext)s")

        # Opciones base
        ydl_opts = {
            'ffmpeg_location': ffmpeg_path,
            'outtmpl': salida,
            'quiet': True,
            'format': 'best',  # reemplazaremos si se elige calidad
        }

        if calidad == "720p":
            ydl_opts['format'] = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif calidad == "1080p":
            ydl_opts['format'] = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"

        # Para audio
        if formato == "mp3":
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                archivo_salida = ydl.prepare_filename(info)

            # Asegurar extensión si es mp3
            if formato == "mp3":
                archivo_salida = archivo_salida.rsplit(".", 1)[0] + ".mp3"

            return send_file(archivo_salida, as_attachment=True)

        except Exception as e:
            flash(f"Ocurrió un error: {str(e)}")
            return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)

