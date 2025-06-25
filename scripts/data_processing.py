import pandas as pd
import numpy as np
import geopandas as gpd
import shapely

valencia_polygons = pd.read_excel(io="./raw-data/Valencia_polygons.xlsx")
valencia_polygons = valencia_polygons.drop(columns=["LOCATIONID", "ZONELEVELID"])
valencia_polygons = valencia_polygons.rename(
    columns={"LOCATIONNAME": "NEIGHBORHOOD", "geometry": "GEO_SHAPE"}
)  # Cambiamos los nombres de las variables
valencia_polygons["GEO_SHAPE"] = valencia_polygons["GEO_SHAPE"].apply(shapely.wkt.loads)
valencia_polygons = gpd.GeoDataFrame(
    valencia_polygons, geometry="GEO_SHAPE", crs="EPSG:4326"
)

valencia_metro = pd.read_excel(io="./raw-data/Valencia_metro.xlsx")
valencia_metro = valencia_metro.rename(
    columns={"Lon": "LONGITUDE", "Lat": "LATITUDE"}
)  # Cambiamos los nombres de las variables
valencia_metro.loc[
    valencia_metro["LONGITUDE"] == 0.4026173, "LONGITUDE"
] = -0.4026173  # Corregimos un error de la estación de metro de San Isidro


def caculate_trimester(periodo):
    month = int(str(periodo)[4:6])
    if month == 3:
        return "T1"
    elif month == 6:
        return "T2"
    elif month == 9:
        return "T3"
    else:
        return "T4"


valencia_sale = pd.read_excel(io="./raw-data/Valencia_Sale.xlsx")
valencia_sale["AGE"] = (
    pd.to_datetime("today").year - valencia_sale["CADCONSTRUCTIONYEAR"]
)  # Calculamos los años de antigüedad del inmueble
valencia_sale["TRIMESTER"] = valencia_sale["PERIOD"].apply(
    caculate_trimester
)  # Calculamos el trimestre de la publicación del anuncio
valencia_sale = valencia_sale.drop(
    columns=["ASSETID", "CONSTRUCTIONYEAR", "geometry"]
)  # Eliminamos las variables que no utilizaremos
valencia_sale = gpd.GeoDataFrame(
    valencia_sale,
    geometry=gpd.points_from_xy(valencia_sale.LONGITUDE, valencia_sale.LATITUDE),
    crs="EPSG:4326",
)

# Creamos una variable para el tipo de construcción
conditions = [
    valencia_sale["BUILTTYPEID_1"] == 1,
    valencia_sale["BUILTTYPEID_2"] == 1,
    valencia_sale["BUILTTYPEID_3"] == 1,
]

choices = [
    "Nueva construcción",
    "Segunda mano a reformar",
    "Segunda mano en buen estado",
]

valencia_sale["BUILDTYPE"] = np.select(conditions, choices, default="Unknown")

joined = gpd.sjoin(valencia_sale, valencia_polygons, how="left", predicate="within")
joined = joined.reset_index(drop=True)
valencia_sale["NEIGHBORHOOD"] = joined["NEIGHBORHOOD"]

count_inmuebles = (
    joined.groupby("NEIGHBORHOOD").size().reset_index(name="REAL_ESTATE_TOTAL")
)
unitpricemean_inmuebles = (
    joined.groupby("NEIGHBORHOOD")["UNITPRICE"]
    .mean()
    .round(2)
    .reset_index(name="UNITPRICE_MEAN")
)
pricemean_inmuebles = (
    joined.groupby("NEIGHBORHOOD")["PRICE"].mean().reset_index(name="PRICE_MEAN")
)
agemean_inmuebles = (
    joined.groupby("NEIGHBORHOOD")["AGE"].mean().round(0).reset_index(name="AGE_MEAN")
)
quality_inmuebles = (
    joined.groupby("NEIGHBORHOOD")["CADASTRALQUALITYID"]
    .mean()
    .round(2)
    .reset_index(name="QUALITY_MEAN")
)

valencia_polygons = valencia_polygons.merge(
    count_inmuebles, left_on="NEIGHBORHOOD", right_on="NEIGHBORHOOD", how="left"
)
valencia_polygons = valencia_polygons.merge(
    unitpricemean_inmuebles, left_on="NEIGHBORHOOD", right_on="NEIGHBORHOOD", how="left"
)
valencia_polygons = valencia_polygons.merge(
    pricemean_inmuebles, left_on="NEIGHBORHOOD", right_on="NEIGHBORHOOD", how="left"
)
valencia_polygons = valencia_polygons.merge(
    agemean_inmuebles, left_on="NEIGHBORHOOD", right_on="NEIGHBORHOOD", how="left"
)
valencia_polygons = valencia_polygons.merge(
    quality_inmuebles, left_on="NEIGHBORHOOD", right_on="NEIGHBORHOOD", how="left"
)


valencia_metro.to_csv("./data/valencia_metro.csv", index=False)
valencia_polygons.to_csv("./data/valencia_polygons.csv", index=False)
valencia_sale.to_csv("./data/valencia_sale.csv", index=False)
