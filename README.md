# **Emulador SAP-1**

Este projeto é um emulador do microcomputador didático SAP-1 (Simple-As-Possible 1), uma implementação visual e interativa da arquitetura detalhada no livro "Digital Computer Electronics" de Albert Paul Malvino. Desenvolvido para fins educacionais na disciplina de Arquitetura de Computadores, o software permite aos usuários escrever código Assembly para o SAP-1, montá-lo e observar sua execução passo a passo, com animações visuais dos componentes internos da CPU.

## **Descrição**

O emulador SAP-1 recria o funcionamento básico de um computador, focando na sua arquitetura fundamental. Ele simula os principais blocos funcionais do SAP-1, como o Contador de Programa (PC), Registrador de Endereço de Memória (MAR), Memória RAM, Registrador de Instruções (IR), Acumulador (ACC), Registrador B, Unidade Lógica Aritmética (ULA) e Registrador de Saída com LEDs.

## **Funcionalidades**

* **Emulação Precisa do SAP-1**: Simula o ciclo de busca-decodifica-executa de cada instrução do SAP-1 conforme descrito por Malvino.  
* **Interface Gráfica Intuitiva**: Permite fácil interação para carregar, montar e executar programas.  
* **Editor Assembly Integrado**: Um editor de texto simples onde o código Assembly pode ser escrito e editado.  
* **Montador (Assembler)**: Traduz o código Assembly (mnemônicos) em código de máquina binário, que é carregado na memória simulada do SAP-1. Suporta diretivas ORG e DB, e ignora comentários.  
* **Visualização Animada da CPU**: Componentes da CPU e fluxos de dados são animados para ilustrar o caminho da instrução e dos dados em tempo real durante a execução.  
* **Controle de Execução**: Permite execução contínua (Executar) ou passo a passo (Passo a Passo), com controle de velocidade do clock.  
* **Visualização de Registradores e Memória**: Exibe o conteúdo atual de todos os registradores e de cada posição da memória RAM.  
* **Indicador Visual de Saída**: LEDs simulados mostram o valor binário do registrador de saída.  
* **Legenda de Cores**: Inclui uma legenda visual para auxiliar na compreensão das animações e destaques.

## **Arquitetura do SAP-1**

O SAP-1 é um computador de 8 bits com 16 bytes de memória RAM, projetado para ensinar os conceitos básicos de um microprocessador. Sua arquitetura é baseada em um barramento único (Barramento W) e um conjunto de instruções reduzido.  
**Componentes Principais (referência ao Capítulo 10 do livro "Digital Computer Electronics" de Albert Paul Malvino):**

* **Contador de Programa (PC)**: Seção 10.1  
* **Registrador de Endereço de Memória (MAR/REM)**: Seção 10.1  
* **Memória RAM (16x8)**: Seção 10.1  
* **Registrador de Instruções (IR)**: Seção 10.1  
* **Acumulador (ACC)**: Seção 10.1  
* **Registrador B**: Seção 10.1  
* **Unidade Lógica Aritmética (ULA) / Somador-Subtrator**: Seção 10.1  
* **Registrador de Saída e LEDs**: Seção 10.1  
* **Barramento W**: Fig. 10-1

**Conjunto de Instruções (referência à Tabela 10-1 e 10-2 do artigo):**

* LDA \<endereço\>: Carrega o acumulador com o conteúdo da memória.  
* ADD \<endereço\>: Soma o conteúdo da memória ao acumulador.  
* SUB \<endereço\>: Subtrai o conteúdo da memória do acumulador.  
* OUT: Transfere o conteúdo do acumulador para o registrador de saída.  
* HLT: Interrompe a execução do programa.

## **Tecnologias Utilizadas**

* **Python**: Linguagem de programação principal.  
* **Tkinter**: Biblioteca padrão do Python para criação de interfaces gráficas. Utilizada para construir a GUI e as animações.

## **Como Executar**

### **Pré-requisitos**

Certifique-se de ter o Python 3 instalado em seu sistema. O Tkinter geralmente já vem incluído com a instalação padrão do Python.

### **Instalação**

1. Clone este repositório para sua máquina local:  
   git clone https://github.com/\[SeuUsuario\]/\[SeuRepositorio\].git  
   cd \[SeuRepositorio\]

### **Execução**

1. Execute o script principal Python:  
   python seu\_emulador\_sap1.py

   (Substitua seu\_emulador\_sap1.py pelo nome do arquivo principal do seu projeto, se for diferente de main.py).

## **Uso**

1. **Carregar Exemplo**: Clique no botão "Carregar Exemplo" para inserir um programa Assembly pré-definido no editor.  
2. **Montar**: Após carregar ou escrever seu código Assembly, clique em "Montar". O montador irá traduzir o código para a linguagem de máquina do SAP-1 e carregá-lo na memória simulada. Erros de sintaxe serão exibidos na barra de status.  
3. **Executar**: Clique em "Executar" para que o programa seja executado continuamente. A simulação parará ao encontrar a instrução HLT ou ao final da memória.  
4. **Passo a Passo**: Clique em "Passo a Passo" para executar uma instrução por vez. Isso é ideal para depuração e para observar as animações detalhadas dos componentes da CPU.  
5. **Reset**: Clique em "Reset" para limpar todos os registradores, a memória e reiniciar o estado da CPU, pronto para um novo programa.  
6. **Velocidade do Clock**: Use o slider "Velocidade do Clock" para ajustar a velocidade da simulação em tempo real.

## **Exemplo de Código Assembly**

; Exemplo SAP-1: Soma 5 \+ 3  
; Conforme descrito no Capítulo 10 do livro de Malvino.  
; O programa ocupa endereços 00-03 (4 bytes de instruções).  
; Os dados ocupam endereços 0E-0F (2 bytes de dados).

LDA 0E   ; Carrega o valor do endereço de memória 0E (5 decimal) para o Acumulador (ACC).  
ADD 0F   ; Soma o valor do endereço de memória 0F (3 decimal) ao conteúdo atual do ACC.  
OUT      ; Transfere o resultado do ACC para o Registrador de Saída, que é exibido nos LEDs.  
HLT      ; Para a execução do programa. Essencial para indicar o fim do programa (Seção 10.2).

ORG 0E   ; Diretiva para o montador: Começa a armazenar os dados a partir do endereço de memória 0E.  
DB 5     ; Define Byte: Armazena o valor decimal 5 no endereço de memória atual (0E).  
DB 3     ; Define Byte: Armazena o valor decimal 3 no próximo endereço de memória (0F).

## **Autor**

* **Marcus Meleiro** \- [https://github.com/marcusmelleiro](https://github.com/marcusmelleiro)
