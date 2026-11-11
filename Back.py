import os
from typing import Dict, List, Union
import pandas as pd

# -----------------------------------------------------------------------
# 1. CLASSE DOS DADOS
# -----------------------------------------------------------------------

class ElementoMTM:

    def __init__(self, codigo: str, descricao: str, frequencia: int, tempo_min: float):
        
        self.codigo = codigo
        self.descricao = descricao
        self.frequencia = frequencia
        self.tempo_min = tempo_min

class Equipamento:

    def __init__(self, codigo: int, nome: str, tempo_por_metro: float, rpm_padrao: float = 0.0):
        
        self.codigo = codigo
        self.nome = nome
        self.tempo_por_metro = tempo_por_metro
        self.rpm_padrao = rpm_padrao

    @property
    def rpm_inferior(self) -> float:
        return self.rpm_padrao * 0.9

    @property
    def rpm_superior(self) -> float:
        return self.rpm_padrao * 1.1

class Demanda:

    def __init__(
        self,
        titulo: str,
        rev: str,                     # Revisão da ficha de Processo Operacional (PO)
        operacao: str,
        agrupamento_familia: str,
        tamanho: str,
        medidas: str,
        pontos_cm: float,
        perimetro_costura: float,
        cod_eqp: int,                #Código do equipamento (máquina) a ser utilizado
        elementos: List[str],
    ):
        self.titulo = titulo
        self.rev = rev
        self.operacao = operacao
        self.agrupamento_familia = agrupamento_familia
        self.tamanho = tamanho
        self.medidas = medidas
        self.pontos_cm = pontos_cm
        self.perimetro_costura = perimetro_costura
        self.cod_eqp = cod_eqp
        self.elementos = elementos


def valorDecimal(valor) -> float:
    try:
        if isinstance(valor, str):
            valor = valor.replace(",", ".")
        return float(valor)
    except (ValueError, TypeError):
        return 0.0


# -----------------------------------------------------------------------
# 2. LEITURA DE PLANILHAS (EXCEL E CSV)
# -----------------------------------------------------------------------


class LerPlanilha:

    def __init__(
        self, caminho_entradas: str, caminho_maquinas_csv: str = None ):
        
        """ Suporta um ficheiro Excel (.xlsx/.ods) com abas ou dois ficheiros CSV
        separados(um para a Matriz MTM e outro opcional para Máquinas). """
        
        self.caminho_entradas = caminho_entradas
        self.caminho_maquinas_csv = caminho_maquinas_csv
        self.catalogo_mtm: Dict[str, ElementoMTM] = {}
        self.maquinas: Dict[int, Equipamento] = {}
        self.carrega_estatisticas()

    def ler_tabela(
        self, caminho: str, aba: str = None, cabecalho: int = 0) -> pd.DataFrame:
        # Deteta se o ficheiro é CSV ou Excel e realiza a leitura com o separador correto.
        
        extensao = os.path.splitext(caminho)[1].lower()

        if extensao == ".csv":
            # Tenta ler CSV testando delimitadores comuns (ponto e vírgula e vírgula)
            
            try:
                return pd.read_csv(caminho, sep=";", header=cabecalho, encoding="utf-8")
            
            except Exception:
                try:
                    return pd.read_csv(caminho, sep=",", header = cabecalho, encoding="utf-8")
                
                except Exception:
                    return pd.read_csv(caminho, sep=";", header = cabecalho, encoding = "latin-1") # É o plano B para ficheiros CSV com acentos e caracteres especiais.
        else:
            # Ficheiros Excel (.xlsx, .ods, .xls)
            return pd.read_excel(caminho, sheet_name=aba, header = cabecalho)

    def carrega_estatisticas(self):
        # 1. Carregar Matriz de Elementos MTM
        extensao = os.path.splitext(self.caminho_entradas)[1].lower()

        if extensao == ".csv":
            aba_mtm = self.ler_tabela(self.caminho_entradas)
        else:
            try:
                aba_mtm = self.ler_tabela(
                    self.caminho_entradas, aba= "MATRIZ_DE_ELEMENTOS"
                )
            except Exception:
                aba_mtm = self.ler_tabela(self.caminho_entradas, aba = "MTM")

        for _, linha in aba_mtm.iterrows():
            
            codigo = str( linha.get("elemento + agrupador", linha.get("Código", ""))).strip()
            descricao = str(linha.get("Descrição do elemento", linha.get("Descrição", ""))).strip()
            frequencia = int(linha.get("Frequência", 1))
            tempo_min = valorDecimal( linha.get("Tempo", linha.get("Tempo (min)", 0)))

            elemento = ElementoMTM(
                codigo = codigo,
                descricao = descricao,
                frequencia = frequencia,
                tempo_min = tempo_min,
            )
            self.catalogo_mtm[elemento.codigo] = elemento

        # 2. Carregar Cadastro de Máquinas
        caminho_maqs = self.caminho_maquinas_csv or self.caminho_entradas
        extensao_maqs = os.path.splitext(caminho_maqs)[1].lower()

        if extensao_maqs == ".csv":
            aba_maquinas = self.ler_tabela(caminho_maqs)
            
        else:
            try:
                aba_maquinas = self.ler_tabela(caminho_maqs, aba = "TEMPO-CM")
                
            except Exception:
                aba_maquinas = self.ler_tabela(caminho_maqs, aba = "Maquinas")

        for _, linha in aba_maquinas.iterrows():
            
            codigo = int(linha.get("Código da Máquina", linha.get("Código", 0)))
            nome = str(linha.get( "Descrição/Modelo", linha.get("Descrição / Modelo", linha.get("Nome", "")),)).strip()
            tempo_por_metro = valorDecimal( linha.get( "Fator de Tempo por Metro min/m", linha.get("Tempo por metro", 0),))
            rpm_padrao = valorDecimal( linha.get("RPM Padrão", linha.get("RPM", 0)))

            equipamento = Equipamento(
                codigo = codigo,
                nome = nome,
                tempo_por_metro = tempo_por_metro,
                rpm_padrao = rpm_padrao,
            )
            self.maquinas[equipamento.codigo] = equipamento


# -----------------------------------------------------------------------
# 3. LEITURA DE DEMANDA VIA CSV OU TXT
# -----------------------------------------------------------------------


def ler_demanda_csv(caminho_csv: str) -> Demanda:
    
    """ Lê um ficheiro CSV contendo os parâmetros de entrada da operação
    Pode estar no formato chave-valor ou em 1 linha de cabeçalho. """
    
    try:
        df = pd.read_csv(caminho_csv, sep=";", encoding="utf-8")
        
    except Exception:
        df = pd.read_csv(caminho_csv, sep=",", encoding="utf-8")

    # Caso o CSV seja no formato de duas colunas (Campo, Valor)
    if len(df.columns) == 2:
        dados = dict(zip(df.iloc[:, 0].astype(str), df.iloc[:, 1].astype(str)))
    else:
        # Caso o CSV seja tabular com 1 linha de dados
        dados = df.iloc[0].to_dict()

    elementos_raw = str(dados.get("Elementos", ""))
    elementos = [e.strip() for e in elementos_raw.split(",") if e.strip()]

    return Demanda(
        titulo = str(dados.get("Título", dados.get("titulo", ""))),
        rev = str(dados.get("REV", dados.get("rev", ""))),
        operacao = str(dados.get("Operação", dados.get("operacao", ""))),
        agrupamento_familia = str(dados.get("Agrupamento família", dados.get("agrupamento_familia", ""))),
        tamanho = str(dados.get("Tamanho", dados.get("tamanho", ""))),
        medidas = str(dados.get("Medidas da peça (em m)", dados.get("medidas", ""))),
        pontos_cm = valorDecimal(dados.get("Pontos/cm", dados.get("pontos_cm", 0))),
        perimetro_costura = valorDecimal( dados.get("Perímetro costura (em m)", dados.get("perimetro_costura", 0))),
        cod_eqp = int(valorDecimal(dados.get("Cód. Eqp", dados.get("cod_eqp", 0)))),
        elementos = elementos,
    )