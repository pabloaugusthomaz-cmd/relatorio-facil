"""Checkout Pro helpers and premium sales report rendering."""

import html
import json
from decimal import Decimal
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from relatorio_facil import brl

PREMIUM_PRICE = Decimal("19.90")
MP_API = "https://api.mercadopago.com"


def api_request(url, access_token, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers)
    try:
        with urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError:
        raise


def create_checkout(access_token, order_ref, app_url):
    payload = api_request(
        f"{MP_API}/checkout/preferences",
        access_token,
        {
            "items": [{
                "title": "Relatório comparativo de vendas",
                "description": "Comparação de faturamento por produto entre dois arquivos CSV.",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(PREMIUM_PRICE),
            }],
            "external_reference": order_ref,
            "back_urls": {"success": app_url, "pending": app_url, "failure": app_url},
            "auto_return": "approved",
        },
    )
    checkout_url = payload.get("init_point")
    if not checkout_url:
        raise ValueError("O Mercado Pago não retornou o endereço de checkout.")
    return checkout_url


def approved_payment(access_token, payment_id, order_ref):
    if not payment_id or not str(payment_id).isdigit():
        return False
    payment = api_request(f"{MP_API}/v1/payments/{payment_id}", access_token)
    try:
        amount_matches = Decimal(str(payment.get("transaction_amount", "0"))) == PREMIUM_PRICE
    except ArithmeticError:
        amount_matches = False
    return (
        payment.get("status") == "approved"
        and payment.get("live_mode") is True
        and payment.get("external_reference") == order_ref
        and payment.get("currency_id") == "BRL"
        and amount_matches
    )


def compare_report(first, second):
    first_total = sum(first["totals"].values(), Decimal("0"))
    second_total = sum(second["totals"].values(), Decimal("0"))
    difference = second_total - first_total
    if first_total:
        variation = f"{difference / first_total * 100:+.1f}%"
    else:
        variation = "—" if not second_total else "Novo período"

    products = sorted(set(first["totals"]) | set(second["totals"]))
    rows = []
    for product in products:
        prior = first["totals"].get(product, Decimal("0"))
        current = second["totals"].get(product, Decimal("0"))
        rows.append(
            "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                html.escape(product), brl(prior), brl(current), brl(current - prior)
            )
        )
    return f"""<!doctype html>
<html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Comparativo de vendas</title><style>
body{{font:16px system-ui,sans-serif;max-width:950px;margin:40px auto;padding:0 18px;color:#17212b;background:#f4f7fa}}
h1{{color:#145b53}}.cards{{display:flex;gap:14px;flex-wrap:wrap}}.card{{background:white;padding:18px 22px;border-radius:12px;min-width:180px}}
.label{{color:#607080;font-size:14px}}.value{{font-size:23px;font-weight:700;margin-top:6px}}table{{border-collapse:collapse;width:100%;background:#fff}}
th,td{{padding:12px 14px;border-bottom:1px solid #e7edf1;text-align:left}}th{{background:#e7f2ef}}footer{{color:#607080;margin-top:25px;font-size:13px}}
</style><h1>Comparativo de vendas</h1>
<p>Período anterior: {html.escape(first['name'])}<br>Período atual: {html.escape(second['name'])}</p>
<div class="cards"><div class="card"><div class="label">Faturamento anterior</div><div class="value">{brl(first_total)}</div></div>
<div class="card"><div class="label">Faturamento atual</div><div class="value">{brl(second_total)}</div></div>
<div class="card"><div class="label">Variação</div><div class="value">{brl(difference)} ({variation})</div></div></div>
<h2>Variação por produto</h2><table><thead><tr><th>Produto</th><th>Anterior</th><th>Atual</th><th>Diferença</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<footer>Relatório gerado automaticamente. A comparação depende de períodos equivalentes e da qualidade dos arquivos enviados.</footer>
</html>"""
