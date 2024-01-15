import sys
import os

# Obtém o caminho absoluto para o diretório raiz do projeto
root_path = os.path.abspath(os.path.dirname(__file__))

# Adiciona os diretórios relevantes ao path
sys.path.append(os.path.join(root_path, 'src'))
sys.path.append(os.path.join(root_path, 'src/extract'))
sys.path.append(os.path.join(root_path, 'src/transform'))
sys.path.append(os.path.join(root_path, 'src/load'))