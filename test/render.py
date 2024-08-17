import os
import sys

sys.path.append(r'C:\OSGeo4W\apps\Python312\Lib\site-packages')

#os.environ['GDAL_DATA'] = r'C:\OSGeo4W\share\gdal'
os.environ['PROJ_LIB'] = r'C:\OSGeo4W\share\proj'

import matplotlib.pyplot as plt

from osgeo import ogr, osr, gdal



def render_s57(file_path):
    # Open the S-57 ENC file using GDAL/OGR
    driver = ogr.GetDriverByName("S57")
    dataset = driver.Open(file_path, 0)  # 0 means read-only

    if not dataset:
        print(f"Failed to open file: {file_path}")
        return

    # Get the spatial reference system of the dataset
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromEPSG(4326)  # WGS84 (standard for S-57)

    # Prepare the plot
    plt.figure(figsize=(10, 10))

    # Iterate over layers and features in the S-57 file
    for layer in dataset:
        layer_name = layer.GetName()
        print(f"Rendering layer: {layer_name}")

        for feature in layer:
            geometry = feature.GetGeometryRef()

            if geometry:
                # Extract coordinates and render based on geometry type
                if geometry.GetGeometryName() == "POINT":
                    x, y = geometry.GetX(), geometry.GetY()
                    plt.scatter(x, y, label=layer_name, s=10)

                elif geometry.GetGeometryName() in ["LINESTRING", "MULTILINESTRING"]:
                    for line in geometry:
                        x = [point[0] for point in line.GetPoints()]
                        y = [point[1] for point in line.GetPoints()]
                        plt.plot(x, y, label=layer_name)

                elif geometry.GetGeometryName() in ["POLYGON", "MULTIPOLYGON"]:
                    for polygon in geometry:
                        exterior_ring = polygon.GetGeometryRef(0)
                        x = [point[0] for point in exterior_ring.GetPoints()]
                        y = [point[1] for point in exterior_ring.GetPoints()]
                        plt.fill(x, y, label=layer_name, alpha=0.5)

    # Customize and show plot
    plt.title("S-57 ENC Data Visualization")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend(loc="upper right", fontsize="small", bbox_to_anchor=(1.15, 1))
    plt.grid(True)
    plt.show()

# Example usage
file_path = r"C:\Users\EverdreamSoft\Desktop\Projects\Toni\DecryptS63\python\data\GB5X01SW.000"  # Replace with your actual S-57 file path
render_s57(file_path)
