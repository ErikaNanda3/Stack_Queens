import os
from typing import Dict, List, Union
import pandas as pd
import json
import openpyxl

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

        for idx, linha in aba_maquinas.iterrows():
            # Busca flexível que testa todos os nomes possíveis de coluna para o código
            raw_codigo = (
                linha.get("Cód. Eqp.")
                or linha.get("Cód. Eqp")
                or linha.get("Código da Máquina")
                or linha.get("Código")
                or (idx + 1)
            )
            codigo = int(valorDecimal(raw_codigo))

            nome = str(
                linha.get("Descrição/Modelo")
                or linha.get("Descrição / Modelo")
                or linha.get("Equipamento")
                or linha.get("Nome")
                or "").strip()

            tempo_por_metro = valorDecimal(
                linha.get("Fator de Tempo por Metro min/m")
                or linha.get("Tempo por metro")
                or linha.get("Tempo por Metro")
                or 0)

            rpm_padrao = valorDecimal(
                linha.get("RPM Padrão")
                or linha.get("RPM - padrão")
                or linha.get("RPM")
                or 0 )

            equipamento = Equipamento(
                codigo=codigo,
                nome=nome,
                tempo_por_metro=tempo_por_metro,
                rpm_padrao=rpm_padrao,
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

def ler_arquivo_demanda(caminho_txt: str) -> Demanda:
    dados = {}
    with open(caminho_txt, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            if ":" in linha:
                chave, valor = linha.split(":", 1)
                dados[chave.strip()] = valor.strip().strip('"')

    elementos_raw = dados.get("Elementos", "")
    elementos = [e.strip() for e in elementos_raw.split(",") if e.strip()]

    return Demanda(
        titulo=dados.get("Título", ""),
        rev=dados.get("REV", ""),
        operacao=dados.get("Operação", ""),
        agrupamento_familia=dados.get("Agrupamento família", ""),
        tamanho=dados.get("Tamanho", ""),
        medidas=dados.get("Medidas da peça (em m)", ""),
        pontos_cm=valorDecimal(dados.get("Pontos/cm", 0)),
        perimetro_costura=valorDecimal(
            dados.get("Perímetro costura (em m)", 0)
        ),
        cod_eqp=int(valorDecimal(dados.get("Cód. Eqp", 0))),
        elementos=elementos,
    )
    
# -----------------------------------------------------------------------
#       4. MOTOR DE CÁLCULO T&M E GERADOR DA FICHA PO
# -----------------------------------------------------------------------
class GeradorFichaPO:

    def __init__(self, demanda: Demanda, leitor: LerPlanilha):
        self.demanda = demanda
        self.leitor = leitor

        # Busca flexível por ID inteiro, ID texto ou primeira máquina da base como fallback seguro
        cod_busca = int(demanda.cod_eqp)
        self.equipamento = (
            leitor.maquinas.get(cod_busca)
            or leitor.maquinas.get(demanda.cod_eqp)
            or (list(leitor.maquinas.values())[0] if leitor.maquinas else None)
        )

    def calcular_e_estruturar(self) -> Dict:
        if not self.equipamento:
            raise ValueError(
                f"Equipamento com código {self.demanda.cod_eqp} não foi encontrado na base estática."
            )

        tempo_fixo = round(
            self.demanda.perimetro_costura * self.equipamento.tempo_por_metro, 4
        )

        linhas_elementos = [
            {
                "codigo": "FIXO",
                "descricao": "Tempo de costura",
                "frequencia": 1,
                "tempo_min": tempo_fixo,
            }
        ]

        tempo_total = tempo_fixo

        # Busca garantindo conversão do código para string tratada
        for cod in self.demanda.elementos:
            elemento = self.leitor.catalogo_mtm.get(str(cod).strip())
            if elemento:
                linhas_elementos.append(
                    {
                        "codigo": elemento.codigo,
                        "descricao": elemento.descricao,
                        "frequencia": elemento.frequencia,
                        "tempo_min": elemento.tempo_min,
                    }
                )
                tempo_total += elemento.tempo_min * elemento.frequencia
            else:
                linhas_elementos.append(
                    {
                        "codigo": str(cod),
                        "descricao": "Elemento não encontrado na base estática",
                        "frequencia": 1,
                        "tempo_min": 0.0,
                    }
                )

        tempo_total = round(tempo_total, 4)

        ficha_po = {
            "identificacao": {
                "titulo": self.demanda.titulo,
                "rev": self.demanda.rev,
                "operacao": self.demanda.operacao,
            },
            "parametros_produto": {
                "agrupamento_familia": self.demanda.agrupamento_familia,
                "tamanho": self.demanda.tamanho,
                "medidas": self.demanda.medidas,
                "pontos_cm": self.demanda.pontos_cm,
                "perimetro_costura": self.demanda.perimetro_costura,
            },
            "equipamento": {
                "cod_eqp": self.equipamento.codigo,
                "nome": self.equipamento.nome,
                "rpm_inferior": round(self.equipamento.rpm_inferior, 2),
                "rpm_padrao": self.equipamento.rpm_padrao,
                "rpm_superior": round(self.equipamento.rpm_superior, 2),
            },
            "elementos": linhas_elementos,
            "totais": {
                "tempo_total_min": tempo_total,
                "tempo_total_horas": round(tempo_total / 60, 4),
            },
        }

        return ficha_po


    def exportar_json(self) -> str:
        #Exporta os dados formatados em String JSON para consumo da interface gráfica (Front-end).
        
        dados = self.calcular_e_estruturar()
        return json.dumps(dados, indent=4, ensure_ascii=False)

    def exportar_excel(self, caminho_saida: str = "Ficha_PO_Gerada.xlsx"):
        #Gera a planilha Excel (.xlsx) idêntica à ficha PO padrão do evento.
        
        dados = self.calcular_e_estruturar()
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "PO"

        # Identificação
        ws["A1"] = dados["identificacao"]["titulo"]
        ws["E1"] = (
            f"Rev. {dados['identificacao']['rev']}"
            if dados["identificacao"]["rev"]
            else "Rev. 00"
        )

        # Operação
        ws["A2"] = "Operação"
        ws["B2"] = dados["identificacao"]["operacao"]

        # Parâmetros da Peça/Produto
        ws.append(["Agrupamento família", "Tamanho", "Medidas da peça (em m)", "Pontos/cm", "Perímetro costura (em m)",])
        ws.append([
                dados["parametros_produto"]["agrupamento_familia"],
                dados["parametros_produto"]["tamanho"],
                dados["parametros_produto"]["medidas"],
                dados["parametros_produto"]["pontos_cm"],
                dados["parametros_produto"]["perimetro_costura"],])

        # Parâmetros do Equipamento
        ws.append(["Cód. Eqp.", "Equipamento", "RPM - limite inferior","RPM - padrão", "RPM - limite superior",])
        ws.append(
            [
                dados["equipamento"]["cod_eqp"],
                dados["equipamento"]["nome"],
                dados["equipamento"]["rpm_inferior"],
                dados["equipamento"]["rpm_padrao"],
                dados["equipamento"]["rpm_superior"],
            ]
        )

        # Tabela de Elementos Operacionais
        ws.append(["Código do elemento","Elementos","", "Frequência","Tempos (em minutos)",])

        for elem in dados["elementos"]:
            ws.append([elem["codigo"],elem["descricao"],"",elem["frequencia"], elem["tempo_min"],])

        wb.save(caminho_saida)
        return caminho_saida    
    
    
# --------------------------------------------------------------
#                   6. MENU 
# --------------------------------------------------------------

if __name__ == "__main__":
    caminho_planilha = "Entradas.ods"

    print("--- 1. Carregando Base Estática ---")
    leitor = LerPlanilha(caminho_entradas=caminho_planilha)
    print(f"Elementos MTM carregados: {len(leitor.catalogo_mtm)}")
    print(f"Máquinas carregadas: {len(leitor.maquinas)}")

    print("\n--- 2. Lendo Demanda de Entrada ---")
    demanda = ler_arquivo_demanda("demanda_000.txt")
    print(f"Operação: {demanda.operacao}")

    print("\n--- 3. Processando Ficha PO (Motor B2) ---")
    gerador = GeradorFichaPO(demanda, leitor)

    # Exibe o resultado formatado em JSON
    json_resultado = gerador.exportar_json()
    print("\n[Saída JSON]:")
    print(json_resultado)

    # Exporta a planilha Excel formatada
    arquivo_gerado = gerador.exportar_excel("PO-SL-001_Gerada.xlsx")
    print(f"\nFicha PO exportada com sucesso para: {arquivo_gerado}")