import os
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, url_for, render_template_string, send_from_directory, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash


# ==========================================================
# 💎 HIDDENGEM
# ==========================================================

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "imagenes")
DB_PATH = os.path.join(BASE_DIR, "hidden_gem.db")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.secret_key = os.urandom(32)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

EXTENSIONES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}

def conectar_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

# Conserva la base de datos anterior si ya existe.
with conectar_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS creaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            creador TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            descripcion TEXT NOT NULL,
            correo TEXT NOT NULL,
            imagen TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            correo TEXT NOT NULL UNIQUE,
            contrasena TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)

PAGINA = r"""
<!DOCTYPE html>
<html lang="es">
<head>
<link rel="manifest" href="/static/manifest.json">
<meta name="theme-color" content="#c8b5e1">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="HiddenGem">

<script>
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/static/sw.js");
    });
}
</script>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HiddenGem | Your talent deserves to be discovered</title>

<style>
:root {
    --lavanda: #eee7f7;
    --lila: #c8b5e1;
    --lila-oscuro: #80669f;
    --texto: #332b3d;
    --suave: #faf8fd;
    --blanco: #ffffff;
    --borde: #eee8f4;
    --gris: #766d80;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    color: var(--texto);
    background: white;
}
button, input, select, textarea { font: inherit; }
a { color: inherit; text-decoration: none; }
button, .boton { cursor: pointer; }

.contenedor {
    width: min(1120px, 92%);
    margin: auto;
}

/* BARRA SUPERIOR FIJA */
header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: rgba(255,255,255,.97);
    border-bottom: 1px solid var(--borde);
    box-shadow: 0 3px 15px #49345b08;
}

.nav {
    min-height: 76px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 18px;
}

.logo {
    display: flex;
    align-items: center;
    gap: 9px;
    font-size: 24px;
    font-weight: bold;
    white-space: nowrap;
    letter-spacing: -.7px;
}

.gema-logo {
    color: var(--lila-oscuro);
    font-size: 35px;
    font-weight: normal;
}

nav {
    display: flex;
    align-items: center;
    gap: 5px;
}

.nav-link {
    border: 0;
    background: transparent;
    color: #665b72;
    padding: 11px 12px;
    border-radius: 10px;
    font-size: 13px;
    white-space: nowrap;
    transition: .2s;
}

.nav-link:hover { background: var(--suave); }

.nav-link.activo {
    background: var(--lavanda);
    color: #6f548e;
    font-weight: bold;
}

.boton {
    display: inline-block;
    border: 0;
    border-radius: 11px;
    padding: 13px 18px;
    background: var(--lila-oscuro);
    color: white;
    font-weight: bold;
    text-align: center;
    transition: .2s;
}

.boton:hover {
    background: #6d5489;
    transform: translateY(-1px);
}

.boton-claro {
    background: var(--lavanda);
    color: var(--texto);
}

.boton-claro:hover { background: #dfd2ef; }

/* PANTALLAS INDEPENDIENTES */
.pantalla {
    display: none;
    min-height: 68vh;
    animation: aparecer .25s ease;
}

.pantalla.activa { display: block; }

@keyframes aparecer {
    from { opacity: .45; transform: translateY(5px); }
    to { opacity: 1; transform: translateY(0); }
}

/* INICIO */
.hero {
    position: relative;
    overflow: hidden;
    background:
        radial-gradient(ellipse at 88% 24%, #eee6f8 0%, transparent 34%),
        linear-gradient(120deg, #fff 40%, #faf7fd 100%);
    padding: 92px 0 96px;
}

.hero-contenido {
    max-width: 720px;
    position: relative;
    z-index: 1;
}

.etiqueta {
    display: inline-block;
    padding: 9px 14px;
    background: #f1ebf8;
    color: #735b91;
    border-radius: 50px;
    font-size: 12px;
    letter-spacing: .8px;
    text-transform: uppercase;
}

h1 {
    font-size: clamp(39px, 6vw, 66px);
    line-height: 1.1;
    letter-spacing: -2px;
    margin: 23px 0;
}

h1 span { color: var(--lila-oscuro); }

.hero p {
    max-width: 590px;
    color: var(--gris);
    font-size: 17px;
    line-height: 1.8;
}

.acciones {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 28px;
}

.gema-flotante {
    position: absolute;
    right: 8%;
    top: 17%;
    font-size: clamp(120px, 19vw, 230px);
    color: #d7c7e9;
    opacity: .5;
    transform: rotate(12deg);
    user-select: none;
}

.bloque-inicio {
    padding: 36px 0;
    text-align: center;
    background: white;
}

.bloque-inicio h2 { margin-bottom: 10px; }
.bloque-inicio p {
    color: var(--gris);
    line-height: 1.7;
}

/* ENCABEZADOS */
.seccion {
    padding: 65px 0 75px;
}

.fondo-suave { background: var(--suave); }

.encabezado {
    max-width: 720px;
    text-align: center;
    margin: 0 auto 35px;
}

.gema-mini {
    color: #b9a4d7;
    font-size: 28px;
}

.encabezado h2 {
    font-size: clamp(28px, 4vw, 39px);
    letter-spacing: -.8px;
    margin: 12px 0;
}

.encabezado p {
    color: var(--gris);
    line-height: 1.8;
    margin: 0;
}

/* MISIÓN Y VISIÓN */
.tarjetas-info {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 22px;
}

.tarjeta-info {
    background: white;
    border: 1px solid var(--borde);
    border-radius: 20px;
    padding: 30px;
}

.icono-gema {
    width: 50px;
    height: 50px;
    display: grid;
    place-items: center;
    border-radius: 15px;
    background: #f2ecf9;
    color: var(--lila-oscuro);
    font-size: 28px;
}

.tarjeta-info h3 {
    font-size: 23px;
    margin: 20px 0 12px;
}

.tarjeta-info p {
    color: var(--gris);
    line-height: 1.9;
    margin: 0;
}

/* EXPLORAR */
.barra-catalogo {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 25px;
}

.busqueda { flex: 1; min-width: 200px; }

.busqueda input, .barra-catalogo select {
    width: 100%;
    padding: 14px;
    border: 1px solid #e5ddeb;
    border-radius: 11px;
    background: white;
    outline: none;
}

.barra-catalogo select { max-width: 230px; }

input:focus, select:focus, textarea:focus {
    border-color: var(--lila-oscuro) !important;
    outline: none;
}

.catalogo {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 22px;
}

.tarjeta-obra {
    background: white;
    border: 1px solid var(--borde);
    border-radius: 18px;
    overflow: hidden;
    transition: .2s;
}

.tarjeta-obra:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 28px #49345b12;
}

.imagen-obra {
    display: block;
    width: 100%;
    height: 220px;
    object-fit: cover;
    background: var(--lavanda);
}

.contenido-obra { padding: 18px; }

.categoria {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 50px;
    background: #f2edf8;
    color: #765d94;
    font-size: 11px;
}

.contenido-obra h3 {
    font-size: 19px;
    margin: 13px 0 7px;
    overflow-wrap: anywhere;
}

.creador {
    font-size: 13px;
    color: #81788a;
}

.descripcion-obra {
    font-size: 14px;
    line-height: 1.65;
    color: #6e6677;
    overflow-wrap: anywhere;
    min-height: 45px;
}

.pie-obra {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-top: 17px;
    padding-top: 15px;
    border-top: 1px solid var(--borde);
}

.precio { font-size: 19px; font-weight: bold; }

.corazon {
    border: 0;
    border-radius: 10px;
    background: #f5f0fa;
    color: #765d94;
    padding: 9px 11px;
}

.corazon.activo { background: #e5d8f4; }

.contactar {
    display: block;
    text-align: center;
    margin-top: 12px;
    padding: 10px;
    border-radius: 10px;
    background: #f5f0fa;
    color: #6f558d;
    font-weight: bold;
    font-size: 13px;
}

.mensaje-vacio {
    grid-column: 1 / -1;
    text-align: center;
    padding: 35px;
    border: 1px dashed #d8cbe8;
    border-radius: 18px;
    color: var(--gris);
    line-height: 1.7;
}

/* PUBLICAR */
.formulario {
    max-width: 760px;
    margin: auto;
    padding: 30px;
    background: white;
    border: 1px solid var(--borde);
    border-radius: 20px;
}

.aviso {
    padding: 14px;
    border-radius: 11px;
    margin-bottom: 22px;
    background: #f2edf8;
    color: #604b79;
    font-size: 13px;
    line-height: 1.7;
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 18px;
}

.grupo {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.grupo.completo { grid-column: 1 / -1; }

.grupo label {
    font-size: 13px;
    font-weight: bold;
}

.grupo input, .grupo select, .grupo textarea {
    width: 100%;
    padding: 13px;
    border: 1px solid #e5ddeb;
    border-radius: 10px;
    background: white;
}

.grupo textarea {
    min-height: 110px;
    resize: vertical;
}

.ayuda {
    font-size: 12px;
    line-height: 1.6;
    color: #82798b;
}

/* FAVORITOS */
.nota-favoritos {
    text-align: center;
    color: var(--gris);
    margin: -12px 0 28px;
    line-height: 1.7;
}

/* FINAL Y PIE */
.frase-final {
    padding: 50px 20px;
    text-align: center;
    background: #fbf9fd;
}

.frase-final .gema-grande {
    color: #c5b1df;
    font-size: 43px;
}

.frase-final h2 {
    font-size: clamp(25px, 4vw, 37px);
    margin: 10px 0;
}

.frase-final p {
    color: var(--gris);
    margin-bottom: 23px;
}

footer {
    padding: 25px 0;
    background: white;
    border-top: 1px solid var(--borde);
    color: #80768b;
    font-size: 13px;
    text-align: center;
    line-height: 1.8;
}

footer strong { color: #6e548e; }

[hidden] { display: none !important; }


/* 🌙 TEMA OSCURO DE HIDDENGEM */

body.tema-oscuro {
    --texto: #f5e8eb;
    --suave: #30252e;
    --blanco: #30252e;
    --borde: #59404f;
    --gris: #d0b9c4;
    --fondo: #211b24;
    --tarjeta: #30252e;

    background:
        radial-gradient(ellipse at 8% 15%, #49303f 0%, transparent 38%),
        radial-gradient(ellipse at 92% 45%, #49342e 0%, transparent 35%),
        var(--fondo);
    color: var(--texto);
}

body.tema-oscuro header,
body.tema-oscuro footer,
body.tema-oscuro .bloque-inicio {
    background: rgba(39, 30, 41, .96);
    color: var(--texto);
}

body.tema-oscuro .hero {
    background:
        radial-gradient(ellipse at 85% 20%, #503346 0%, transparent 40%),
        radial-gradient(ellipse at 65% 90%, #49362f 0%, transparent 38%),
        linear-gradient(120deg, #261e2a, #30232d);
}

body.tema-oscuro .fondo-suave,
body.tema-oscuro .frase-final {
    background:
        radial-gradient(ellipse at 10% 20%, #49303f 0%, transparent 42%),
        radial-gradient(ellipse at 90% 80%, #49342e 0%, transparent 40%),
        #29212d;
}

body.tema-oscuro .tarjeta-info,
body.tema-oscuro .tarjeta-obra,
body.tema-oscuro .formulario,
body.tema-oscuro .grupo input,
body.tema-oscuro .grupo select,
body.tema-oscuro .grupo textarea,
body.tema-oscuro .busqueda input,
body.tema-oscuro .barra-catalogo select {
    background-color: var(--tarjeta);
    color: var(--texto);
    border-color: var(--borde);
}

body.tema-oscuro .nav-link {
    color: #e4d1dc;
}

body.tema-oscuro .nav-link.activo,
body.tema-oscuro .etiqueta,
body.tema-oscuro .icono-gema,
body.tema-oscuro .aviso,
body.tema-oscuro .categoria,
body.tema-oscuro .corazon,
body.tema-oscuro .contactar {
    background: #493344;
    color: #f5d2df;
}

body.tema-oscuro .boton-claro {
    background: linear-gradient(120deg, #493344, #514035);
    color: #fff0f2;
}

body.tema-oscuro .gema-logo,
body.tema-oscuro h1 span {
    color: #e8a9bd;
}

body.tema-oscuro .creador,
body.tema-oscuro .descripcion-obra,
body.tema-oscuro .ayuda,
body.tema-oscuro footer {
    color: var(--gris);
}

body.tema-oscuro .acceso-qr {
    background: var(--tarjeta);
    border-color: var(--borde);
}

body.tema-oscuro .mensaje-vacio {
    border-color: var(--borde);
    color: var(--gris);
}


/* 🖼️ VISOR DE IMÁGENES GRANDES */

#visor-imagen {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: rgba(25, 19, 29, 0.94);
    align-items: center;
    justify-content: center;
    padding: 55px 20px 25px;
}

#visor-imagen.abierto {
    display: flex;
}

#imagen-ampliada {
    max-width: 95%;
    max-height: 85vh;
    width: auto;
    height: auto;
    object-fit: contain;
    border-radius: 10px;
    transition: transform 0.2s ease;
    cursor: zoom-in;
}

#cerrar-visor,
#acercar-visor,
#alejar-visor {
    position: absolute;
    border: 1px solid #ffffff55;
    background: #49353a;
    color: white;
    border-radius: 50%;
    width: 44px;
    height: 44px;
    font-size: 23px;
    cursor: pointer;
}

#cerrar-visor {
    top: 12px;
    right: 15px;
}

#acercar-visor {
    right: 72px;
    bottom: 20px;
}

#alejar-visor {
    right: 124px;
    bottom: 20px;
}

.imagen-obra {
    cursor: zoom-in;
}

@media (max-width: 560px) {
    #imagen-ampliada {
        max-width: 100%;
        max-height: 80vh;
    }
}


/* ADAPTACIÓN A TELÉFONOS */
@media (max-width: 920px) {
    .nav {
        flex-direction: column;
        align-items: flex-start;
        padding: 12px 0;
        gap: 8px;
    }
    nav {
        width: 100%;
        overflow-x: auto;
        padding-bottom: 3px;
    }
    .nav-link { flex-shrink: 0; }
    .catalogo { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .gema-flotante { right: 0; opacity: .25; }
}

@media (max-width: 560px) {
    .hero { padding: 55px 0; }
    .seccion { padding: 48px 0; }
    .tarjetas-info, .catalogo, .form-grid { grid-template-columns: 1fr; }
    .grupo.completo { grid-column: auto; }
    .formulario { padding: 20px; }
    .barra-catalogo select { max-width: none; }
    .imagen-obra { height: 240px; }
}

/* ✨ DECORACIÓN ARTÍSTICA DE HIDDENGEM */
.pantalla {
    position: relative;
    isolation: isolate;
}

.pantalla::before,
.pantalla::after {
    position: absolute;
    top: 115px;
    z-index: 5;
    pointer-events: none;
    white-space: pre-line;
    color: #b9a4d7;
    opacity: 0.22;
    font-size: 27px;
    line-height: 3;
    font-weight: normal;
}

.pantalla::before {
    content: "◇\A ✎\A ✧\A 🖌";
    left: 12px;
}

.pantalla::after {
    content: "✧\A ◇\A 🖌\A ✎";
    right: 12px;
    text-align: center;
}

/* Los dibujos no deben estorbar en pantallas pequeñas */
@media (max-width: 560px) {
    .pantalla::before,
    .pantalla::after {
        font-size: 17px;
        opacity: 0.13;
    }

    .pantalla::before { left: 3px; }
    .pantalla::after { right: 3px; }
}

/* ✨ ANIMACIONES DE BOTONES */
.boton,
.nav-link,
.corazon,
.contactar {
    transition:
        transform 0.25s ease,
        background-color 0.25s ease,
        box-shadow 0.25s ease;
}

.boton:hover,
.contactar:hover {
    transform: translateY(-3px);
    box-shadow: 0 7px 17px #80669f25;
}

.boton:active,
.nav-link:active,
.corazon:active {
    transform: scale(0.96);
}

.nav-link:hover {
    transform: translateY(-2px);
}

.corazon:hover {
    transform: scale(1.06);
}

@keyframes gemaBrilla {
    0%, 100% { opacity: 0.45; }
    50% { opacity: 0.8; }
}

.gema-flotante {
    animation: gemaBrilla 4s ease-in-out infinite;
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: 0.01ms !important;
    }
}


/* 💗 NUEVA PALETA HIDDENGEM: CREMA, ROSA Y MELÓN */

:root {
    --lavanda: #f7e5e9;
    --lila: #efbfc5;
    --lila-oscuro: #a95f75;
    --texto: #49353a;
    --suave: #fff6ed;
    --blanco: #ffffff;
    --borde: #f0d9d7;
    --gris: #806c6c;

    --fondo: #fffaf2;
    --tarjeta: #ffffff;
    --rosa: #f5d2d7;
    --melon: #f8d9c4;
}

/* Fondos principales con colores suaves mezclados */
body {
    background:
        radial-gradient(ellipse at 8% 15%, #fbe2e8 0%, transparent 35%),
        radial-gradient(ellipse at 92% 45%, #fbe1cf 0%, transparent 32%),
        var(--fondo);
    color: var(--texto);
}

header {
    background: rgba(255, 250, 242, 0.94);
    backdrop-filter: blur(12px);
}

.hero {
    background:
        radial-gradient(ellipse at 85% 20%, #f6d4dc 0%, transparent 38%),
        radial-gradient(ellipse at 65% 90%, #f9dfca 0%, transparent 36%),
        linear-gradient(120deg, #fffaf2, #fff2f0);
}

.bloque-inicio,
.tarjeta-info,
.tarjeta-obra,
.formulario,
.grupo input,
.grupo select,
.grupo textarea,
.busqueda input,
.barra-catalogo select {
    background-color: var(--tarjeta);
}

.fondo-suave,
.frase-final {
    background:
        radial-gradient(ellipse at 10% 20%, #fbe5e8 0%, transparent 40%),
        radial-gradient(ellipse at 90% 80%, #fbe1cc 0%, transparent 38%),
        #fff8f0;
}

.etiqueta,
.icono-gema,
.aviso {
    background: #fbe5e8;
    color: #96566b;
}

.nav-link.activo {
    background: #f7e1e6;
    color: #96566b;
}

.boton {
    background: linear-gradient(120deg, #b66b80, #d58b8c);
    color: #ffffff;
}

.boton:hover {
    background: linear-gradient(120deg, #a45a71, #c77b7d);
}

.boton-claro {
    background: linear-gradient(120deg, #f8e0e5, #fbe3cf);
    color: #69444d;
}

.boton-claro:hover {
    background: linear-gradient(120deg, #f2cfd8, #f8d6bd);
}

.categoria,
.corazon,
.contactar {
    background: #f9e8e9;
    color: #96566b;
}

.corazon.activo {
    background: #f2cbd4;
}

.gema-logo,
h1 span {
    color: #ad647b;
}

.gema-flotante,
.gema-mini,
.frase-final .gema-grande {
    color: #d6a0a7;
}

.pantalla::before,
.pantalla::after {
    color: #d49b9b;
}

footer {
    background: #fff8f0;
}

@media (max-width: 560px) {
    .hero {
        background:
            radial-gradient(ellipse at 90% 15%, #f6d4dc 0%, transparent 45%),
            linear-gradient(120deg, #fffaf2, #fff2f0);
    }
}

</style>
</head>

<body>

<!-- 💎 ACCESO A HIDDENGEM -->
<style>
.acceso-hg {
    background: linear-gradient(135deg, #f7effb, #fff5f2);
    padding: 45px 20px;
    text-align: center;
}

.acceso-hg h2 {
    color: #80669f;
    margin-bottom: 8px;
}

.acceso-hg .subtitulo {
    color: #766d80;
    margin-bottom: 25px;
}

.acceso-contenedor {
    display: flex;
    justify-content: center;
    align-items: stretch;
    flex-wrap: wrap;
    gap: 20px;
    max-width: 850px;
    margin: auto;
}

.acceso-tarjeta {
    background: white;
    padding: 25px;
    border-radius: 18px;
    width: min(100%, 380px);
    box-shadow: 0 5px 20px #80669f18;
    text-align: left;
}

.acceso-tarjeta h3 {
    color: #80669f;
    text-align: center;
    margin-top: 0;
}

.acceso-tarjeta label {
    display: block;
    margin: 13px 0 6px;
    font-size: 14px;
}

.acceso-tarjeta input {
    width: 100%;
    padding: 12px;
    border: 1px solid #e5d9ef;
    border-radius: 9px;
    outline-color: #c8b5e1;
}

.acceso-tarjeta button {
    width: 100%;
    margin-top: 20px;
}
</style>

{% if not session.get("usuario_id") %}
<section class="acceso-hg">
    <div class="gema-grande">◇</div>

    <h2>Bienvenido/a a HiddenGem</h2>

    <p class="subtitulo">
        Inicia sesión o crea tu cuenta para formar parte de nuestra comunidad.
    </p>

    <div class="acceso-contenedor">

        <!-- INICIAR SESIÓN -->
        <form class="acceso-tarjeta"
              action="{{ url_for('login') }}" method="POST">

            <h3>Iniciar sesión</h3>

            <label for="login-identificador">Usuario o correo</label>
            <input id="login-identificador" name="identificador"
                   type="text" required placeholder="Tu usuario o correo">

            <label for="login-contrasena">Contraseña</label>
            <input id="login-contrasena" name="contrasena"
                   type="password" required placeholder="Tu contraseña">

            <button class="boton" type="submit">
                Entrar a mi cuenta
            </button>
        </form>

        <!-- CREAR CUENTA -->
        <form class="acceso-tarjeta"
              action="{{ url_for('registro') }}" method="POST">

            <h3>Crear una cuenta</h3>

            <label for="registro-nombre">Nombre completo</label>
            <input id="registro-nombre" name="nombre"
                   type="text" maxlength="80" required placeholder="Tu nombre">

            <label for="registro-usuario">Nombre de usuario</label>
            <input id="registro-usuario" name="usuario"
                   type="text" maxlength="30" required placeholder="Ej. gema123">

            <label for="registro-correo">Correo electrónico</label>
            <input id="registro-correo" name="correo"
                   type="email" maxlength="120" required placeholder="tu@email.com">

            <label for="registro-contrasena">Contraseña</label>
            <input id="registro-contrasena" name="contrasena"
                   type="password" minlength="8" required placeholder="Mínimo 8 caracteres">

            <button class="boton" type="submit">
                Crear mi cuenta
            </button>
        </form>

    </div>
</section>
{% endif %}


{% if session.get("usuario_id") %}
<header>
    <div class="contenedor nav">
        <a href="#inicio" class="logo" data-ir="inicio">
            <span class="gema-logo">◇</span>
            HiddenGem
        </a>

        <nav aria-label="Navegación principal">

            <button class="nav-link activo" data-ir="inicio">Inicio</button>
            <button class="nav-link" data-ir="nosotros">Misión y visión</button>
            <button class="nav-link" data-ir="explorar">Explorar</button>
            <button class="nav-link" data-ir="publicar">Publicar creación</button>
            <button class="nav-link" data-ir="favoritos">Favoritos ♡</button>
<button class="nav-link" data-ir="perfil">Mi perfil ♡</button>
<button type="button" class="nav-link" id="boton-tema" aria-label="Cambiar tema">
    🌙 Tema oscuro
</button>


        </nav>
    </div>
</header>
{% endif %}

<main>
    <!-- PANTALLA INICIO -->
{% if session.get("usuario_id") %}
    <div class="acceso-tarjeta" style="margin: 20px auto; text-align:center;">
        <h3>¡Hola, {{ session.get("nombre_usuario") }}! 💎</h3>
        <p>Qué alegría tenerte en HiddenGem.</p>
    </div>
{% endif %}
    {% if session.get("usuario_id") %}
    <section class="pantalla activa" id="pantalla-inicio">
        <div class="hero">
            <div class="contenedor">
                <div class="hero-contenido">
                    <span class="etiqueta">◇ Un espacio para nuevos talentos</span>
                    <h1>Tu talento es una joya.<br>
                        <span>Deja que el mundo la descubra.</span>
                    </h1>
                    <p>
                        HiddenGem conecta a artistas y creadores emergentes
                        con personas que valoran lo hecho con creatividad,
                        pasión y dedicación. Tu próxima gran oportunidad
                        puede comenzar aquí.
                    </p>
                    <div class="acciones">
                        <button class="boton" data-ir="explorar">Descubrir creaciones</button>
                        <button class="boton boton-claro" data-ir="publicar">Compartir mi talento</button>
                    </div>

                </div>
            </div>
            <div class="gema-flotante" aria-hidden="true">◇</div>
        </div>

        <div class="bloque-inicio">
            <div class="contenedor">
                <h2>◇ Cada creación tiene una historia</h2>
                <p>
                    Descubre artistas, encuentra piezas especiales y apoya
                    el talento que merece una oportunidad.
                </p>
                <button class="boton boton-claro" data-ir="nosotros">Conoce HiddenGem</button>
            </div>
        </div>

        <div class="frase-final">
            <div class="gema-grande" aria-hidden="true">◇ ✧ ◇</div>
            <h2>Your talent deserves to be discovered.</h2>
            <p>Cada gran historia puede comenzar con una joya escondida.</p>
            <button class="boton" data-ir="publicar">Comparte tu talento</button>
        </div>
    </section>

    <!-- PANTALLA MISIÓN Y VISIÓN -->
    <section class="pantalla" id="pantalla-nosotros">
        <div class="seccion fondo-suave">
            <div class="contenedor">
                <div class="encabezado">
                    <span class="gema-mini">◇</span>
                    <h2>Conoce el corazón de HiddenGem</h2>
                    <p>
                        Creemos que el talento no necesita ser famoso para
                        tener valor. Solo necesita una oportunidad para brillar.
                    </p>
                </div>

                <div class="tarjetas-info">
                    <article class="tarjeta-info">
                        <div class="icono-gema" aria-hidden="true">◇</div>
                        <h3>Nuestra misión</h3>
                        <p>
                            Brindar un espacio accesible donde jóvenes artistas
                            y creadores puedan mostrar y ofrecer sus creaciones,
                            conectar con posibles compradores y tener más
                            oportunidades para desarrollar su talento.
                        </p>
                    </article>

                    <article class="tarjeta-info">
                        <div class="icono-gema" aria-hidden="true">✧</div>
                        <h3>Nuestra visión</h3>
                        <p>
                            Ser una plataforma reconocida por descubrir y apoyar
                            nuevos talentos, creando una comunidad donde la
                            creatividad sea valorada y cada creación tenga la
                            oportunidad de llegar a alguien que la aprecie.
                        </p>
                    </article>
                </div>
            </div>
        </div>
        <div class="frase-final">
            <div class="gema-grande">◇</div>
            <h2>Todo talento merece una oportunidad.</h2>
            <button class="boton" data-ir="explorar">Explorar creaciones</button>
        </div>
    </section>

    <!-- PANTALLA EXPLORAR -->
    <section class="pantalla" id="pantalla-explorar">
        <div class="seccion">
            <div class="contenedor">
                <div class="encabezado">
                    <span class="gema-mini">◇</span>
                    <h2>Explora pequeñas joyas</h2>
                    <p>
                        Encuentra arte, ideas y creaciones únicas de artistas
                        que están dando sus primeros pasos.
                    </p>
                </div>

                <div class="barra-catalogo">
                    <div class="busqueda">
                        <input id="busqueda" type="search"
                            placeholder="Buscar por nombre, artista o creación..."
                            aria-label="Buscar creaciones">
                    </div>
                    <select id="filtro" aria-label="Filtrar por categoría">
                        <option value="">Todas las categorías</option>
                        <option>Arte y dibujo</option>
                        <option>Pintura</option>
                        <option>Arte digital</option>
                        <option>Fotografía</option>
                        <option>Accesorios</option>
                        <option>Manualidades</option>
                        <option>Otros</option>
                    </select>
                </div>

                <div class="catalogo" id="lista-obras">
                    {% for obra in obras %}
                    <article class="tarjeta-obra"
                        data-busqueda="{{ (obra.titulo ~ ' ' ~ obra.creador ~ ' ' ~ obra.categoria ~ ' ' ~ obra.descripcion)|lower }}"
                        data-categoria="{{ obra.categoria }}"
                        data-id-obra="{{ obra.id }}">

                        <img class="imagen-obra"
                            src="{{ url_for('imagen_subida', nombre=obra.imagen) }}"
                            alt="Creación: {{ obra.titulo }}"
                            loading="lazy">

                        <div class="contenido-obra">
                            <span class="categoria">{{ obra.categoria }}</span>
                            <h3>{{ obra.titulo }}</h3>
                            <p class="creador">Creado por {{ obra.creador }}</p>
                            <p class="descripcion-obra">{{ obra.descripcion }}</p>

                            <div class="pie-obra">
                                <span class="precio">${{ "%.2f"|format(obra.precio) }}</span>
                                <button type="button" class="corazon"
                                    data-favorito="{{ obra.id }}"
                                    aria-label="Guardar en favoritos">♡ Guardar</button>
                            </div>

                            <a class="contactar"
                                href="mailto:{{ obra.correo|urlencode }}?subject={{ ('Me interesa tu creación: ' ~ obra.titulo)|urlencode }}">
                                Contactar al creador
                            </a>
                        </div>
                    </article>
                    {% else %}
                    <div class="mensaje-vacio" id="mensaje-vacio">
                        <div class="gema-mini">◇</div>
                        <h3>¡Tu creación puede ser la primera joya!</h3>
                        <p>Aún no hay creaciones publicadas. Anímate a compartir la tuya.</p>
                        <button class="boton" data-ir="publicar">Publicar mi creación</button>
                    </div>
                    {% endfor %}

                    <div class="mensaje-vacio" id="sin-coincidencias" hidden>
                        <h3>No encontramos esa joyita todavía</h3>
                        <p>Prueba otra palabra o selecciona otra categoría.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- PANTALLA PUBLICAR -->
    <section class="pantalla" id="pantalla-publicar">
        <div class="seccion fondo-suave">
            <div class="contenedor">
                <div class="encabezado">
                    <span class="gema-mini">◇</span>
                    <h2>Tu creación merece ser descubierta</h2>
                    <p>
                        Comparte los detalles de tu obra para que otras personas
                        puedan conocerla y contactarte.
                    </p>
                </div>

                <form class="formulario" action="{{ url_for('publicar') }}"
                    method="POST" enctype="multipart/form-data">

                    <div class="aviso">
                        💎 <strong>Antes de publicar:</strong> este es un prototipo
                        de prueba. Usa datos de prueba y un correo destinado a
                        este proyecto. El correo que registres será visible
                        para quienes quieran contactarte.
                    </div>

                    <div class="form-grid">
                        <div class="grupo">
                            <label for="titulo">Nombre de la creación *</label>
                            <input id="titulo" name="titulo" type="text"
                                maxlength="100" required
                                placeholder="Ej. Atardecer de ensueño">
                        </div>

                        <div class="grupo">
                            <label for="creador">Nombre del artista *</label>
                            <input id="creador" name="creador" type="text"
                                maxlength="80" required
                                placeholder="¿Quién la creó?">
                        </div>

                        <div class="grupo">
                            <label for="categoria">Categoría *</label>
                            <select id="categoria" name="categoria" required>
                                <option value="">Selecciona una categoría</option>
                                <option>Arte y dibujo</option>
                                <option>Pintura</option>
                                <option>Arte digital</option>
                                <option>Fotografía</option>
                                <option>Accesorios</option>
                                <option>Manualidades</option>
                                <option>Otros</option>
                            </select>
                        </div>

                        <div class="grupo">
                            <label for="precio">Precio en dólares (USD) *</label>
                            <input id="precio" name="precio" type="number"
                                min="0" max="1000000" step="0.01"
                                required placeholder="Ej. 15.00">
                        </div>

                        <div class="grupo completo">
                            <label for="descripcion">Cuéntanos sobre tu creación *</label>
                            <textarea id="descripcion" name="descripcion"
                                maxlength="1000" required
                                placeholder="¿Qué la hace especial?"></textarea>
                        </div>

                        <div class="grupo completo">
                            <label for="correo">Correo de contacto *</label>
                            <input id="correo" name="correo" type="email"
                                maxlength="150" required
                                placeholder="artista@ejemplo.com">
                            <span class="ayuda">
                                En esta versión, el botón de contacto abre
                                un correo para escribirle al creador.
                            </span>
                        </div>

                        <div class="grupo completo">
                            <label for="imagen">Fotografía de la creación *</label>
                            <input id="imagen" name="imagen" type="file"
                                accept=".jpg,.jpeg,.png,.webp,.gif"
                                required>
                            <span class="ayuda">
                                Formatos permitidos: JPG, PNG, WEBP o GIF.
                                Tamaño máximo: 8 MB.
                            </span>
                        </div>

                        <div class="grupo completo">
                            <button class="boton" type="submit">
                                ◇ Publicar mi creación
                            </button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </section>

    <!-- PANTALLA FAVORITOS -->
    <section class="pantalla" id="pantalla-favoritos">
        <div class="seccion">
            <div class="contenedor">
                <div class="encabezado">
                    <span class="gema-mini">♡</span>
                    <h2>Tus joyas favoritas</h2>
                    <p>
                        Aquí encontrarás las creaciones que hayas guardado
                        mientras exploras HiddenGem.
                    </p>
                </div>

                <p class="nota-favoritos">
                    Tus favoritos se guardan en este navegador.
                </p>

                <div class="catalogo" id="lista-favoritos"></div>
                <div class="mensaje-vacio" id="favoritos-vacios" hidden>
                    <div class="gema-mini">◇</div>
                    <h3>Aún no has guardado ninguna joya</h3>
                    <p>Explora las creaciones y presiona «Guardar» en las que te gusten.</p>
                    <button class="boton" data-ir="explorar">Explorar creaciones</button>
                </div>
            </div>
        </div>
    </section>

<!-- PANTALLA MI PERFIL -->
<section class="pantalla" id="pantalla-perfil">
    <div class="seccion">
        <div class="contenedor">

            <div class="encabezado">
                <span class="gema-mini">◇</span>
                <h2>Mi perfil</h2>
                <p>Este es tu pequeño espacio dentro de HiddenGem.</p>
            </div>

            <div class="acceso-tarjeta" style="max-width: 550px; margin: auto; text-align: center;">

                <div class="gema-mini" style="font-size: 45px;">💎</div>

                <h3>{{ session.get("nombre_usuario", "Usuario") }}</h3>

                <p>¡Qué alegría tenerte en HiddenGem!</p>

                <p>Aquí podrás descubrir y compartir tus creaciones.</p>

                <div style="margin-top: 35px;">
                    <a href="{{ url_for('logout') }}" class="boton">
                        Cerrar sesión
                    </a>
                </div>

            </div>

        </div>
    </div>
</section>

</main>
<!-- 🖼️ VENTANA PARA AMPLIAR LAS IMÁGENES -->
<div id="visor-imagen" role="dialog" aria-modal="true"
     aria-label="Imagen ampliada">
    <button type="button" id="cerrar-visor"
            aria-label="Cerrar imagen">×</button>

    <img id="imagen-ampliada" src="" alt="Imagen ampliada">

    <button type="button" id="alejar-visor"
            aria-label="Alejar">−</button>
    <button type="button" id="acercar-visor"
            aria-label="Acercar">+</button>
</div>
<footer>
    <div class="contenedor">
        <strong>◇ HiddenGem</strong> · Your talent deserves to be discovered.
        <br>Un espacio para descubrir, valorar y compartir creatividad.
    </div>

</footer>
{% endif %}
{% if session.get("usuario_id") %}
<script>

// ==========================================================
// NAVEGACIÓN ENTRE PANTALLAS
// ==========================================================

const nombresPantallas = ["inicio", "nosotros", "explorar", "publicar", "favoritos", "perfil"];

function irA(nombre, actualizarDireccion = true) {
    if (!nombresPantallas.includes(nombre)) nombre = "inicio";

    document.querySelectorAll(".pantalla").forEach(pantalla => {
        pantalla.classList.toggle("activa", pantalla.id === "pantalla-" + nombre);
    });

    document.querySelectorAll(".nav-link").forEach(boton => {
        boton.classList.toggle("activo", boton.dataset.ir === nombre);
    });

    if (actualizarDireccion) {
        history.replaceState(null, "", "#" + nombre);
    }

    if (nombre === "favoritos") renderFavoritos();

    window.scrollTo({ top: 0, behavior: "smooth" });
}

document.addEventListener("click", evento => {
    const boton = evento.target.closest("[data-ir]");
    if (!boton) return;

    evento.preventDefault();
    irA(boton.dataset.ir);
});

function leerPantallaInicial() {
    const nombre = location.hash.replace("#", "");
    irA(nombresPantallas.includes(nombre) ? nombre : "inicio", false);
}

window.addEventListener("hashchange", leerPantallaInicial);

// ==========================================================
// BUSCADOR Y FILTRO DEL CATÁLOGO
// ==========================================================
const busqueda = document.getElementById("busqueda");
const filtro = document.getElementById("filtro");
const listaObras = document.getElementById("lista-obras");
const mensajeSinCoincidencias = document.getElementById("sin-coincidencias");

function filtrarObras() {
    const texto = busqueda.value.trim().toLowerCase();
    const categoria = filtro.value;
    let visibles = 0;

    listaObras.querySelectorAll(".tarjeta-obra").forEach(tarjeta => {
        const contenido = tarjeta.dataset.busqueda || "";
        const categoriaObra = tarjeta.dataset.categoria || "";
        const mostrar = contenido.includes(texto) &&
            (!categoria || categoriaObra === categoria);

        tarjeta.hidden = !mostrar;
        if (mostrar) visibles++;
    });

    if (mensajeSinCoincidencias) {
        mensajeSinCoincidencias.hidden =
            listaObras.querySelectorAll(".tarjeta-obra").length === 0 ||
            visibles > 0;
    }
}

busqueda.addEventListener("input", filtrarObras);
filtro.addEventListener("change", filtrarObras);

// ==========================================================
// FAVORITOS EN EL NAVEGADOR
// ==========================================================
let favoritos = [];

try {
    favoritos = JSON.parse(localStorage.getItem("hiddengem_favoritos") || "[]");
    if (!Array.isArray(favoritos)) favoritos = [];
} catch (error) {
    favoritos = [];
}

function guardarFavoritos() {
    try {
        localStorage.setItem("hiddengem_favoritos", JSON.stringify(favoritos));
    } catch (error) {
        // La aplicación sigue funcionando aunque el navegador no permita guardar.
    }
}

function actualizarBotonesFavoritos() {
    document.querySelectorAll("[data-favorito]").forEach(boton => {
        const guardado = favoritos.includes(String(boton.dataset.favorito));
        boton.classList.toggle("activo", guardado);
        boton.textContent = guardado ? "♥ Guardado" : "♡ Guardar";
        boton.setAttribute("aria-pressed", String(guardado));
    });
}

function renderFavoritos() {
    const contenedor = document.getElementById("lista-favoritos");
    const aviso = document.getElementById("favoritos-vacios");
    contenedor.innerHTML = "";

    const tarjetas = [...document.querySelectorAll("#lista-obras .tarjeta-obra")];
    let cantidad = 0;

    tarjetas.forEach(tarjeta => {
        if (favoritos.includes(String(tarjeta.dataset.idObra))) {
            const copia = tarjeta.cloneNode(true);
            copia.hidden = false;
            contenedor.appendChild(copia);
            cantidad++;
        }
    });

    aviso.hidden = cantidad > 0;
    actualizarBotonesFavoritos();
}

   document.addEventListener("click", evento => {
    const boton = evento.target.closest("[data-favorito]");
    if (!boton) return;

    const id = String(boton.dataset.favorito);

    if (favoritos.includes(id)) {
        favoritos = favoritos.filter(item => item !== id);
    } else {
        favoritos.push(id);
    }

    guardarFavoritos();
    actualizarBotonesFavoritos();

    const pantallaFavoritos = document.getElementById("pantalla-favoritos");

    if (pantallaFavoritos && pantallaFavoritos.classList.contains("activa")) {
        renderFavoritos();
    }
});

actualizarBotonesFavoritos();
leerPantallaInicial();


/* 🌗 CAMBIAR Y RECORDAR EL TEMA */

const botonTema = document.getElementById("boton-tema");

function aplicarTema(oscuro) {
    document.body.classList.toggle("tema-oscuro", oscuro);

    botonTema.textContent = oscuro ? "☀️ Tema claro" : "🌙 Tema oscuro";
    botonTema.setAttribute(
        "aria-label",
        oscuro ? "Cambiar a tema claro" : "Cambiar a tema oscuro"
    );

    try {
        localStorage.setItem("hiddengem_tema", oscuro ? "oscuro" : "claro");
    } catch (error) {
        // La página sigue funcionando si el navegador no permite guardar.
    }
}

let temaGuardado = "claro";

try {
    temaGuardado = localStorage.getItem("hiddengem_tema") || "claro";
} catch (error) {
    temaGuardado = "claro";
}

aplicarTema(temaGuardado === "oscuro");

botonTema.addEventListener("click", () => {
    aplicarTema(!document.body.classList.contains("tema-oscuro"));
});

// 🖼️ VISOR DE IMÁGENES Y ZOOM

const visorImagen = document.getElementById("visor-imagen");
const imagenAmpliada = document.getElementById("imagen-ampliada");
const cerrarVisor = document.getElementById("cerrar-visor");
const acercarVisor = document.getElementById("acercar-visor");
const alejarVisor = document.getElementById("alejar-visor");

let zoomImagen = 1;

function actualizarZoom() {
    imagenAmpliada.style.transform = `scale(${zoomImagen})`;
}

function abrirVisor(imagen) {
    imagenAmpliada.src = imagen.src;
    imagenAmpliada.alt = imagen.alt;
    zoomImagen = 1;
    actualizarZoom();

    visorImagen.classList.add("abierto");
    document.body.style.overflow = "hidden";
}

function cerrarVisorImagen() {
    visorImagen.classList.remove("abierto");
    imagenAmpliada.src = "";
    document.body.style.overflow = "";
}

document.addEventListener("click", evento => {
    const imagen = evento.target.closest(".imagen-obra");

    if (imagen) {
        abrirVisor(imagen);
    }
});

cerrarVisor.addEventListener("click", cerrarVisorImagen);

acercarVisor.addEventListener("click", () => {
    zoomImagen = Math.min(zoomImagen + 0.25, 3);
    actualizarZoom();
});

alejarVisor.addEventListener("click", () => {
    zoomImagen = Math.max(zoomImagen - 0.25, 0.5);
    actualizarZoom();
});

visorImagen.addEventListener("click", evento => {
    if (evento.target === visorImagen) {
        cerrarVisorImagen();
    }
});

document.addEventListener("keydown", evento => {
    if (evento.key === "Escape" &&
        visorImagen.classList.contains("abierto")) {
        cerrarVisorImagen();
    }
});

</script>
{% endif %}
</body>
</html>
"""

# ==========================================================
# RUTAS DE FLASK
# ==========================================================
# ==========================================================
# REGISTRO E INICIO DE SESIÓN
# ==========================================================

@app.route("/registro", methods=["POST"])

@app.route("/registro", methods=["POST"])
def registro():
    nombre = request.form.get("nombre", "").strip()
    usuario = request.form.get("usuario", "").strip()
    correo = request.form.get("correo", "").strip().lower()
    contrasena = request.form.get("contrasena", "")

    if not all([nombre, usuario, correo, contrasena]):
        return "Completa todos los campos.", 400

    if len(contrasena) < 8:
        return "La contraseña debe tener al menos 8 caracteres.", 400

    contrasena_segura = generate_password_hash(contrasena)

    try:
        with conectar_db() as db:
            cursor = db.execute("""
                INSERT INTO usuarios
                (nombre, usuario, correo, contrasena, fecha)
                VALUES (?, ?, ?, ?, ?)
            """, (
                nombre,
                usuario,
                correo,
                contrasena_segura,
                datetime.now().strftime("%Y-%m-%d %H:%M")
            ))

            nuevo_id = cursor.lastrowid

        session["usuario_id"] = nuevo_id
        session["nombre_usuario"] = usuario

        flash("¡Tu cuenta fue creada! Bienvenido/a a HiddenGem 💎")
        return redirect(url_for("inicio"))

    except sqlite3.IntegrityError:
        return "Ese nombre de usuario o correo ya está registrado.", 400


@app.route("/login", methods=["POST"])
def login():
    identificador = request.form.get("identificador", "").strip()
    contrasena = request.form.get("contrasena", "")

    with conectar_db() as db:
        usuario = db.execute("""
            SELECT * FROM usuarios
            WHERE correo = ? OR usuario = ?
        """, (
            identificador.lower(),
            identificador
        )).fetchone()

    if usuario and check_password_hash(usuario["contrasena"], contrasena):
        session["usuario_id"] = usuario["id"]
        session["nombre_usuario"] = usuario["usuario"]

        flash("¡Bienvenido/a a HiddenGem!")
        return redirect(url_for("inicio"))

    return "Usuario, correo o contraseña incorrectos.", 401


@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.")
    return redirect(url_for("inicio"))
@app.route("/")
def inicio():
    with conectar_db() as db:
        obras = db.execute(
            "SELECT * FROM creaciones ORDER BY id DESC"
        ).fetchall()

    return render_template_string(PAGINA, obras=obras)


@app.route("/publicar", methods=["POST"])
def publicar():
    titulo = request.form.get("titulo", "").strip()
    creador = request.form.get("creador", "").strip()
    categoria = request.form.get("categoria", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    correo = request.form.get("correo", "").strip()
    precio_texto = request.form.get("precio", "").strip()
    archivo = request.files.get("imagen")

    categorias_validas = {
        "Arte y dibujo", "Pintura", "Arte digital", "Fotografía",
        "Accesorios", "Manualidades", "Otros"
    }

    if not all([titulo, creador, categoria, descripcion, correo, precio_texto]):
        return "Faltan campos obligatorios. Regresa y completa el formulario.", 400

    if categoria not in categorias_validas:
        return "La categoría seleccionada no es válida.", 400

    if not archivo or not archivo.filename:
        return "Debes seleccionar una imagen.", 400

    extension = archivo.filename.rsplit(".", 1)[-1].lower() if "." in archivo.filename else ""
    if extension not in EXTENSIONES_PERMITIDAS:
        return "Formato de imagen no permitido.", 400

    try:
        precio = float(precio_texto)
        if precio < 0 or precio > 1000000:
            raise ValueError
    except ValueError:
        return "Introduce un precio válido.", 400

    nombre_seguro = secure_filename(archivo.filename)
    nombre_final = f"{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{nombre_seguro}"
    ruta_imagen = os.path.join(UPLOAD_DIR, nombre_final)
    archivo.save(ruta_imagen)

    try:
        with conectar_db() as db:
            db.execute("""
                INSERT INTO creaciones
                (titulo, creador, categoria, precio, descripcion,
                 correo, imagen, fecha)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                titulo, creador, categoria, precio, descripcion,
                correo, nombre_final, datetime.now().strftime("%Y-%m-%d %H:%M")
            ))
    except Exception:
        if os.path.exists(ruta_imagen):
            os.remove(ruta_imagen)
        raise

    return redirect(url_for("inicio") + "#explorar")


@app.route("/uploads/<path:nombre>")
def imagen_subida(nombre):
    return send_from_directory(UPLOAD_DIR, nombre)

# INICIAR APLICACION EN RENDER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
