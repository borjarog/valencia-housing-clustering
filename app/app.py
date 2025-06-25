import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import dash
from flask import Flask
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
import geopandas as gpd
import shapely
import json
import os

# Importar los datos
data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

valencia_sale_path = os.path.join(data_dir, "valencia_sale.csv")
valencia_barrios_path = os.path.join(data_dir, "valencia_polygons.csv")
valencia_metro_path = os.path.join(data_dir, "valencia_metro.csv")
valencia_sale_clustered_path = os.path.join(data_dir, "valencia_sale_clustered.csv")

valencia_sale = pd.read_csv(valencia_sale_path)
valencia_metro = pd.read_csv(valencia_metro_path)
valencia_barrios = pd.read_csv(valencia_barrios_path)
valencia_sale_clustered = pd.read_csv(valencia_sale_clustered_path)

# Convertir Cluster a string para el gráfico
valencia_sale_clustered["Cluster"] = valencia_sale_clustered["CLUSTER"].astype(str)

valencia_barrios["GEO_SHAPE"] = valencia_barrios["GEO_SHAPE"].apply(shapely.wkt.loads)
valencia_polygons = gpd.GeoDataFrame(
    valencia_barrios, geometry="GEO_SHAPE", crs="EPSG:4326"
)

geojson_data = valencia_polygons.geometry.to_json()
geojson_obj = json.loads(geojson_data)

for idx, feature in enumerate(geojson_obj["features"]):
    neighborhood_name = valencia_polygons.loc[idx, "NEIGHBORHOOD"]
    feature["id"] = neighborhood_name

# Inicializar la app
server = Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.FLATLY])

# Construcción de los componentes

titulo = html.H1("Análisis del Sector Inmobiliario en Valencia")

# Componentes de la segunda fila

total_inmuebles_titulo = html.H3("Inmuebles totales")
total_inmuebles = html.H4(valencia_sale.shape[0])

barrio_mas_ventas_titulo = html.H3("Barrio con más inmuebles en venta")
barrio_mas_ventas = html.H4(
    valencia_barrios.loc[valencia_barrios["REAL_ESTATE_TOTAL"].idxmax(), "NEIGHBORHOOD"]
)

barrio_mas_caro_titulo = html.H3("Barrio con los precios más caros")
barrio_mas_caro = html.H4(
    valencia_barrios.loc[valencia_barrios["PRICE_MEAN"].idxmax(), "NEIGHBORHOOD"]
)

nueva_obra_titulo = html.H3("Inmuebles de nueva obra")
nueva_obra_total = html.H4(valencia_sale[valencia_sale["BUILTTYPEID_1"] == 1].shape[0])

anyo_titulo = html.H3("Año")
anyo_valor = html.H4(str(2018))

# Componentes de la tercera fila

## Mapa con filtros

scatter_map_wfilters = px.scatter_map(
    data_frame=valencia_sale,
    lat="LATITUDE",
    lon="LONGITUDE",
    zoom=11.5,
)

scatter_map_wfilters.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),  # Eliminar márgenes
)

scatter_map_wfilters.update_traces(marker=dict(size=5, color="orange"))

# Gráficos de la cuarta fila

## Mapas - Columna 1

titulo_mapas_adicionales = html.H3("Mapas adicionales")

### Mapa de los tipos de construcción
scatter_map_buildtype = px.scatter_map(
    data_frame=valencia_sale,
    lat="LATITUDE",
    lon="LONGITUDE",
    zoom=11.5,
    color="BUILDTYPE",
    title="Distribución de los inmuebles por tipo de construcción",
)

scatter_map_buildtype.update_layout(
    margin=dict(l=0, r=0, t=40, b=0),  # Eliminar márgenes
    title_font=dict(color="white"),
    title_x=0.5,  # Centrar el título
    title_y=0.965,  # Ajustar la posición vertical del título
    legend=dict(
        title=None,  # Quitar título de la leyenda
        orientation="v",  # Configurar la leyenda verticalmente
        yanchor="top",  # Fija la leyenda en la parte superior
        y=1,  # Coloca la leyenda en el extremo superior
        xanchor="left",  # Alinea la leyenda a la izquierda
        x=0,  # Posiciona la leyenda en el lado izquierdo
    ),
)


scatter_map_buildtype.update_traces(marker=dict(size=5))

## Gráficos - Columna 2

### Inmuebles por barrios
ordered_neig_total = valencia_barrios.sort_values(
    by="REAL_ESTATE_TOTAL", ascending=True
)

top5 = ordered_neig_total.nlargest(10, "REAL_ESTATE_TOTAL").sort_values(
    by="REAL_ESTATE_TOTAL", ascending=True
)

houses_per_neighborhood = px.bar(
    top5,
    x="REAL_ESTATE_TOTAL",
    y="NEIGHBORHOOD",
    orientation="h",
    title="Número de inmuebles por barrio",
    color_discrete_sequence=["#F5A64D"],
)

houses_per_neighborhood.update_layout(
    title=dict(text="Número de inmuebles por barrio", x=0.5, xanchor="center"),
    xaxis=dict(
        title=dict(
            text="Número de inmuebles",
            font=dict(size=14),
            standoff=120,
        ),
    ),
    yaxis=dict(
        title=None,
    ),
    margin=dict(l=60, r=20, t=50, b=80),
)


## Gráficos - Columna 3

### Inmuebles según el número de habitaciones

counts_bedrooms = valencia_sale.groupby(["ROOMNUMBER"]).size().reset_index(name="count")

houses_per_roomnumber = px.bar(
    counts_bedrooms,
    x="count",
    y="ROOMNUMBER",
    orientation="h",
    title="Número de inmuebles por número de habitaciones",
    color_discrete_sequence=["#F5A64D"],  # Color amarillo
)

houses_per_roomnumber.update_layout(
    title_x=0.5,
    title_y=0.965,
    yaxis=dict(
        range=[0, 9],
        title="Número de habitaciones",
        showgrid=True,
    ),
    xaxis=dict(
        range=[0, 17000],
        title=dict(
            text="Número de inmuebles",
            font=dict(size=14),
            standoff=120,
        ),
    ),
)

## Grafico 4 -  Matriz Corr

# Crear la matriz de correlación
corr = valencia_sale.select_dtypes(np.number).corr()
price_corr = corr["PRICE"].drop("PRICE")

sorted_price_corr = price_corr.sort_values(ascending=True)
filtered_price_corr = sorted_price_corr[
    (sorted_price_corr > 0.2) | (sorted_price_corr < -0.2)
]

colors = ["green" if value > 0 else "red" for value in filtered_price_corr.values]
text_labels = [f"{value:.2f}" for value in filtered_price_corr.values]

price_corr_bar = go.Figure(
    go.Bar(
        x=filtered_price_corr.values,
        y=filtered_price_corr.index,
        orientation="h",  # Barras horizontales
        marker=dict(color=colors),
        text=text_labels,
        textposition="none",
    )
)

# Configurar diseño del gráfico
price_corr_bar.update_layout(
    title="Correlación de PRICE con las demás variables",
    xaxis=dict(
        title=dict(
            text="Correlación",
            font=dict(size=14),
            standoff=150,
        ),
    ),
    yaxis=dict(title="Variables"),
    height=600,
    width=800,
)

## Grafico 5 y 6 - Choropleth

quality_mean_neighborhood = px.choropleth_mapbox(
    valencia_polygons,
    geojson=geojson_obj,
    locations="NEIGHBORHOOD",
    color="QUALITY_MEAN",
    mapbox_style="carto-positron",
    opacity=0.6,
    zoom=11,
    center={"lat": 39.46, "lon": -0.37},
    hover_data=["NEIGHBORHOOD"],
    title="Calidad media del inmueble por Barrio",
    height=1000,
    labels={"NEIGHBORHOOD": "Barrio", "QUALITY_MEAN": "Calidad media"},
)

quality_mean_neighborhood.update_coloraxes(
    colorscale="plasma",
    colorbar=dict(
        title=dict(text="", side="right", font=dict(size=16, weight=600)),
    ),
)

mean_age_per_neighborhood = px.choropleth_mapbox(
    valencia_polygons,
    geojson=geojson_obj,
    locations="NEIGHBORHOOD",
    color="AGE_MEAN",
    mapbox_style="carto-positron",
    opacity=0.6,
    zoom=11,
    height=1000,
    center={"lat": 39.46, "lon": -0.37},
    hover_data=["NEIGHBORHOOD"],
    title="Antigüedad media de los inmuebles por barrio",
    labels={"AGE_MEAN": "Antigüedad media", "NEIGHBORHOOD": "Barrio"},
)

## Grafiocs 7 y 8 - Box Plot
avg_price_by_neighborhood = valencia_sale.groupby("NEIGHBORHOOD")["PRICE"].mean()

top_3_expensive = avg_price_by_neighborhood.nlargest(3).index
top_3_cheap = avg_price_by_neighborhood.nsmallest(3).index
selected_neighborhoods = top_3_expensive.union(top_3_cheap)

filtered_data = valencia_sale[
    valencia_sale["NEIGHBORHOOD"].isin(selected_neighborhoods)
]

sorted_neighborhoods = (
    filtered_data.groupby("NEIGHBORHOOD")["PRICE"]
    .mean()
    .sort_values(ascending=False)
    .index
)

price_boxplot = go.Figure()

for neighborhood in sorted_neighborhoods:
    neighborhood_data = filtered_data[filtered_data["NEIGHBORHOOD"] == neighborhood][
        "PRICE"
    ]
    price_boxplot.add_trace(
        go.Box(y=neighborhood_data, name=neighborhood, boxmean=True)
    )

# Configurar diseño del gráfico
price_boxplot.update_layout(
    title="Distribución de Precios por Barrio (Top 3 más caros y baratos)",
    xaxis=dict(
        title=dict(
            text="Barrios",
            font=dict(size=14),
            standoff=160,
        ),
    ),
    yaxis=dict(title="Precio de las viviendas"),
    height=600,
    width=800,
)

## Gráfico de Clustering - Distribución Geográfica de Inmuebles por Clúster
clustering_map = px.scatter_mapbox(
    valencia_sale_clustered,
    lat="LATITUDE",
    lon="LONGITUDE",
    color="Cluster",
    zoom=12,
    height=700,
    mapbox_style="carto-positron",
    title="Distribución Geográfica de Inmuebles por Clúster",
)

clustering_map.update_layout(
    margin=dict(l=10, r=10, t=40, b=10),
    title_font=dict(color="white"),
    title_x=0.5,
    title_y=0.965,
)

clustering_map.update_traces(marker=dict(size=5))

# Diseño de la disposición de la app
app.layout = dbc.Container(
    [
        html.Div(
            [
                html.Div(  # Primera fila con el título
                    [
                        html.H1(
                            "Trabajo Académico EDM",
                            style={"text-align": "center"},
                        ),
                        html.Img(
                            src="https://www.upv.es/imagenes/svg/logo-upv.svg",
                            style={"width": "250px"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "space-around",
                        "align-items": "center",
                    },
                ),
                html.Div(
                    style={
                        "borderTop": "5px dashed black",  # Línea de 2px de grosor y color
                        "marginTop": "10px",  # Espaciado arriba de la línea
                        "marginBottom": "10px",  # Espaciado debajo de la línea
                    }
                ),
                dbc.Row(  # Primera fila con el título
                    [
                        html.Div(
                            titulo,
                            style={
                                "display": "flex",
                                "justify-content": "center",
                                "align-items": "center",
                                "width": "100%",
                            },
                        )
                    ]
                ),
                dbc.Row(  # Segunda fila con datos totales y agregados
                    [
                        dbc.Col(
                            [
                                html.Div(total_inmuebles_titulo),
                                html.Div(total_inmuebles, className="value"),
                            ],
                            style={"text-align": "center", "flex": "1"},
                        ),
                        dbc.Col(
                            [
                                html.Div(barrio_mas_ventas_titulo),
                                html.Div(barrio_mas_ventas, className="value"),
                            ],
                            style={"text-align": "center", "flex": "2"},
                        ),
                        dbc.Col(
                            [
                                html.Div(barrio_mas_caro_titulo),
                                html.Div(barrio_mas_caro),
                            ],
                            style={"text-align": "center", "flex": "2"},
                        ),
                        dbc.Col(
                            [
                                html.Div(nueva_obra_titulo),
                                html.Div(nueva_obra_total),
                            ],
                            style={"text-align": "center", "flex": "1.5"},
                        ),
                        dbc.Col(
                            [
                                html.Div(anyo_titulo),
                                html.Div(anyo_valor),
                            ],
                            style={"text-align": "center", "flex": "0.5"},
                        ),
                    ],
                    style={
                        "display": "flex",
                    },
                ),
                dbc.Row(  # Tercera fila con el mapa principal y los filtros
                    [
                        dbc.Col(
                            [
                                html.H3(
                                    "Selecciona la cantidad de metros cuadrados",
                                    style={"text-align": "center"},
                                ),
                                dcc.RangeSlider(
                                    id="constructed-area-range-slider",
                                    min=valencia_sale["CONSTRUCTEDAREA"].min(),
                                    max=valencia_sale["CONSTRUCTEDAREA"].max(),
                                    step=15,
                                    marks={
                                        int(
                                            valencia_sale["CONSTRUCTEDAREA"].min()
                                        ): str(valencia_sale["CONSTRUCTEDAREA"].min()),
                                        int(
                                            valencia_sale["CONSTRUCTEDAREA"].max()
                                        ): str(valencia_sale["CONSTRUCTEDAREA"].max()),
                                    },
                                    value=[
                                        valencia_sale["CONSTRUCTEDAREA"].min(),
                                        valencia_sale["CONSTRUCTEDAREA"].max(),
                                    ],
                                    className="custom-slider",
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.H3(
                                    "Selecciona el rango de precios",
                                    style={"text-align": "center"},
                                ),
                                dcc.RangeSlider(
                                    id="price-range-slider",
                                    min=valencia_sale["PRICE"].min(),
                                    max=valencia_sale["PRICE"].max(),
                                    step=1000,
                                    marks={
                                        int(
                                            valencia_sale["PRICE"].min()
                                        ): f"{valencia_sale['PRICE'].min()}€",
                                        int(
                                            valencia_sale["PRICE"].max()
                                        ): f"{valencia_sale['PRICE'].max()}€",
                                    },
                                    value=[
                                        valencia_sale["PRICE"].min(),
                                        valencia_sale["PRICE"].max(),
                                    ],
                                    className="custom-slider",
                                ),
                            ],
                            width=4,
                        ),
                        dbc.Col(
                            [
                                html.H3(
                                    "Selecciona el número de habitaciones",
                                    style={"text-align": "center"},
                                ),
                                dcc.Dropdown(
                                    id="room-number-dropdown",
                                    options=[
                                        {"label": "Todas", "value": -1},
                                        *[
                                            {"label": f"{i} habitación(es)", "value": i}
                                            for i in sorted(
                                                valencia_sale["ROOMNUMBER"].unique()
                                            )
                                        ],
                                    ],
                                    value=-1,  # Valor por defecto para mostrar todos
                                    clearable=False,
                                    style={"width": "80%", "margin": "0 auto"},
                                ),
                            ],
                            width=4,
                        ),
                    ],
                    style={"margin-top": "4rem"},
                ),
                dbc.Row(  # Fila con el mapa
                    [
                        dbc.Col(
                            dcc.Graph(id="scatter-map", figure=scatter_map_wfilters),
                            width=12,
                        ),
                    ],
                    style={"margin-top": "4rem"},
                ),
                dbc.Row(  # Cuarta fila con los gráficos adicionales
                    [
                        html.H2(
                            "Datos sobre la vivienda en Valencia",
                            style={"text-align": "center"},
                        ),
                        dbc.Col(
                            dcc.Graph(
                                figure=scatter_map_buildtype,
                            ),
                            width=4,
                        ),
                        dbc.Col(
                            dcc.Graph(
                                figure=houses_per_neighborhood,
                            ),
                            width=4,
                        ),
                        dbc.Col(
                            dcc.Graph(
                                figure=houses_per_roomnumber,
                            ),
                            width=4,
                        ),
                    ],
                    style={"margin-top": "4rem"},
                ),
                dbc.Row(
                    [
                        html.H2(
                            "Calidad media y antigüedad media de los inmuebles por barrio",
                            style={"text-align": "center"},
                        ),
                        dcc.Graph(
                            id="quality-mean-map",
                            figure=quality_mean_neighborhood,
                            style={"width": "48%", "display": "inline-block"},
                        ),
                        dcc.Graph(
                            id="age-mean-map",
                            figure=mean_age_per_neighborhood,
                            style={
                                "width": "48%",
                                "display": "inline-block",
                                "margin-left": "4%",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "margin-top": "4rem",
                    },
                ),
                dbc.Row(
                    [
                        html.H2(
                            "Análisis de los precios de las viviendas",
                            style={"text-align": "center"},
                        ),
                        dcc.Graph(
                            id="price-corr-bar",
                            figure=price_corr_bar,
                            style={"width": "48%", "display": "inline-block"},
                        ),
                        dcc.Graph(
                            id="price-boxplot",
                            figure=price_boxplot,
                            style={
                                "width": "48%",
                                "display": "inline-block",
                                "margin-left": "4%",
                            },
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "margin-top": "4rem",
                    },
                ),
                dbc.Row(
                    [
                        html.H2(
                            "Distribución Geográfica de Inmuebles por Clúster",
                            style={"text-align": "center"},
                        ),
                        dcc.Graph(
                            id="clustering-map",
                            figure=clustering_map,
                            style={"width": "100%", "display": "inline-block"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justify-content": "center",
                        "margin-top": "4rem",
                    },
                ),
            ],
        ),
    ],
    fluid=True,
    className="dashboard-container",
)


@app.callback(
    Output("scatter-map", "figure"),
    [
        Input("constructed-area-range-slider", "value"),
        Input("price-range-slider", "value"),
        Input("room-number-dropdown", "value"),
    ],
)
def update_map(selected_area, selected_price, selected_room):
    min_area, max_area = selected_area
    min_price, max_price = selected_price

    filtered_data = valencia_sale[
        (valencia_sale["CONSTRUCTEDAREA"] >= min_area)
        & (valencia_sale["CONSTRUCTEDAREA"] <= max_area)
        & (valencia_sale["PRICE"] >= min_price)
        & (valencia_sale["PRICE"] <= max_price)
    ]

    if selected_room != -1:
        filtered_data = filtered_data[filtered_data["ROOMNUMBER"] == selected_room]

    scatter_map_wfilters = px.scatter_mapbox(
        data_frame=filtered_data,
        lat="LATITUDE",
        lon="LONGITUDE",
        zoom=11.5,
        mapbox_style="carto-positron",
        color="PRICE",
    )

    scatter_map_wfilters.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
    )

    scatter_map_wfilters.update_traces(marker=dict(size=5, color="orange"))

    return scatter_map_wfilters


if __name__ == "__main__":
    app.run(debug=True, port=8082)

server = app.server
