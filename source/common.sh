# srs_info: gdalsrsinfo -o wkt --single-line <my_raster>.tiff
# extent: west north east south


# Small area
# area="pyrenees"
# input_dataset_pathname="$LUE_ROUTING_DATA/$area/ldd_108680.lue"
# flow_direction_array_pathname="area/raster/ldd_108680"
# srs_info='PROJCRS["unknown",BASEGEOGCRS["unknown",DATUM["Unknown_based_on_GRS80_ellipsoid",ELLIPSOID["GRS 1980",6378137,298.257222101004,LENGTHUNIT["metre",1],ID["EPSG",7019]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]]],CONVERSION["Lambert Azimuthal Equal Area",METHOD["Lambert Azimuthal Equal Area",ID["EPSG",9820]],PARAMETER["Latitude of natural origin",43.5,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",1.5,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["False easting",0,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",0,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["(E)",east,ORDER[1],LENGTHUNIT["metre",1]],AXIS["(N)",north,ORDER[2],LENGTHUNIT["metre",1]]]'
# extent="-41612.5000000000000000 56812.5000000000000000 41612.5000000000000000 -56537.5000000000000000"


# Bigger area
area="south_africa"
input_dataset_pathname="$LUE_ROUTING_DATA/$area/south_africa.lue"
flow_direction_array_pathname="area/raster/ldd_southafrica"
srs_info='PROJCRS["unknown",BASEGEOGCRS["unknown",DATUM["Unknown_based_on_GRS80_ellipsoid",ELLIPSOID["GRS 1980",6378137,298.257222101004,LENGTHUNIT["metre",1],ID["EPSG",7019]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433,ID["EPSG",9122]]]],CONVERSION["Lambert Azimuthal Equal Area",METHOD["Lambert Azimuthal Equal Area",ID["EPSG",9820]],PARAMETER["Latitude of natural origin",-15,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8801]],PARAMETER["Longitude of natural origin",25,ANGLEUNIT["degree",0.0174532925199433],ID["EPSG",8802]],PARAMETER["False easting",0,LENGTHUNIT["metre",1],ID["EPSG",8806]],PARAMETER["False northing",0,LENGTHUNIT["metre",1],ID["EPSG",8807]]],CS[Cartesian,2],AXIS["(E)",east,ORDER[1],LENGTHUNIT["metre",1]],AXIS["(N)",north,ORDER[2],LENGTHUNIT["metre",1]]]'
extent="-2802950 2105050 2802950 -2390550"


# Biggest area
# area="africa"
# input_dataset_pathname="$LUE_ROUTING_DATA/$area/africa.lue"
# flow_direction_array_pathname="area/raster/ldd"
# srs_info='GEOGCRS["WGS 84",DATUM["World Geodetic System 1984",ELLIPSOID["WGS 84",6378137,298.257223563,LENGTHUNIT["metre",1]]],PRIMEM["Greenwich",0,ANGLEUNIT["degree",0.0174532925199433]],CS[ellipsoidal,2],AXIS["geodetic latitude (Lat)",north,ORDER[1],ANGLEUNIT["degree",0.0174532925199433]],AXIS["geodetic longitude (Lon)",east,ORDER[2],ANGLEUNIT["degree",0.0174532925199433]],ID["EPSG",4326]]'
# extent="-18 38 52 -35"
