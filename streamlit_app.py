import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

docentes_url = 'https://www.dropbox.com/scl/fi/ub2g0606rmqu4ykn4ef15/Docentes.csv?rlkey=3v26fp1cp4tjam3j7si17f5e2&st=aea42d23&dl=1'
docentes_auto_url = 'https://www.dropbox.com/scl/fi/o7fhl9bvp1ey89qdwworu/Docentes-Autoadministrada.csv?rlkey=0a8a8gg61eus8bssvilievbkk&st=86wyxizg&dl=1'

docentes = pd.read_csv(docentes_url)
docentes_auto = pd.read_csv(docentes_auto_url)

data = pd.concat([docentes, docentes_auto])

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="High Frequency Checks Dashboard",
    layout="wide"
)

# Título de la aplicación
st.title("High Frequency Checks Dashboard")

# Columnas relevantes
col = ['SubmissionDate', 'starttime', 'endtime', 'duration',
        'encuestador', 'encuestador_other', 'docente',
        'docente_int_dui', 'docente_int_tel', 'docente_int_correo']

# Dividir las variables en módulos
modules = {
    "Modulo A": [col for col in data.columns if col.startswith('ma_')],
    "Modulo B": [col for col in data.columns if col.startswith('mb_')],
    "Modulo C": [col for col in data.columns if col.startswith('mc_')],
    "Modulo D": [col for col in data.columns if col.startswith('md_')],
    "Modulo E": [col for col in data.columns if col.startswith('me_')],
    "Modulo F": [col for col in data.columns if col.startswith('mf_')],
    "Modulo G": [col for col in data.columns if col.startswith('mg_')]
}

def display_category_percentages(df, variables):
    category_counts = {}
    for var in variables:
        if df[var].dtype in [np.float64, np.int64] or df[var].dtype == 'float64':
            counts = df[var].value_counts(normalize=True) * 100
            category_counts[var] = counts
    category_counts_df = pd.DataFrame(category_counts).transpose()
    category_counts_df.fillna(0, inplace=True)
    return category_counts_df

def display_descriptive_stats(df, variables):
    descriptive_stats = df[variables].describe().transpose()
    return descriptive_stats

# Crear pestañas en Streamlit
tabs = st.tabs(["General", "Missing Values"] + list(modules.keys()))

with tabs[0]:
    # Mostrar los datos en una tabla
    st.write("Datos cargados:")
    st.write(data[col])

    # Verificación 1: Duración de las entrevistas
    data['starttime'] = pd.to_datetime(data['starttime'], format='%d/%m/%Y, %H:%M:%S', errors='coerce')
    data['endtime'] = pd.to_datetime(data['endtime'], format='%d/%m/%Y, %H:%M:%S', errors='coerce')
    data['duration'] = (data['endtime'] - data['starttime']).dt.total_seconds() / 60  # Duración en minutos
    duration_check = data[(data['duration'] < 2) | (data['duration'] > 60)]
    st.write("Entrevistas con duración fuera del rango razonable (2 min - 1 hr):")
    st.write(duration_check[col])

    # Verificación 2: Duplicados
    duplicate_check = data[data['docente'].duplicated(keep=False)]
    st.write("Registros duplicados:")
    st.write(duplicate_check[col])

with tabs[1]:
    # Analizar valores faltantes
    st.write("Análisis de Valores Faltantes")

    missing_values = data.isnull().sum()
    missing_percentage = (missing_values / len(data)) * 100
    missing_data = pd.DataFrame({'Total Missing': missing_values, 'Percentage Missing': missing_percentage})

    st.write("Tabla de valores faltantes:")
    st.write(missing_data)

    # Mostrar gráfico de valores faltantes
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x=missing_data.index, y=missing_data['Total Missing'], ax=ax)
    plt.xticks(rotation=90)
    plt.ylabel("Número de valores faltantes")
    plt.title("Valores faltantes por variable")
    st.pyplot(fig)

# Crear pestañas para cada módulo
for i, module in enumerate(modules.keys(), 2):
    with tabs[i]:
        st.write(f"Análisis de Valores Faltantes en {module}")

        variables = modules[module]
        module_missing_values = data[variables].isnull().sum()
        module_missing_percentage = (module_missing_values / len(data)) * 100
        module_missing_data = pd.DataFrame({'Total Missing': module_missing_values, 'Percentage Missing': module_missing_percentage})

        st.write(f"Tabla de valores faltantes en {module}:")
        st.write(module_missing_data)

        # Mostrar tabla de porcentajes para variables categóricas con menos de 5 categorías
        category_counts = display_category_percentages(data, variables)
        st.write("Porcentajes de respuestas categóricas:")
        st.write(category_counts)

        # Descriptive statistics for numerical variables
        descriptive_stats = display_descriptive_stats(data, variables)
        st.write("Estadísticas descriptivas:")
        st.write(descriptive_stats)

