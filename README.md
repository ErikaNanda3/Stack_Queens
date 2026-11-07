# Auto-T&M Karsten — Gerador Automático de Processo Operacional (PO)

Solução desenvolvida pela equipe **Stake Queens** para o **Hackathon Auto-T&M Karsten**, competição de inovação e desenvolvimento de software promovida pela **Universidade Tecnológica Federal do Paraná, câmpus Apucarana (UTFPR-AP)** em parceria com a **Karsten S.A.**

## Equipe

| Integrante | R.A. |
|---|---|
| Arieli Leandro Gutierres | a2669447 |
| Anna Beatriz Correia dos Santos | a2586436 |
| Érika Fernanda Santos de Souza | a2478382 |

## O que o programa faz

Automatiza a formação de tempos operacionais da Engenharia de Tempos e Métodos (T&M):

1. **Lê os cadastros de apoio** da planilha `Entradas.ods`: catálogo de elementos MTM (aba `MATRIZ_DE_ELEMENTOS`) e máquinas de costura (aba `TEMPO-CM`).
2. **Lê a demanda** (produto, equipamento e sequência de elementos) de um arquivo `.txt`.
3. **Calcula os tempos**:
   - **FIXO (costura)** = `Perímetro de costura (m) × Tempo por metro da máquina (min/m)`
   - **Tempo Total (TP)** = soma do FIXO + todos os elementos MTM (cada tempo multiplicado pela frequência, que hoje é sempre 1)
   - O TP também é apresentado em **horas** (`minutos ÷ 60`) e em **dias** (`horas ÷ 8`, jornada de trabalho; veja "Configurações").
4. **Exibe a ficha na tela** e **exporta** a ficha em `.ods` no layout do modelo `PO-SL-000.ods`.

## Requisitos

- **Python 3.10 ou superior** (testado com Python 3.13; o desenvolvimento no Windows usou Python 3.14)
- Bibliotecas: `pandas` e `odfpy` (listadas em `requirements.txt`)

## Instalação

1. Clone o repositório (ou baixe e extraia o ZIP):

   ```bash
   git clone <URL-DO-REPOSITORIO>
   cd <PASTA-DO-REPOSITORIO>
   ```

2. (Opcional, recomendado) Crie um ambiente virtual:

   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

## Arquivos necessários na mesma pasta do `back-end.py`

| Arquivo | Para que serve |
|---|---|
| `Entradas.ods` | Cadastros de apoio (aba `MATRIZ_DE_ELEMENTOS` e aba `TEMPO-CM`) |
| `demanda_000.txt` | Dados da operação a ser roteirizada |
| `PO-SL-000.ods` | Modelo (gabarito) usado como layout da ficha exportada |

Esses três arquivos são os do kit oficial do desafio.

## Como executar

Na pasta do projeto:

```bash
python back-end.py
```

(No Windows, se `python` não for reconhecido, use `py back-end.py`.)

### Resultado esperado para o cenário oficial (`demanda_000.txt`)

```
=== FICHA GERADA AUTOMATICAMENTE ===
Título: PO-SL-001  (Rev. 00)
Operação: Bainhar no corpo do SL - 1 lado
Peça: Sobre-lençol / Solteiro / 1,80 x 2,50
Pontos/cm: 2.5  |  Perímetro: 6.96 m
Equipamento: [1] Interlock  RPM 4500 / 5000 / 5500
--------------------------------------------------
ELEMENTOS:
 - [FIXO] Tempo de costura (x1): 0.6709 min
 - [2.1] Apanhar peça e posicionar na mesa (x1): 0.15 min
 - [1.1] Costurar Elemento (sem tempo) (x1): 0.0 min
 - [3.1] Ajeitar peça (x1): 0.12 min
--------------------------------------------------
TEMPO TOTAL DA OPERAÇÃO (TP): 0.9409 min
                              0.015682 h
                              0.00196 dia(s) de 8 h

Ficha salva em: .../PO-SL-001_gerada.ods
```

Além da tela, é gerado o arquivo **`PO-SL-001_gerada.ods`** (nome = título da operação + `_gerada.ods`), com o mesmo layout do `PO-SL-000.ods` mais as linhas de **TP** em minutos, horas e dias. Se o `PO-SL-000.ods` não estiver na pasta, o programa mostra a ficha na tela e avisa que não gerou o `.ods`.

## Formato do arquivo de demanda (`.txt`)

Uma informação por linha, no formato `Chave: valor`. Acentos e maiúsculas nas chaves são ignorados.

```
Título: PO-SL-001
REV: 00
Operação: "Bainhar no corpo do SL - 1 lado"
Agrupamento família: Sobre-lençol
Tamanho: Solteiro
Medidas da peça (em m): 1,80 x 2,50
Pontos/cm: 2,50
Perímetro costura (em m): 6,96
Cód. Eqp: 1
Elementos: 2.1, 1.1, 3.1
```

- `Cód. Eqp` deve existir na aba `TEMPO-CM` (1, 2 ou 3 no kit oficial); caso contrário o programa para com uma mensagem de erro.
- `Elementos` é a sequência ordenada de códigos MTM separados por vírgula. Códigos que não existem no catálogo geram um aviso e são ignorados.
- Números aceitam vírgula ou ponto como separador decimal.

## Configurações

No topo de `back-end.py`:

```python
HORAS_POR_DIA = 8   # 8 = jornada de trabalho; use 24 para dia corrido
```

## Estrutura do código (`back-end.py`)

| Parte | Responsabilidade |
|---|---|
| `ElementoMTM`, `Equipamento`, `Peca`, `ProcessoOperacional` | Modelo de dados e motor de cálculo (`gerar_relatorio_po`) |
| `LeitorPlanilhas` | Leitura de `Entradas.ods` e do arquivo de demanda `.txt` |
| `exportar_po_ods` | Preenche o modelo `PO-SL-000.ods` e salva a ficha final |
| bloco `if __name__ == "__main__"` | Fluxo completo: ler → calcular → exibir → exportar |

## Premissas

- Os **limites de RPM** (inferior e superior) são calculados como padrão × 0,9 e padrão × 1,1, a mesma regra das fórmulas do modelo `PO-SL-000.ods`.
- A conversão de **horas em dias** usa `HORAS_POR_DIA = 8` (ajustável).
- A **frequência** de cada elemento é 1, como no gabarito oficial.

## Solução de problemas

| Mensagem | O que fazer |
|---|---|
| `ModuleNotFoundError: No module named 'odf'` | Rode `pip install odfpy` |
| `ModuleNotFoundError: No module named 'pandas'` | Rode `pip install pandas` |
| `FileNotFoundError: ... Entradas.ods` (ou `demanda_000.txt`) | Coloque o arquivo na mesma pasta do `back-end.py` |
| `Equipamento X não existe na aba TEMPO-CM` | Confira o valor de `Cód. Eqp` na demanda |
| `[AVISO] Elemento 'X' não encontrado no catálogo MTM` | Confira os códigos em `Elementos` na demanda |

## Licença e propriedade intelectual

Conforme o regulamento do hackathon, os direitos autorais e de propriedade intelectual do código-fonte pertencem aos alunos participantes.
