# Aplicativo final de optimización · Investigación de Operaciones

ITM · Ingeniería de Sistemas · Curso 190304002

Aplicativo para tres técnicas, con un solo contexto (cafetería universitaria):

1. Método gráfico de programación lineal (2 variables)
2. Teoría de colas (M/M/s, con costo total y número óptimo de cajeros)
3. Cadenas de Markov (proyección, estado estable, clasificación, primera pasada)

## Enlaces

- **Aplicativo web (sin instalar nada):** https://yhanca96.github.io/InvestigacionOperacionesLab/
- **Guía de apoyo (PDF):** [Guia_Apoyo_Aplicativo_IO.pdf](Guia_Apoyo_Aplicativo_IO.pdf)

## Estructura

| Carpeta | Contenido |
|---|---|
| `docs/` | Versión web (HTML + JavaScript, se publica con GitHub Pages) |
| `python/` | Versión Python (Streamlit), motores en `python/modulos/` y pruebas en `python/pruebas/` |

## Ejecutar la versión Python

```bash
cd python
pip install -r requirements.txt
streamlit run app.py
```

Pruebas de los motores: `python pruebas/test_motores.py`

Los datos precargados son un ejemplo ilustrativo; todos se pueden modificar desde la interfaz sin tocar el código.
