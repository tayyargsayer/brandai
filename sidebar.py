import streamlit as st
from curator import *
import pandas as pd
def sidebar():

    st.sidebar.title("Machinho Assistans")
    st.sidebar.subheader("Datalarin yuklenmesi biraz zaman alabilir. Lutfen bekleyin.")

    machine_names = [""] + machines()
    selected_machine = st.sidebar.selectbox("Hangi Makine Grubunu İstiyorsun?", machine_names)
    machine_data = machine_datas(selected_machine)

    @st.cache_data
    def get_machine_data(machine_name):
        return machine_datas(machine_name)

    @st.cache_data
    def get_brand_names(machine_data):
        return machine_data["Manufacturer"].unique()

    # Initialize selected_machine, machine_data, and selected_brands to default values
    selected_machine = ""
    machine_data = pd.DataFrame()
    selected_brands = []

    if selected_machine:
        st.text_input("Sorunu gonder gelsin")

        machine_data = get_machine_data(selected_machine)
        brand_names = get_brand_names(machine_data)

        selected_brands = st.sidebar.multiselect("Hangi Markayı İstiyorsun?", brand_names)

    st.sidebar.checkbox("Asistanım inisiyatif alabilsin ve harici makineleri ekleyebilsin.", key="inisiyatif")

    return selected_machine, machine_data, selected_brands
