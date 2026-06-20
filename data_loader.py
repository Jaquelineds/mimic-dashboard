import os

import pandas as pd
import streamlit as st

BASE_PATH = "dataset"


@st.cache_data
def load_data():
    """Lê os arquivos .csv.gz do dataset MIMIC-IV Demo e retorna os DataFrames."""
    patients = pd.read_csv(os.path.join(BASE_PATH, "hosp/patients.csv.gz"))
    admissions = pd.read_csv(os.path.join(BASE_PATH, "hosp/admissions.csv.gz"))
    labevents = pd.read_csv(os.path.join(BASE_PATH, "hosp/labevents.csv.gz"))
    prescriptions = pd.read_csv(os.path.join(BASE_PATH, "hosp/prescriptions.csv.gz"))
    d_labitems = pd.read_csv(os.path.join(BASE_PATH, "hosp/d_labitems.csv.gz"))
    return patients, admissions, labevents, prescriptions, d_labitems
