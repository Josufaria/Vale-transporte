# ==============================================================
# 🚌 Cálculo Automático de Vale-Transporte
# 2026 • Pagamento Quinzenal • Feriados incluídos
# ==============================================================

import pandas as pd
import googlemaps
import time
import os
from datetime import date

# ==============================================================
# 🔐 CHAVE DA API (variável de ambiente)
# ==============================================================

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_API_KEY:
    raise Exception("❌ Defina a variável de ambiente GOOGLE_MAPS_API_KEY.")

gmaps = googlemaps.Client(key=GOOGLE_API_KEY)

# ==============================================================
# ⚙️ CONFIGURAÇÕES
# ==============================================================

ARQ_FUNC = "FRM VT 01-11-2025 A 15-11-2025.xlsx"
ARQ_SAIDA = "resultado_vale_transporte_2026.xlsx"

# Verificar se arquivo de saída está aberto/bloqueado
try:
    with open(ARQ_SAIDA, "a"):
        pass
except PermissionError:
    print(f"\n❌ ERRO: O arquivo '{ARQ_SAIDA}' está aberto no Excel.")
    print("⚠️  Por favor, FECHE o arquivo e tente novamente.")
    exit(1)

ANO_CALCULO = 2026
MES_CALCULO = 1   # ajuste conforme o mês

# ==============================================================
# 📅 FERIADOS NACIONAIS — 2026 (Brasil)
# (pode acrescentar feriados estaduais/municipais depois)
# ==============================================================

FERIADOS_2026 = [
    date(2026, 1, 1),   # Confraternização Universal
    date(2026, 4, 3),   # Sexta-feira Santa
    date(2026, 4, 21),  # Tiradentes
    date(2026, 5, 1),   # Dia do Trabalho
    date(2026, 9, 7),   # Independência
    date(2026, 10, 12), # Nossa Senhora Aparecida
    date(2026, 11, 2),  # Finados
    date(2026, 11, 15), # Proclamação da República
    date(2026, 12, 25)  # Natal
]

# ==============================================================
# 📅 FUNÇÕES DE DIAS ÚTEIS (com feriados)
# ==============================================================

def dias_uteis_mes_com_feriados(ano, mes, feriados):
    inicio = pd.Timestamp(year=ano, month=mes, day=1)
    fim = inicio + pd.offsets.MonthEnd(1)

    # Dias úteis padrão (seg-sex)
    dias = pd.date_range(inicio, fim, freq="B")

    # Remover feriados
    feriados_ts = pd.to_datetime(feriados)
    dias = dias.difference(feriados_ts)

    return dias

def separar_quinzenas(dias_uteis):
    """
    Divide os dias úteis em:
    - 1ª quinzena: até dia 15
    - 2ª quinzena: do dia 16 em diante
    """
    primeira = [d for d in dias_uteis if d.day <= 15]
    segunda = [d for d in dias_uteis if d.day > 15]
    return len(primeira), len(segunda)

# Gerar calendário do mês
DIAS_UTEIS_LISTA = dias_uteis_mes_com_feriados(ANO_CALCULO, MES_CALCULO, FERIADOS_2026)
DIAS_Q1, DIAS_Q2 = separar_quinzenas(DIAS_UTEIS_LISTA)

print(f"📅 Dias úteis 1ª quinzena: {DIAS_Q1}")
print(f"📅 Dias úteis 2ª quinzena: {DIAS_Q2}")

# ==============================================================
# 🧭 FUNÇÕES AUXILIARES
# ==============================================================

# ==============================================================
# ⚙️ CONFIGURAÇÕES DE TARIFAS (2026)
# ==============================================================

# Tarifas para Vale-Transporte (alguns valores são maiores que o comum)
PRECOS_VT_2026 = {
    "SPTrans": 5.30,
    "Metrô de São Paulo": 5.92,
    "CPTM": 5.92,
    "ViaQuatro": 5.92,
    "ViaMobilidade": 5.92,
    "CMTO - Osasco": 6.10,
    "Viação Osasco": 6.10,
    "Ralip Transportes - Barueri": 6.10,
    "BB Urbano - Itapevi": 6.10,
    "Viação Raposo Tavares - Cotia": 6.10,
    "Guarupass - Guarulhos": 6.20,
    "Suzantur - Mauá": 7.50,
    "Sou + Diadema": 7.50,
    "Santo André Transportes": 7.25,
    "Com Embu das Artes": 5.80,
    "TIC Trens": 5.92  # CPTM/Trem fallback
}

# EMTU - Tarifas específicas por linha (Intermunicipais)
EMTU_ESPECIFICOS = {
    "125": 6.40, "408": 9.35, "032": 7.15, "288": 6.35, "158": 9.20, "396": 8.25,
    "257": 7.75, "555": 7.75, "182": 6.35, "290": 6.35, "084": 6.35, "194": 6.35,
    "176": 6.40, "531": 7.15, "384": 8.00, "489": 7.50, "163": 7.75, "497": 8.00,
    "835": 8.00, "833": 8.00, "260": 8.00, "463": 8.00
}

VALOR_PADRAO_EMTU = 6.40 # Fallback para intermunicipais desconhecidas
VALOR_PADRAO_ONIBUS = 5.30

INTEGRACAO_SPTRANS_METRO = 9.38
DESCONTO_EMTU_TRILHO = 1.50

def identifica_tipo_e_preco(step_details):
    """
    Identifica o valor da tarifa para um único trecho de transporte.
    Retorna (valor, agencia, linha, tipo_veiculo)
    """
    line = step_details.get("line", {})
    agencies = line.get("agencies", [{}])
    agency_name = agencies[0].get("name", "Desconhecido")
    short_name = line.get("short_name", "N/A")
    vehicle = line.get("vehicle", {}).get("name", "Ônibus")
    
    # 1. Verificar EMTU
    if "EMTU" in agency_name.upper():
        preco = EMTU_ESPECIFICOS.get(short_name, VALOR_PADRAO_EMTU)
        return preco, "EMTU", short_name, vehicle
    
    # 2. Verificar agências mapeadas
    for key, valor in PRECOS_VT_2026.items():
        if key in agency_name:
            return valor, agency_name, short_name, vehicle
            
    # 3. Fallback por nome de agência ou tipo
    if vehicle in ["Metrô", "Trem", "Monotrilho"]:
        return 5.92, agency_name, short_name, vehicle
        
    return VALOR_PADRAO_ONIBUS, agency_name, short_name, vehicle

def calcula_rota_detalhada(origem, destino):
    """
    Retorna:
    - pernas_info: Lista de dicionários com detalhes de cada trecho.
    - erro: Mensagem de erro se houver.
    """
    try:
        rotas = gmaps.directions(
            origem,
            destino,
            mode="transit",
            transit_routing_preference="less_walking",
            language="pt-BR"
        )

        if not rotas:
            return [], "Nenhuma rota encontrada"

        leg = rotas[0]["legs"][0]
        steps = leg["steps"]

        pernas_transporte = []
        for step in steps:
            if step["travel_mode"] == "TRANSIT":
                detalhes = step.get("transit_details", {})
                preco, agencia, linha, veiculo = identifica_tipo_e_preco(detalhes)
                
                pernas_transporte.append({
                    "agencia": agencia,
                    "linha": linha,
                    "veiculo": veiculo,
                    "preco_base": preco,
                    "distancia_caminhada_anterior": 0 # será preenchido
                })
        
        if not pernas_transporte:
            return [], "Trajeto a pé"

        # Calcular distâncias de caminhada entre conexões para checar integração
        ultima_caminhada = 0
        idx_transporte = 0
        for step in steps:
            if step["travel_mode"] == "WALKING":
                ultima_caminhada = step["distance"]["value"]
            elif step["travel_mode"] == "TRANSIT":
                pernas_transporte[idx_transporte]["distancia_caminhada_anterior"] = ultima_caminhada
                idx_transporte += 1
                ultima_caminhada = 0

        return pernas_transporte, None

    except Exception as e:
        return [], f"Erro: {e}"

def calcula_custo_total_diario(pernas):
    """
    Calcula o custo total de IDA (ou VOLTA) considerando integrações.
    """
    if not pernas:
        return 0.0
    
    total = 0.0
    
    # Lógica simplificada de integração:
    i = 0
    while i < len(pernas):
        atual = pernas[i]
        proxima = pernas[i+1] if i+1 < len(pernas) else None
        
        # Caso especial: Integração SPTrans + Trilhos
        if proxima and (
            (atual["agencia"] == "SPTrans" and proxima["veiculo"] in ["Metrô", "Trem", "Monotrilho"]) or
            (proxima["agencia"] == "SPTrans" and atual["veiculo"] in ["Metrô", "Trem", "Monotrilho"])
        ) and proxima["distancia_caminhada_anterior"] < 400:
            total += INTEGRACAO_SPTRANS_METRO
            i += 2 # pula os dois
            continue
            
        # Caso especial: Integração EMTU + Trilhos
        if proxima and (
            (atual["agencia"] == "EMTU" and proxima["veiculo"] in ["Metrô", "Trem", "Monotrilho"]) or
            (proxima["agencia"] == "EMTU" and atual["veiculo"] in ["Metrô", "Trem", "Monotrilho"])
        ) and proxima["distancia_caminhada_anterior"] < 400:
            if atual["agencia"] == "EMTU":
                total += atual["preco_base"] + (proxima["preco_base"] - DESCONTO_EMTU_TRILHO)
            else:
                total += proxima["preco_base"] + (atual["preco_base"] - DESCONTO_EMTU_TRILHO)
            i += 2
            continue
            
        # Caso Geral: Soma tarifa
        if i > 0 and atual["distancia_caminhada_anterior"] < 150:
             # Assume integração gratuita se for mesma agência ou terminal
             pass 
        else:
            total += atual["preco_base"]
            
        i += 1
        
    return round(total, 2)

# ==============================================================
# 🧮 PROCESSAMENTO
# ==============================================================

print("\n🚀 Iniciando cálculo automático de vale-transporte...\n")

df = pd.read_excel(ARQ_FUNC, header=3)
df.columns = df.columns.str.strip().str.upper()

print("✅ Colunas detectadas:", df.columns.tolist())

colunas_necessarias = ["CHAPA", "NOME", "SITUAÇÃO", "DIV RH", "CEP", "ENDEREÇO OBRA"]
faltando = [c for c in colunas_necessarias if c not in df.columns]
if faltando:
    raise Exception(f"⚠️ Colunas faltando: {faltando}")

resultados = []

for _, row in df.iterrows():
    chapa = str(row["CHAPA"]).strip()
    if chapa.endswith(".0"):    
        chapa = chapa[:-2]

    nome = str(row["NOME"]).strip()
    situacao = str(row["SITUAÇÃO"]).strip().upper()
    
    cep = str(row["CEP"]).strip()
    if cep.endswith(".0"):
        cep = cep[:-2]

    endereco_obra = str(row["ENDEREÇO OBRA"]).strip()

    print(f"➡️  Processando: {nome} ({situacao})")

    origem = f"{cep}, Brasil"
    destino = f"{endereco_obra}, Brasil"

    # Se não estiver ATIVO, não calcula VT
    if situacao != "ATIVO":
        resultados.append({
            "CHAPA": chapa,
            "NOME": nome,
            "SITUAÇÃO": situacao,   # ex: SOB CUSTÓDIA
            "ORIGEM": origem,
            "DESTINO": destino,
            "DIAS_UTEIS_Q1": DIAS_Q1,
            "DIAS_UTEIS_Q2": DIAS_Q2,
            "VT_QUINZENA_1": None,
            "VT_QUINZENA_2": None
        })
        continue

    # Cálculo só para ATIVO
    pernas, erro_rota = calcula_rota_detalhada(origem, destino)
    
    if erro_rota:
        print(f"   ⚠️ {erro_rota}")
        valor_diario = 0.0
        detalhe_viagem = erro_rota
    else:
        custo_ida = calcula_custo_total_diario(pernas)
        valor_diario = custo_ida * 2
        
        # Criar string de detalhe para a planilha
        detalhe_viagem = " + ".join([f"{p['agencia']} ({p['linha']})" for p in pernas])
        print(f"   🚌 Rota: {detalhe_viagem}")
        print(f"   🎫 Custo Diário: R$ {valor_diario:.2f}")

    if valor_diario > 0:
        vt_q1 = round(valor_diario * DIAS_Q1, 2)
        vt_q2 = round(valor_diario * DIAS_Q2, 2)
    else:
        vt_q1 = 0.0
        vt_q2 = 0.0

    resultados.append({
        "CHAPA": chapa,
        "NOME": nome,
        "SITUAÇÃO": situacao,
        "ORIGEM": origem,
        "DESTINO": destino,
        "ROTA_DETALHADA": detalhe_viagem,
        "VALOR_DIARIO": valor_diario,
        "DIAS_UTEIS_Q1": DIAS_Q1,
        "DIAS_UTEIS_Q2": DIAS_Q2,
        "VT_QUINZENA_1": vt_q1,
        "VT_QUINZENA_2": vt_q2
    })

    time.sleep(0.2)  # evita estouro de quota

# ==============================================================
# 📁 SAÍDA
# ==============================================================

df_saida = pd.DataFrame(resultados)
df_saida.to_excel(ARQ_SAIDA, index=False)

print("\n✅ Cálculo concluído com sucesso!")
print(f"📁 Planilha gerada: {ARQ_SAIDA}")
print("------------------------------------------------------")
print("Colunas finais:")
print("CHAPA, NOME, SITUAÇÃO, ORIGEM, DESTINO,")
print("DIAS_UTEIS_Q1, DIAS_UTEIS_Q2,")
print("VT_QUINZENA_1, VT_QUINZENA_2")
print("------------------------------------------------------") 