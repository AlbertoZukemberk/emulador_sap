# **Emulador SAP-1 com Interface Gráfica e Animação**

Este projeto é um emulador do microcomputador didático SAP-1 (Simple-As-Possible 1), uma implementação visual e interativa da arquitetura detalhada no livro "Digital Computer Electronics" de Albert Paul Malvino. Desenvolvido para fins educacionais na disciplina de Arquitetura de Computadores, o software permite aos usuários escrever código Assembly para o SAP-1, montá-lo e observar sua execução passo a passo, com animações visuais dos componentes internos da CPU.

## **Descrição**

O emulador SAP-1 recria o funcionamento básico de um computador, focando na sua arquitetura fundamental. Ele simula os principais blocos funcionais do SAP-1, como o Contador de Programa (PC), Registrador de Endereço de Memória (MAR), Memória RAM, Registrador de Instruções (IR), Acumulador (ACC), Registrador B, Unidade Lógica Aritmética (ULA) e Registrador de Saída com LEDs.

## **Funcionalidades**

O emulador oferece um conjunto robusto de funcionalidades para o estudo interativo do SAP-1:

* **Emulação Precisa do SAP-1**: Simula o ciclo de busca-decodifica-executa de cada instrução do SAP-1 conforme descrito por Malvino.  
* **Interface Gráfica Intuitiva e Aprimorada**:  
  * Permite fácil interação para carregar, montar e executar programas.  
  * Possui um tema visual moderno (clam), botões com estilo aprimorado e sombras sutis nos componentes da CPU para uma estética mais agradável.  
* **Nova Entrada de Expressão Numérica**:  
  * Adiciona uma área dedicada para digitar expressões matemáticas simples (e.g., "5+3", "10-2") usando botões numéricos e de operação.  
  * **Gera automaticamente o código Assembly** correspondente à expressão, inserindo-o no editor principal. Esta funcionalidade foi inspirada em exemplos práticos dados em aula pelo Professor Cláudio, tornando a programação para cálculos básicos muito mais acessível.  
* **Editor Assembly Integrado**: Um editor de texto simples onde o código Assembly pode ser escrito e editado. A linha de instrução atualmente em execução é destacada visualmente.  
* **Montador (Assembler)**: Traduz o código Assembly (mnemônicos) em código de máquina binário, que é carregado na memória simulada do SAP-1. Suporta diretivas ORG e DB, e ignora comentários. Erros de montagem são identificados e destacados na linha correspondente do editor.  
* **Visualização Animada da CPU**: Componentes da CPU e fluxos de dados são animados para ilustrar o caminho da instrução e dos dados em tempo real durante a execução. O valor intermediário de operações é exibido na ULA para maior clareza.  
* **Controle de Execução**: Permite execução contínua (Executar) ou passo a passo (Passo a Passo), com controle de velocidade do clock.  
* **Visualização de Registradores e Memória**: Exibe o conteúdo atual de todos os registradores e de cada posição da memória RAM, com destaque para a célula de memória sendo acessada.  
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

## **Vídeo Demonstrativo**
* \- https://youtu.be/KukRnkmfO_s

## **Tecnologias Utilizadas**

* **Python**: Linguagem de programação principal.  
* **Tkinter**: Biblioteca padrão do Python para criação de interfaces gráficas. Utilizada para construir a GUI e as animações.

## **Autor**

* **Marcus Meleiro** \- [https://github.com/marcusmelleiro](https://github.com/marcusmelleiro)
