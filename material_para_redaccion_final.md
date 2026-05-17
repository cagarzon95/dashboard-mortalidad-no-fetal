# Material para redacción final

## A. Resumen técnico del proyecto
El proyecto implementa un dashboard en Python con Dash y Plotly para analizar la mortalidad no fetal en Colombia durante 2019. La arquitectura separa carga, procesamiento, visualización e interfaz en módulos independientes. La app se despliega en Render y expone `server = app.server`, lo que permite el arranque con Gunicorn.

Puntos técnicos clave:
- lectura de Excel con `dtype=str` para conservar ceros iniciales;
- normalización explícita de códigos;
- cruces territoriales por código y no por nombre;
- preparación previa de datos en `data/processed/`;
- visualizaciones interactivas con hover, leyendas y textos en español;
- pruebas automatizadas con `pytest`.

## B. Resultados verificados con cifras
- Total de defunciones registradas: **244.355**
- Departamento con mayor número de defunciones: **BOGOTÁ, D.C.** con **38.760**
- Mes con mayor número de defunciones: **Diciembre** con **21.678**
- Principal causa de muerte: **I219 - Infarto agudo del miocardio, sin otra especificacion** con **35.088**
- Ciudad con más homicidios X95: **Santiago de Cali** con **971**

Top 5 ciudades X95:
1. Santiago de Cali - 971
2. Bogotá, D.C. - 601
3. Medellín - 428
4. Barranquilla - 260
5. San José de Cúcuta - 206

Distribución por sexo:
- Hombre: **134.573**
- Mujer: **109.689**
- Indeterminado: **93**

Distribución por edad:
- mayor carga en **Vejez (115.453)** y **Longevidad / Centenarios (56.061)**.

## C. Pruebas ejecutadas
Pruebas técnicas ejecutadas recientemente:
- `python scripts/prepare_data.py`
- `pytest -q`
- `python -c "import app; print(type(app.server))"`

Resultados:
- preparación de datos exitosa;
- `pytest` exitoso: **10 passed**;
- `app.server` existe y es un objeto Flask;
- la aplicación responde correctamente en `http://127.0.0.1:8050`.

## D. Estado de GitHub
- Repositorio remoto: https://github.com/cagarzon95/dashboard-mortalidad-no-fetal
- Rama principal: `main`
- Estado local y remoto: sincronizados
- Historial limpio en `main`, sin referencias a `cmgarzono`
- Autor del historial actual: `cagarzon95`

## E. Estado de Render
- URL pública: https://dashboard-mortalidad-no-fetal.onrender.com
- Build command configurado:
  - `pip install -r requirements.txt && python scripts/prepare_data.py`
- Start command configurado:
  - `gunicorn app:server`
- Estado funcional: desplegado y operativo

## F. Lista exacta de capturas que debe proporcionar el usuario
1. Página principal del dashboard desplegado en Render.
2. Mapa coroplético por departamento.
3. Serie mensual de defunciones.
4. Barras de cinco ciudades con homicidios X95.
5. Gráfico de menor mortalidad registrada.
6. Tabla de causas principales.
7. Barras apiladas por sexo y departamento.
8. Gráfico por grupo de edad.
9. Página o panel de Render donde se vea el servicio activo.
10. Captura o PDF de evidencia visual del dashboard desplegado.

## G. Problemas encontrados y correcciones realizadas
- Se detectó que no había Python en el PATH general; se resolvió con el entorno de Anaconda `mortalidad-dash`.
- Se encontró que el diccionario de causas requería detección flexible del encabezado; se corrigió en el preprocesamiento.
- Se ajustó la carga de CSV procesados para preservar códigos como texto y no perder ceros a la izquierda.
- Se corrigió la documentación para que usara únicamente el tema correcto: **mortalidad no fetal**.
- Se limpió la historia de Git para que el historial actual quedara asociado a `cagarzon95`.

## H. Recomendaciones para maximizar la nota según la rúbrica
1. Insertar capturas reales de cada visualización dentro del informe.
2. Incluir la captura del dashboard desplegado en Render y del estado activo del servicio.
3. Resaltar en la redacción que el cruce territorial se hace por código y no por nombre.
4. Explicar con cuidado que el gráfico de menor mortalidad es conteo absoluto y no tasa.
5. Señalar que la app usa datos reales y que la preparación de datos está automatizada.
6. Mencionar las pruebas técnicas como evidencia de estabilidad.
7. Evitar afirmaciones causales no demostradas por el dashboard.
8. Enfatizar que el despliegue en Render usa `main`, `buildCommand` y `gunicorn app:server`.

