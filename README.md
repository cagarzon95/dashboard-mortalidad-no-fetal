# Dashboard de Mortalidad No Fetal en Colombia

## 1. Descripción general del proyecto
Esta aplicación web analítica fue desarrollada en Python con Dash y Plotly para explorar patrones territoriales, temporales, demográficos y causales de la mortalidad no fetal en Colombia durante 2019.

## 2. Objetivo de la aplicación
Visualizar y resumir los registros oficiales de mortalidad no fetal de 2019 para apoyar el análisis exploratorio mediante mapas, series de tiempo, barras, tabla y tarjetas KPI.

## 3. Fuente y naturaleza de los datos
- `Anexo1.NoFetal2019_CE_15-03-23.xlsx`: archivo principal de mortalidad no fetal 2019.
- `Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx`: diccionario de causas de muerte.
- `Divipola_CE_.xlsx`: división político-administrativa de Colombia.
- `Colombia.geo.json`: geojson departamental de Colombia.

La app trabaja con datos reales, no con datos sintéticos. Los archivos originales son necesarios para regenerar los datos procesados en el arranque de despliegue.

## 4. Estructura del proyecto

```text
.
├── app.py
├── requirements.txt
├── render.yaml
├── README.md
├── .gitignore
├── .python-version
├── data/
│   ├── Anexo1.NoFetal2019_CE_15-03-23.xlsx
│   ├── Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx
│   ├── Divipola_CE_.xlsx
│   ├── Colombia.geo.json
│   └── processed/
├── src/
├── scripts/
├── tests/
└── assets/
```

## 5. Principales funcionalidades del dashboard
1. Mapa coroplético por departamento.
2. Gráfico de líneas mensual.
3. Barras de cinco ciudades con mayor número de homicidios por armas de fuego, código X95.
4. Gráfico circular de diez ciudades con menor mortalidad registrada.
5. Tabla de diez principales causas de muerte.
6. Barras apiladas por sexo y departamento.
7. Barras por grupo de edad.

## 6. Tecnologías usadas
- Python 3.11
- Dash
- Plotly
- Pandas
- OpenPyXL
- Gunicorn
- Pytest

## 7. Instalación de dependencias
Crear un entorno virtual e instalar los paquetes:

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

Luego:

```bash
pip install -r requirements.txt
```

## 8. Ejecución local
Una vez instaladas las dependencias:

```bash
python scripts/prepare_data.py
python app.py
```

La aplicación debe quedar disponible en:

```text
http://127.0.0.1:8050
```

## 9. Instrucciones de prueba
Ejecutar:

```bash
pytest -q
```

Las pruebas verifican:
- importación de módulos principales;
- carga de datos;
- creación de figuras Plotly;
- exposición de `server = app.server`.

## 10. Preparación de datos
El script `scripts/prepare_data.py` procesa los Excel originales y genera archivos livianos en `data/processed/`:
- `deaths_by_department.csv`
- `deaths_by_month.csv`
- `top_violent_cities_x95.csv`
- `lowest_mortality_cities.csv`
- `top_causes.csv`
- `deaths_by_sex_department.csv`
- `deaths_by_age_group.csv`
- `kpis.json`

La app lee preferiblemente `data/processed/`. Si esos archivos faltan, la interfaz muestra un mensaje claro indicando que debe ejecutarse:

```bash
python scripts/prepare_data.py
```

## 11. Despliegue en Render
El archivo `render.yaml` está preparado para Render con:
- `buildCommand`: `pip install -r requirements.txt && python scripts/prepare_data.py`
- `startCommand`: `gunicorn app:server`

Esto permite que Render regenere los archivos procesados durante el build y arranque la app con Gunicorn.

## 12. Enlaces del proyecto
- Repositorio GitHub: [https://github.com/cagarzon95/dashboard-mortalidad-no-fetal](https://github.com/cagarzon95/dashboard-mortalidad-no-fetal)
- URL de la aplicación desplegada: pendiente de actualización

## 13. Evidencia de pruebas realizadas
Pruebas ejecutadas localmente:
- `python scripts/prepare_data.py`
- `pytest -q`
- `python app.py`

Resultado observado:
- preparación de datos exitosa;
- `10 passed` en pytest;
- la aplicación respondió correctamente en `http://127.0.0.1:8050`.

## 14. Limitaciones conocidas
- El análisis de "menor mortalidad" se presenta como conteo absoluto de defunciones, no como tasa poblacional, porque el conjunto de datos no incluye población municipal.
- La tabla `dash_table.DataTable` muestra una advertencia de deprecación de Dash, pero funciona correctamente.

## 15. Créditos académicos 
Proyecto académico desarrollado en el curso Aplicaciones I, de la Maestría en Inteligencia Artificial de la Universidad de la Salle, https://lasalle.edu.co/, Actividad 4: Aplicación web interactiva para el análisis de mortalidad en Colombia

## 16. Autoría
- Esta actividad fue desarrollada por Carlos Mario Garzón
