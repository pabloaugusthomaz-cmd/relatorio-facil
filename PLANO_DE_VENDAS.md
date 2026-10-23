# Como testar vendas do Relatório Fácil

O app já automatiza a geração do relatório depois que alguém envia um CSV. A parte que ainda não é automática é conseguir clientes e receber pagamentos: isso exige uma oferta, divulgação e uma conta de pagamentos. Não há garantia de venda ou lucro.

## Oferta inicial para validar

**Relatório Fácil — teste de lançamento**

- Gratuito: a pessoa envia o CSV e baixa o resumo padrão no app.
- Serviço pago opcional, como hipótese de teste: R$ 29 por uma análise personalizada de um mês, com resumo por produto e uma conversa curta para explicar os números.
- Só aceite arquivos sem dados pessoais de clientes. Oriente a pessoa a remover nomes, telefones, endereços e dados de pagamento antes de enviar.
- O preço de R$ 29 é apenas um ponto de partida experimental, não um preço validado. Ajuste com base em conversas e pedidos reais.

O código agora tem um Checkout Pro opcional para vender um comparativo automático por R$ 19,90, mas ele só fica ativo após configurar seu Access Token de produção nos Secrets do Streamlit e validar uma compra real. A análise personalizada acima continua sendo um serviço separado e manual.

## Texto de divulgação para adaptar

> Você exporta vendas em CSV e depois perde tempo tentando entender os números? Fiz um app gratuito que transforma uma planilha CSV em um resumo por produto e faturamento. Estou procurando 3 lojistas para testar e me dizer o que falta. O arquivo deve estar sem dados pessoais de clientes. Teste: https://relatorio-facil-pf8fkbysecxhwesvy9dgmh.streamlit.app

Publique em grupos onde divulgação de ferramentas seja permitida, ou envie individualmente apenas para pessoas com quem já existe uma conversa. Não automatize mensagens não solicitadas.

## Roteiro de validação (uma semana)

1. Converse com 10 pequenos lojistas ou prestadores de serviço e pergunte como analisam as vendas hoje.
2. Compartilhe o app apenas com quem demonstrar interesse e peça para testar com um CSV anonimizado.
3. Pergunte se o relatório ajudou, o que faltou e quanto pagariam por uma versão que resolva esse problema.
4. Registre quantas pessoas testaram, concluíram o upload e pediram uma melhoria ou análise paga.
5. Só construa cobrança recorrente se houver pessoas que peçam o serviço repetidamente. Até lá, mantenha a versão gratuita e valide a necessidade.

## Próxima automação técnica

O MVP de checkout consulta o status do pagamento no servidor antes de liberar o relatório. Para operação mais confiável, ainda é preciso configurar um webhook assinado e armazenamento persistente de pedidos; o retorno do checkout depende da sessão do navegador permanecer ativa. Tokens e chaves devem ficar nos Secrets do Streamlit, nunca no repositório público.
