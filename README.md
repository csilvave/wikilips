# 💄 WikiLips

**WikiLips** es una aplicación web que ayuda a encontrar el *dupe* perfecto de cualquier labial. A partir de una marca, producto y tono seleccionado, el algoritmo compara colores en el espacio HSV y muestra las 3 alternativas más similares disponibles en la base de datos.

🌐 **[wikilips.cl](https://wikilips.cl)**

---

## ✨ Características

- 🔍 **Buscador de dupes** — selecciona marca, producto y tono y obtén las 3 alternativas más similares por color
- 🎨 **Comparación visual** — preview del color en tiempo real y comparación lado a lado entre tu tono y las alternativas
- 🏷️ **Filtros** — filtra las recomendaciones por acabado (Matte, Brillante, Hidratante, Satinado, Natural) y formato (Barra, Brillo Labial, Líquido, Tinte, Bálsamo, Delineador)
- 📊 **Base de datos amplia** — más de 1.300 tonos de más de 40 marcas
- 🔧 **Panel de administración** — interfaz para agregar y gestionar marcas, productos y tonos
- 📱 **Responsive** — funciona en móvil, tablet y desktop

---

## 🛠️ Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python + Flask |
| Base de datos | SQLite |
| Algoritmo de color | Distancia HSV con NumPy |
| Frontend | HTML + CSS + JavaScript vanilla |
| Tipografías | Cormorant Garamond + Jost (Google Fonts) |
| Servidor | Gunicorn |
| Hosting | Render |

---

## 🚀 Correr el proyecto localmente

### Requisitos
- Python 3.9+
- pip

### Instalación

```bash
# Clonar el repositorio
git clone https://github.com/csilvave/wikilips.git
cd wikilips/proyecto_wikilips

# Instalar dependencias
pip install -r requirements.txt

# Correr la aplicación
python app.py
```

La app estará disponible en `http://localhost:5000`

---

## 📁 Estructura del proyecto

```
proyecto_wikilips/
├── app.py                  # Aplicación Flask principal
├── BBDDWikilips.db         # Base de datos SQLite
├── requirements.txt        # Dependencias Python
├── Procfile                # Configuración para Render/Gunicorn
├── cargar_tonos.py         # Script de carga masiva desde CSV
├── tonos_wikilips.csv      # Plantilla CSV para agregar tonos
└── templates/
    ├── base.html           # Layout base
    ├── landing.html        # Página de inicio
    ├── index.html          # Buscador de dupes
    ├── login.html          # Acceso al panel admin
    ├── admin_home.html     # Panel de administración
    ├── agregar_marca.html  # Formulario agregar marca
    ├── agregar_producto.html # Formulario agregar producto
    └── agregar_detalle.html  # Formulario agregar tono
```

---

## 🗄️ Base de datos

La base de datos SQLite contiene las siguientes tablas:

- **Marca** — marcas de maquillaje
- **Producto** — productos por marca
- **Detalle** — tonos con su código RGB, acabado y formato
- **Acabado** — Matte, Brillante, Hidratante, Satinado, Natural
- **Formato** — Barra, Brillo Labial, Líquido, Tinte, Bálsamo, Delineador

### Carga masiva de tonos

Para agregar tonos en cantidad, usa el script `cargar_tonos.py`:

```bash
# 1. Edita tonos_wikilips.csv con los nuevos tonos
# Formato: marca, producto, tono, acabado, formato, rgb

# 2. Corre el script
python3 cargar_tonos.py
```

El script detecta automáticamente si la marca o producto ya existen y no duplica registros.

---

## 🎨 Algoritmo de matching

WikiLips convierte los colores RGB a espacio HSV y calcula la distancia euclidiana entre el tono buscado y todos los tonos de la base:

```
distancia = √( (ΔH/255)² + (ΔS/255)² + (ΔV/255)² )
```

El componente de tono (H) considera la naturaleza circular del espectro de color, tomando el mínimo entre la diferencia directa y la diferencia circular.

---

## 🔐 Variables de entorno

Para producción, configura estas variables en Render:

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta para sesiones Flask |
| `ADMIN_USER` | Usuario del panel de administración |
| `ADMIN_PASS` | Contraseña del panel de administración |

---

## 📬 Contacto

Desarrollado por **Camila Silva** — [wikilips.cl](https://wikilips.cl)

---

*© 2025 WikiLips — Todos los derechos reservados*
