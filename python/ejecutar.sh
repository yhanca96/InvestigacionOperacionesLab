#!/usr/bin/env bash
# Instala dependencias (solo la primera vez) y abre el aplicativo en el navegador
python3 -m pip install -r requirements.txt && python3 -m streamlit run app.py
