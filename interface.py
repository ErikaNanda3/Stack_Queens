import streamlit as st
import pandas as pd
from Back import LerPlanilha, Demanda, GeradorFichaPO

st.set_page_config(page_title="Auto-T&M Karsten", layout="wide")

st.title("Auto-T&M Karsten - Formação de Ficha PO")
st.caption("Engenharia de Tempos e Métodos • Stake Queens")

leitor = LerPlanilha("Entradas.ods")

col_esq, col_dir = st.columns([1, 1.2], gap="large")

with col_esq:
    st.subheader("1. Parâmetros de Entrada")
    
    with st.expander("Dados do Produto", expanded=True):
        c1, c2 = st.columns([2, 1])
        titulo_po = c1.text_input("Título da PO", "PO-SL-001")
        rev = c2.text_input("Revisão", "00")
        
        operacao = st.text_input("Operação", "Bainhar no corpo do SL - 1 lado")
        
        c3, c4 = st.columns(2)
        nome_produto = c3.text_input("Família / Peça", "Sobre-lençol")
        tamanho = c4.text_input("Tamanho", "Solteiro")
        
        medidas = st.text_input("Medidas da Peça (m)", "1,80 x 2,50")
        
        c5, c6 = st.columns(2)
        perimetro = c5.number_input("Perímetro de Costura (m)", min_value=0.0, value=6.96, step=0.1)
        densidade = c6.number_input("Pontos / cm", min_value=0.0, value=2.5, step=0.5)

    with st.expander("Equipamento (Máquinas)", expanded=True):
        maquinas_dict = {}
        for cod, maq in leitor.maquinas.items():
            maquinas_dict[f"{cod} - {maq.nome} ({maq.tempo_por_metro:.4f} min/m)"] = cod
            
        maq_escolhida = st.selectbox("Selecione a Máquina", list(maquinas_dict.keys()))
        cod_eqp = maquinas_dict[maq_escolhida]

    with st.expander("Sequência MTM", expanded=True):
        roteiro = st.text_input("Códigos MTM", "2.1, 1.1, 3.1")
        
        arq = st.file_uploader("Subir demanda (.txt)", type=["txt"])
        if arq:
            linhas = arq.getvalue().decode("utf-8").splitlines()
            for l in linhas:
                if "Elementos:" in l:
                    roteiro = l.split(":", 1)[1].strip()

    btn_gerar = st.button("Gerar Ficha PO", type="primary", use_container_width=True)

with col_dir:
    st.subheader("2. Ficha de Processo Operacional (PO)")
    
    if btn_gerar:
        elementos = [x.strip() for x in roteiro.split(",") if x.strip()]
        
        demanda = Demanda(
            titulo=titulo_po,
            rev=rev,
            operacao=operacao,
            agrupamento_familia=nome_produto,
            tamanho=tamanho,
            medidas=medidas,
            pontos_cm=densidade,
            perimetro_costura=perimetro,
            cod_eqp=cod_eqp,
            elementos=elementos
        )
        
        gerador = GeradorFichaPO(demanda, leitor)
        res = gerador.calcular_e_estruturar()
        
        t_fixo = res["elementos"][0]["tempo_min"]
        t_total = res["totais"]["tempo_total_min"]
        t_mtm = round(t_total - t_fixo, 4)
        
        st.success(f"{nome_produto} ({tamanho}) | {operacao} | {res['equipamento']['nome']}")
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tempo FIXO", f"{t_fixo:.4f} min")
        m2.metric("Tempo MTM", f"{t_mtm:.4f} min")
        m3.metric("Tempo Total", f"{t_total:.4f} min")
        m4.metric("Tempo em Horas", f"{res['totais']['tempo_total_horas']:.5f} h")
        
        st.write("### Elementos da Operação")
        
        cols = st.columns(len(res["elementos"]))
        for i, item in enumerate(res["elementos"]):
            with cols[i]:
                with st.container(border=True):
                    st.caption(f"Código {item['codigo']}")
                    st.markdown(f"**{item['descricao']}**")
                    st.write(f"{item['tempo_min']:.4f} min")
                    pct = round((item["tempo_min"] * item["frequencia"] / t_total) * 100, 1) if t_total > 0 else 0
                    st.progress(pct / 100, text=f"{pct}%")
        
        st.write("### Detalhamento da PO")
        
        tabela = []
        for i, item in enumerate(res["elementos"]):
            tabela.append({
                "Seq": i,
                "Código MTM": item["codigo"],
                "Descrição": item["descricao"],
                "Tipo": "Costura" if item["codigo"] == "FIXO" else "Manual",
                "Freq": item["frequencia"],
                "Tempo (min)": item["tempo_min"]
            })
            
        df = pd.DataFrame(tabela)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        c_down1, c_down2 = st.columns(2)
        c_down1.download_button(
            "Exportar CSV",
            df.to_csv(index=False).encode("utf-8"),
            f"PO_{titulo_po}.csv",
            "text/csv",
            use_container_width=True
        )
        
        nome_excel = f"{titulo_po}_Gerada.xlsx"
        gerador.exportar_excel(nome_excel)
        with open(nome_excel, "rb") as f:
            c_down2.download_button(
                "Exportar Excel (.xlsx)",
                f.read(),
                nome_excel,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.info("Preencha os campos ao lado e clique em **Gerar Ficha PO**.")
