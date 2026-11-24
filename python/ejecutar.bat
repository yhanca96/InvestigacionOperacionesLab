@echo off
REM Instala dependencias (solo la primera vez) y abre el aplicativo en el navegador
python -m pip install -r requirements.txt
python -m streamlit run app.py
pause
