from typing import Dict
import pandas as pd


class ElementoMTM:

    def __init__(
        self, codigo: str, descricao: str, frequencia: int, tempo_min: float
    ):
        self.codigo = codigo
        self.descricao = descricao
        self.frequencia = frequencia
        self.tempo_min = tempo_min


class Equipamento:

    def __init__(
        self, nome: str, tempo_por_metro: float, rpm_padrao: float = 0.0):
        self.nome = nome
        self.tempo_por_metro = tempo_por_metro
        self.rpm_padrao = rpm_padrao

    @property
    def rpm_inferior(self):
        return self.rpm_padrao * 0.9

    @property
    def rpm_superior(self):
        return self.rpm_padrao * 1.1


class Peca:

    def __init__(self, familia: str, tamanho: str, medidas: str):
        self.familia = familia
        self.tamanho = tamanho
        self.medidas = medidas
class Operacao:

    def __init__(self, nome: str, perimetro_costura: float, equipamento: Equipamento):
        
        self.nome = nome
        self.perimetro_costura = perimetro_costura
        self.equipamento = equipamento
        self.elementos = []

    def adicionar_elemento(self, elemento: ElementoMTM):
        self.elementos.append(elemento)

    def relatorio_po(self):
        tempo_costura = round(self.perimetro_costura * self.equipamento.tempo_por_metro, 4)
        linhas = [
            {
                "codigo": "FIXO",
                "descricao": "Tempo de costura",
                "frequencia": 1,
                "tempo_min": tempo_costura,
            }
        ]
        for e in self.elementos:
            linhas.append(
                {
                    "codigo": e.codigo,
                    "descricao": e.descricao,
                    "frequencia": e.frequencia,
                    "tempo_min": e.tempo_min,
                }
            )

        # Cálculos de totais posicionados antes do retorno
        total_tempo = tempo_costura + sum(e.tempo_min * e.frequencia for e in self.elementos)
        total_tempo_horas = total_tempo / 60
        total_frequencia = 1 + sum(e.frequencia for e in self.elementos)

        return {
            "operacao": self.nome,
            "perimetro_costura": self.perimetro_costura,
            "equipamento": self.equipamento.nome,
            "linhas": linhas,
            "total_tempo_min": round(total_tempo, 4),
            "total_tempo_horas": round(total_tempo_horas, 4),
            "total_frequencia": total_frequencia,
        }


# ----------------------------------------------------------------------
#                     Função auxiliar
# ----------------------------------------------------------------------

def valorDecimal(valor):
    try:
        return float(valor)
    except (ValueError, TypeError):
        return 0.0

# -----------------------------------------------------------------------
#                 Leitor de planilhas
# -----------------------------------------------------------------------
class LerPlanilha:

    def __init__(self, caminho_entradas: str):
        self.caminho_entradas = caminho_entradas
        self.catalogo_mtm: Dict[str, ElementoMTM] = {}
        self.maquinas: Dict[str, Equipamento] = {}
        self.carrega_estatisticas()

    def ler_aba(self, aba: str, cabecalho: int = 0):
        df = pd.read_excel(
            self.caminho_entradas, sheet_name=aba, header=cabecalho
        )
        return df

    def carrega_estatisticas(self):
        # Leitura da aba de Elementos MTM
        try:
            aba_mtm = self.ler_aba(aba="MATRIZ_DE_ELEMENTOS")
        except Exception:
            aba_mtm = self.ler_aba(aba="MTM")

        for _, linha in aba_mtm.iterrows():
            codigo = str(
                linha.get("elemento + agrupador", linha.get("Código", ""))
            )
            descricao = str(
                linha.get(
                    "Descrição do elemento", linha.get("Descrição", "")
                )
            )
            frequencia = int(linha.get("Frequência", 1))
            tempo_min = valorDecimal(
                linha.get("Tempo", linha.get("Tempo (min)", 0))
            )

            elemento = ElementoMTM(
                codigo=codigo,
                descricao=descricao,
                frequencia=frequencia,
                tempo_min=tempo_min,
            )
            self.catalogo_mtm[elemento.codigo] = elemento

        # Leitura da aba de Máquinas
        try:
            aba_maquinas = self.ler_aba(aba="TEMPO-CM")
        except Exception:
            aba_maquinas = self.ler_aba(aba="Maquinas")

        for _, linha in aba_maquinas.iterrows():
            nome = str(
                linha.get(
                    "Descrição / Modelo", linha.get("Nome", "")
                )
            )
            tempo_por_metro = valorDecimal(
                linha.get(
                    "Tempo por metro", linha.get("Tempo por Metro", 0)
                )
            )
            rpm_padrao = valorDecimal(
                linha.get("RPM Padrão", linha.get("RPM", 0))
            )

            equipamento = Equipamento(
                nome=nome,
                tempo_por_metro=tempo_por_metro,
                rpm_padrao=rpm_padrao,
            )
            self.maquinas[equipamento.nome] = equipamento