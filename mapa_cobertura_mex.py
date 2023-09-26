# -*- coding: utf-8 -*-
"""mapa_cobertura_mex.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wft01G55kh7DmiuJGqS4Zz9oKc5Jb_VE
"""


import requests
import io
import urllib.request
import fiona
from shapely.geometry import Point, Polygon, LineString
import pandas as pd

import psycopg2
from datetime import datetime,timedelta
import pytz
import streamlit as st
import json
import geopandas as gpd
import pyproj
import plotly.graph_objs as go
import itertools

st.set_page_config(page_title=None, page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
def select_query(query):
	try:
		conn = psycopg2.connect(host="rocketpin-bi.ckgzkrdcz2xh.us-east-1.rds.amazonaws.com",
				port = 5432, database="rocketpin_bi", user="rocketpin", password="4yZ784OGLqi94wLwONTD")
		cur = conn.cursor()
		cur.execute(query)
		query_array = cur.fetchall()
	except (Exception, psycopg2.Error) as error:
		print("Error while fetching data from PostgreSQL", error)
	finally:
		if conn:
			cur.close()
			conn.close()
	return query_array



@st.cache_data#(allow_output_mutation=True)
def query2tableApprove(query):
	conn = psycopg2.connect(host="rocketpin-bi.ckgzkrdcz2xh.us-east-1.rds.amazonaws.com", port = 5432, database="rocketpin_bi", user="rocketpin", password="4yZ784OGLqi94wLwONTD")
	cur = conn.cursor()
	def create_pandas_table(sql_query, database = conn):
		table = pd.read_sql_query(sql_query, database)
		return table
	info = create_pandas_table(query)
	df = pd.DataFrame(info)
	cur.close()
	conn.close()
	return df

@st.cache_data#(allow_output_mutation=True)
def query2tableDisapprove(query):
	conn = psycopg2.connect(host="rocketpin-bi.ckgzkrdcz2xh.us-east-1.rds.amazonaws.com", port = 5432, database="rocketpin_bi", user="rocketpin", password="4yZ784OGLqi94wLwONTD")
	cur = conn.cursor()
	def create_pandas_table(sql_query, database = conn):
		table = pd.read_sql_query(sql_query, database)
		return table
	info = create_pandas_table(query)
	df = pd.DataFrame(info)
	cur.close()
	conn.close()
	return df

@st.cache_data#(allow_output_mutation=True)
def query2tableTaken(query):
	conn = psycopg2.connect(host="rocketpin-bi.ckgzkrdcz2xh.us-east-1.rds.amazonaws.com", port = 5432, database="rocketpin_bi", user="rocketpin", password="4yZ784OGLqi94wLwONTD")
	cur = conn.cursor()
	def create_pandas_table(sql_query, database = conn):
		table = pd.read_sql_query(sql_query, database)
		return table
	info = create_pandas_table(query)
	df = pd.DataFrame(info)
	cur.close()
	conn.close()
	return df



def kml_to_list(df, all_missions):
    sectores = []

    for i in range(len(df)):
        name = df['Name'][i]
        description = df['Description'][i]
        polygon = df['geometry'][i]
        name = name.lower()#.replace('rango urbano ', '').strip()

        if str(type(polygon)).replace('>', '').replace("'", '').split(".")[-1] == 'MultiPolygon':
            for polygon_obj in list(polygon.geoms):
                coords_array = polygon_obj.exterior.coords.xy
                h = 0
                list_coords = []
                while h < len(coords_array[0]):
                    x = coords_array[0][h]
                    y = coords_array[1][h]
                    list_coords.append((x, y))
                    h = h + 1
                sectores.append([name, description, Polygon(list_coords)])
        elif str(type(polygon)).replace('>', '').replace("'", '').split(".")[-1] == 'LineString':
            pass
        else:
            coords_array = polygon.exterior.coords.xy
            h = 0
            list_coords = []
            while h < len(coords_array[0]):
                x = coords_array[0][h]
                y = coords_array[1][h]
                list_coords.append((x, y))
                h = h + 1
            sectores.append([name, description, Polygon(list_coords)])

    results = []
    #matching_commune = mi_per_commune

    for sector in sectores:
        name, description, polygon = sector
        points_inside_polygon = all_missions[all_missions.geometry.within(polygon)]
        points_outside_polygon = all_missions[~all_missions.geometry.within(polygon)]

       # outside_count = len(points_outside_polygon) - matching_commune.filter(like=f'{name}').sum()

        result_df = pd.DataFrame({
            'name': name,
            #'description': description,
            'inside_count': len(points_inside_polygon),
            #'outside_count': len(points_outside_polygon)
        }, index=[0])

        results.append(result_df)

    return pd.concat (results, ignore_index=True)



today = datetime.now(pytz.timezone('America/Mexico_City')).date()
before = today + timedelta(days=-180)
start_date = st.sidebar.date_input('Fecha de Inicio Aprobadas y rechazadas', before,min_value = today + timedelta(days=-180),max_value = today)
end_date = st.sidebar.date_input('Fecha de término Aprobadas y rechazadas', today,min_value = today + timedelta(days=-180),max_value = today)


q = '''SELECT distinct commune
FROM missions mi
WHERE created_at>=(current_date - '6 month'::interval) and deleted = 0 and country='México' and campain_id in ('2661','2246','2384','2124','1688','2181','2182','2177','2327','2379','2269','2431','1734','2065','2662','1750','1732','1689','1654','1653','1633','1946','2663','1666','1392','2557','2572','1768','2655','2658','2657','2624','2622','2623','2659','1424','1491','1980','2805','2806','1978','2069','2070','2630','2696','2695','2536','2693','1813','2676','2690','2176','2673','2045','2731','1464','1883','1675','2580','1923','2094','2748','2575','2122','1841','2842','2844','2843','2625','2626','2796','2149','2675','2479','2387','1592','2802','2804','2750','2848','2799','1947','1948','2009','2433','2889','2891','2962','2890','2999','2998','2995','3128','3127','2044','2062','2901','2902','2068','1465','2063','2064','1467','2380','2381','2382','2618','2631','2632','2898','1979','2131','2677','2126','2378','3126','3123','3398','3367','3108','3157','2319','3238',
'3237','3236') and quote_state not in ('requested','quantified')
and (state = 'approved' or state = 'disapproved')
ORDER by 1 asc
'''

if start_date > end_date:
	st.warning("La fecha de inicio es mayor a la de término")
	comuna = ''
else:
	comunas = [comuna[0] for comuna in select_query(q)]
	comunas.insert(0,'')
	comuna = st.sidebar.selectbox('Selecciona la comuna: ',comunas)



fiona.drvsupport.supported_drivers['kml'] = 'rw'
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'
fiona.drvsupport.supported_drivers['KML'] = 'rw'

### URL's de los KML's
#dangerous_zones_kml = 'https://www.google.com/maps/d/u/1/kml?mid=1rvGtQj85SJp1ssuxUhHDn9VU2ZfAd2th&lid=PuBoecvUf5w&forcekml=1&cid=mp&cv=w7Bf3o_v8Lw.es.'
urban_ranges_kml = 'https://www.google.com/maps/d/u/4/kml?mid=1xIeeoOuyRuc7itp7Zx8vbtpt6h96eo4&lid=PR8Tje6gWz0&forcekml=1&cid=mp&cv=EizL-D3uEzA.es.'

polygon = gpd.read_file(urllib.request.urlopen(urban_ranges_kml))
#redzones = gpd.read_file(urllib.request.urlopen(dangerous_zones_kml))
#st.write('asdasd'+str(type(urban_ranges_kml)))

# project GeoPandas dataframe
kml_df = polygon
polygons = kml_df['Name'].to_list()

#kml_df_redzones = redzones
#polygons_redzone = kml_df_redzones['Name'].to_list()


emails_taken = ['zonaroja@rocketpin.com','errordireccion@rocketpin.com','sincobertura@rocketpin.com',
	'sinnumero@rocketpin.com','comunaerronea@rocketpin.com','faltainformacion@rocketpin.com']
selected_emails_taken = st.sidebar.multiselect("Seleccione los emails para filtrar las asignadas",emails_taken)
emails_to_taken="'"+"','".join(selected_emails_taken)+"'"


#EMPIEZA ACA
data_query_app_tabla='''SELECT
    id,headquarter_street,commune,split_part(headquarter_location,',',1)::float as latitude,split_part(headquarter_location,',',2)::float as longitude,
  campain_id,state,
  CASE WHEN state = 'approved' THEN approve_detail
  WHEN state = 'disapproved' THEN disapprove_detail
  ELSE null END as substate,
  created_at at time zone 'utc' at time zone 'America/Mexico_City' as created_at,
  approved_at at time zone 'utc' at time zone 'America/Mexico_City' as approved_at,
  disapproved_at at time zone 'utc' at time zone 'America/Mexico_City' as disapproved_at,
  CASE WHEN state = 'approved' THEN approved_at at time zone 'utc' at time zone 'America/Mexico_City'
  WHEN state = 'disapproved' THEN disapproved_at at time zone 'utc' at time zone 'America/Mexico_City'
  ELSE null END as revision_timestamp
  FROM missions mi
  WHERE created_at at time zone 'utc' at time zone 'America/Mexico_City'>='{}'
  and created_at at time zone 'utc' at time zone 'America/Mexico_City' <= '{}' and deleted = 0 and country='México'
  and campain_id in ('2661','2246','2384','2124','1688','2181','2182','2177','2327','2379','2269','2431','1734','2065','2662','1750','1732','1689','1654','1653','1633','1946','2663','1666','1392','2557','2572','1768','2655','2658','2657','2624','2622','2623','2659','1424','1491','1980','2805','2806','1978','2069','2070','2630','2696','2695','2536','2693','1813','2676','2690','2176','2673','2045','2731','1464','1883','1675','2580','1923','2094','2748','2575','2122','1841','2842','2844','2843','2625','2626','2796','2149','2675','2479','2387','1592','2802','2804','2750','2848','2799','1947','1948','2009','2433','2889','2891','2962','2890','2999','2998','2995','3128','3127','2044','2062','2901','2902','2068','1465','2063','2064','1467','2380','2381','2382','2618','2631','2632','2898','1979','2131','2677','2126','2378','3126','3123','3398','3367','3108','3157','2319','3238',
'3237','3236') and commune in {} and quote_state not in ('requested','quantified')
  and state = 'approved' '''.format(start_date,end_date,tuple(comunas),emails_to_taken)


points_all_missions = query2tableApprove(data_query_app_tabla)
points_all_missions = gpd.GeoDataFrame(points_all_missions, geometry=gpd.points_from_xy(points_all_missions.longitude, points_all_missions.latitude))

#mi_per_commune= get_sum_of_points_by_commune(query_sum)
#mi_per_commune['commune']=mi_per_commune.commune.str.lower().str.strip()
gdf = gpd.read_file(urllib.request.urlopen(urban_ranges_kml))
#df="Rangos_Urbanos.kml"
#gdf = gpd.read_file("Rangos_Urbanos.kml")
result = kml_to_list(gdf, points_all_missions)
result= result.sort_values(by='name')




def get_sum_of_points_by_commune(query):
  conn = psycopg2.connect(host="rocketpin-bi.ckgzkrdcz2xh.us-east-1.rds.amazonaws.com", port = 5432, database="rocketpin_bi", user="rocketpin", password="4yZ784OGLqi94wLwONTD")
  cur = conn.cursor()
  def create_pandas_table(sql_query, database = conn):
    table = pd.read_sql_query(sql_query, database)
    return table
  info = create_pandas_table(query)
  df = pd.DataFrame(info)
  cur.close()
  conn.close()
  return df

query_sum =  '''SELECT commune, COUNT(distinct id)
  FROM missions mi
  WHERE created_at at time zone 'utc' at time zone 'America/Mexico_City'>='{}'
  and created_at at time zone 'utc' at time zone 'America/Mexico_City' <= '{}' and deleted = 0 and country='México'
  and campain_id in ('2661','2246','2384','2124','1688','2181','2182','2177','2327','2379','2269','2431','1734','2065','2662','1750','1732','1689','1654','1653','1633','1946','2663','1666','1392','2557','2572','1768','2655','2658','2657','2624','2622','2623','2659','1424','1491','1980','2805','2806','1978','2069','2070','2630','2696','2695','2536','2693','1813','2676','2690','2176','2673','2045','2731','1464','1883','1675','2580','1923','2094','2748','2575','2122','1841','2842','2844','2843','2625','2626','2796','2149','2675','2479','2387','1592','2802','2804','2750','2848','2799','1947','1948','2009','2433','2889','2891','2962','2890','2999','2998','2995','3128','3127','2044','2062','2901','2902','2068','1465','2063','2064','1467','2380','2381','2382','2618','2631','2632','2898','1979','2131','2677','2126','2378','3126','3123','3398','3367','3108','3157','2319','3238',
'3237','3236') and commune in {} and quote_state not in ('requested','quantified')
  and state = 'approved'
  GROUP BY commune 
  ORDER BY commune ASC'''.format(start_date,end_date,tuple(comunas))

suma_por_comuna= get_sum_of_points_by_commune(query_sum)
suma_por_comuna['commune']=suma_por_comuna['commune'].apply(lambda x: f"rango urbano {x}")
suma_por_comuna['commune']=suma_por_comuna['commune'].lower()

if str(comuna) != '' and (start_date > end_date) == False:
	data_query_app = '''SELECT
	  id,headquarter_street,commune,split_part(headquarter_location,',',1)::float as latitude,split_part(headquarter_location,',',2)::float as longitude,
	campain_id,state,
	CASE WHEN state = 'approved' THEN approve_detail
	WHEN state = 'disapproved' THEN disapprove_detail
	ELSE null END as substate,
	created_at at time zone 'utc' at time zone 'America/Mexico_City' as created_at,
	approved_at at time zone 'utc' at time zone 'America/Mexico_City' as approved_at,
	disapproved_at at time zone 'utc' at time zone 'America/Mexico_City' as disapproved_at,
	CASE WHEN state = 'approved' THEN approved_at at time zone 'utc' at time zone 'America/Mexico_City'
	WHEN state = 'disapproved' THEN disapproved_at at time zone 'utc' at time zone 'America/Mexico_City'
	ELSE null END as revision_timestamp
	FROM missions mi
	WHERE created_at at time zone 'utc' at time zone 'America/Mexico_City'>='{}'
	and created_at at time zone 'utc' at time zone 'America/Mexico_City' <= '{}' and deleted = 0 and country='México'
	and campain_id in ('2661','2246','2384','2124','1688','2181','2182','2177','2327','2379','2269','2431','1734','2065','2662','1750','1732','1689','1654','1653','1633','1946','2663','1666','1392','2557','2572','1768','2655','2658','2657','2624','2622','2623','2659','1424','1491','1980','2805','2806','1978','2069','2070','2630','2696','2695','2536','2693','1813','2676','2690','2176','2673','2045','2731','1464','1883','1675','2580','1923','2094','2748','2575','2122','1841','2842','2844','2843','2625','2626','2796','2149','2675','2479','2387','1592','2802','2804','2750','2848','2799','1947','1948','2009','2433','2889','2891','2962','2890','2999','2998','2995','3128','3127','2044','2062','2901','2902','2068','1465','2063','2064','1467','2380','2381','2382','2618','2631','2632','2898','1979','2131','2677','2126','2378','3126','3123','3398','3367','3108','3157','2319','3238',
'3237','3236') and commune = '{}' and quote_state not in ('requested','quantified')
	and state = 'approved' '''.format(start_date,end_date,comuna)
	data_app = query2tableApprove(data_query_app)


	### PUNTO PARA CENTRAR MAPA
	points_app = gpd.GeoDataFrame(data_app, geometry=gpd.points_from_xy(data_app.longitude, data_app.latitude))
	points_app = points_app.set_crs('epsg:4326')

	# project GeoPandas dataframe
	points_app.to_crs(pyproj.CRS.from_epsg(4326), inplace=True,epsg=None)
	# define lat, long for points
	idApp = points_app['id']
	#revisionApp=points_app['revision_timestamp']
	LatApp = points_app['latitude']
	LongApp = points_app['longitude']

	##DISAPPROVED
	data_query_dis = '''SELECT distinct
		  id,headquarter_street,commune,split_part(headquarter_location,',',1)::float as latitude,split_part(headquarter_location,',',2)::float as longitude,
		campain_id,state,
		CASE WHEN state = 'approved' THEN approve_detail
		WHEN state = 'disapproved' THEN disapprove_detail
		ELSE null END as substate,
		created_at at time zone 'utc' at time zone 'America/Mexico_City' as created_at,
		approved_at at time zone 'utc' at time zone 'America/Mexico_City' as approved_at,
		disapproved_at at time zone 'utc' at time zone 'America/Mexico_City' as disapproved_at,
		CASE WHEN state = 'approved' THEN approved_at at time zone 'utc' at time zone 'America/Mexico_City'
		WHEN state = 'disapproved' THEN disapproved_at at time zone 'utc' at time zone 'America/Mexico_City'
		ELSE null END as revision_timestamp,
		shopper_email
		FROM missions mi
		WHERE created_at at time zone 'utc' at time zone 'America/Mexico_City'>='{}'
		and created_at at time zone 'utc' at time zone 'America/Mexico_City' <= '{}' and deleted = 0 and country='México'
		and campain_id in ('2661','2246','2384','2124','1688','2181','2182','2177','2327','2379','2269','2431','1734','2065','2662','1750','1732','1689','1654','1653','1633','1946','2663','1666','1392','2557','2572','1768','2655','2658','2657','2624','2622','2623','2659','1424','1491','1980','2805','2806','1978','2069','2070','2630','2696','2695','2536','2693','1813','2676','2690','2176','2673','2045','2731','1464','1883','1675','2580','1923','2094','2748','2575','2122','1841','2842','2844','2843','2625','2626','2796','2149','2675','2479','2387','1592','2802','2804','2750','2848','2799','1947','1948','2009','2433','2889','2891','2962','2890','2999','2998','2995','3128','3127','2044','2062','2901','2902','2068','1465','2063','2064','1467','2380','2381','2382','2618','2631','2632','2898','1979','2131','2677','2126','2378','3126','3123','3398','3367','3108','3157','2319','3238',
'3237','3236') and quote_state not in ('requested','quantified') and commune = '{}'
		and (state = 'disapproved' and disapprove_detail in ('out_of_coverage','dangerous_zone')) '''.format(start_date,end_date,comuna)

	data_dis = query2tableDisapprove(data_query_dis)

	### PUNTO PARA CENTRAR MAPA
	points_dis = gpd.GeoDataFrame(data_dis, geometry=gpd.points_from_xy(data_dis.longitude, data_dis.latitude))
	points_dis = points_dis.set_crs('epsg:4326')

	# project GeoPandas dataframe
	points_dis.to_crs(pyproj.CRS.from_epsg(4326), inplace=True,epsg=None)
	# define lat, long for points
	idDis = points_dis['id']
	shopperDis = points_dis['shopper_email']
	substateDis = points_dis['substate']
	#revisionDis=points_dis['revision_timestamp']
	LatDis = points_dis['latitude']
	LongDis = points_dis['longitude']

	try:
		lat_center = data_app['latitude'][0]
		long_center = data_app['longitude'][0]
	except:
		lat_center = data_dis['latitude'][0]
		long_center = data_dis['longitude'][0]


	##TAKEN MES CURSO
	data_query_taken = '''SELECT distinct
	  id,headquarter_street,commune,split_part(headquarter_location,',',1)::float as latitude,split_part(headquarter_location,',',2)::float as longitude,
	campain_id,state,
	CASE WHEN state = 'approved' THEN approve_detail
	WHEN state = 'disapproved' THEN disapprove_detail
	ELSE null END as substate,
	created_at at time zone 'utc' at time zone 'America/Mexico_City' as created_at,
	approved_at at time zone 'utc' at time zone 'America/Mexico_City' as approved_at,
	disapproved_at at time zone 'utc' at time zone 'America/Mexico_City' as disapproved_at,
	CASE WHEN state = 'approved' THEN approved_at at time zone 'utc' at time zone 'America/Mexico_City'
	WHEN state = 'disapproved' THEN disapproved_at at time zone 'utc' at time zone 'America/Mexico_City'
	ELSE null END as revision_timestamp,
	shopper_email
	FROM missions mi
	WHERE created_at at time zone 'utc' at time zone 'America/Mexico_City' >= date_trunc('month',CURRENT_DATE) and deleted = 0 and country='México'
	and campain_id in ('2661','2246','2384','2124','1688','2181','2182','2177','2327','2379','2269','2431','1734','2065','2662','1750','1732','1689','1654','1653','1633','1946','2663','1666','1392','2557','2572','1768','2655','2658','2657','2624','2622','2623','2659','1424','1491','1980','2805','2806','1978','2069','2070','2630','2696','2695','2536','2693','1813','2676','2690','2176','2673','2045','2731','1464','1883','1675','2580','1923','2094','2748','2575','2122','1841','2842','2844','2843','2625','2626','2796','2149','2675','2479','2387','1592','2802','2804','2750','2848','2799','1947','1948','2009','2433','2889','2891','2962','2890','2999','2998','2995','3128','3127','2044','2062','2901','2902','2068','1465','2063','2064','1467','2380','2381','2382','2618','2631','2632','2898','1979','2131','2677','2126','2378','3126','3123','3398','3367','3108','3157','2319','3238',
'3237','3236')and quote_state not in ('requested','quantified') and commune = '{}' and shopper_email in ({}) and (state = 'taken') '''.format(comuna,emails_to_taken)

	data_taken = query2tableTaken(data_query_taken)

	### PUNTO PARA CENTRAR MAPA
	points_taken = gpd.GeoDataFrame(data_taken, geometry=gpd.points_from_xy(data_taken.longitude, data_taken.latitude))
	points_taken = points_taken.set_crs('epsg:4326')

	# project GeoPandas dataframe
	points_taken.to_crs(pyproj.CRS.from_epsg(9155), inplace=True,epsg=None)
	# define lat, long for points
	LatTaken = points_taken['latitude']
	LongTaken = points_taken['longitude']
	idTaken = points_taken['id']
	shopperTaken = points_taken['shopper_email']

	##### POLIGONOS DE COBERTURAS ####
	selected_polygons = st.multiselect('Seleccione Rango Urbano', polygons)
	#selected_polygons = st.sidebar.multiselect('Seleccione Rango Urbano', polygons)
	map_df = kml_df[kml_df['Name'].isin(selected_polygons)].reset_index(drop = True)
	map_df['STFIPS']=4
	map_df = map_df.set_crs('epsg:4326',allow_override = True)
	map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)


	#Poligono para el contador
	selected_polygon = map_df.geometry.iloc[0]
	points_inside_comuna = points_app[points_app.commune == comuna]
	#Contador de misiones dentro de la comuna
	inside_count = len(points_inside_comuna)
	points_outside_polygon = points_inside_comuna[~points_inside_comuna.geometry.within(selected_polygon)]
	outside_count = len(points_outside_polygon)
	#misiones=gpd.GeoDataFrame(data_app, geometry=gpd.points_from_xy(data_app.longitude, data_app.latitude))
	#select_polygons(polygons, misiones, comunas)
	#points_inside_comuna=gpd.GeoDataFrame(data_app, geometry=gpd.points_from_xy(data_app.longitude, data_app.latitude))






	# write GeoJSON to file
	j_file = json.loads(map_df.to_json())
	# index geojson
	i=0
	for feature in j_file["features"]:
		feature['id'] = int(i)
		i += 1



	#### MAPEO DE MISIONES Y POLIGONOS ####
	# mapbox token
	mapboxt = 'pk.eyJ1Ijoid2FsbHk5MDUiLCJhIjoiY2wwZ3V0eGRkMDJkNTNjbXE2ZHV3MGh4eiJ9.xhEsQ-nALWX3ixl8_9b9Tw'

	# define layers and plot map
	choro = go.Choroplethmapbox(z=map_df['STFIPS'], locations =
			map_df.index, colorscale = 'Greens', geojson = j_file,
			text = map_df['Name'], marker_line_width=0.8,marker_opacity=0.3)
	#choro_redzone = go.Choroplethmapbox(z=map_redzone['STFIPS'], locations =
			#map_redzone.index, colorscale = 'reds', geojson = j_file_redzone,
			#text = map_redzone['Name'], marker_line_width=0.8,marker_opacity=0.3)
	scattApp = go.Scattermapbox(name='Aprobadas',lat=LatApp, lon=LongApp,mode='markers',
			below='True', marker=dict( size=6, color ='rgb(0, 63,154)'),text=idApp)
	scattDis = go.Scattermapbox(name='Rechazadas',lat=LatDis, lon=LongDis,mode='markers',
			below='False', marker=dict( size=6, color ='rgb(255, 0,0)'),text=idDis+" "+substateDis)
	scattTaken = go.Scattermapbox(name='Asignadas Mes Curso',lat=LatTaken, lon=LongTaken,mode='markers',
		below='False', marker=dict( size=6, color ='rgb(128, 0,128)'),text = idTaken+" "+shopperTaken)
	layout = go.Layout(title_text ='Chile', title_x =0.5,
			width=1280, height=900,mapbox = dict(center= dict(lat=lat_center,
			lon=long_center),accesstoken= mapboxt, zoom=12,style="light"))

	# streamlit multiselect widget
	layer1 = st.multiselect('Layer Selection', [choro, scattApp, scattDis, scattTaken],
			format_func=lambda x: 'Polygon' if x==choro else 'Points')
	# assign Graph Objects figure
	fig = go.Figure(data=[choro,scattApp,scattDis,scattTaken], layout=layout)
	fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
	fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01))

	#display streamlit map
  #diplay el contador por zona
	#st.write('Total de misiones dentro de la comuna:', inside_count)
	#st.write('Cantidad de misiones fuera del rango urbano:', outside_count)
	#st.write(select_polygons)
	#st.write("DataFrame de conteo de puntos fuera de polígonos:")
	#st.write(counts)
	st.write('Misiones por comuna: ')
	st.write(suma_por_comuna)
	st.write('Misiones dentro del rango: ')
	st.write(result)
	
	


	fig.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01,
    title=dict(text=f"Puntos fuera del rango urbano: {outside_count}")))
	st.plotly_chart(fig,use_container_width=True)
else:
	print('error')
