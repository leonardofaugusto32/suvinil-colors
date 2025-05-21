import streamlit as st
import io
from olho_da_mel import parse_rgb, find_similar_colors, create_color_visualization
import json

# Configuração da página
st.set_page_config(
    page_title="👁️ OLHO DA MEL - Cores Similares Suvinil",
    page_icon="👁️",
    layout="wide"
)

# Título e descrição
st.title("👁️ OLHO DA MEL - Encontrar Cores Similares Suvinil")
st.write("Digite os valores RGB para encontrar cores similares na paleta Suvinil")

# Input dos valores RGB
col1, col2, col3 = st.columns(3)
with col1:
    r = st.number_input("R", min_value=0, max_value=255, value=158)
with col2:
    g = st.number_input("G", min_value=0, max_value=255, value=76)
with col3:
    b = st.number_input("B", min_value=0, max_value=255, value=29)

# Botão para buscar cores similares
if st.button("Buscar Cores Similares"):
    try:
        # Carregar dados das cores
        with open('suvinil_colors.json', 'r', encoding='utf-8') as f:
            colors_data = json.load(f)
        
        # Encontrar cores similares
        target_rgb = (r, g, b)
        similar_colors = find_similar_colors(target_rgb, colors_data)
        
        # Criar visualização
        img_bytes = io.BytesIO()
        create_color_visualization(target_rgb, similar_colors, img_bytes=img_bytes)
        img_bytes.seek(0)
        
        # Mostrar resultados
        st.subheader("Cores mais próximas encontradas:")
        
        # Centralizar a imagem usando colunas
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Mostrar a imagem com largura fixa
            st.image(img_bytes, use_container_width=False)
        
        # Mostrar detalhes em uma tabela
        results = []
        for color in similar_colors:
            results.append({
                "Nome": color['name'],
                "Código": color['code'],
                "RGB": color['rgb'],
                "Distância": f"{color['distance']:.2f}"
            })
        
        st.table(results)
        
    except FileNotFoundError:
        st.error("Erro: Arquivo suvinil_colors.json não encontrado. Execute primeiro o script try.py para gerar o arquivo de cores.")
    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")

# Adicionar informações no rodapé
st.markdown("---")
st.markdown("Desenvolvido com ❤️ para ajudar na escolha de cores Suvinil")
