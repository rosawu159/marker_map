import streamlit as st
import leafmap.foliumap as leafmap
import os
import mysql.connector


# 数据库连接配置
def connect_db():
    return mysql.connector.connect( host="localhost",
                                    port="3306",
                                    user="root",
                                    passwd="",
                                    db="iam_db"
                                  )

# 将地标添加到数据库
def add_landmark_to_db(latitude, longitude, mood):
    conn = connect_db()
    cursor = conn.cursor()
    query = "INSERT INTO landmarks (latitude, longitude, mood) VALUES (%s, %s, %s)"
    cursor.execute(query, (latitude, longitude, mood))
    conn.commit()
    conn.close()

# 从数据库获取所有地标
def get_landmarks_from_db():
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT latitude, longitude, mood FROM landmarks"
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result

st.set_page_config(layout="wide")

# Customize the sidebar
markdown = """
This is about
"""

st.sidebar.title("About")
st.sidebar.info(markdown)
logo = "https://cdn-icons-png.flaticon.com/512/3286/3286370.png"
st.sidebar.image(logo)

# Customize page title
st.title("Streamlit for Geospatial Applications")

st.markdown(
    """
    This multipage app template demonstrates various interactive web apps created using [streamlit](https://streamlit.io) and [leafmap](https://leafmap.org). It is an open-source project and you are very welcome to contribute to the [GitHub repository](https://github.com/opengeos/streamlit-map-template).
    """
)

st.header("Instructions")

markdown = """
1. For the [GitHub repository](https://github.com/opengeos/streamlit-map-template) or [use it as a template](https://github.com/opengeos/streamlit-map-template/generate) for your own project.
2. Customize the sidebar by changing the sidebar text and logo in each Python files.
3. Find your favorite emoji from https://emojipedia.org.
4. Add a new app to the `pages/` directory with an emoji in the file name, e.g., `1_🚀_Chart.py`.

"""

st.markdown(markdown)

m = leafmap.Map(center=[40, -100], zoom=4)

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

# Streamlit 互動組件
coordinates = st.text_input('請輸入地標坐標 (格式如 40,-100)')
mood = st.text_input('請描述你的心情')
if st.button('添加地標'):
    if coordinates:
        lat, lon = [float(coord) for coord in coordinates.split(',')]
        add_landmark_to_db(lat, lon, mood)
        st.success('地標和心情已保存到数据库！')
landmarks = get_landmarks_from_db()
for lat, lon, mood in landmarks:
    m.add_marker(location=(lat, lon), popup=f'心情: {mood}')



m.to_streamlit(height=320)



# Everything is accessible via the st.secrets dict:
st.write("My cool secrets:", st.secrets["my_cool_secrets"]["things_i_like"])

# And the root-level secrets are also accessible as environment variables:
st.write(
    "Has environment variables been set:",
    os.environ["db_username"] == st.secrets["db_username"],
)
