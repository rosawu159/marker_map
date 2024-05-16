import streamlit as st
import leafmap.foliumap as leafmap
from pymongo import MongoClient
from folium import Icon
st.set_page_config(layout="wide")

#@st.cache_resource
#def init_connection():
#    return MongoClient("mongodb+srv://{st.secrets['db_username']}:{st.secrets['db_pswd']}@cluster0.zskuvse.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
#
#client = init_connection()
#
#@st.cache_data(ttl=600)
#def get_db():
#    db = client.admin
#    items = db.mycollection.find()
#    items = list(items)  # make hashable for st.cache_data
#    return items

# 将地标添加到数据库
def add_landmark_to_db(latitude, longitude, mood):
    db = get_db()
    db.insert_one({'latitude': latitude, 'longitude': longitude, 'mood': mood})

# 从数据库获取所有地标
def get_landmarks_from_db():
    db = get_db()
    return list(db.find({}, {'_id': 0, 'latitude': 1, 'longitude': 1, 'mood': 1}))

# 初始化地图
def init_map():
    m = leafmap.Map(center=[40, -100], zoom=4)
    return m


# Customize the sidebar
markdown = """
This is a daily.
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://cdn-icons-png.flaticon.com/512/3286/3286370.png"
st.sidebar.image(logo)

# Customize page title
st.title("將你的心情轉成旅遊計畫！")

st.markdown(
    """
    不管是什麼樣的心情，記錄下來，可以給你對應的旅遊計畫喔～
    """
)

st.header("寫下你的日記")

markdown = """
1. 寫下自己的心情，會幫你選一個國家並給你推薦的旅遊計畫

"""

st.markdown(markdown)

mood = st.text_area('請描述你的心情')
if st.button('添加心情'):
    if coordinates:
        lat, lon = [float(coord) for coord in coordinates.split(',')]
        add_landmark_to_db(lat, lon, mood)
        st.success('地標和心情已保存到数据库！')

# 显示地图和所有数据库中的地标
m = init_map()
cities = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_cities.csv"
regions = "https://raw.githubusercontent.com/giswqs/leafmap/master/examples/data/us_regions.geojson"

m.add_geojson(regions, layer_name="US Regions")
m.add_points_from_xy(
    cities,
    x="longitude",
    y="latitude",
    color_column="region",
    icon_names=["gear", "map", "leaf", "globe"],
    spin=True,
    add_legend=True,
)
m.to_streamlit(height=320)

