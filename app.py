from __future__ import annotations

import hashlib
import html
import uuid
from decimal import Decimal

import streamlit as st
from urllib.error import HTTPError, URLError

from billing import PREMIUM_PRICE, approved_payment, compare_report, create_checkout
from relatorio_facil import brl, summarize_csv_text


APP_URL = "https://relatorio-facil-pf8fkbysecxhwesvy9dgmh.streamlit.app"
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


def csv_summary(uploaded_file):
    raw = uploaded_file.getvalue()
    text = raw.decode("utf-8-sig")
    totals, count, errors = summarize_csv_text(text)
    return {"name": uploaded_file.name, "raw": raw, "totals": totals, "count": count, "errors": errors}


def get_access_token():
    try:
        token = st.secrets.get("MERCADOPAGO_ACCESS_TOKEN", "")
    except (FileNotFoundError, KeyError):
        token = ""
    return token.strip() if isinstance(token, str) else ""


def resolve_returned_payment(access_token):
    order = st.session_state.get("premium_order")
    payment_id = st.query_params.get("payment_id")
    external_ref = st.query_params.get("external_reference")
    if not order or not payment_id or external_ref != order["reference"]:
        return
    try:
        if approved_payment(access_token, payment_id, order["reference"]):
            st.session_state["premium_paid_digest"] = order["digest"]
            st.session_state["premium_order"] = None
            st.query_params.clear()
    except (HTTPError, URLError, TimeoutError, ValueError, ArithmeticError):
        st.session_state["payment_check_error"] = True


st.title("Seu resumo de vendas, sem montar planilha")
st.markdown('<p class="hero">Envie um CSV e receba faturamento total, vendas por produto e dados que precisam de revisão.</p>', unsafe_allow_html=True)
st.caption("O arquivo é processado em memória durante esta sessão e não é armazenado pelo aplicativo.")

with st.expander("Formato necessário", expanded=True):
    st.write("CSV com `data`, `produto`, `quantidade` e `valor_unitario`. Data AAAA-MM-DD. Preços aceitam vírgula decimal.")
    with open("vendas_exemplo.csv", "rb") as example:
        st.download_button("Baixar CSV de exemplo", example, file_name="vendas_exemplo.csv", mime="text/csv")

upload = st.file_uploader("Escolha sua planilha exportada como CSV", type=["csv"], max_upload_size=10, key="free_upload")
if upload:
    try:
        free = csv_summary(upload)
        total = sum(free["totals"].values(), Decimal("0"))
        col1, col2, col3 = st.columns(3)
        col1.metric("Vendas válidas", free["count"])
        col2.metric("Faturamento", brl(total))
        col3.metric("Produtos", len(free["totals"]))
        st.success("Resumo gratuito pronto.")
        rows = "\n".join(
            f"| {html.escape(name)} | {brl(value)} |"
            for name, value in sorted(free["totals"].items(), key=lambda item: item[1], reverse=True)
        )
        simple_html = f"<html lang='pt-BR'><meta charset='utf-8'><h1>Resumo de vendas</h1><p>Arquivo: {html.escape(free['name'])}</p><p>Faturamento: {brl(total)}</p><table><tr><th>Produto</th><th>Faturamento</th></tr>{''.join(f'<tr><td>{html.escape(name)}</td><td>{brl(value)}</td></tr>' for name, value in sorted(free['totals'].items(), key=lambda item:item[1], reverse=True))}</table></html>"
        st.download_button("Baixar relatório HTML", simple_html.encode("utf-8"), file_name="relatorio_vendas.html", mime="text/html", type="primary")
        if free["errors"]:
            st.warning(f"{len(free['errors'])} linha(s) precisam de revisão.")
    except (UnicodeDecodeError, ValueError) as error:
        st.error(f"Não consegui ler esse arquivo: {error}")

st.divider()
st.subheader("Relatório comparativo")
st.write("Compare o faturamento por produto entre dois períodos. Preço de lançamento: R$ 19,90 por relatório; valor ainda em teste.")
previous_file = st.file_uploader("CSV do período anterior", type=["csv"], max_upload_size=10, key="previous_upload")
current_file = st.file_uploader("CSV do período atual", type=["csv"], max_upload_size=10, key="current_upload")

premium_files = None
if previous_file and current_file:
    try:
        previous = csv_summary(previous_file)
        current = csv_summary(current_file)
        if previous["errors"] or current["errors"]:
            st.warning("Corrija as linhas inválidas nos dois arquivos antes de gerar o comparativo pago.")
        else:
            premium_files = (previous, current)
    except (UnicodeDecodeError, ValueError) as error:
        st.error(f"Não consegui ler os arquivos do comparativo: {error}")

token = get_access_token()
if token:
    resolve_returned_payment(token)
    if st.session_state.get("payment_check_error"):
        st.error("Não foi possível confirmar o pagamento agora. Atualize a página em alguns instantes; não faça outro pagamento.")
    if premium_files:
        digest = hashlib.sha256(premium_files[0]["raw"] + b"\0" + premium_files[1]["raw"]).hexdigest()
        paid_digest = st.session_state.get("premium_paid_digest")
        if paid_digest == digest:
            report = compare_report(*premium_files)
            st.success("Pagamento confirmado. Seu comparativo está pronto.")
            st.download_button("Baixar relatório comparativo", report.encode("utf-8"), file_name="comparativo_vendas.html", mime="text/html", type="primary")
        else:
            if st.button("Ir para pagamento seguro — R$ 19,90", type="primary"):
                order_ref = uuid.uuid4().hex
                st.session_state["premium_order"] = {"reference": order_ref, "digest": digest}
                try:
                    checkout_url = create_checkout(token, order_ref, APP_URL)
                    st.link_button("Continuar no Mercado Pago", checkout_url, type="primary")
                    st.info("Após o pagamento aprovado, volte a esta aba para validar e liberar o download.")
                except (HTTPError, URLError, TimeoutError, ValueError):
                    st.session_state["premium_order"] = None
                    st.error("Não consegui iniciar o checkout. Tente novamente mais tarde.")
else:
    st.info("A versão gratuita funciona normalmente. A cobrança online só será ativada depois de configurar as credenciais seguras do vendedor no Streamlit.")

st.divider()
st.caption("Confira os dados de origem antes de tomar decisões financeiras. Não envie dados pessoais de clientes.")
