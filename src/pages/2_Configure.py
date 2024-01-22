import streamlit as st
import configparser
import os

# Configura os paths dos arquivos que serão utilizados
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PATH_TO_CONFIG_FILE = os.path.join(ROOT_DIR, 'config.ini')

# Função para ler as configurações do arquivo config.ini
config = configparser.ConfigParser()
config.read(PATH_TO_CONFIG_FILE)
toggles = config['Toggle']

# Retorna o valor booleano de um toggle a partir de seu nome
def bool_for_toggle(toggle_name):
    value = toggles.get(toggle_name)
    if value == "true":
        return True
    elif value == "false":
        return False

# Faz com que o layout da página ocupe todo o espaço em tela
st.set_page_config(layout="wide")

# Título da página
st.title('Configuration')

# Declara as 4 colunas
col1, col2, col3, col4 = st.columns(4)

# Declara lista de toggles da página
page_toggles = []

# Coluna 1: Geral
with col1:
    st.header('General')

    st.subheader('Log level')
    
    label = 'Verbose Mode'
    key = 'verbose'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)
    
    st.subheader('Categorization')
    
    label = 'Simple Match'
    key = 'simple_match'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Similar Match'
    key = 'similar_match'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'AI Match'
    key = 'ai_match'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Update categories from history'
    key = 'load_xlsx'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

# Coluna 2: Extract
with col2:
    st.header('Extract')

    st.subheader('Cards')

    label = 'BTG'
    key = 'toggle_extract_btg'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Flash'
    key = 'toggle_extract_flash'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'GPA'
    key = 'toggle_extract_gpa'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'XP'
    key = 'toggle_extract_xp'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key), disabled=True)
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    st.subheader('Accounts')

    label = 'Itaú'
    key = 'toggle_extract_itau_cc'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    st.subheader('Investments')

    label = 'BTG Invest.'
    key = 'toggle_extract_btg_ci'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key), disabled=True)
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Rico Invest.'
    key = 'toggle_extract_rico_ci'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key), disabled=True)
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Sofisa Invest.'
    key = 'toggle_extract_sofisa_ci'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key), disabled=True)
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'XP Invest.'
    key = 'toggle_extract_xp_ci'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key), disabled=True)
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

# Coluna 3: Transform
with col3:
    st.header('Transform')

    st.subheader('Cards')

    label = 'BTG'
    key = 'toggle_transform_btg'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Flash'
    key = 'toggle_transform_flash'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'GPA'
    key = 'toggle_transform_gpa'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'XP'
    key = 'toggle_transform_xp'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    st.subheader('Accounts')

    label = 'Itaú'
    key = 'toggle_transform_itau_cc'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    st.subheader('Investments')

    label = 'BTG Invest.'
    key = 'toggle_transform_btg_ci'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Rico Invest.'
    key = 'toggle_transform_rico_ci'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Sofisa Invest.'
    key = 'toggle_transform_sofisa_ci'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'XP Invest.'
    key = 'toggle_transform_xp_ci'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

# Coluna 4: Load
with col4:
    st.header('Load')

    st.subheader('Excel')

    label = 'Temp Sheet'
    key = 'toggle_temp_sheet'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Final Sheet'
    key = 'toggle_final_sheet'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key), disabled=True)
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Save from DB to Excel'
    key = 'toggle_dump_history'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    st.subheader('Database')

    label = 'Load Excel in DB'
    key = 'toggle_load_history'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)

    label = 'Store parsed data in DB'
    key = 'toggle_db'
    st_toggle = st.toggle(label, key=key, value=bool_for_toggle(key))
    toggle = {'key': key, 'st_toggle': st_toggle}
    page_toggles.append(toggle)



# Função para salvar as configurações de volta ao arquivo
def salvar_configuracoes(config):
    with open(PATH_TO_CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
        
# Botão Executar
if st.button('Salvar'):

    for toggle in page_toggles:

        if config.has_option('Toggle', toggle['key']):
            if toggle['st_toggle']:
                new_value = 'true'
            else:
                new_value = 'false'
            config.set('Toggle', toggle['key'], new_value)
        salvar_configuracoes(config)

    st.write('Configurações salvas!')