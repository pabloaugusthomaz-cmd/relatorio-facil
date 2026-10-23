# Relatório Fácil

Aplicativo web de autoatendimento: a pessoa envia um CSV, vê um resumo das vendas e baixa um relatório HTML. O processamento acontece em memória durante a sessão; o app não grava os arquivos enviados.

## Rodar no computador

Requer Python 3.10 ou superior.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

O navegador abrirá o app. O CSV precisa das colunas `data`, `produto`, `quantidade`, `valor_unitario`; datas no formato `AAAA-MM-DD` e preços como `32,90` ou `32.90`. Há um exemplo para baixar na própria página.

## Publicar sem pagar hospedagem

1. Crie uma conta no GitHub e um repositório para estes arquivos.
2. Envie `app.py`, `relatorio_facil.py`, `requirements.txt` e `vendas_exemplo.csv` ao repositório.
3. Entre no Streamlit Community Cloud, conecte ao GitHub e escolha o repositório e o arquivo `app.py`.
4. Publique e compartilhe o endereço gerado.

O Streamlit Community Cloud oferece hospedagem gratuita para apps comunitários; a disponibilidade e os limites podem mudar. A publicação requer uma conta GitHub. O código deve ir para o repositório usado na publicação, portanto será visível a quem tiver acesso a esse repositório.

## Como pode gerar receita

Esta primeira versão fica gratuita para facilitar a divulgação e aprender o que as pessoas usam. Depois de validar procura, opções são cobrar por relatórios avançados, processamento de mais arquivos ou uma assinatura para recursos recorrentes. Mercado Pago oferece links e planos de assinatura, mas a cobrança ainda não está integrada neste protótipo: é preciso criar o produto/assinatura na conta e implementar uma confirmação de pagamento antes de liberar funções pagas. Taxas do meio de pagamento reduzem o valor recebido.

Hospedagem gratuita e automatização da entrega não atraem compradores por conta própria. A aquisição inicial precisa vir de divulgação: demonstrações em comunidades e grupos relevantes, conteúdo útil e compartilhamento do link. Não há garantia de vendas ou lucro.

## Próximo experimento

Publique a versão gratuita e observe se pessoas realmente tentam enviar um arquivo e baixar o relatório. Divulgue em alguns canais gratuitos voltados a pequenos lojistas, sem enviar spam. Anote onde travam e que função pedem; só então implemente um plano pago. Evite receber planilhas com dados pessoais ou financeiros desnecessários.
