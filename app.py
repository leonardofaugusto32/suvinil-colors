import streamlit as st
import io
from olho_da_mel import parse_rgb, find_similar_colors
import json

# Configuração da página
st.set_page_config(
    page_title="OLHO MÍOPE DA MEL - Cores Similares Suvinil",
    page_icon="👁️",
    layout="wide"
)

# Estilo CSS para os blocos de cor
st.markdown("""
<style>
.color-block {
    width: 100%;
    height: 120px;
    border-radius: 8px;
    margin-bottom: 8px;
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.color-block:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.color-info {
    text-align: center;
    margin-bottom: 24px;
    padding: 0 10px;
}

.color-info strong {
    display: block;
    margin-bottom: 4px;
    font-size: 1.1em;
}

.color-metrics {
    font-size: 0.9em;
    color: #666;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .color-block {
        height: 100px;
    }
    .color-info {
        font-size: 0.9em;
    }
}
</style>
""", unsafe_allow_html=True)

# Título e descrição
st.title("OLHO MÍOPE DA MEL - Encontrar Cores Similares Suvinil")
st.write("Cansado de ser mais indeciso que o Phil na hora de escolher cores de parede? Utilize o OLHO MÍOPE DA MEL e evite deixar sua casa mais assombrosa que a criaça do cemitério.")

# Adicionar instruções
st.markdown("""
### Como usar:
1. Digite os valores RGB (0-255) para cada componente de cor
2. Clique em "Buscar Cores Similares"
3. Veja as cores Suvinil mais próximas à sua cor desejada

💡 **Dica:** Você pode usar ferramentas como o Color Picker do seu sistema ou sites de cores para encontrar os valores RGB da cor que deseja.
""")

# Container para os inputs
with st.container():
    st.subheader("Valores RGB")
    col1, col2, col3 = st.columns(3)
    with col1:
        r = st.number_input("Vermelho (R)", min_value=0, max_value=255, value=158, help="Valor entre 0 e 255 para o componente vermelho")
    with col2:
        g = st.number_input("Verde (G)", min_value=0, max_value=255, value=76, help="Valor entre 0 e 255 para o componente verde")
    with col3:
        b = st.number_input("Azul (B)", min_value=0, max_value=255, value=29, help="Valor entre 0 e 255 para o componente azul")

# Preview da cor selecionada
st.markdown(f"""
<div style='
    background-color: rgb({r},{g},{b}); 
    width: 100px; 
    height: 50px; 
    border-radius: 8px;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
'>
</div>
""", unsafe_allow_html=True)

# Botão para buscar cores similares
if st.button("Buscar Cores Similares", type="primary"):
    try:
        # Carregar dados das cores
        with open('suvinil_colors.json', 'r', encoding='utf-8') as f:
            colors_data = json.load(f)
        
        # Encontrar cores similares
        target_rgb = (r, g, b)
        similar_colors = find_similar_colors(target_rgb, colors_data)
        
        # Mostrar resultados
        st.subheader("Cores mais próximas encontradas:")
        
        # Criar grid de cores (2 colunas)
        cols = st.columns(2)
        
        # Mostrar cor original
        with cols[0]:
            st.markdown(f"""
            <div class='color-block' style='background-color: rgb{target_rgb}'></div>
            <div class='color-info'>
                <strong>Cor Original</strong>
                <div class='color-metrics'>
                    RGB{target_rgb}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar primeira cor similar
        with cols[1]:
            color = similar_colors[0]
            rgb_values = parse_rgb(color["rgb"])
            st.markdown(f"""
            <div class='color-block' style='background-color: rgb{rgb_values}'></div>
            <div class='color-info'>
                <strong>{color["name"]} ({color["code"]})</strong>
                <div class='color-metrics'>
                    {color["rgb"]}<br>
                    Distância: {color["distance"]:.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Mostrar as outras cores similares em pares
        for i in range(1, len(similar_colors), 2):
            col1, col2 = st.columns(2)
            
            # Cor da esquerda
            with col1:
                color = similar_colors[i]
                rgb_values = parse_rgb(color["rgb"])
                st.markdown(f"""
                <div class='color-block' style='background-color: rgb{rgb_values}'></div>
                <div class='color-info'>
                    <strong>{color["name"]} ({color["code"]})</strong>
                    <div class='color-metrics'>
                        {color["rgb"]}<br>
                        Distância: {color["distance"]:.2f}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Cor da direita (se existir)
            if i + 1 < len(similar_colors):
                with col2:
                    color = similar_colors[i + 1]
                    rgb_values = parse_rgb(color["rgb"])
                    st.markdown(f"""
                    <div class='color-block' style='background-color: rgb{rgb_values}'></div>
                    <div class='color-info'>
                        <strong>{color["name"]} ({color["code"]})</strong>
                        <div class='color-metrics'>
                            {color["rgb"]}<br>
                            Distância: {color["distance"]:.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.error("Erro: Arquivo suvinil_colors.json não encontrado. Execute primeiro o script try.py para gerar o arquivo de cores.")
    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")

# Adicionar informações no rodapé
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Desenvolvido com ❤️ e um pouquinho de sacanagem para ajudar na escolha de cores Suvinil</p>
    <p style='font-size: 0.9em;'>
        Este é um projeto independente e não tem vínculo oficial com a Suvinil.<br>
        As cores são apenas referência e podem variar dependendo do dispositivo e condições de visualização.
    </p>
    <p style='font-size: 0.8em;'>
        Sugestões ou problemas? 
        <a href="https://github.com/yourusername/suvinil-colors/issues" target="_blank">Abra uma issue no GitHub</a>
    </p>
</div>
""", unsafe_allow_html=True)
