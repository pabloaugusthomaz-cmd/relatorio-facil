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

## Cobrança do relatório comparativo

O app mantém o relatório de um CSV gratuito e oferece um comparativo entre dois períodos por R$ 19,90 como preço de teste. O Checkout Pro do Mercado Pago só aparece quando a credencial do vendedor está configurada. Após o retorno do checkout, o servidor consulta o pagamento e só libera o download se o pagamento estiver aprovado, em modo de produção, com o valor, moeda e referência esperados.

Para ativar:

1. Crie uma aplicação no painel de desenvolvedores do Mercado Pago e obtenha um Access Token de produção. Nunca coloque esse token no código ou no GitHub.
2. No Streamlit Community Cloud, abra as configurações do app e adicione em **Secrets**: `MERCADOPAGO_ACCESS_TOKEN = "seu-token-de-producao"`.
3. Reinicie o app e faça uma compra real de baixo valor para validar o fluxo completo antes de divulgar a função paga.

O retorno do checkout depende da sessão do navegador continuar ativa; se a sessão cair antes da validação, a pessoa pode ter de enviar os dois CSVs novamente. Esta versão não possui armazenamento persistente de pedidos nem webhook, portanto ainda é um MVP, não um sistema de cobrança robusto para escala. A comissão do provedor e eventuais obrigações fiscais/comerciais não estão incluídas no preço de teste.

## Operação e validação

O app automatiza a geração e entrega do arquivo após a confirmação do pagamento, mas não encontra clientes por conta própria. Faça conversas com lojistas, divulgue apenas em grupos que permitem esse tipo de postagem e ajuste o produto com base no uso real. Não há garantia de vendas ou lucro. Evite receber CSVs com nomes, telefones, endereços ou dados de pagamento de clientes.

Execute os testes com `python -m unittest discover -s tests`.
