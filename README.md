# ⬛ BLACKBOX
### escucha con intención · música libre · mente abierta

Reproductor de música offline con descarga desde YouTube.
Gótico minimalista. Ratas, unicornios, dragones.

---

## 🐉 Setup en Termux (Android)

### 1. Instalar dependencias
```bash
pkg update && pkg upgrade
pkg install python ffmpeg
pip install flask flask-cors yt-dlp mutagen
```

### 2. Clonar / copiar el proyecto
```bash
# Copia la carpeta blackbox/ a tu almacenamiento
cp -r blackbox/ ~/storage/shared/blackbox/
cd ~/storage/shared/blackbox/
```

### 3. Iniciar el servidor backend
```bash
python server.py
```
El servidor corre en `http://localhost:5000`

### 4. Abrir el reproductor
En el navegador (Chrome/Firefox en Android):
```
file:///storage/emulated/0/blackbox/index.html
```

O si usas termux-httpd:
```bash
pkg install termux-services
# Sirve el frontend en puerto 8080
python -m http.server 8080
# Abre: http://localhost:8080
```

---

## 📱 Uso

### Reproducir música local
1. Sección **Biblioteca** → **+ cargar archivo**
2. Selecciona archivos MP3/M4A/OGG de tu dispositivo
3. Doble tap en cualquier canción para reproducir

### Descargar de YouTube
1. Asegúrate que `server.py` esté corriendo
2. Sección **Descargar** → pega URL de YouTube
3. Puede ser canción individual o playlist completo

### Controles del reproductor
- **▶/⏸** — Play/Pause
- **⏮/⏭** — Anterior/Siguiente
- **⇌** — Aleatorio
- **↻** — Repetir (off / todo / una)

### Notas por canción
1. Pon a sonar una canción
2. Sección **Notas** → escribe tu pensamiento o sentimiento
3. Queda guardado en la base de datos local

### Juegos
- **PAC·RAT** — Pac-Man con rata gótica
- **VOID DRAGON** — nave espacial vs el vacío
- **PIXEL ALTAR** — editor de pixel art (guarda PNG)

---

## 🗃️ Arquitectura

```
blackbox/
├── index.html          — App principal
├── css/
│   └── style.css       — Estética gótica
├── js/
│   ├── db.js           — IndexedDB (tracks, notas, settings)
│   ├── player.js       — Motor de audio
│   ├── library.js      — Biblioteca, artistas, búsqueda
│   ├── download.js     — Cliente del backend YT
│   ├── notes.js        — Sistema de notas
│   ├── games.js        — PAC·RAT, VOID DRAGON, PIXEL ALTAR
│   └── app.js          — Controlador principal
└── server.py           — Backend Flask + yt-dlp
```

**Almacenamiento:**
- Música y metadatos → IndexedDB del navegador (offline)
- Archivos de audio → IndexedDB como Blob
- Descargas YT → carpeta `downloads/` (via backend)

---

## 🚀 Roadmap

- [ ] Etiquetas ID3 automáticas (MusicBrainz)
- [ ] Modo karaoke con letras (lrclib)
- [ ] Ecualizador
- [ ] Carga a dispositivo físico (Raspberry Pi Zero / ESP32 + pantalla)
- [ ] Sincronización entre dispositivos

---

*⬛ blackbox — música consciente y gratuita* 🐀🦄🐉
