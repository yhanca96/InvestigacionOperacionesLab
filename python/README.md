# Aplicativo final de optimización — Investigación de Operaciones (ITM)

Aplicativo semiautomatizado con tres módulos (una pestaña por técnica):

| Pestaña | Técnica | Qué calcula |
|---|---|---|
| 1 | Método gráfico (programación lineal, 2 variables) | Región factible, vértices, óptimo, holguras, escenario what-if de recursos |
| 2 | Teoría de colas M/M/s | ρ, P₀, L, Lq, W, Wq, P(esperar), costo total vs. número de servidores, s óptimo |
| 3 | Cadenas de Markov | π(n) a n pasos, estado estable, ergodicidad, tiempos de retorno y primera pasada, what-if |

El ejemplo precargado (cafetería universitaria) es ilustrativo. **Todos los datos se editan en pantalla; no hay que tocar el código.**

## Ejecutar

Requiere Python 3.10 o superior.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en `http://localhost:8501`. Atajos: `ejecutar.bat` (Windows) o `./ejecutar.sh` (Linux/macOS).

## Publicar como enlace web (Streamlit Community Cloud)

1. Subir esta carpeta a un repositorio de GitHub (con `app.py` y `requirements.txt` en la raíz).
2. Entrar a https://share.streamlit.io con la cuenta de GitHub → *Create app*.
3. Elegir el repositorio, rama `main` y archivo principal `app.py` → *Deploy*.

## Estructura

```
app.py                  interfaz (entrada de datos, gráficos, tablas)
modulos/grafico.py      motor del método gráfico
modulos/colas.py        motor M/M/s
modulos/markov.py       motor de cadenas de Markov
pruebas/test_motores.py pruebas automáticas de los motores
requirements.txt        dependencias
```

## Verificar que todo funciona

```bash
python pruebas/test_motores.py
```

Comprueba los motores contra los valores calculados a mano de la guía de apoyo
(óptimo (20, 60) con Z = 180; M/M/3 con s óptimo = 3; estado estable 17/36, 1/3, 7/36) y los casos límite
(infactible, no acotado, óptimos alternos, sistema inestable, matriz inválida, cadena absorbente o periódica).
