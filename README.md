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


## Arquivos necessários na mesma pasta do `back-end.py`

| Arquivo | Para que serve |
|---|---|
| `Entradas.ods` | Cadastros de apoio (aba `MATRIZ_DE_ELEMENTOS` e aba `TEMPO-CM`) |
| `demanda_000.txt` | Dados da operação a ser roteirizada |
| `PO-SL-000.ods` | Modelo (gabarito) usado como layout da ficha exportada |

Esses três arquivos são os do kit oficial do desafio.

## Como executar


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

## Formato do arquivo de demanda (`.txt`)


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



## Estrutura do código (`back-end.py`)

## Premissas

## Licença e propriedade intelectual

Conforme o regulamento do hackathon, os direitos autorais e de propriedade intelectual do código-fonte pertencem aos alunos participantes.
