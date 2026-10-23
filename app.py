import streamlit as st

from relatorio_facil import render_report, summarize_csv_text


st.set_page_config(page_title="Relatório Fácil", page_icon="📊", layout="centered")
st.markdown("""
<style>
.stApp {background: #f4f7fa;}
[data-testid="stHeader"] {background: rgba(0,0,0,0);}
.block-container {max-width: 850px; padding-top: 3rem;}
h1 {color: #145b53; letter-spacing: -1px;}
.hero {color: #566575; font-size: 1.12rem; max-width: 680px;}
.stDownloadButton button {background:#145b53;color:white;border:0;border-radius:9px;padding:.7rem 1.2rem;}
</style>
""", unsafe_allow_html=True)

st.title("Seu resumo de vendas, sem montar planilha")
st.markdown('<p class="hero">Envie um CSV e receba um relatório com faturamento total, vendas por produto e dados que precisam de revisão.</p>', unsafe_allow_html=True)
st.caption("O arquivo é processado durante esta sessão e não é armazenado pelo aplicativo.")

with st.expander("Formato necessário", expanded=True):
    st.write("O CSV deve ter as colunas `data`, `produto`, `quantidade` e `valor_unitario`. Data no formato AAAA-MM-DD. Preços aceitam vírgula decimal.")
    with open("vendas_exemplo.csv", "rb") as example:
        st.download_button("Baixar CSV de exemplo", example, file_name="vendas_exemplo.csv", mime="text/csv")

upload = st.file_uploader("Escolha sua planilha exportada como CSV", type=["csv"], max_upload_size=10)
if upload:
    try:
        content = upload.getvalue().decode("utf-8-sig")
        totals, count, errors = summarize_csv_text(content)
        report = render_report(totals, count, errors, upload.name)
        total_value = sum(totals.values())
        money = f"R$ {total_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        col1, col2, col3 = st.columns(3)
        col1.metric("Vendas válidas", count)
        col2.metric("Faturamento", money)
        col3.metric("Produtos", len(totals))
        st.success("Relatório pronto para baixar.")
        st.download_button("Baixar relatório HTML", report.encode("utf-8"), file_name="relatorio_vendas.html", mime="text/html", type="primary")
        if errors:
            st.warning(f"{len(errors)} linha(s) precisam de revisão. Os detalhes aparecem no relatório baixado.")
    except (UnicodeDecodeError, ValueError) as error:
        st.error(f"Não consegui ler esse arquivo: {error}")

st.divider()
st.caption("Ferramenta demonstrativa gratuita. Confira os dados de origem antes de tomar decisões financeiras.")
