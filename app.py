import streamlit as st
import json
from PIL import Image
import io
from olho_da_mel import parse_rgb, find_similar_colors, create_color_visualization

# Configuração da página
st.set_page_config(
    page_title="👁️ Olho da Mel - Encontrar Cores Suvinil",
    page_icon="👁️",
    layout="wide"
)

# Título e descrição
st.title("👁️ Olho da Mel - Encontrar Cores Suvinil")
st.markdown("""
    Encontre as cores Suvinil mais próximas da sua cor desejada!
    
    Você pode:
    * Inserir valores RGB manualmente
    * Usar o seletor de cores
""")

# Carregar dados das cores
@st.cache_data
def load_color_data():
    with open('suvinil_colors.json', 'r', encoding='utf-8') as f:
        return json.load(f)

try:
    colors_data = load_color_data()
except FileNotFoundError:
    st.error("Arquivo de cores não encontrado. Por favor, execute o script try.py primeiro.")
    st.stop()

# Sidebar com opções de entrada
st.sidebar.title("Escolha sua cor")
input_method = st.sidebar.radio(
    "Como você quer informar a cor?",
    ["Seletor de Cores", "Valores RGB"]
)

target_rgb = None

if input_method == "Seletor de Cores":
    color = st.sidebar.color_picker("Escolha uma cor", "#9E4C1D")  # Cor padrão (Pecan Pie)
    # Converter hex para RGB
    target_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
else:
    col1, col2, col3 = st.sidebar.columns(3)
    r = col1.number_input("R", 0, 255, 158)  # Valor padrão do Pecan Pie
    g = col2.number_input("G", 0, 255, 76)
    b = col3.number_input("B", 0, 255, 29)
    target_rgb = (r, g, b)

# Mostrar a cor selecionada
st.sidebar.markdown("### Cor Selecionada")
st.sidebar.markdown(
    f'<div style="background-color: rgb{target_rgb}; height: 50px; border-radius: 5px;"></div>',
    unsafe_allow_html=True
)
st.sidebar.markdown(f"RGB: {target_rgb}")

# Botão para encontrar cores similares
if st.sidebar.button("Encontrar Cores Similares"):
    # Encontrar cores similares
    similar_colors = find_similar_colors(target_rgb, colors_data)
    
    # Criar visualização
    img_bytes = io.BytesIO()
    create_color_visualization(target_rgb, similar_colors, output_file=None, img_bytes=img_bytes)
    img_bytes.seek(0)
    
    # Mostrar resultados
    st.markdown("## Cores Similares Encontradas")
    
    # Mostrar a imagem
    st.image(img_bytes, use_column_width=True)
    
    # Mostrar detalhes em uma tabela
    st.markdown("### Detalhes das Cores")
    for color in similar_colors:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(
                f'<div style="background-color: rgb{color["rgb"]}; height: 50px; border-radius: 5px;"></div>',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(f"""
                **Nome:** {color['name']}  
                **Código:** {color['code']}  
                **RGB:** {color['rgb']}  
                **Distância:** {color['distance']:.2f}
            """)

# Footer
st.markdown("---")
st.markdown("Desenvolvido com ❤️ por Mel") 