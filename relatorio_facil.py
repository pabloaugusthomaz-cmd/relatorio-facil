#!/usr/bin/env python3
"""Gera um resumo de vendas em HTML a partir de um CSV, usando só Python padrão."""

import argparse
import csv
import html
import io
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


def parse_money(value: str) -> Decimal:
    value = (value or "").strip().replace("R$", "").replace(" ", "")
    if not value:
        raise ValueError("valor vazio")
    if "," in value:
        value = value.replace(".", "").replace(",", ".")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"valor inválido: {value}") from exc


def brl(value: Decimal) -> str:
    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def summarize_sales(file):
    totals = defaultdict(Decimal)
    count = 0
    errors = []
    reader = csv.DictReader(file)
    required = {"data", "produto", "quantidade", "valor_unitario"}
    headers = {h.strip().lower() for h in (reader.fieldnames or [])}
    if not required.issubset(headers):
        raise ValueError("CSV precisa das colunas: data, produto, quantidade, valor_unitario")
    # Mapeia cabeçalhos sem depender de maiúsculas/minúsculas.
    names = {h.strip().lower(): h for h in reader.fieldnames}
    for line, row in enumerate(reader, start=2):
        try:
            datetime.strptime(row[names["data"]].strip(), "%Y-%m-%d")
            product = row[names["produto"]].strip()
            qty = int(row[names["quantidade"]])
            price = parse_money(row[names["valor_unitario"]])
            if not product or qty <= 0 or price < 0:
                raise ValueError("produto, quantidade ou preço inválido")
            totals[product] += qty * price
            count += 1
        except (ValueError, KeyError) as exc:
            errors.append(f"Linha {line}: {exc}")
    return totals, count, errors


def read_sales(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return summarize_sales(file)


def summarize_csv_text(content: str):
    return summarize_sales(io.StringIO(content, newline=""))


def render_report(totals, count, errors, source: str) -> str:
    grand_total = sum(totals.values(), Decimal("0"))
    rows = "\n".join(
        f"<tr><td>{html.escape(name)}</td><td>{brl(amount)}</td></tr>"
        for name, amount in sorted(totals.items(), key=lambda item: item[1], reverse=True)
    ) or '<tr><td colspan="2">Nenhuma venda válida encontrada.</td></tr>'
    error_block = ""
    if errors:
        error_block = "<h2>Linhas que precisam de revisão</h2><ul>" + "".join(
            f"<li>{html.escape(error)}</li>" for error in errors
        ) + "</ul>"
    return f"""<!doctype html>
<html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Relatório de vendas</title>
<style>
body{{font:16px system-ui,sans-serif;max-width:850px;margin:40px auto;padding:0 18px;color:#17212b;background:#f4f7fa}}
h1{{color:#145b53}}.cards{{display:flex;gap:14px;flex-wrap:wrap}}.card{{background:white;padding:18px 22px;border-radius:12px;box-shadow:0 2px 12px #10203012;min-width:180px}}
.label{{color:#607080;font-size:14px}}.value{{font-size:25px;font-weight:700;margin-top:6px}}table{{border-collapse:collapse;width:100%;background:#fff;border-radius:10px;overflow:hidden}}
th,td{{padding:12px 14px;border-bottom:1px solid #e7edf1;text-align:left}}th{{background:#e7f2ef}}li{{margin:8px 0}}footer{{color:#607080;margin-top:25px;font-size:13px}}
</style>
<h1>Resumo de vendas</h1><p>Arquivo analisado: {html.escape(source)}</p>
<div class="cards"><div class="card"><div class="label">Vendas válidas</div><div class="value">{count}</div></div>
<div class="card"><div class="label">Faturamento total</div><div class="value">{brl(grand_total)}</div></div>
<div class="card"><div class="label">Produtos vendidos</div><div class="value">{len(totals)}</div></div></div>
<h2>Faturamento por produto</h2><table><thead><tr><th>Produto</th><th>Faturamento</th></tr></thead><tbody>{rows}</tbody></table>
{error_block}<footer>Relatório gerado automaticamente. Confira os dados de origem antes de tomar decisões.</footer>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Cria relatório HTML de vendas a partir de CSV.")
    parser.add_argument("arquivo_csv", type=Path, help="CSV com data,produto,quantidade,valor_unitario")
    parser.add_argument("-o", "--saida", type=Path, default=Path("relatorio.html"), help="caminho do HTML")
    args = parser.parse_args()
    totals, count, errors = read_sales(args.arquivo_csv)
    args.saida.write_text(render_report(totals, count, errors, args.arquivo_csv.name), encoding="utf-8")
    print(f"Relatório salvo em {args.saida.resolve()} | {count} vendas válidas | {len(errors)} linha(s) para revisar")


if __name__ == "__main__":
    main()
