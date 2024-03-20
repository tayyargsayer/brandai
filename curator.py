import streamlit as st


def machines():

    machine_names = [
        "Backhoe Loader",
        "Compact Tracked Loader",
        "Mini Excavator",
        "Skid Steer Loader",
        "Telehandler",
        "Tracked Excavator",
        "Wheeled Excavator",
        "Wheeled Loader"
    ]

    return machine_names

@st.cache_data
def machine_datas(machine_type):
    import pandas as pd

    if machine_type == "":
        return pd.DataFrame()

    machine_data = {
        "Backhoe Loader": pd.read_excel('data/yellowbook_backhoe-loaders_26-02-2024.xlsx'),
        "Compact Tracked Loader": pd.read_excel('data/yellowbook_compact-tracked-loaders_26-02-2024.xlsx'),
        "Mini Excavator": pd.read_excel('data/yellowbook_mini-excavators_26-02-2024.xlsx'),
        "Skid Steer Loader": pd.read_excel('data/yellowbook_skid-steer-loaders_26-02-2024.xlsx'),
        "Telehandler": pd.read_excel('data/yellowbook_telehandler_26-02-2024.xlsx'),
        "Tracked Excavator": pd.read_excel('data/yellowbook_tracked-excavators_26-02-2024.xlsx'),
        "Wheeled Excavator": pd.read_excel('data/yellowbook_wheeled-excavators_26-02-2024.xlsx'),
        "Wheeled Loader": pd.read_excel('data/yellowbook_wheeled-loaders_26-02-2024.xlsx')
    }

    return machine_data[machine_type]










