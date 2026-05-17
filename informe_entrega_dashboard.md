# Informe de entrega: Dashboard de Mortalidad No Fetal en Colombia, 2019

## 1. Portada o información general
- Nombre del estudiante: Carlos Mario Garzón Ospina.
- Nombre de la aplicación: Dashboard de Mortalidad No Fetal en Colombia.
- Repositorio GitHub: https://github.com/cagarzon95/dashboard-mortalidad-no-fetal
- URL de la aplicación desplegada en Render: https://dashboard-mortalidad-no-fetal.onrender.com
- Fecha de elaboración: 16 de mayo de 2026.

## 2. Introducción
La presente actividad consistió en el desarrollo de una aplicación web interactiva para analizar la mortalidad no fetal en Colombia durante 2019. El ejercicio articuló limpieza de datos, agregación estadística, diseño de visualizaciones y despliegue en la nube mediante una plataforma PaaS. La solución se implementó con Python, Dash y Plotly, tecnologías adecuadas para construir tableros analíticos reproducibles, interactivos y orientados a la exploración de patrones territoriales, temporales, causales y demográficos.

El valor académico de este tipo de desarrollo no se limita a la presentación gráfica. La visualización interactiva permite contrastar territorios, comparar meses, identificar concentraciones de causas de muerte y explorar diferencias por sexo y grupo de edad. En ese sentido, el dashboard no reemplaza el análisis estadístico formal, pero sí facilita una lectura exploratoria robusta y verificable de los datos oficiales.

## 3. Objetivo general
Desarrollar y documentar un dashboard en Python/Dash que permita explorar la mortalidad no fetal en Colombia durante 2019 a partir de visualizaciones interactivas, tarjetas resumen y tabla analítica, con despliegue funcional en Render y repositorio GitHub reproducible.

## 4. Datos utilizados
La solución usa archivos reales ubicados en `data/` y generados o procesados por scripts reproducibles:

- `Anexo1.NoFetal2019_CE_15-03-23.xlsx`: base principal de registros de mortalidad no fetal.
- `Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx`: diccionario de causas de muerte, necesario para traducir `COD_MUERTE` a descripciones textuales.
- `Divipola_CE_.xlsx`: tabla de división político-administrativa de Colombia; aporta códigos y nombres de departamento y municipio.
- `Colombia.geo.json`: geojson departamental; se usa para el mapa coroplético.
- `data/processed/*.csv` y `data/processed/kpis.json`: agregaciones livianas producidas por `scripts/prepare_data.py`.

La app lee preferiblemente los archivos procesados, pero la preparación depende de los archivos originales. Por eso, para reproducir el proyecto de principio a fin, deben conservarse tanto los Excel base como los archivos generados en `data/processed/`.

### Advertencia metodológica
El proyecto trabaja con conteos absolutos de defunciones. No es posible calcular tasas o índices poblacionales reales por municipio porque la base entregada no incluye población municipal. Por tanto, expresiones como "menor mortalidad" deben interpretarse como menor número absoluto de defunciones registradas.

## 5. Metodología de desarrollo
El desarrollo siguió una estructura modular orientada a reproducibilidad:

1. Carga robusta de datos con `dtype=str` para conservar ceros iniciales y evitar pérdida de precisión en códigos.
2. Normalización explícita de `COD_DEPARTAMENTO`, `COD_DANE`, `COD_MUNICIPIO`, `COD_MUERTE`, `MES` y `SEXO`.
3. Construcción de tablas agregadas para departamento, mes, ciudades X95, causas principales, sexo por departamento y grupos de edad.
4. Cruces por código, no por nombre, para evitar ambigüedades entre fuentes.
5. Uso de Plotly para generar gráficos interactivos con hover claro, leyendas y etiquetas legibles.
6. Organización modular con:
   - `app.py` para inicializar la app Dash;
   - `src/` para carga, procesamiento, figuras y layout;
   - `scripts/prepare_data.py` para generar los archivos livianos;
   - `tests/` para verificación técnica.

### Flujo de datos
La aplicación en ejecución no recalcula el Excel completo en cada carga. En cambio:
- `scripts/prepare_data.py` lee los archivos originales.
- procesa y escribe CSV/JSON en `data/processed/`.
- `app.py` y `src/data_loader.py` consumen esos archivos procesados.

## 6. Arquitectura del proyecto
La arquitectura está pensada para mantener separación de responsabilidades:

- `app.py`: inicializa Dash, expone `server = app.server` y permite ejecución local.
- `src/config.py`: define rutas y parámetros compartidos.
- `src/data_loader.py`: carga Excel, GeoJSON y archivos procesados; valida existencia de datos.
- `src/processing.py`: contiene funciones puras de agregación y normalización.
- `src/figures.py`: construye las figuras Plotly.
- `src/layout.py`: arma la interfaz Dash con títulos, KPI cards, gráficos y tabla.
- `scripts/prepare_data.py`: ejecuta el preprocesamiento una sola vez.
- `tests/`: verifica contratos de datos, figuras y carga de la app.
- `assets/style.css`: contiene la hoja de estilos para la interfaz.
- `requirements.txt`: declara las dependencias.
- `render.yaml`: define build y start command para Render.
- `README.md`: resume instalación, ejecución, despliegue y visualizaciones.

Esta organización permite que la app sea más estable en Render, porque la lógica de visualización depende de agregados ya calculados y no de operaciones pesadas en cada arranque.

## 7. Despliegue en Render
La aplicación fue desplegada en Render como servicio web de Python con la siguiente configuración:

- Rama de despliegue: `main`
- Build command:
  - `pip install -r requirements.txt && python scripts/prepare_data.py`
- Start command:
  - `gunicorn app:server`
- URL pública:
  - https://dashboard-mortalidad-no-fetal.onrender.com

La variable `server = app.server` es la clave para que Gunicorn encuentre el objeto WSGI correcto. En otras palabras, `app.py` expone una aplicación Flask subyacente compatible con Render.

### Evidencia visual de funcionamiento
Se generó un PDF con captura del dashboard desplegado en Render como evidencia visual del funcionamiento. Ese archivo puede insertarse como anexo o evidenciarse como salida visual de la aplicación ya publicada.

## 8. Pruebas de funcionamiento
Se ejecutaron pruebas locales y validaciones técnicas sobre el proyecto:

- `python scripts/prepare_data.py`
- `pytest -q`
- `python -c "import app; print(type(app.server))"`

Resultado:
- la preparación de datos fue exitosa;
- `pytest` reportó `10 passed`;
- la importación de `app` fue correcta;
- `type(app.server)` devolvió `<class 'flask.app.Flask'>`, confirmando la exposición del servidor WSGI;
- la aplicación respondió localmente en `http://127.0.0.1:8050`.

## 9. Resultados e interpretación de visualizaciones

### 9.1 Indicadores generales o tarjetas resumen
Los KPI resumen los valores principales del conjunto:

- Total de defunciones registradas: **244.355**
- Departamento con más defunciones: **BOGOTÁ, D.C.** con **38.760**
- Mes con más defunciones: **Diciembre** con **21.678**
- Principal causa de muerte: **I219 - Infarto agudo del miocardio, sin otra especificacion** con **35.088**
- Ciudad con más homicidios X95: **Santiago de Cali** con **971**

Interpretación:
La carga general de mortalidad se concentra en territorios altamente poblados y en causas crónicas dominantes. El resultado sobre la principal causa evidencia que, para este año y esta base, las enfermedades cardiovasculares tienen una presencia muy alta frente a otras causas.

### 9.2 Mapa coroplético por departamento
Archivo y función:
- `src/figures.py:33` -> `make_department_map`
- `src/layout.py:132` -> inserción del gráfico en el layout
- Cruce territorial por código departamental usando `COD_DEPARTAMENTO` y `properties.DPTO` del GeoJSON.

Variables usadas:
- `COD_DEPARTAMENTO`
- `NOMBRE_DEPARTAMENTO`
- `TOTAL`
- `geojson_colombia`

Resultado principal:
- Bogotá, D.C. lidera con 38.760 muertes.
- Le siguen Antioquia (34.473), Valle del Cauca (28.443), Atlántico (14.804) y Santander (11.894).

Interpretación:
La distribución departamental sugiere concentración de defunciones en territorios con mayor población y mayor densidad urbana. El mapa permite apreciar visualmente esa concentración espacial sin depender de etiquetas textuales ambiguas, porque el cruce se realiza por código y no por nombre.

### 9.3 Serie mensual de defunciones
Archivo y función:
- `src/figures.py:57` -> `make_monthly_line`
- `src/layout.py:140` -> inserción del gráfico

Variables usadas:
- `MES`
- `MES_NOMBRE`
- `TOTAL`

Resultado principal:
- Mes con mayor número de defunciones: **Diciembre (21.678)**
- Mes con menor número de defunciones: **Febrero (17.974)**

Interpretación:
La serie mensual presenta variación durante el año, con un cierre más alto en diciembre y un mínimo en febrero. El gráfico sirve para identificar estacionalidad o cambios coyunturales, aunque no debe interpretarse como tendencia epidemiológica causal sin análisis complementario.

### 9.4 Cinco ciudades con más homicidios X95
Archivo y función:
- `src/figures.py:78` -> `make_violent_cities_bar`
- `src/layout.py:148` -> inserción del gráfico

Variables usadas:
- `COD_MUERTE` con filtro `startswith("X95")`
- `COD_DANE`
- `NOMBRE_MUNICIPIO`
- `NOMBRE_DEPARTAMENTO`
- `TOTAL`

Resultado principal:
| Ciudad | Departamento | Código DANE | Total |
|---|---|---:|---:|
| Santiago de Cali | Valle del Cauca | 76001 | 971 |
| Bogotá, D.C. | Bogotá, D.C. | 11001 | 601 |
| Medellín | Antioquia | 05001 | 428 |
| Barranquilla | Atlántico | 08001 | 260 |
| San José de Cúcuta | Norte de Santander | 54001 | 206 |

Interpretación:
La concentración de homicidios X95 en grandes ciudades refuerza la necesidad de leer el indicador en clave urbana, territorial y social. El filtro por prefijo `X95` es correcto porque captura subcódigos y no se limita a la cadena exacta `X95`.

### 9.5 Diez ciudades con menor mortalidad registrada
Archivo y función:
- `src/figures.py:102` -> `make_lowest_mortality_pie`
- `src/layout.py:158` -> inserción del gráfico

Variables usadas:
- `COD_DANE`
- `NOMBRE_MUNICIPIO`
- `NOMBRE_DEPARTAMENTO`
- `TOTAL`

Resultado principal:
| Ciudad | Departamento | Total |
|---|---|---:|
| Alto Baudó | Chocó | 1 |
| Bituima | Cundinamarca | 1 |
| El Calvario | Meta | 1 |
| El Encanto | Amazonas | 1 |
| Hato | Santander | 1 |
| La Tola | Nariño | 1 |
| Mapiripana | Guainía | 1 |
| Margarita | Bolívar | 1 |
| Nuquí | Chocó | 1 |
| Puerto Alegría | Amazonas | 1 |

Interpretación:
El gráfico no representa una tasa poblacional. En términos estrictamente descriptivos, identifica municipios con el menor conteo absoluto de defunciones registradas. La lectura debe ser prudente porque los municipios pequeños pueden tener pocos casos sin que ello signifique menor riesgo relativo.

### 9.6 Diez principales causas de muerte
Archivo y función:
- `src/figures.py:117` -> `make_top_causes_table_data`
- `src/layout.py:178` -> `dash_table.DataTable`

Variables usadas:
- `COD_MUERTE`
- `CAUSA_DE_MUERTE`
- `TOTAL`

Resultado principal:
| Código | Causa de muerte | Total de casos |
|---|---|---:|
| I219 | Infarto agudo del miocardio, sin otra especificacion | 35.088 |
| J449 | Enfermedad pulmonar obstructiva cronica, no especificada | 7.210 |
| J440 | Enfermedad pulmonar obstructiva cronica con infeccion aguda de las vias respiratorias inferiores | 6.445 |
| J189 | Neumonia, no especificada | 5.798 |
| C169 | Tumor maligno del estomago, parte no especificada | 5.125 |
| C349 | Tumor maligno de los bronquios o del pulmon, parte no especificada | 4.438 |
| X954 | Agresion con disparo de otras armas de fuego, y las no especificadas, calles y carreteras | 4.396 |
| C509 | Tumor maligno de la mama, parte no especificada | 3.619 |
| C61 | Tumor Maligno De La Prostata | 3.437 |
| I10 | Hipertension Esencial (Primaria) | 3.317 |

Interpretación:
La tabla evidencia predominio de causas crónicas y degenerativas, especialmente cardiovasculares y respiratorias. También aparece un código asociado a violencia (`X954`) dentro de los diez primeros lugares, lo que muestra que el análisis causal no es exclusivamente sanitario, sino también social y violento. La tabla cumple con el requisito de traducir código a descripción y ordenar de mayor a menor.

### 9.7 Muertes por sexo en cada departamento
Archivo y función:
- `src/figures.py:135` -> `make_sex_department_stacked_bar`
- `src/layout.py:207` -> inserción del gráfico

Variables usadas:
- `COD_DEPARTAMENTO`
- `NOMBRE_DEPARTAMENTO`
- `SEXO_LABEL`
- `TOTAL`

Resultado principal:
- Hombres: **134.573**
- Mujeres: **109.689**
- Indeterminado: **93**

Interpretación:
En el total nacional hay una mayor cantidad de defunciones registradas en hombres que en mujeres. La gráfica apilada por departamento permite ver que esa diferencia se repite en la mayoría de territorios. Esto puede relacionarse con perfiles diferenciales de riesgo, causas externas y patrones demográficos, pero el dashboard por sí solo no prueba causalidad.

### 9.8 Distribución por grupo de edad
Archivo y función:
- `src/figures.py:166` -> `make_age_group_bar`
- `src/layout.py:215` -> inserción del gráfico

Variables usadas:
- `GRUPO_EDAD1`
- `CATEGORIA_EDAD`
- `RANGO_EDAD`
- `TOTAL`

Resultado principal:
| Categoría | Rango | Total |
|---|---|---:|
| Mortalidad neonatal | Menor de 1 mes | 4.520 |
| Mortalidad infantil | 1 a 11 meses | 2.771 |
| Primera infancia | 1 a 4 años | 1.518 |
| Niñez | 5 a 14 años | 1.993 |
| Adolescencia | 15 a 19 años | 3.795 |
| Juventud | 20 a 29 años | 11.840 |
| Adultez temprana | 30 a 44 años | 17.276 |
| Adultez intermedia | 45 a 59 años | 29.105 |
| Vejez | 60 a 84 años | 115.453 |
| Longevidad / Centenarios | 85 a 100+ años | 56.061 |
| Edad desconocida | Sin información | 23 |

Interpretación:
La mayor carga de mortalidad se concentra en la vejez y en la longevidad, lo que es coherente con el comportamiento esperado de la mortalidad en poblaciones envejecidas. La utilidad del gráfico es ordenar el ciclo de vida de forma pedagógica y permitir comparar rápidamente etapas críticas.

## 10. Discusión
El dashboard permite identificar varios patrones generales:

- la mortalidad se concentra en departamentos grandes y altamente urbanizados;
- la serie mensual muestra variaciones dentro del año, con pico en diciembre;
- las causas principales están dominadas por enfermedades crónicas;
- los homicidios X95 se concentran en ciudades principales;
- los hombres presentan más defunciones que las mujeres;
- la mortalidad aumenta marcadamente en los grupos de mayor edad.

La interactividad aporta valor porque permite explorar el dato por territorio, hover, comparación visual y lectura inmediata sin necesidad de tablas externas. También facilita la verificación académica: cada gráfico responde a una pregunta concreta y está soportado por agregaciones reproducibles.

Sin embargo, el análisis debe interpretarse con cautela. El tablero trabaja con conteos absolutos y con un solo año, por lo que no permite inferir tasas poblacionales, riesgo relativo real ni tendencias de largo plazo. Para un análisis epidemiológico más fuerte se requerirían series multianuales y denominadores poblacionales por municipio o departamento.

## 11. Cumplimiento de la rúbrica

| Criterio de desempeño | Evidencia en la aplicación/proyecto | Cómo se cumple | Riesgo o comentario |
|---|---|---|---|
| Funcionalidad | `app.py`, `src/layout.py`, `src/figures.py`, `tests/` | La app abre en Dash, usa datos reales y genera los 7 elementos visuales exigidos. | La advertencia de `DataTable` no bloquea la ejecución. |
| Presentación visual y claridad | Títulos, etiquetas, leyendas y texto en español en `src/layout.py` y `src/figures.py` | Cada gráfico tiene título, eje o hover claro y texto interpretativo. | La codificación en algunos archivos se ve extraña en consola Windows, pero el proyecto funciona y el README está publicado. |
| Despliegue en la nube | `render.yaml` y URL pública | Render usa `buildCommand` y `startCommand` correctos, y la app está publicada. | Si se modifica la estructura de datos, hay que volver a ejecutar `prepare_data.py`. |
| Informe de entrega | Este documento y `material_para_redaccion_final.md` | Se documentan resultados, pruebas y evidencia visual. | Deben insertarse capturas reales en los anexos. |

## 12. Conclusiones
El proyecto logró convertir un conjunto de datos oficiales en una aplicación analítica usable, reproducible y desplegada en la nube. Técnicamente, se resolvió el problema de carga de datos con normalización de códigos, cruces por llave territorial y preparación previa de archivos livianos para evitar recálculo innecesario en producción.

Desde el punto de vista analítico, el dashboard muestra que la mortalidad no fetal de 2019 se concentra en territorios urbanos, en adultos mayores y en causas crónicas, con presencia adicional de homicidios por armas de fuego en ciudades de alta densidad. La interactividad de Dash y Plotly permite explorar esos patrones con más claridad que una tabla estática.

Finalmente, el trabajo deja una base sólida para una entrega académica completa: repositorio GitHub, despliegue en Render, evidencia visual en PDF, pruebas automatizadas y documentación técnica suficiente para auditar el funcionamiento.

## 13. Anexos sugeridos
- Captura de la app desplegada en Render.
- Captura del servicio en Render con el estado activo.
- Captura de la configuración de build y start command.
- Captura del repositorio GitHub.
- Captura del README.md actualizado.
- PDF con la evidencia visual del dashboard desplegado.

