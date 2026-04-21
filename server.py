#!/usr/bin/env python3
# server.py — Blackbox Backend Flask
# Instalar: pip install flask flask-cors yt-dlp
# Correr: python server.py

import os
import uuid
import threading
import hashlib
import glob
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

try:
    import yt_dlp
    from yt_dlp.utils import sanitize_filename
except ImportError:
    yt_dlp = None
    def sanitize_filename(s): return s

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

jobs = {}


# ── HEALTH ──────────────────────────────────
@app.route('/ping')
def ping():
    return jsonify({'status': 'alive', 'message': 'el dragon esta despierto'})


# ── START DOWNLOAD ───────────────────────────
@app.route('/download', methods=['POST'])
def download():
    if not yt_dlp:
        return jsonify({'error': 'yt-dlp no instalado — pip install yt-dlp'}), 500

    data    = request.get_json(force=True)
    url     = (data.get('url') or '').strip()
    fmt     = data.get('format', 'mp3')
    quality = str(data.get('quality', '128'))

    if not url:
        return jsonify({'error': 'URL requerida'}), 400

    job_id = uuid.uuid4().hex[:8]
    jobs[job_id] = {'status': 'pending', 'progress': 0, 'title': '...'}

    t = threading.Thread(target=run_download, args=(job_id, url, fmt, quality), daemon=True)
    t.start()

    return jsonify({'job_id': job_id})


# ── DOWNLOAD WORKER ──────────────────────────
def run_download(job_id, url, fmt, quality):
    ext = fmt if fmt in ('mp3', 'm4a', 'opus') else 'mp3'

    def postproc_hook(d):
        if d.get('status') == 'finished':
            jobs[job_id]['progress'] = min(jobs[job_id].get('progress', 0) + 10, 95)

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            done  = d.get('downloaded_bytes', 0)
            if total:
                jobs[job_id]['progress'] = int(done / total * 80)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': ext, 'preferredquality': quality},
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'},
        ],
        'writethumbnail': True,
        'progress_hooks':      [progress_hook],
        'postprocessor_hooks': [postproc_hook],
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        if info is None:
            jobs[job_id] = {'status': 'error', 'error': 'yt-dlp no pudo obtener info'}
            return

        entries = info.get('entries') or [info]
        results = []

        for entry in entries:
            if not entry:
                continue
            title    = entry.get('title') or 'sin titulo'
            artist   = entry.get('uploader') or entry.get('artist') or 'desconocido'
            album    = entry.get('album') or entry.get('playlist_title') or ''
            duration = entry.get('duration') or 0

            filepath = find_audio_file(title, ext)
            if not filepath:
                candidates = sorted(glob.glob(os.path.join(DOWNLOAD_DIR, f'*.{ext}')), key=os.path.getmtime, reverse=True)
                if candidates:
                    filepath = candidates[0]

            if not filepath or not os.path.exists(filepath):
                continue

            file_hash = compute_hash(filepath)
            cover_rel = find_cover(filepath, title)
            rel_audio = os.path.relpath(filepath, DOWNLOAD_DIR)

            results.append({
                'title':     title,
                'artist':    artist,
                'album':     album,
                'duration':  duration,
                'hash':      file_hash,
                'file_url':  f'/audio/{rel_audio}',
                'cover_url': f'/cover/{cover_rel}' if cover_rel else None,
            })

        if not results:
            jobs[job_id] = {'status': 'error', 'error': 'no se encontraron archivos de audio'}
            return

        if len(results) == 1:
            jobs[job_id] = {'status': 'done', 'progress': 100, **results[0]}
        else:
            jobs[job_id] = {'status': 'done', 'progress': 100, 'files': results}

    except Exception as e:
        jobs[job_id] = {'status': 'error', 'progress': 0, 'error': str(e)}


def find_audio_file(title, ext):
    safe = sanitize_filename(title)
    for candidate in [os.path.join(DOWNLOAD_DIR, f'{safe}.{ext}'),
                      os.path.join(DOWNLOAD_DIR, f'{title}.{ext}')]:
        if os.path.exists(candidate):
            return candidate
    prefix = safe[:30].lower()
    for f in os.listdir(DOWNLOAD_DIR):
        if f.lower().startswith(prefix) and f.endswith(f'.{ext}'):
            return os.path.join(DOWNLOAD_DIR, f)
    words = [w for w in safe.lower().split() if len(w) > 3]
    for f in os.listdir(DOWNLOAD_DIR):
        if not f.endswith(f'.{ext}'): continue
        if words and all(w in f.lower() for w in words[:2]):
            return os.path.join(DOWNLOAD_DIR, f)
    return None


def find_cover(audio_path, title):
    base = os.path.splitext(audio_path)[0]
    safe = sanitize_filename(title)
    for thumb_ext in ('jpg', 'jpeg', 'webp', 'png'):
        for candidate in (base, os.path.join(DOWNLOAD_DIR, safe)):
            full = f'{candidate}.{thumb_ext}'
            if os.path.exists(full):
                return os.path.relpath(full, DOWNLOAD_DIR)
    return None


def compute_hash(path):
    try:
        with open(path, 'rb') as f:
            return hashlib.sha256(f.read(65536)).hexdigest()
    except Exception:
        return ''


# ── STATUS ───────────────────────────────────
@app.route('/status/<job_id>')
def status(job_id):
    if job_id not in jobs:
        return jsonify({'status': 'not_found'}), 404
    return jsonify(jobs[job_id])


# ── SERVE FILES ──────────────────────────────
@app.route('/audio/<path:filename>')
def serve_audio(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if not os.path.exists(path):
        return jsonify({'error': 'archivo no encontrado'}), 404
    return send_file(path)

@app.route('/cover/<path:filename>')
def serve_cover(filename):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if not os.path.exists(path):
        return jsonify({'error': 'cover no encontrado'}), 404
    return send_file(path)

@app.route('/list')
def list_files():
    files = os.listdir(DOWNLOAD_DIR)
    return jsonify({'files': sorted(files), 'count': len(files)})


# ── MAIN ─────────────────────────────────────
if __name__ == '__main__':
    print()
    print('  ⬛  BLACKBOX SERVER')
    print(f'  Descargas en: {DOWNLOAD_DIR}')
    print('  Escuchando en http://0.0.0.0:5000')
    print()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
