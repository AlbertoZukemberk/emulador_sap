"""
Emulador SAP-1 - Implementação Completa com Interface Gráfica

Este código foi desenvolvido para um projeto da disciplina de Arquitetura de Computadores,
tendo como objetivo emular o microcontrolador SAP-1, conforme descrito no livro "Digital Computer Electronics" de Albert Malvino.

Autor: [Seu Nome]
Matrícula: [Sua Matrícula]
Disciplina: Arquitetura de Computadores
Professor: [Nome do Professor]
Data: [Data de Entrega]
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time

class SAP1Emulator:
    def __init__(self, root):
        """
        Inicializa o emulador SAP-1 com a interface gráfica.
        
        A implementação da arquitetura e o funcionamento do SAP-1 é baseado no Capítulo 10 do livro
        "Digital Computer Electronics" de Albert Paul Malvino.
        """
        self.root = root
        self.root.title("Emulador SAP-1 - Arquitetura de Computadores")
        self.setup_ui()
        self.initialize_cpu()
        
        # Variáveis de controle para o ciclo de instrução e a simulação
        self.running = False
        self.clock_speed = 1.0  # Velocidade padrão do clock (1Hz)
        
    def setup_ui(self):
        """
        Configura a interface gráfica do emulador.
        Organiza os elementos visuais como o editor de código, controle e a visualização da CPU.
        """
        # Aplica um estilo ttk moderno para uma aparência melhor
        style = ttk.Style()
        style.theme_use('clam') # 'clam' ou 'alt' costumam ser mais planos e modernos

        # Configura o estilo dos botões
        style.configure('TButton',
                        font=('Arial', 10, 'bold'),
                        foreground='black',
                        background='#e0e0e0',
                        padding=6,
                        relief='raised', # 'raised', 'flat', 'sunken', 'groove', 'ridge'
                        borderwidth=2)
        style.map('TButton',
                  background=[('active', '#c0c0c0'), ('pressed', '#a0a0a0')])
        
        # Cria o frame principal para organizar a janela
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Define a área dedicada ao editor de código Assembly
        code_frame = ttk.LabelFrame(main_frame, text="Código Assembly", padding="10")
        code_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        # Cria a caixa de texto para o editor de código, com tamanho e fonte específicos
        self.editor = tk.Text(code_frame, wrap=tk.NONE, width=35, height=12, 
                            font=('Courier', 12), relief="sunken", borderwidth=2) # Adicionei relevo
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Adiciona uma barra de rolagem vertical ao editor para facilitar a navegação no código
        scrollbar = ttk.Scrollbar(code_frame, orient=tk.VERTICAL, command=self.editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor['yscrollcommand'] = scrollbar.set
        
        # Cria o painel de controle que conterá os botões de interação do usuário
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.pack(fill=tk.Y, side=tk.LEFT)
        
        # Adiciona os botões para as funcionalidades do emulador
        ttk.Button(control_frame, text="Carregar Exemplo", 
                  command=self.load_example).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Montar", 
                  command=self.assemble).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Executar", 
                  command=self.run_program).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Passo a Passo", 
                  command=self.step).pack(fill=tk.X, pady=5)
        ttk.Button(control_frame, text="Reset", 
                  command=self.reset_cpu).pack(fill=tk.X, pady=5)
        
        # Cria a seção para controlar a velocidade da simulação do clock
        speed_frame = ttk.LabelFrame(control_frame, text="Velocidade do Clock", padding="5")
        speed_frame.pack(fill=tk.X, pady=10)
        self.speed_slider = ttk.Scale(speed_frame, from_=0.1, to=2.0, value=1.0,
                                    command=self.update_speed,
                                    orient=tk.HORIZONTAL, length=150) # Ajustei o tamanho do slider
        self.speed_slider.pack(fill=tk.X)
        
        # Cria o frame para a visualização gráfica da CPU
        cpu_frame = ttk.LabelFrame(main_frame, text="Visualização da CPU", padding="10")
        cpu_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cria o Canvas principal onde os componentes da CPU serão desenhados e animados
        self.canvas = tk.Canvas(cpu_frame, width=850, height=600, bg="#f0f0f0", relief="sunken", borderwidth=2) # Fundo mais claro e relevo
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Cria a barra de status na parte inferior para exibir mensagens ao usuário
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto para executar")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, padding="5", font=('Arial', 10))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Chama a função para desenhar os componentes da CPU na inicialização da interface
        self.draw_cpu_components()
        # Adiciona a legenda de cores ao canvas
        self.draw_legend()
    
    def draw_cpu_components(self):
        """
        Desenha os componentes da CPU SAP-1 no canvas, baseando-se na arquitetura de barramento único
        apresentada na Fig. 10-1 do artigo do Malvino.
        """
        self.canvas.delete("all") # Limpa o canvas antes de redesenhar
        
        # Cores para os elementos visuais
        reg_color = "#e6f3ff"  # Cor de fundo dos registradores
        shadow_color = "#cccccc" # Cor para simular sombra
        bus_color = "#666666"    # Cor do barramento

        # Função auxiliar para desenhar um componente com sombra
        def create_component_with_shadow(x1, y1, x2, y2, fill_color, tags, text_label, text_tag, text_value_tag, default_value, font_label, font_value):
            # Desenha a sombra primeiro
            self.canvas.create_rectangle(x1 + 5, y1 + 5, x2 + 5, y2 + 5, fill=shadow_color, tags=f"{tags}_shadow", width=0)
            # Desenha o componente principal
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, tags=tags, width=2, outline=bus_color)
            self.canvas.create_text((x1+x2)/2, y1 + (y2-y1)/3, text=text_label, tags=text_tag, font=font_label)
            self.canvas.create_text((x1+x2)/2, y1 + 2*(y2-y1)/3, text=default_value, tags=text_value_tag, font=font_value)

        # Barramento Principal Horizontal (Barramento W - Fig. 10-1 do artigo)
        BUS_Y = 320 
        self.canvas.create_line(30, BUS_Y, 820, BUS_Y, width=4, fill=bus_color, tags="main_bus")

        # Desenha e posiciona o Contador de Programa (PC) - Referência: Seção 10.1 do artigo
        create_component_with_shadow(50, 50, 200, 125, reg_color, "pc", "PC", "pc_text", "pc_value", "0x00", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_line(125, 125, 125, BUS_Y, width=2, fill=bus_color, tags="pc_to_bus")

        # Desenha e posiciona o Registrador de Endereço de Memória (MAR/REM) - Referência: Seção 10.1 do artigo
        create_component_with_shadow(250, 50, 400, 125, reg_color, "mar", "MAR", "mar_text", "mar_value", "0x00", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_line(325, 125, 325, BUS_Y, width=2, fill=bus_color, tags="mar_to_bus")

        # Desenha e posiciona o Registrador de Instruções (IR) - Referência: Seção 10.1 do artigo
        create_component_with_shadow(450, 50, 600, 125, reg_color, "ir", "IR", "ir_text", "ir_value", "0x0000", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_text(525, 25, text="IR (Opcode | Operando)", font=('Arial', 10), fill="gray")
        self.canvas.create_line(525, 125, 525, BUS_Y, width=2, fill=bus_color, tags="ir_to_bus")

        # Desenha e posiciona o Acumulador (ACC/Registrador A) - Referência: Seção 10.1 do artigo
        create_component_with_shadow(50, 200, 200, 275, reg_color, "acc", "ACC", "acc_text", "acc_value", "0x00", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_line(125, 275, 125, BUS_Y, width=2, fill=bus_color, tags="acc_to_bus_main")
        # Conexão direta do ACC para a ULA (para o operando A da ULA)
        self.canvas.create_line(200, 237.5, 250, 237.5, width=2, fill=bus_color, tags="acc_to_alu_direct")

        # Desenha e posiciona o Registrador B - Referência: Seção 10.1 do artigo
        create_component_with_shadow(250, 200, 400, 275, reg_color, "b_reg", "Reg B", "b_reg_text", "b_reg_value", "0x00", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_line(325, 275, 325, BUS_Y, width=2, fill=bus_color, tags="b_reg_to_bus_main")
        # Conexão direta do Registrador B para a ULA (para o operando B da ULA)
        self.canvas.create_line(400, 237.5, 450, 237.5, width=2, fill=bus_color, tags="b_reg_to_alu_direct")

        # Desenha e posiciona a ULA (Unidade Lógica Aritmética / Somador-Subtrator) - Referência: Seção 10.1 do artigo
        create_component_with_shadow(450, 200, 600, 275, reg_color, "alu", "ULA", "alu_text", "alu_value", "", ('Arial', 14, 'bold'), ('Courier', 12)) # ULA não tem valor direto
        self.canvas.create_line(525, 275, 525, BUS_Y, width=2, fill=bus_color, tags="alu_to_bus_main") # Saída da ULA para o barramento

        # Desenha e posiciona a Memória RAM (16 bytes, 16x8) - Referência: Seção 10.1 e Fig. 10-1 do artigo
        MEM_X_START = 650
        MEM_Y_START = 50
        MEM_WIDTH = 180 
        MEM_HEIGHT = 280 
        self.canvas.create_rectangle(MEM_X_START + 5, MEM_Y_START + 5, MEM_X_START + MEM_WIDTH + 5, MEM_Y_START + MEM_HEIGHT + 5, fill=shadow_color, tags="mem_block_shadow", width=0)
        self.canvas.create_rectangle(MEM_X_START, MEM_Y_START, MEM_X_START + MEM_WIDTH, MEM_Y_START + MEM_HEIGHT, fill="#f0f8ff", width=2, tags="mem_block", outline=bus_color)
        self.canvas.create_text(MEM_X_START + MEM_WIDTH/2, MEM_Y_START - 20, text="MEMÓRIA (16 bytes)", tags="mem_title", font=('Arial', 14, 'bold'))
        self.canvas.create_line(MEM_X_START + MEM_WIDTH/2, MEM_Y_START + MEM_HEIGHT, MEM_X_START + MEM_WIDTH/2, BUS_Y, width=2, fill=bus_color, tags="mem_to_bus_main") 

        # Cria as células de memória organizadas em uma grade 4x4
        self.memory_cells = []
        self.memory_text_ids = []
        self.memory_addr_ids = []

        cell_width_inner = 35
        cell_height_inner = 30
        gap_x_inner = 7
        gap_y_inner = 7
        mem_grid_start_x = MEM_X_START + 10 
        mem_grid_start_y = MEM_Y_START + 30 
        
        for i in range(16):
            col = i % 4
            row = i // 4
            x1 = mem_grid_start_x + col * (cell_width_inner + gap_x_inner)
            y1 = mem_grid_start_y + row * (cell_height_inner + gap_y_inner)
            x2 = x1 + cell_width_inner
            y2 = y1 + cell_height_inner
            
            cell = self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", tags=f"mem_{i}", width=1, outline="lightgray")
            self.memory_cells.append(cell)
            
            text_id = self.canvas.create_text(x1 + cell_width_inner/2, y1 + cell_height_inner/2, text="00", tags=f"mem_text_{i}", font=('Courier', 10, 'bold'))
            self.memory_text_ids.append(text_id)

            addr_id = self.canvas.create_text(x1 + cell_width_inner/2, y1 - 10, text=f"{i:02X}", tags=f"mem_addr_{i}", font=('Arial', 8), fill="gray")
            self.memory_addr_ids.append(addr_id)
        
        # Desenha e posiciona o Registrador de Saída (Output Register) e o Indicador Visual em Binário (LEDs) - Referência: Seção 10.1 do artigo
        create_component_with_shadow(50, 400, 200, 475, "#f0f0f0", "output_reg", "SAÍDA", "output_text_label", "output_value", "0x00", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_line(125, 400, 125, BUS_Y, width=2, fill=bus_color, tags="output_to_bus_main")

        # Representação visual dos LEDs de Saída
        led_start_x = 50
        led_start_y = 500
        self.led_rects = []
        for i in range(8):
            x = led_start_x + i * 20
            led = self.canvas.create_oval(x, led_start_y, x+15, led_start_y+15, fill="lightgray", outline="gray")
            self.led_rects.append(led)
            self.canvas.create_text(x+7, led_start_y+25, text=f"{7-i}", font=('Arial', 8))

        # Desenha e posiciona o Clock (CLK) - Referência: Seção 10.7 (Circuitos de Relógio) e Fig. 10-2 do artigo
        self.canvas.create_oval(700, 400, 775, 475, fill="#f0f0f0", width=2, tags="clock", outline=bus_color)
        self.canvas.create_text(737.5, 437.5, text="CLK", tags="clock_text", font=('Arial', 14, 'bold'))
    
    def draw_legend(self):
        """
        Adiciona uma legenda de cores ao canvas para explicar o significado dos destaques visuais.
        Coloquei a legenda num canto para não atrapalhar os componentes principais.
        """
        # Posição da legenda no canto inferior direito do canvas
        legend_x = 650
        legend_y = 480
        line_height = 20

        self.canvas.create_text(legend_x, legend_y, anchor="nw", text="Legenda de Cores:", font=('Arial', 10, 'bold'))

        # Componente Ativo / Bus Ativo
        self.canvas.create_rectangle(legend_x, legend_y + line_height, legend_x + 15, legend_y + line_height + 15, fill="#ff9999", outline="gray")
        self.canvas.create_text(legend_x + 20, legend_y + line_height + 7, anchor="w", text="Componente/Barramento Ativo", font=('Arial', 9))

        # Memória Acessada
        self.canvas.create_rectangle(legend_x, legend_y + 2 * line_height, legend_x + 15, legend_y + 2 * line_height + 15, fill="#ffff99", outline="gray")
        self.canvas.create_text(legend_x + 20, legend_y + 2 * line_height + 7, anchor="w", text="Memória Acessada", font=('Arial', 9))
        
        # LED Ligado (Bit 1)
        self.canvas.create_oval(legend_x, legend_y + 3 * line_height, legend_x + 15, legend_y + 3 * line_height + 15, fill="red", outline="gray")
        self.canvas.create_text(legend_x + 20, legend_y + 3 * line_height + 7, anchor="w", text="LED Ligado (Bit 1)", font=('Arial', 9))

        # LED Desligado (Bit 0)
        self.canvas.create_oval(legend_x, legend_y + 4 * line_height, legend_x + 15, legend_y + 4 * line_height + 15, fill="lightgray", outline="gray")
        self.canvas.create_text(legend_x + 20, legend_y + 4 * line_height + 7, anchor="w", text="LED Desligado (Bit 0)", font=('Arial', 9))


    def initialize_cpu(self):
        """
        Inicializa o estado dos componentes da CPU SAP-1, definindo os valores iniciais
        para os registradores e limpando a memória.
        A referência para isso é a Seção 10.1 do artigo (Arquitetura).
        """
        self.cpu = {
            "PC": 0,      # Contador de Programa (4 bits) - Inicia em 0000 para a primeira instrução.
            "ACC": 0,     # Acumulador (8 bits)
            "MAR": 0,     # Registrador de Endereço de Memória (4 bits)
            "IR": 0,      # Registrador de Instruções (8 bits)
            "B": 0,       # Registrador B (8 bits)
            "memory": [0] * 16,  # A memória é de 16 byte (16x8 RAM - Seção 10.1 do artigo)
            "output": 0,  # Registrador de Saída (8 bits)
            "flags": {"Z": 0, "C": 0}  # Inclui as Flags Zero e Carry, mesmo que o SAP-1 básico não as use totalmente, para futuras expansões.
        }
        
        # Mapeia os opcodes para os mnemônicos e as funções de execução correspondentes.
        # Isso reflete o Conjunto de Instruções do SAP-1 (Tabela 10-1 e Tabela 10-2 do artigo).
        self.instructions = {
            0b0000: ("LDA", self.lda), # LDA - Carrega o acumulador
            0b0001: ("ADD", self.add), # ADD - Soma ao acumulador
            0b0010: ("SUB", self.sub), # SUB - Subtrai ao acumulador
            0b1110: ("OUT", self.out), # OUT - Saída do acumulador
            0b1111: ("HLT", self.hlt)  # HLT - Parada
        }
        
        self.update_visualization() # Atualiza a interface com o estado inicial da CPU
    
    def update_visualization(self):
        """
        Atualiza os valores exibidos na interface gráfica para refletir o estado atual da CPU.
        Isso inclui o conteúdo dos registradores, da memória e o estado dos LEDs de saída.
        """
        # Atualiza os valores hexadecimais dos registradores na interface
        self.canvas.itemconfig("pc_value", text=f"0x{self.cpu['PC']:01X}")
        self.canvas.itemconfig("mar_value", text=f"0x{self.cpu['MAR']:01X}")
        self.canvas.itemconfig("ir_value", text=f"0x{self.cpu['IR']:02X}")
        self.canvas.itemconfig("acc_value", text=f"0x{self.cpu['ACC']:02X}")
        self.canvas.itemconfig("b_reg_value", text=f"0x{self.cpu['B']:02X}")
        self.canvas.itemconfig("output_value", text=f"0x{self.cpu['output']:02X}")
        
        # Atualiza o texto de cada célula de memória para exibir seu conteúdo atual
        for i in range(16):
            self.canvas.itemconfig(f"mem_text_{i}", text=f"{self.cpu['memory'][i]:02X}")
        
        # Reseta o destaque de todas as células de memória e endereços
        for i in range(16):
            self.canvas.itemconfig(f"mem_{i}", fill="white")
            self.canvas.itemconfig(f"mem_addr_{i}", fill="gray")
        # Destaca a célula de memória atualmente apontada pelo MAR
        if 0 <= self.cpu['MAR'] < 16:
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ffff99") # Amarelo para destacar
            self.canvas.itemconfig(f"mem_addr_{self.cpu['MAR']}", fill="red") # Endereço em vermelho para indicar acesso

        # Atualiza o estado visual dos LEDs de Saída com base no valor do registrador 'output'
        output_val = self.cpu['output']
        for i in range(8):
            # Verifica se o i-ésimo bit está ligado (1) ou desligado (0)
            if (output_val >> i) & 1: 
                self.canvas.itemconfig(self.led_rects[7-i], fill="red") # Liga o LED (7-i para ordem MSB a LSB)
            else:
                self.canvas.itemconfig(self.led_rects[7-i], fill="lightgray") # Desliga o LED

    def animate_main_bus_transfer(self, source_comp_tag, target_comp_tag, duration=0.3):
        """
        Anima a transferência de dados pelo barramento principal (Barramento W).
        Destaca visualmente o componente de origem, o barramento e o componente de destino.
        Baseado na Fig. 10-1 (Arquitetura de barramento único) e nas Fig. 10-3, 10-4, 10-6, 10-8 do artigo.
        """
        active_color = "#ff9999" # Cor de destaque temporário
        original_bus_color = "#666666" # Cor original do barramento
        original_reg_color = "#e6f3ff" # Cor original dos registradores

        # Infere as tags das linhas de conexão ao barramento principal
        source_conn_tag = f"{source_comp_tag}_to_bus_main" if source_comp_tag not in ["mem_block", "output_reg"] else f"{source_comp_tag[:-5]}_to_bus_main"
        target_conn_tag = f"{target_comp_tag}_to_bus_main" if target_comp_tag not in ["mem_block", "output_reg"] else f"{target_comp_tag[:-5]}_to_bus_main"

        # Tenta obter a cor original do componente de destino para resetar corretamente
        try:
            target_obj_color = self.canvas.itemcget(target_comp_tag, "fill")
        except:
            target_obj_color = original_reg_color # Fallback para a cor padrão

        # Passo 1: Destaca o componente de origem e sua linha de conexão com o barramento
        self.canvas.itemconfig(source_comp_tag, fill=active_color)
        if source_conn_tag:
            self.canvas.itemconfig(source_conn_tag, fill="red", width=3) # Ativa a linha de conexão
        self.canvas.update()
        time.sleep(duration / (3 * self.clock_speed))

        # Passo 2: Destaca o barramento principal (Barramento W)
        self.canvas.itemconfig("main_bus", fill="red", width=5) # Ativa o barramento
        self.canvas.update()
        time.sleep(duration / (3 * self.clock_speed))

        # Passo 3: Destaca a linha de conexão com o destino e o próprio componente de destino
        if target_conn_tag:
            self.canvas.itemconfig(target_conn_tag, fill="red", width=3) # Ativa a linha de conexão
        self.canvas.itemconfig(target_comp_tag, fill=active_color) # Componente destino ativo
        self.canvas.update()
        time.sleep(duration / (3 * self.clock_speed))

        # Reseta as cores e larguras para o estado original após a animação
        self.canvas.itemconfig(source_comp_tag, fill=original_reg_color)
        if source_conn_tag:
            self.canvas.itemconfig(source_conn_tag, fill=original_bus_color, width=2)
        self.canvas.itemconfig("main_bus", fill=original_bus_color, width=4)
        if target_conn_tag:
            self.canvas.itemconfig(target_conn_tag, fill=original_bus_color, width=2)
        self.canvas.itemconfig(target_comp_tag, fill=target_obj_color) # Volta para a cor original do componente destino
        self.canvas.update()
        time.sleep(0.1 / self.clock_speed) # Pequena pausa para visualização do reset

    def animate_direct_transfer(self, source_comp_tag, target_comp_tag, line_tag, duration=0.3):
        """
        Anima a transferência de dados direta entre dois componentes (sem passar pelo barramento principal).
        Exemplo: ACC para ULA, Reg B para ULA.
        """
        active_color = "#ff9999"
        original_bus_color = "#666666"
        original_reg_color = "#e6f3ff"

        # Tenta obter a cor original do componente de destino para resetar corretamente
        try:
            target_obj_color = self.canvas.itemcget(target_comp_tag, "fill")
        except:
            target_obj_color = original_reg_color # Fallback para cor padrão

        # Destaca o componente de origem, a linha de conexão direta e o componente de destino
        self.canvas.itemconfig(source_comp_tag, fill=active_color)
        self.canvas.itemconfig(line_tag, fill="red", width=3)
        self.canvas.itemconfig(target_comp_tag, fill=active_color)
        self.canvas.update()
        time.sleep(duration / self.clock_speed)

        # Reseta as cores para o estado original
        self.canvas.itemconfig(source_comp_tag, fill=original_reg_color)
        self.canvas.itemconfig(line_tag, fill=original_bus_color, width=2)
        self.canvas.itemconfig(target_comp_tag, fill=target_obj_color) # Volta para a cor original do componente destino
        self.canvas.update()
        time.sleep(0.1 / self.clock_speed)

    def animate_clock(self):
        """
        Anima o pulso de clock, simulando a transição de relógio que sincroniza as operações.
        Referência: Fig. 10-2b do artigo (Sinais de relógio e temporização) e Exemplo 10.6.
        """
        for _ in range(2): # Duas transições para simular o pulso completo (alto e baixo)
            self.canvas.itemconfig("clock", fill="#ff9999") # Clock ativo
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
            self.canvas.itemconfig("clock", fill="#f0f0f0") # Clock inativo
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
    
    def highlight_component(self, component_tag, duration=0.5):
        """
        Destaca visualmente um componente específico da CPU para indicar sua atividade.
        """
        original_reg_color = "#e6f3ff"
        original_text_color = "black"
        
        # Tenta obter a cor original do componente para resetar corretamente
        try:
            original_fill = self.canvas.itemcget(component_tag, "fill")
        except:
            original_fill = original_reg_color

        self.canvas.itemconfig(component_tag, fill="#ff9999") # Cor de destaque (vermelho claro)
        # Tenta encontrar e mudar a cor do texto associado, se existir
        text_tag = component_tag.replace("_reg", "") + "_text" if "_reg" in component_tag else component_tag + "_text"
        try:
             self.canvas.itemconfig(text_tag, fill="red") # Texto em vermelho
        except:
             pass # Não faz nada se não houver tag de texto correspondente

        self.canvas.update()
        time.sleep(duration / self.clock_speed)
        
        # Reseta as cores para o estado original
        self.canvas.itemconfig(component_tag, fill=original_fill)
        try:
            self.canvas.itemconfig(text_tag, fill=original_text_color)
        except:
            pass
        self.canvas.update()
    
    def load_example(self):
        """
        Carrega um programa exemplo no editor de código.
        Este exemplo soma 5 + 3 e exibe o resultado, utilizando as instruções básicas do SAP-1.
        O programa é desenhado para caber na memória de 16 bytes.
        """
        example_code = """; Exemplo SAP-1: Soma 5 + 3
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
"""
        self.editor.delete(1.0, tk.END) # Limpa o conteúdo atual do editor
        self.editor.insert(1.0, example_code) # Insere o código de exemplo
        self.status_var.set("Exemplo carregado: Soma 5 + 3")
    
    def assemble(self):
        """
        Monta o código Assembly para código de máquina (binário) que o emulador pode executar.
        Este processo envolve a tradução de mnemônicos para opcodes e o processamento de
        diretivas como ORG e DB, ignorando comentários.
        Referência: Seção 10.3 (Programação do SAP-1) e Tabela 10-2 (Código Op do SAP-1).
        """
        code = self.editor.get(1.0, tk.END) # Obtém todo o texto do editor
        lines = code.split('\n') # Divide o texto em linhas
        
        assembled_memory = [0] * 16 # Inicializa a memória com zeros para a montagem (16 bytes)
        
        # Ponteiros para o próximo endereço de instrução e o próximo endereço de dado
        instruction_ptr = 0
        data_ptr = None # 'None' indica que a seção de dados ainda não foi definida por uma diretiva ORG
        
        try:
            for line_num, line in enumerate(lines, 1): # Itera sobre cada linha, com seu número
                line = line.strip() # Remove espaços em branco do início e fim da linha
                if not line: # Ignora linhas completamente vazias
                    continue
                
                # Remove comentários inline (tudo após ';')
                comment_start = line.find(';')
                if comment_start != -1:
                    line = line[:comment_start].strip() # Pega a parte da linha antes do ';' e remove espaços
                
                if not line: # Se a linha se tornar vazia após remover o comentário (ex: linha que só tinha comentário)
                    continue

                parts = line.split() # Divide a linha em partes (mnemônico, operando, etc.)
                mnemonic = parts[0].upper() # Pega o mnemônico e converte para maiúsculas

                # Processa a diretiva ORG (Define o ponto de origem para dados) - Seção 10.3
                if mnemonic == "ORG":
                    if len(parts) < 2:
                        raise ValueError(f"Linha {line_num}: ORG requer um endereço.")
                    addr = int(parts[1], 16) # Converte o endereço hexadecimal para inteiro
                    if not (0 <= addr < 16):
                        raise ValueError(f"Linha {line_num}: Endereço ORG fora do range (00-0F).")
                    data_ptr = addr # Define o início da área de dados
                    continue
                
                # Processa a diretiva DB (Define Byte - para dados) - Seção 10.3
                elif mnemonic == "DB":
                    if data_ptr is None:
                        raise ValueError(f"Linha {line_num}: Diretiva DB antes de ORG.")
                    if len(parts) < 2:
                        raise ValueError(f"Linha {line_num}: DB requer um valor.")
                    
                    value = int(parts[1]) # Converte o valor para inteiro
                    if not (0 <= value <= 255): # Valores devem caber em 8 bits
                        raise ValueError(f"Linha {line_num}: Valor DB deve estar entre 0 e 255.")
                    
                    # Verifica se há memória suficiente ANTES de armazenar o byte.
                    # A memória do SAP-1 é de 16 bytes (endereços 0 a 15).
                    if data_ptr > 15: # Se o data_ptr já estiver em 16 ou mais, significa que o endereço 15 já foi preenchido
                        raise ValueError(f"Linha {line_num}: Memória insuficiente para DB (máx. 16 bytes, endereço 0F).")
                    
                    assembled_memory[data_ptr] = value # Armazena o valor na memória montada
                    data_ptr += 1 # Avança para o próximo endereço de dado
                    continue
                
                # Processa as instruções do SAP-1 (LDA, ADD, SUB, OUT, HLT)
                # Verifica se o programa excede o limite de memória ANTES de atribuir a instrução.
                if instruction_ptr > 15: # Se o ponteiro de instrução já estiver em 16 ou mais
                    raise ValueError(f"Linha {line_num}: Programa muito grande para memória (máx. 16 bytes, endereço 0F).")

                # Verifica se o mnemônico é uma instrução válida do SAP-1
                if mnemonic not in ["LDA", "ADD", "SUB", "OUT", "HLT"]:
                    raise ValueError(f"Linha {line_num}: Instrução inválida: {mnemonic}.")
                
                # Converte o mnemônico para seu opcode binário correspondente (Tabela 10-2)
                opcode = {
                    "LDA": 0b0000,
                    "ADD": 0b0001,
                    "SUB": 0b0010,
                    "OUT": 0b1110,
                    "HLT": 0b1111
                }[mnemonic]
                
                operand = 0 # Assume operando 0 por padrão (para instruções sem operando)
                # Processa operandos para instruções que os requerem (LDA, ADD, SUB)
                if mnemonic in ["LDA", "ADD", "SUB"]:
                    if len(parts) < 2:
                        raise ValueError(f"Linha {line_num}: Falta operando para {mnemonic}.")
                    operand = int(parts[1], 16) # Converte o operando (endereço) hexadecimal para inteiro
                    if not (0 <= operand < 16): # O operando também deve estar dentro do range de endereços da memória
                        raise ValueError(f"Linha {line_num}: Operando {mnemonic} deve estar entre 00 e 0F.")
                elif len(parts) > 1: # Se a instrução não requer operando (OUT, HLT) mas algum texto adicional foi encontrado
                     raise ValueError(f"Linha {line_num}: Instrução {mnemonic} não aceita operando.")
                
                # Combina o opcode (4 bits MSB) e o operando (4 bits LSB) em um único byte (8 bits)
                assembled_memory[instruction_ptr] = (opcode << 4) | operand
                instruction_ptr += 1 # Avança o ponteiro de instrução para o próximo endereço
            
            # Após a montagem, a memória do emulador é atualizada com o programa montado.
            self.cpu['memory'] = assembled_memory
            self.cpu['PC'] = 0  # Reseta o Contador de Programa para o endereço 0000, pronto para a execução.
            self.update_visualization() # Atualiza a GUI com a memória montada
            self.status_var.set("Montagem concluída com sucesso!")
            return True
            
        except Exception as e: # Captura e exibe qualquer erro ocorrido durante a montagem
            messagebox.showerror("Erro na montagem", f"Erro: {str(e)}")
            self.status_var.set(f"Erro na montagem: {str(e)}")
            return False
    
    def run_program(self):
        """
        Executa o programa carregado na memória continuamente até que uma instrução HLT seja encontrada
        ou o Contador de Programa exceda o limite da memória.
        """
        if self.running: # Previne múltiplas execuções simultâneas
            return
            
        self.cpu['PC'] = 0 # Garante que o PC está no início do programa antes de executar
        self.update_visualization()
            
        def run_thread(): # Executa em uma thread separada para não travar a GUI
            self.running = True
            self.status_var.set("Executando programa...")
            
            while self.running and self.cpu['PC'] < 16: # Continua enquanto não houver HLT e PC estiver dentro dos limites
                if not self.step(): # Chama a função step para executar uma instrução. Se step retornar False (HLT), para.
                    break
                time.sleep(0.5 / self.clock_speed) # Pausa baseada na velocidade do clock
            
            self.running = False
            if self.cpu['PC'] >= 16: # Se o programa terminou porque o PC excedeu a memória
                self.status_var.set("Execução concluída (PC fora do limite de memória)")
            else: # Se o programa parou por HLT
                self.status_var.set("Execução concluída (HLT encontrado)")
        
        import threading
        threading.Thread(target=run_thread).start() # Inicia a thread de execução
    
    def step(self):
        """
        Executa uma única instrução do programa (passo a passo).
        Implementa o ciclo Fetch-Execute do SAP-1 em 6 estados T.
        Referência: Seção 10.4 (Ciclo de Busca) e Seção 10.5 (Ciclo de Execução) do artigo.
        """
        if self.cpu['PC'] >= 16: # Verifica se o PC excedeu o limite da memória
            self.status_var.set("PC fora do limite de memória. Reset necessário.")
            self.running = False # Para a execução automática se for o caso
            return False
        
        self.animate_clock() # Animação do pulso de clock
        
        # 1. CICLO DE BUSCA (FETCH) - 3 Estados T (T1, T2, T3) - Seção 10.4 do artigo
        
        # Estado T1: Estado de Endereço (PC -> MAR) - Fig. 10-3a
        self.status_var.set(f"Busca (Fetch) - T1: PC ({self.cpu['PC']:01X}) -> MAR")
        self.animate_main_bus_transfer("pc", "mar") # Animação da transferência via barramento principal
        self.cpu['MAR'] = self.cpu['PC'] # Conteúdo do PC é transferido para o MAR
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # Estado T2: Estado de Incremento (PC++) - Fig. 10-3b
        self.status_var.set(f"Busca (Fetch) - T2: Incrementa PC ({self.cpu['PC']:01X} -> {self.cpu['PC']+1:01X})")
        self.highlight_component("pc") # Destaca o PC indicando que ele está sendo incrementado
        self.cpu['PC'] += 1 # Incrementa o Contador de Programa
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # Estado T3: Estado de Memória (Memória[MAR] -> IR) - Fig. 10-3c
        self.status_var.set(f"Busca (Fetch) - T3: Memória[{self.cpu['MAR']:01X}] -> IR")
        if 0 <= self.cpu['MAR'] < 16: # Garante que o endereço da memória é válido
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ff9999") 
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
            self.animate_main_bus_transfer("mem_block", "ir") # Animação da transferência da memória para o IR
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ffff99") 
        
        self.cpu['IR'] = self.cpu['memory'][self.cpu['MAR']] # Conteúdo da memória no endereço do MAR é transferido para o IR
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # 2. CICLO DE EXECUÇÃO - 3 Estados T (T4, T5, T6) - Seção 10.5 do artigo
        # O Registrador de Instruções (IR) contém agora o opcode e o operando.
        opcode = self.cpu['IR'] >> 4 # Extrai os 4 bits mais significativos (opcode)
        operand = self.cpu['IR'] & 0x0F # Extrai os 4 bits menos significativos (operando/endereço)
        
        # Procura e executa a função correspondente ao opcode decodificado
        if opcode in self.instructions:
            instr_name, instr_func = self.instructions[opcode]
            self.status_var.set(f"Executando: {instr_name} 0x{operand:01X}")
            
            # Chama a função de execução da instrução, que contém suas próprias animações
            halted = instr_func(operand)
            self.update_visualization() # Atualiza a GUI após a execução completa da instrução
            return not halted # Retorna True se a execução deve continuar, False se HLT foi encontrado
        else:
            # Em caso de opcode inválido, exibe um erro e para a execução.
            messagebox.showerror("Erro", f"Opcode inválido: {opcode:04b} na instrução 0x{self.cpu['IR']:02X} no endereço 0x{self.cpu['MAR']:01X}.")
            self.running = False
            return False 
    
    def reset_cpu(self):
        """
        Reseta todos os registradores da CPU e limpa a memória para um novo início.
        """
        self.running = False # Para qualquer execução contínua
        self.initialize_cpu() # Reinicializa o estado da CPU
        self.status_var.set("CPU resetada. Carregue e monte um programa.")
        # Limpa o destaque de todas as células de memória e seus endereços na interface
        for i in range(16):
            self.canvas.itemconfig(f"mem_{i}", fill="white")
            self.canvas.itemconfig(f"mem_addr_{i}", fill="gray")

    def update_speed(self, value):
        """
        Atualiza a velocidade da simulação do clock com base no valor do slider.
        """
        self.clock_speed = float(value)
    
    # Implementação das instruções básicas do SAP-1 (Macroinstruções) - Seção 10.2 do artigo
    # Cada instrução é dividida em microinstruções que ocorrem nos estados T4, T5, T6.
    
    def lda(self, operand):
        """
        Instrução LDA (Load Accumulator) - Carrega o acumulador.
        Transfere o valor da memória no endereço especificado pelo operando para o Acumulador.
        Referência: Seção 10.2 (LDA) e Rotina LDA (Seção 10.5, Fig. 10-4, Fig. 10-5).
        """
        self.status_var.set(f"Execução LDA: Carrega Mem[{operand:01X}] para ACC")
        # Estado T4: Operando do IR -> MAR (Endereço da RAM a ser acessado)
        self.highlight_component("ir") # Destaca o IR (origem do operando)
        self.animate_main_bus_transfer("ir", "mar") # Anima IR (operando) indo para MAR
        self.cpu['MAR'] = operand # Carrega o operando (endereço de memória) no MAR
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # Estado T5: Memória[MAR] -> ACC (Carga do dado no acumulador)
        self.status_var.set(f"Execução LDA: Memória[{self.cpu['MAR']:01X}] -> ACC")
        if 0 <= self.cpu['MAR'] < 16:
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ff9999") 
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
            self.animate_main_bus_transfer("mem_block", "acc") # Anima a transferência da memória para o ACC
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ffff99") 
        self.cpu['ACC'] = self.cpu['memory'][self.cpu['MAR']] # Realiza a carga do valor da memória no ACC
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # Estado T6: NOP (Sem operação) - Seção 10.5 (Rotina LDA)
        return False # Não sinaliza HLT
    
    def add(self, operand):
        """
        Instrução ADD - Soma ao acumulador.
        Soma o valor da memória no endereço especificado com o conteúdo do Acumulador,
        armazenando o resultado de volta no Acumulador.
        Referência: Seção 10.2 (ADD) e Rotina ADD (Seção 10.5, Fig. 10-6, Fig. 10-7).
        """
        self.status_var.set(f"Execução ADD: Soma Mem[{operand:01X}] ao ACC")
        # Estado T4: Operando do IR -> MAR
        self.highlight_component("ir")
        self.animate_main_bus_transfer("ir", "mar")
        self.cpu['MAR'] = operand
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # Estado T5: Memória[MAR] -> Reg B (Operando B para a ULA)
        self.status_var.set(f"Execução ADD: Memória[{self.cpu['MAR']:01X}] -> Reg B")
        if 0 <= self.cpu['MAR'] < 16:
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ff9999") 
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
            self.animate_main_bus_transfer("mem_block", "b_reg") # Anima a transferência da memória para o Registrador B
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ffff99") 
        self.cpu['B'] = self.cpu['memory'][self.cpu['MAR']] # Carrega o valor da memória no Registrador B
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # Estado T6: ACC + Reg B -> ULA -> ACC (Operação de Soma e armazenamento do resultado)
        self.status_var.set("Execução ADD: ACC + Reg B -> ULA -> ACC")
        self.animate_direct_transfer("acc", "alu", "acc_to_alu_direct") # ACC envia para ULA
        self.animate_direct_transfer("b_reg", "alu", "b_reg_to_alu_direct") # Reg B envia para ULA

        self.highlight_component("alu") # Destaca a ULA realizando a operação
        self.animate_main_bus_transfer("alu", "acc") # Anima o resultado da ULA indo para o ACC
        
        self.cpu['ACC'] = (self.cpu['ACC'] + self.cpu['B']) & 0xFF  # Realiza a soma e limita o resultado a 8 bits (0-255)
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        return False
    
    def sub(self, operand):
        """
        Instrução SUB - Subtrai do acumulador.
        Subtrai o valor da memória no endereço especificado do conteúdo do Acumulador,
        armazenando o resultado de volta no Acumulador.
        Referência: Seção 10.2 (SUB) e Rotina SUB (Seção 10.5, similar a ADD, Fig. 10-6, Fig. 10-7).
        """
        self.status_var.set(f"Execução SUB: Subtrai Mem[{operand:01X}] do ACC")
        self.highlight_component("ir")
        self.animate_main_bus_transfer("ir", "mar")
        self.cpu['MAR'] = operand
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # Estado T5: Memória[MAR] -> Reg B
        self.status_var.set(f"Execução SUB: Memória[{self.cpu['MAR']:01X}] -> Reg B")
        if 0 <= self.cpu['MAR'] < 16:
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ff9999") 
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
            self.animate_main_bus_transfer("mem_block", "b_reg") # Anima a transferência da memória para o Registrador B
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ffff99") 
        self.cpu['B'] = self.cpu['memory'][self.cpu['MAR']]
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # Estado T6: ACC - Reg B -> ULA -> ACC (Operação de Subtração e armazenamento do resultado)
        self.status_var.set("Execução SUB: ACC - Reg B -> ULA -> ACC")
        self.animate_direct_transfer("acc", "alu", "acc_to_alu_direct") # ACC envia para ULA
        self.animate_direct_transfer("b_reg", "alu", "b_reg_to_alu_direct") # Reg B envia para ULA

        self.highlight_component("alu") # Destaca a ULA
        self.animate_main_bus_transfer("alu", "acc") # Anima o resultado da ULA indo para o ACC
        
        # Realiza a subtração. O '& 0xFF' garante que o resultado permaneça em 8 bits (complemento de 2 para negativos).
        self.cpu['ACC'] = (self.cpu['ACC'] - self.cpu['B']) & 0xFF 
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        return False
    
    def out(self, _): # O operando é ignorado para a instrução OUT
        """
        Instrução OUT - Saída do acumulador.
        Transfere o valor atual do Acumulador para o Registrador de Saída,
        que controla os LEDs.
        Referência: Seção 10.2 (OUT) e Rotina OUT (Seção 10.5, Fig. 10-8, Fig. 10-9).
        """
        self.status_var.set("Execução OUT: ACC -> Saída")
        # Estado T4: ACC -> Registrador de Saída
        self.highlight_component("acc") # Destaca o ACC
        self.animate_main_bus_transfer("acc", "output_reg") # Anima a transferência do ACC para o Registrador de Saída
        
        self.cpu['output'] = self.cpu['ACC'] # O valor do ACC é copiado para o registrador de saída
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # Estados T5 e T6: NOP (Sem operação) - Seção 10.5 (Rotina OUT)
        return False
    
    def hlt(self, _): # O operando é ignorado para a instrução HLT
        """
        Instrução HLT (Halt) - Parada.
        Interrompe a execução do programa no SAP-1.
        Referência: Seção 10.2 (HLT) e HLT (Seção 10.5).
        """
        self.status_var.set("Execução interrompida (HLT)")
        self.highlight_component("ir") # Destaca o IR que contém a instrução HLT
        self.running = False # Sinaliza para o loop de execução que deve parar
        return True # Retorna True para indicar que a execução deve ser interrompida

# Ponto de entrada principal da aplicação
if __name__ == "__main__":
    root = tk.Tk() # Cria a janela principal do Tkinter
    app = SAP1Emulator(root) # Instancia o emulador
    root.mainloop() # Inicia o loop de eventos do Tkinter, mantendo a janela aberta e interativa
