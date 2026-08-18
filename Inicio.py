import sys
import os

# Ponto de entrada sem acentuação para compatibilidade com a configuração do Streamlit Cloud
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

with open(os.path.join(os.path.dirname(__file__), "Início.py"), encoding="utf-8") as f:
    code = compile(f.read(), "Início.py", "exec")
    exec(code, globals())
