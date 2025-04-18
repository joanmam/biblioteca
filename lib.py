import streamlit as st
import requests
import pandas as pd
import sqlitecloud
from altres.variables import cami_db
import openpyxl


st.set_page_config(layout="wide")

conn = sqlitecloud.connect(cami_db)
cursor = conn.cursor()



# Carregar el fitxer Excel
excel_file = "altres/Biblioteca2.xlsx"
df = pd.read_excel(excel_file, sheet_name="HandyLib-17Apr25")



# Carregar les dades existents a la taula SQL
sqlite_query = "SELECT * FROM llibres"
sqlite_df = pd.read_sql(sqlite_query, conn)



# Comparar les dues taules
if df.equals(sqlite_df):
    st.write("No hi ha diferències. No cal actualitzar la taula SQL.")
else:
    st.write("Actualitzant la taula SQL...")
    cursor.execute("DROP TABLE IF EXISTS Llibres")
    df.to_sql('llibres', conn, if_exists='replace', index=False)



# User input for filtering
author_filter = st.text_input("🔎 Entra un nom d'autor:", "")
# url_filter = st.text_input("🔎 Entra un nom d'url:", "")
if st.button("Buscar"):

    # Fetch data with correct pagination in SQLiteCloud
    query = f'SELECT "Id", ISBN, ImageUrl, ItemUrl, Title, Author, Bookshelf FROM llibres WHERE Author COLLATE NOCASE LIKE "%{author_filter}%"'
    # query2 = f'SELECT "Id", ISBN, ImageUrl, ItemUrl, Title, Author, Bookshelf FROM llibres WHERE ItemUrl COLLATE NOCASE LIKE "%{url_filter}%"'
    select_df = pd.read_sql(query, conn)
    # select_df2 = pd.read_sql(query2, conn)
    num_registres = len(select_df)
    # num_registres2 = len(select_df2)
    st.write(f"Tenim **{num_registres}** registres")
    # st.write(f"Tenim **{num_registres2}** registres")

    select_df['ISBN'] = select_df['ISBN'].fillna(0).astype('Int64')  # Allows nullable integers
    select_df['OpenLib'] = select_df['ISBN'].apply(lambda isbn: f"https://openlibrary.org/isbn/{isbn}" if pd.notna(isbn) else "")
    select_df['OpenLib2'] = select_df['ISBN'].apply(
        lambda isbn: f"https://www.librarything.com/isbn/{isbn}" if pd.notna(isbn) else "")
    column_order = ["ImageUrl", "ISBN", "Id", "Title", "Author", "BookShelf", "OpenLib", "OpenLib2"]
    select_df = select_df[column_order]


    select_df = st.dataframe(
        select_df,
        column_config={
            "ImageUrl": st.column_config.ImageColumn(
                label="Image", width="medium"
            ),
            "ISBN": st.column_config.NumberColumn(
                label="ISBN",
            ),
            "Id": st.column_config.NumberColumn(
                label="ID",
            ),
            "Title": st.column_config.TextColumn(
                label="Titol",
            ),
            "Author": st.column_config.TextColumn(
                label="Autor",
            ),
            "BookShelf": st.column_config.TextColumn(
                label="Estante",
            ),
            "OpenLib": st.column_config.LinkColumn(
                label="Link", display_text="Open Link"
            ),
            "OpenLib2": st.column_config.LinkColumn(
                label="Link2", display_text="LibThing"
            ),
        },
        hide_index=True, use_container_width=False, row_height=100)


