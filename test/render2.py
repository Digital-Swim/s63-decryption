import os
import sys

sys.path.append(r'C:\OSGeo4W\apps\Python312\Lib\site-packages')

#os.environ['GDAL_DATA'] = r'C:\OSGeo4W\share\gdal'
os.environ['PROJ_LIB'] = r'C:\OSGeo4W\share\proj'

import matplotlib.pyplot as plt

from osgeo import ogr, osr, gdal

import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point
import matplotlib.patches as mpatches

def render_s57(file_path):
    # Open the S-57 file
    driver = ogr.GetDriverByName('S57')
    dataset = driver.Open(file_path)

    if not dataset:
        print(f"Failed to open file: {file_path}")
        return

    # Prepare plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Define color codes for different feature types
    feature_colors = {
        'COALNE': 'brown',   # Coastlines
        'DEPCNT': 'blue',    # Depth Contours
        'SOUNDG': 'cyan',    # Soundings (depth points)
        'BOYLAT': 'yellow',  # Lateral Buoys
        'LIGHTS': 'red',     # Lights
        'WRECKS': 'red',     # Wrecks
        'UWTROC': 'orange',  # Underwater Rocks
        'OBSTRN': 'purple',  # Obstructions
        'ISODGR': 'black',   # Isolated Dangers
        'DEPARE': 'blue',    # Depth Areas
        'DSID': 'gray',      # Metadata layer
        'Point': 'green',    # General point features
        'Line': 'blue',      # General line features
        'Area': 'lightblue', # General area features
        'Meta': 'magenta'    # General metadata
    }

    # Iterate over layers and render specific features
    for layer in dataset:
        layer_name = layer.GetName()
        print(f"Rendering layer: {layer_name}")

        if layer_name in feature_colors:
            for feature in layer:
                geometry = feature.GetGeometryRef()

               
                if geometry:
                    geom_type = geometry.GetGeometryName()
                    print(geom_type)
                    if geom_type == "POINT":
                        x, y = geometry.GetX(), geometry.GetY()
                        ax.plot(x, y, 'o', color=feature_colors[layer_name], markersize=4, label=layer_name)

                    elif geom_type == "LINESTRING":
                        points = geometry.GetPoints()
                        x = [point[0] for point in points]
                        y = [point[1] for point in points]
                        ax.plot(x, y, color=feature_colors[layer_name], label=layer_name)

                    elif geom_type == "POLYGON":
                        ring = geometry.GetGeometryRef(0)
                        x = [point[0] for point in ring.GetPoints()]
                        y = [point[1] for point in ring.GetPoints()]
                        ax.fill(x, y, color=feature_colors[layer_name], alpha=0.3, label=layer_name)

    # Customize plot
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize="small", bbox_to_anchor=(1.15, 1))

    ax.set_title("IHO S-57 Dataset Visualization")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True)
    plt.show()

def render_navigational_hazards(file_path):
    # Open the S-57 file
    driver = ogr.GetDriverByName('S57')
    dataset = driver.Open(file_path)

    if not dataset:
        print(f"Failed to open file: {file_path}")
        return

    # Define color codes for hazard features
    hazard_colors = {
        'WRECKS': 'red',     # Wrecks
        'UWTROC': 'orange',  # Underwater Rocks
        'OBSTRN': 'purple',  # Obstructions
        'ISODGR': 'black',   # Isolated Dangers
        'DEPARE': 'blue',     # Shallow Depth Areas
        'DSID': 'gray',      # Metadata layer
        'Point': 'green',    # General point features
        'Line': 'blue',      # General line features
        'Area': 'lightblue', # General area features
        'Meta': 'magenta'    # General metadata
    }

    # Prepare the plot
    fig, ax = plt.subplots(figsize=(10, 10))

    # Iterate over layers and render hazard features
    for layer in dataset:
        layer_name = layer.GetName()

        print(f"Rendering layer: {layer_name}")

        # Only process layers that contain hazard features
        if layer_name in hazard_colors:

            print(f"Rendering layer: {layer_name}")
            for feature in layer:
                geometry = feature.GetGeometryRef()

                if geometry:
                    geom_type = geometry.GetGeometryName()
                    print(geom_type)

                    if geom_type == "POINT" or geom_type == "MULTIPOINT":
                        x, y = geometry.GetX(), geometry.GetY()
                        ax.plot(x, y, 'o', color=hazard_colors[layer_name], markersize=6, label=layer_name)

                    elif geom_type == "LINESTRING" or geom_type == "MULTILINESTRING":
                        points = geometry.GetPoints()
                        x = [point[0] for point in points]
                        y = [point[1] for point in points]
                        ax.plot(x, y, color=hazard_colors[layer_name], label=layer_name)

                    elif geom_type == "POLYGON1" or geom_type == "MULTIPOLYGON1":
                        for polygon in geometry:
                            ring = polygon.GetGeometryRef(0)
                            x = [point[0] for point in ring.GetPoints()]
                            y = [point[1] for point in ring.GetPoints()]
                            ax.fill(x, y, color=hazard_colors[layer_name], alpha=0.3, label=layer_name)
                    
                    elif geom_type == "POLYGON" or geom_type == "MULTIPOLYGON":
                        ring = geometry.GetGeometryRef(0)
                        x = [point[0] for point in ring.GetPoints()]
                        y = [point[1] for point in ring.GetPoints()]
                        ax.fill(x, y, color=hazard_colors[layer_name], alpha=0.3, label=layer_name)

    # Customize plot
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize="small", bbox_to_anchor=(1.15, 1))

    ax.set_title("Navigational Hazards (IHO S-57)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True)
    plt.show()

def render_enc_with_geopandas(file_path):
    # Use geopandas to read the ENC file (S-57 format)
    gdf = gpd.read_file(file_path)

    # Filter and highlight navigational hazard features
    hazard_features = ['WRECKS', 'UWTROC', 'OBSTRN', 'ISODGR', 'DEPARE']
    hazard_gdf = gdf[gdf['objl'].isin(hazard_features)]  # 'objl' is the S-57 feature code attribute

    # Plot the filtered hazard features
    fig, ax = plt.subplots(figsize=(12, 8))
    hazard_gdf.plot(ax=ax, column='objl', legend=True, cmap='Set1', edgecolor='black')

    # Customize plot
    ax.set_title("Navigational Hazards in ENC Data (Rendered with GeoPandas)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.grid(True)
    plt.show()


def render_all_features_with_geopandas(file_path):
    # Load the ENC dataset using geopandas
    gdf = gpd.read_file(file_path)

    # Separate the data by geometry type
    point_features = gdf[gdf.geometry.type == 'Point']
    line_features = gdf[gdf.geometry.type == 'LineString']
    polygon_features = gdf[gdf.geometry.type == 'Polygon']

    # Plot all features
    fig, ax = plt.subplots(figsize=(14, 10))

    # Plot point features
    if not point_features.empty:
        point_features.plot(ax=ax, color='red', marker='o', markersize=5, label='Point Features')

    # Plot line features
    if not line_features.empty:
        line_features.plot(ax=ax, color='blue', linewidth=1, label='Line Features')

    # Plot polygon features
    if not polygon_features.empty:
        polygon_features.plot(ax=ax, color='green', edgecolor='black', alpha=0.5, label='Polygon Features')

    # Customize plot
    ax.set_title("All ENC Features with Different Geometric Shapes")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.legend()
    plt.grid(True)
    plt.show()

def render_all_layers1(file_path):
    # Open the dataset using OGR to handle multiple layers
    driver = ogr.GetDriverByName('S57')
    dataset = driver.Open(file_path)

    if not dataset:
        print(f"Failed to open file: {file_path}")
        return

    # Prepare the plot
    fig, ax = plt.subplots(figsize=(14, 10))

    # Iterate over each layer in the dataset
    for layer_index in range(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(layer_index)
        layer_name = layer.GetName()
        print(f"Rendering layer: {layer_name}")

        # Convert the OGR layer to a GeoPandas GeoDataFrame
        gdf = gpd.read_file(file_path, layer=layer_name)

        # Separate by geometry types
        point_features = gdf[gdf.geometry.type == 'Point']
        line_features = gdf[gdf.geometry.type == 'LineString']
        polygon_features = gdf[gdf.geometry.type == 'Polygon']

        # Plot point features
        if not point_features.empty:
            point_features.plot(ax=ax, color='red', marker='o', markersize=5, label=f'Point Features ({layer_name})')

        # Plot line features
        if not line_features.empty:
            line_features.plot(ax=ax, color='blue', linewidth=1, label=f'Line Features ({layer_name})')

        # Plot polygon features
        if not polygon_features.empty:
            polygon_features.plot(ax=ax, color='green', edgecolor='black', alpha=0.5, label=f'Polygon Features ({layer_name})')

    # Customize plot
    ax.set_title("ENC Data with Multiple Layers Rendered")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.legend(loc="upper right", fontsize="small")
    plt.grid(True)
    plt.show()


def render_all_layers2(file_path):
    # Open the dataset using OGR to handle multiple layers
    driver = ogr.GetDriverByName('S57')
    dataset = driver.Open(file_path)

    if not dataset:
        print(f"Failed to open file: {file_path}")
        return

    # Prepare the plot
    fig, ax = plt.subplots(figsize=(14, 10))

    # Iterate over each layer in the dataset
    for layer_index in range(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(layer_index)
        layer_name = layer.GetName()
        print(f"Rendering layer: {layer_name}")

        # Convert the OGR layer to a GeoPandas GeoDataFrame, if possible
        try:
            gdf = gpd.read_file(file_path, layer=layer_name)
        except Exception as e:
            print(f"Could not load layer {layer_name} as GeoDataFrame: {e}")
            continue

        # Check if the loaded layer is a valid GeoDataFrame
        if not isinstance(gdf, gpd.GeoDataFrame):
            print(f"Layer {layer_name} is not a GeoDataFrame.")
            continue

        # Ensure the GeoDataFrame has a 'geometry' column
        if 'geometry' not in gdf.columns:
            print(f"Layer {layer_name} does not contain geometry data.")
            continue

        # Separate by geometry types
        point_features = gdf[gdf.geometry.type == 'Point']
        line_features = gdf[gdf.geometry.type == 'LineString']
        polygon_features = gdf[gdf.geometry.type == 'Polygon']

        # Plot point features
        if not point_features.empty:
            point_features.plot(ax=ax, color='red', marker='o', markersize=5, label=f'Point Features ({layer_name})')

        # Plot line features
        if not line_features.empty:
            line_features.plot(ax=ax, color='blue', linewidth=1, label=f'Line Features ({layer_name})')

        # Plot polygon features
        if not polygon_features.empty:
            polygon_features.plot(ax=ax, color='green', edgecolor='black', alpha=0.5, label=f'Polygon Features ({layer_name})')

    # Customize plot
    ax.set_title("ENC Data with Multiple Layers Rendered")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.legend(loc="upper right", fontsize="small")
    plt.grid(True)
    plt.show()


def ogr_layer_to_geopandas(layer):
    """Convert an OGR layer to a GeoPandas GeoDataFrame."""
    features = []
    for feature in layer:
        geom = feature.GetGeometryRef()
        geom_type = geom.GetGeometryName()

        # Convert the OGR geometry to Shapely geometry
        if geom_type == "POINT":
            shapely_geom = Point(geom.GetX(), geom.GetY())
        elif geom_type == "LINESTRING":
            points = geom.GetPoints()
            shapely_geom = LineString(points)
        elif geom_type == "POLYGON":
            ring = geom.GetGeometryRef(0)
            shapely_geom = Polygon(ring.GetPoints())
        else:
            # Skip unsupported geometry types
            continue

        # Convert feature attributes to a dictionary
        attributes = feature.items()
        attributes["geometry"] = shapely_geom
        features.append(attributes)

    # Convert to GeoPandas GeoDataFrame
    return gpd.GeoDataFrame(features)

def render_all_layers(file_path):
    # Open the dataset using OGR to handle multiple layers
    driver = ogr.GetDriverByName('S57')
    dataset = driver.Open(file_path)

    if not dataset:
        print(f"Failed to open file: {file_path}")
        return

    # Prepare the plot
    fig, ax = plt.subplots(figsize=(5, 5))

    # Iterate over each layer in the dataset
    for layer_index in range(dataset.GetLayerCount()):
        layer = dataset.GetLayerByIndex(layer_index)
        layer_name = layer.GetName()
        print(f"Rendering layer: {layer_name}")

        # Convert the OGR layer to a GeoPandas GeoDataFrame
        try:
            gdf = ogr_layer_to_geopandas(layer)
        except Exception as e:
            print(f"Could not convert layer {layer_name} to GeoDataFrame: {e}")
            continue

        # Check if the GeoDataFrame is valid
        if gdf.empty:
            print(f"Layer {layer_name} is empty or not supported.")
            continue

        # Separate by geometry types
        point_features = gdf[gdf.geometry.type == 'Point']
        line_features = gdf[gdf.geometry.type == 'LineString']
        polygon_features = gdf[gdf.geometry.type == 'Polygon']

        # Plot point features
        if not point_features.empty:
            point_features.plot(ax=ax, color='red', marker='o', markersize=5, label=f'Point Features ({layer_name})')

        # Plot line features
        if not line_features.empty:
            line_features.plot(ax=ax, color='blue', linewidth=1, label=f'Line Features ({layer_name})')

        # Plot polygon features
        if not polygon_features.empty:
            polygon_features.plot(ax=ax, color='green', edgecolor='black', alpha=0.5, label=f'Polygon Features ({layer_name})')

    # Customize plot
    ax.set_title("ENC Data with Multiple Layers Rendered")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.legend(loc="upper right", fontsize="small")
    plt.grid(True)
    plt.show()



# Example usage
render_all_layers(r'C:\Users\EverdreamSoft\Desktop\Projects\Toni\DecryptS63\python\data\GB4X0000.000')
