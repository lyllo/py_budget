import streamlit as st
from subprocess import Popen, PIPE, STDOUT
import os

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

IMG_DIR = os.path.join(ROOT_DIR, 'img\\')

st.set_page_config(layout="centered")

# Título da página
st.title('Update')

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

with col1:
    st.image(os.path.join(IMG_DIR, 'golden_source-white.svg'), caption="Source")

# with col2:
#     st.image(os.path.join(IMG_DIR, 'progress.gif'), use_column_width=True)

with col3:
    st.image(os.path.join(IMG_DIR, 'local_file-white.svg'), caption="Local File")

# with col4:
#     st.image(os.path.join(IMG_DIR, 'progress-still.png'))

with col5:
    st.image(os.path.join(IMG_DIR, 'transform-white.svg'), caption="Transform")

# with col6:
#     st.image(os.path.join(IMG_DIR, 'progress-still.png'))

with col7:
    st.image(os.path.join(IMG_DIR, 'database-white.svg'), caption="Database")

# Criar um botão no Streamlit
if st.button("Clique para executar o script"):
    # Substitua 'seu_arquivo.py' pelo nome do seu arquivo Python
    nome_do_arquivo = 'main.py'

    # Comando para executar o script Python com o argumento -u para desativar o buffering
    comando = f'python -u {nome_do_arquivo}'

    # Usar subprocess.Popen para capturar a saída em tempo real
    with Popen(comando, shell=True, stdout=PIPE, stderr=STDOUT, bufsize=1, text=True, universal_newlines=True) as process:
        with st.container(height=300):
            for line in process.stdout:
                st.markdown(line.strip())