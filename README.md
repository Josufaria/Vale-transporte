Automatização de Vale Transporte 🚌💸
Um poderoso sistema desenvolvido em Python projetado para automatizar, agilizar e calcular com precisão os custos de Vale Transporte (VT) de funcionários.

O sistema elimina o trabalho manual minucioso de RH e Departamento Pessoal cruzando arquivos no Excel e consultando rotas reais utilizando a infraestrutura do Google Maps.

🎯 O Que o Projeto Faz?
Historicamente, calcular a melhor rota e o custo exato do deslocamento casa-trabalho para cada funcionário exige pesquisa manual, especialmente com múltiplas integrações (Ônibus Municipal, Trólebus, Trem, Metrô e Integrações Intermunicipais como a EMTU).

O código resolve exatamente isso de forma 100% automatizada:

O usuário fornece uma planilha de entrada (Excel) contendo os dados dos funcionários e seus endereços de residência/trabalho.
O sistema em Python processa tudo utilizando a Google Maps API para extrair as melhores rotas, linhas e baldeações de transporte público.
Com base nas tabelas de preços oficiais atualizadas (SPTrans, EMTU, Metrô/CPTM), o sistema devolve uma nova planilha processada com o detalhamento exato de valores diários e o total a ser depositado para cada funcionário.
🚀 Funcionalidades Principais
✔️ Integração com Google Maps API: Roteamento inteligente de transporte público.
✔️ Leitura e Escrita de Arquivos Excel: Usa bibliotecas Pandas/Openpyxl para interagir facilmente com padrões do pacote Office.
✔️ Cálculo de Tarifas Complexas: Lida com variações de preços para ônibus de cidade, trens/metrô, EMTU e integrações de sistema único.
✔️ Cálculo de Dias Úteis: Considera feriados nacionais e conta os dias úteis exatos dentro do período.
🛠️ Tecnologias Utilizadas
Linguagem Principal: Python 3
Manipulação de Dados: Pandas / Openpyxl
Integração Externa: Google Maps API
Arquitetura: Script Local (VT.py)
