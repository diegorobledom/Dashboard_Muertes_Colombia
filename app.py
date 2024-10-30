import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import geojson  # Importar el archivo geojson.py que maneja la descarga y carga

# Cargar datos desde el archivo Excel
file_path = 'Anexo4.Covid-19_CE_15-03-23.xlsx'
data = pd.read_excel(file_path)

# Reemplazar caracteres con tildes en la columna 'DEPARTAMENTO'
data['DEPARTAMENTO'] = data['DEPARTAMENTO'].str.replace('Á', 'A') \
                                             .str.replace('É', 'E') \
                                             .str.replace('Í', 'I') \
                                             .str.replace('Ó', 'O') \
                                             .str.replace('Ú', 'U')

# Remover el símbolo ' del primer carácter en la columna 'FECHA DEFUNCIÓN' si existe
data['AÑO'] = data['FECHA DEFUNCIÓN'].astype(str).str[-4:]

# Crear una nueva columna 'MES' extrayendo los caracteres 5 y 6 de la columna 'FECHA DEFUNCIÓN'
data['MES'] = data['FECHA DEFUNCIÓN'].astype(str).str[4:6]
data['MES'] = data['MES'].str.replace("/", "", regex=False)

# Crear una nueva columna 'MES_AÑO' concatenando las columnas 'MES' y 'AÑO'
data['MES_AÑO'] = data['AÑO'] + '-' + data['MES']

# Eliminar los caracteres dentro de los paréntesis y los paréntesis de la columna 'EDAD FALLECIDO'
data['EDAD FALLECIDO'] = data['EDAD FALLECIDO'].str.replace(r"\(.*\)", "", regex=True).str.strip()

# Filtrar los datos para el año 2020 y solo la categoría "CONFIRMADO" en la columna COVID-19
data_2020_confirmed = data[(data['AÑO'] == "2020") & (data['COVID-19'] == 'CONFIRMADO')]
data_2020_confirmed['EDAD FALLECIDO'] = pd.to_numeric(data_2020_confirmed['EDAD FALLECIDO'], errors='coerce')

# Crear los rangos quinquenales para el histograma
bins = list(range(0, 91, 5)) + [float('inf')]
labels = [f"{i}-{i+4}" for i in range(0, 90, 5)] + ["90 o más"]
data_2020_confirmed['RANGO EDAD'] = pd.cut(data_2020_confirmed['EDAD FALLECIDO'], bins=bins, labels=labels, right=False)

# Crear los gráficos
fig_hist = px.histogram(data_2020_confirmed, x='RANGO EDAD', title="Frecuencia de Muertes Confirmadas por COVID-19 por Edades Quinquenales (2020)", labels={'RANGO EDAD': 'Rango de Edad', 'count': 'Frecuencia de Muertes'}, category_orders={'RANGO EDAD': labels})

data_2020_2021_confirmed = data[(data['COVID-19'] == 'CONFIRMADO')]
deaths_by_month = data_2020_2021_confirmed.groupby('MES_AÑO').size().reset_index(name='TOTAL_MUERTES')
fig_line = px.line(deaths_by_month, x='MES_AÑO', y='TOTAL_MUERTES', title="Total de Muertes Confirmadas por Mes (2020 y 2021)", labels={'MES_AÑO': 'Mes y Año', 'TOTAL_MUERTES': 'Total Muertes'}, markers=True)

data_2021_confirmed = data[(data['AÑO'] == "2021") & (data['COVID-19'] == 'CONFIRMADO')]
deaths_by_department_2021 = data_2021_confirmed.groupby('DEPARTAMENTO').size().reset_index(name='TOTAL_MUERTES')
colombia_geojson = geojson.load_geojson(geojson.geojson_path)

fig_map = px.choropleth(deaths_by_department_2021, geojson=colombia_geojson, locations='DEPARTAMENTO', featureidkey="properties.NOMBRE_DPT", color='TOTAL_MUERTES', hover_name='DEPARTAMENTO', title="Total Muertes Confirmadas por COVID-19 en 2021")
fig_map.update_geos(fitbounds="locations", visible=False)

deaths_by_city_2021 = data_2021_confirmed.groupby('MUNICIPIO').size().reset_index(name='TOTAL_MUERTES')
top_5_cities = deaths_by_city_2021.sort_values(by='TOTAL_MUERTES', ascending=False).head(5)
fig_bars = px.bar(top_5_cities, x='TOTAL_MUERTES', y='MUNICIPIO', orientation='h', title="Top 5 ciudades con más muertes confirmadas por COVID-19 en 2021", labels={'TOTAL_MUERTES': 'Total Muertes', 'MUNICIPIO': 'Municipio'})

cases_by_status_2021 = data[data['AÑO'] == '2021'].groupby('COVID-19').size().reset_index(name='TOTAL_CASOS')
fig_pie = px.pie(cases_by_status_2021, names='COVID-19', values='TOTAL_CASOS', title='Distribución de Casos de COVID-19 en 2021 (Confirmados, Sospechosos, Descartados)', labels={'COVID-19': 'Estado del Caso'})

# Configurar el layout de la app Dash
app = dash.Dash(__name__, title="Dashboard COVID-19")
app.layout = html.Div([
    html.H1("Actividad 4 - Aplicaciones I", style={'text-align': 'center'}),
    html.H4("Realizado por:", style={'text-align': 'center'}),
    html.P("Alexander Almeida Espinosa", style={'text-align': 'center'}),
    html.P("Juan Carlos González Torres", style={'text-align': 'center'}),
    html.P("Diego Alejandro Robledo Mejía", style={'text-align': 'center'}),

    # Mapa de muertes confirmadas
    html.Div([dcc.Graph(figure=fig_map)], style={'margin-bottom': '30px'}),
    html.Hr(style={'border': '1px solid #ccc'}),  # Línea divisoria

    # Gráficos en la misma línea
    html.Div([
        html.Div(dcc.Graph(figure=fig_bars), style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
        html.Div(dcc.Graph(figure=fig_pie), style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '30px'}),
    html.Hr(style={'border': '1px solid #ccc'}),  # Línea divisoria

    # Gráficos de línea y de histograma en la misma línea
    html.Div([
        html.Div(dcc.Graph(figure=fig_line), style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
        html.Div(dcc.Graph(figure=fig_hist), style={'width': '48%', 'display': 'inline-block', 'padding': '0 10px'}),
    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '30px'}),
    html.Hr(style={'border': '1px solid #ccc'}),  # Línea divisoria al final
])

# Ejecutar el servidor
if __name__ == '__main__':
    app.run_server(debug=True)