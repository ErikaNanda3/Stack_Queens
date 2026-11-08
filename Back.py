from turtle import tt
from altair import Dict


class ElementoMTM:
    def __init__ (self, codigo: str, descricao: str, frequencia: int, tempo_min: float):
        self.codigo = codigo
        self.descricao = descricao
        self.frequencia = frequencia
        self.tempo_min = tempo_min
        
class Equipamento:
    def __init__(self, nome: str, tempo_por_metro: float):
        self.nome = nome
        self.tempo_por_metro = tempo_por_metro

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
                {"codigo": "FIXO", "descricao": "Tempo de costura", "frequencia": 1, "tempo_min": tempo_costura}
            ]
            for e in self.elementos:
                linhas.append({
                    "codigo": e.codigo,
                    "descricao": e.descricao,
                    "frequencia": e.frequencia,
                    "tempo_min": e.tempo_min
                })
            return {
                "operacao": self.nome,
                "perimetro_costura": self.perimetro_costura,
                "equipamento": self.equipamento.nome,
                "linhas": linhas
            }

            total_tempo = tempo_costura + sum(e.tempo_min * e.frequencia for e in self.elementos)
            total_tempo_horas = total_tempo / 60
            total_frequencia = 1 + sum(e.frequencia for e in self.elementos)
            total_tempo_medio = total_tempo / total_frequencia if total_frequencia > 0 else 0
# ----------------------------------------------------------------------
#                    Função auxiliar
# ----------------------------------------------------------------------

def valorDecimal(valor):
    try:
        return float(valor)
    except ValueError:
        return 0.0
    
# -----------------------------------------------------------------------
#                   Leitor de planilhas
# -----------------------------------------------------------------------

class LerPlanilha:
    
    def __init__(self, caminho_entradas: str):
            self.caminho_entradas = caminho_entradas
            self.catalogo_mtm: Dict[str, ElementoMTM] = {}
            self.maquinas: Dict[int, Equipamento] = {}
            self._carregar_bases_estaticas()

def ler_aba(self, aba= str, cabecalho: int = 0):
    df = tt.read_excel(self.caminho_entradas, sheet_name=aba, header=cabecalho)
    return df

def carrega_estatisticas(self):
    df_mtm = self.ler_aba(aba="MTM")
    for _, row in df_mtm.iterrows():
        elemento = ElementoMTM(
            codigo=row["Código"],
            descricao=row["Descrição"],
            frequencia=int(row["Frequência"]),
            tempo_min=valorDecimal(row["Tempo (min)"])
        )
        self.catalogo_mtm[elemento.codigo] = elemento

    df_maquinas = self.ler_aba(aba="Maquinas")
    for _, row in df_maquinas.iterrows():
        equipamento = Equipamento(
            nome=row["Nome"],
            tempo_por_metro=valorDecimal(row["Tempo por metro"])
        )
        self.maquinas[equipamento.nome] = equipamento
        
        