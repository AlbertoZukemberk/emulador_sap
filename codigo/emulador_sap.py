"""
Emulador SAP-1 - Implementação Completa com Interface Gráfica

Este código foi desenvolvido para um projeto da disciplina de Arquitetura de Computadores,
tendo como objetivo emular o microcomputador SAP-1, conforme descrito no livro "Digital Computer Electronics" de Albert Malvino.

Autor: Marcus Meleiro
Disciplina: Arquitetura de Computadores
Professor: Claúdio
Data: 20/06/2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import re # Módulo 're' para expressões regulares

# Tamanho da memória do SAP-1, conforme a arquitetura.
MEMORY_SIZE = 16

class SAP1Emulator:
    def __init__(self, root):
        """
        Inicialização do emulador SAP-1.
        Baseado na lógica do Capítulo 10 do livro de Malvino.
        """
        self.root = root
        self.root.title("Emulador SAP-1 - Arquitetura de Computadores")
        
        self.running = False
        self.clock_speed = 1.0  # Velocidade padrão do clock (1Hz).
        
        # Variáveis para a funcionalidade de "Entrada de Expressão", inspirada em aula.
        self.current_expression = tk.StringVar(value="")
        self.expression_numbers = []
        self.expression_operators = []
        
        # Controle de destaque de linha no editor Assembly.
        self.current_assembly_line = -1 

        self.setup_ui()
        self.initialize_cpu()
        
    def setup_ui(self):
        """
        Configuração da interface gráfica do emulador.
        """
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TButton',
                        font=('Arial', 10, 'bold'),
                        foreground='black',
                        background='#e0e0e0',
                        padding=6,
                        relief='raised',
                        borderwidth=2)
        style.map('TButton',
                  background=[('active', '#c0c0c0'), ('pressed', '#a0a0a0')])
        
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        code_input_frame = ttk.Frame(main_frame)
        code_input_frame.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        # ====================================================================
        # Área de Entrada de Expressão (Implementada a partir de exemplo do Professor Cláudio)
        # ====================================================================
        expression_frame = ttk.LabelFrame(code_input_frame, text="Entrada de Valores da Expressão", padding="10")
        expression_frame.pack(fill=tk.X, pady=5)

        ttk.Label(expression_frame, text="Expressão a ser Processada:", font=('Arial', 10, 'bold')).pack(anchor='w')
        ttk.Entry(expression_frame, textvariable=self.current_expression, state='readonly', font=('Courier', 12), width=35).pack(fill=tk.X, pady=5)

        buttons_frame = ttk.Frame(expression_frame)
        buttons_frame.pack(pady=5)

        for i in range(10):
            ttk.Button(buttons_frame, text=str(i), command=lambda val=str(i): self._handle_expression_button(val)).grid(row=(i//5), column=(i%5), padx=2, pady=2)

        ttk.Button(buttons_frame, text="+", command=lambda: self._handle_expression_button("+")).grid(row=0, column=5, padx=2, pady=2)
        ttk.Button(buttons_frame, text="-", command=lambda: self._handle_expression_button("-")).grid(row=1, column=5, padx=2, pady=2)

        ttk.Button(buttons_frame, text="Entrar", command=self._process_expression).grid(row=0, column=6, padx=5, pady=2)
        ttk.Button(buttons_frame, text="Limpar", command=self._clear_expression).grid(row=1, column=6, padx=5, pady=2)
        # ====================================================================
        
        code_frame = ttk.LabelFrame(code_input_frame, text="Código Assembly", padding="10")
        code_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.editor = tk.Text(code_frame, wrap=tk.NONE, width=35, height=12, 
                            font=('Courier', 12), relief="sunken", borderwidth=2)
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(code_frame, orient=tk.VERTICAL, command=self.editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor['yscrollcommand'] = scrollbar.set
        
        control_frame = ttk.Frame(main_frame, padding="10")
        control_frame.pack(fill=tk.Y, side=tk.LEFT)
        
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
        
        speed_frame = ttk.LabelFrame(control_frame, text="Velocidade do Clock", padding="5")
        speed_frame.pack(fill=tk.X, pady=10)
        self.speed_slider = ttk.Scale(speed_frame, from_=0.1, to=2.0, value=1.0,
                                    command=self.update_speed,
                                    orient=tk.HORIZONTAL, length=150)
        self.speed_slider.pack(fill=tk.X)
        
        cpu_frame = ttk.LabelFrame(main_frame, text="Visualização da CPU", padding="10")
        cpu_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(cpu_frame, width=850, height=600, bg="#f0f0f0", relief="sunken", borderwidth=2)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto para executar")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, padding="5", font=('Arial', 10))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.draw_cpu_components()
        self.draw_legend()

        self.editor.tag_configure("current_line", background="#ffffcc")
        self.editor.tag_configure("error_line", background="red", foreground="white")

    def draw_cpu_components(self):
        """
        Desenha os componentes da CPU SAP-1 no canvas.
        Baseado na Fig. 10-1 do artigo do Malvino (Arquitetura de barramento único).
        """
        self.canvas.delete("all")
        
        reg_color = "#e6f3ff"
        shadow_color = "#cccccc"
        bus_color = "#666666"

        def create_component_with_shadow(x1, y1, x2, y2, fill_color, tags, text_label, text_tag, text_value_tag, default_value, font_label, font_value):
            self.canvas.create_rectangle(x1 + 5, y1 + 5, x2 + 5, y2 + 5, fill=shadow_color, tags=f"{tags}_shadow", width=0)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, tags=tags, width=2, outline=bus_color)
            self.canvas.create_text((x1+x2)/2, y1 + (y2-y1)/3, text=text_label, tags=text_tag, font=font_label)
            self.canvas.create_text((x1+x2)/2, y1 + 2*(y2-y1)/3, text=default_value, tags=text_value_tag, font=font_value)

        # Barramento Principal (Barramento W - Fig. 10-1)
        BUS_Y = 320 
        self.canvas.create_line(30, BUS_Y, 820, BUS_Y, width=4, fill=bus_color, tags="main_bus")

        # Contador de Programa (PC) - Seção 10.1
        create_component_with_shadow(50, 50, 200, 125, reg_color, "pc", "PC", "pc_text", "pc_value", "0x00", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_line(125, 125, 125, BUS_Y, width=2, fill=bus_color, tags="pc_to_bus")

        # Registrador de Endereço de Memória (MAR/REM) - Seção 10.1
        create_component_with_shadow(250, 50, 400, 125, reg_color, "mar", "MAR", "mar_text", "mar_value", "0x00", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_line(325, 125, 325, BUS_Y, width=2, fill=bus_color, tags="mar_to_bus")

        # Registrador de Instruções (IR) - Seção 10.1
        create_component_with_shadow(450, 50, 600, 125, reg_color, "ir", "IR", "ir_text", "ir_value", "0x0000", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_text(525, 25, text="IR (Opcode | Operando)", font=('Arial', 10), fill="gray")
        self.canvas.create_line(525, 125, 525, BUS_Y, width=2, fill=bus_color, tags="ir_to_bus")

        # Acumulador (ACC/Registrador A) - Seção 10.1
        create_component_with_shadow(50, 200, 200, 275, reg_color, "acc", "ACC", "acc_text", "acc_value", "0x00", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_line(125, 275, 125, BUS_Y, width=2, fill=bus_color, tags="acc_to_bus_main")
        # Conexão ACC -> ULA
        self.canvas.create_line(200, 237.5, 250, 237.5, width=2, fill=bus_color, tags="acc_to_alu_direct")

        # Registrador B - Seção 10.1
        create_component_with_shadow(250, 200, 400, 275, reg_color, "b_reg", "Reg B", "b_reg_text", "b_reg_value", "0x00", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_line(325, 275, 325, BUS_Y, width=2, fill=bus_color, tags="b_reg_to_bus_main")
        # Conexão Reg B -> ULA
        self.canvas.create_line(400, 237.5, 450, 237.5, width=2, fill=bus_color, tags="b_reg_to_alu_direct")

        # ULA (Unidade Lógica Aritmética / Somador-Subtrator) - Seção 10.1
        create_component_with_shadow(450, 200, 600, 275, reg_color, "alu", "ULA", "alu_text", "alu_value", "", ('Arial', 14, 'bold'), ('Courier', 12))
        self.canvas.create_line(525, 275, 525, BUS_Y, width=2, fill=bus_color, tags="alu_to_bus_main")

        # Memória RAM (16 bytes, 16x8) - Seção 10.1 e Fig. 10-1
        MEM_X_START = 650
        MEM_Y_START = 50
        MEM_WIDTH = 180 
        MEM_HEIGHT = 280 
        self.canvas.create_rectangle(MEM_X_START + 5, MEM_Y_START + 5, MEM_X_START + MEM_WIDTH + 5, MEM_Y_START + MEM_HEIGHT + 5, fill=shadow_color, tags="mem_block_shadow", width=0)
        self.canvas.create_rectangle(MEM_X_START, MEM_Y_START, MEM_X_START + MEM_WIDTH, MEM_Y_START + MEM_HEIGHT, fill="#f0f8ff", width=2, tags="mem_block", outline=bus_color)
        self.canvas.create_text(MEM_X_START + MEM_WIDTH/2, MEM_Y_START - 20, text="MEMÓRIA (16 bytes)", font=('Arial', 14, 'bold'))
        self.canvas.create_line(MEM_X_START + MEM_WIDTH/2, MEM_Y_START + MEM_HEIGHT, MEM_X_START + MEM_WIDTH/2, BUS_Y, width=2, fill=bus_color, tags="mem_to_bus_main") 

        # Células de memória (grade 4x4)
        self.memory_cells = []
        self.memory_text_ids = []
        self.memory_addr_ids = []

        cell_width_inner = 35
        cell_height_inner = 30
        gap_x_inner = 7
        gap_y_inner = 7
        mem_grid_start_x = MEM_X_START + 10 
        mem_grid_start_y = MEM_Y_START + 30 
        
        for i in range(MEMORY_SIZE):
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
        
        # Registrador de Saída (Output Register) e Indicador Visual em Binário (LEDs) - Seção 10.1
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

        # Clock (CLK) - Seção 10.7 (Circuitos de Relógio) e Fig. 10-2
        self.canvas.create_oval(700, 400, 775, 475, fill="#f0f0f0", width=2, tags="clock", outline=bus_color)
        self.canvas.create_text(737.5, 437.5, text="CLK", tags="clock_text", font=('Arial', 14, 'bold'))
    
    def draw_legend(self):
        """
        Adiciona uma legenda de cores ao canvas.
        Explica o significado dos destaques visuais para a gente entender a simulação.
        """
        legend_x = 650
        legend_y = 480
        line_height = 20

        self.canvas.create_text(legend_x, legend_y, anchor="nw", text="Legenda de Cores:", font=('Arial', 10, 'bold'))

        self.canvas.create_rectangle(legend_x, legend_y + line_height, legend_x + 15, legend_y + line_height + 15, fill="#ff9999", outline="gray")
        self.canvas.create_text(legend_x + 20, legend_y + line_height + 7, anchor="w", text="Componente/Barramento Ativo", font=('Arial', 9))

        self.canvas.create_rectangle(legend_x, legend_y + 2 * line_height, legend_x + 15, legend_y + 2 * line_height + 15, fill="#ffff99", outline="gray")
        self.canvas.create_text(legend_x + 20, legend_y + 2 * line_height + 7, anchor="w", text="Memória Acessada", font=('Arial', 9))
        
        self.canvas.create_oval(legend_x, legend_y + 3 * line_height, legend_x + 15, legend_y + 3 * line_height + 15, fill="red", outline="gray")
        self.canvas.create_text(legend_x + 20, legend_y + 3 * line_height + 7, anchor="w", text="LED Ligado (Bit 1)", font=('Arial', 9))

        self.canvas.create_oval(legend_x, legend_y + 4 * line_height, legend_x + 15, legend_y + 4 * line_height + 15, fill="lightgray", outline="gray")
        self.canvas.create_text(legend_x + 20, legend_y + 4 * line_height + 7, anchor="w", text="LED Desligado (Bit 0)", font=('Arial', 9))

    def _handle_expression_button(self, char):
        """
        Função para adicionar caracteres à expressão no campo de entrada.
        """
        current_text = self.current_expression.get()
        if char in ['+', '-']:
            if not current_text or current_text[-1] in ['+', '-']:
                return 
        
        if char.isdigit() and current_text == "Erro na expressão!":
            current_text = ""

        self.current_expression.set(current_text + char)

    def _clear_expression(self):
        """Limpa o campo de entrada da expressão."""
        self.current_expression.set("")

    def _process_expression(self):
        """
        Processa a expressão numérica digitada e a converte em código Assembly para o SAP-1.
        O código gerado é inserido no editor e o montador é chamado automaticamente.
        """
        expression_str = self.current_expression.get()
        if not expression_str:
            messagebox.showwarning("Expressão Vazia", "Por favor, insira uma expressão para processar.")
            return

        parts = re.findall(r'(\d+)|([+-])', expression_str)
        
        numbers = []
        operators = []
        
        try:
            current_num_str = ""
            for num_part, op_part in parts:
                if num_part:
                    current_num_str += num_part
                elif op_part:
                    if current_num_str:
                        numbers.append(int(current_num_str))
                        current_num_str = ""
                    operators.append(op_part)
            
            if current_num_str:
                numbers.append(int(current_num_str))

            if not numbers:
                raise ValueError("Nenhum número válido encontrado na expressão.")
            
            if len(operators) >= len(numbers):
                 raise ValueError("Expressão mal formatada (operador sem número ou excesso de operadores).")
            
            generated_assembly = "; Código Assembly gerado da expressão: " + expression_str + "\n"
            generated_assembly += "; Os dados serão armazenados a partir do final da memória.\n\n"
            
            data_start_address = MEMORY_SIZE - len(numbers) - 1 
            if data_start_address < 0:
                raise ValueError(f"Expressão muito longa. Max {MEMORY_SIZE - 2} números na memória.")
            
            generated_assembly += f"LDA {data_start_address:01X}   ; Carrega o primeiro número\n"
            
            for i in range(len(operators)):
                op = operators[i]
                num_address = data_start_address + i + 1
                if op == "+":
                    generated_assembly += f"ADD {num_address:01X}   ; Soma o proximo numero\n"
                elif op == "-":
                    generated_assembly += f"SUB {num_address:01X}   ; Subtrai o proximo numero\n"
            
            generated_assembly += "OUT      ; Exibe o resultado\n"
            generated_assembly += "HLT      ; Finaliza a execução\n\n"
            
            generated_assembly += f"ORG {data_start_address:01X}   ; Área de dados na memória\n"
            for num in numbers:
                if not (0 <= num <= 255):
                    raise ValueError(f"Número '{num}' fora do limite (0-255) para DB.")
                generated_assembly += f"DB {num}     ; Dado\n"
            
            self.editor.delete(1.0, tk.END)
            self.editor.insert(1.0, generated_assembly)
            self.status_var.set("Código Assembly gerado com sucesso! Clique em Montar.")
            self.current_expression.set(expression_str)
            self_assemble_success = self.assemble()
            
            if not self_assemble_success:
                 self.editor.delete(1.0, tk.END)
                 self.status_var.set("Erro ao montar o código gerado da expressão.")
                 self.current_expression.set("Erro na expressão!")


        except Exception as e:
            messagebox.showerror("Erro na Expressão", f"Não foi possível processar a expressão: {str(e)}")
            self.status_var.set(f"Erro na expressão: {str(e)}")
            self.current_expression.set("Erro na expressão!")

    def initialize_cpu(self):
        """
        Inicializa o estado da CPU SAP-1, zerando registradores e memória.
        Referência: Seção 10.1 do artigo de Malvino (Arquitetura).
        """
        self.cpu = {
            "PC": 0,      # Contador de Programa (4 bits)
            "ACC": 0,     # Acumulador (8 bits)
            "MAR": 0,     # Registrador de Endereço de Memória (4 bits)
            "IR": 0,      # Registrador de Instruções (8 bits)
            "B": 0,       # Registrador B (8 bits)
            "memory": [0] * MEMORY_SIZE,  # Memória de 16 bytes (16x8 RAM) - Seção 10.1
            "output": 0,  # Registrador de Saída (8 bits)
            "flags": {"Z": 0, "C": 0}  # Flags (Zero e Carry)
        }
        
        # Mapeamento de opcodes para instruções e funções de execução.
        # Referência: Tabela 10-1 e Tabela 10-2 do artigo.
        self.instructions = {
            0b0000: ("LDA", self.lda),
            0b0001: ("ADD", self.add),
            0b0010: ("SUB", self.sub),
            0b1110: ("OUT", self.out),
            0b1111: ("HLT", self.hlt)
        }
        
        self.update_visualization()
        self.current_assembly_line = -1
    
    def update_visualization(self):
        """
        Atualiza os valores exibidos na interface gráfica da CPU (registradores, memória, LEDs).
        """
        self.canvas.itemconfig("pc_value", text=f"0x{self.cpu['PC']:01X}")
        self.canvas.itemconfig("mar_value", text=f"0x{self.cpu['MAR']:01X}")
        self.canvas.itemconfig("ir_value", text=f"0x{self.cpu['IR']:02X}")
        self.canvas.itemconfig("acc_value", text=f"0x{self.cpu['ACC']:02X}")
        self.canvas.itemconfig("b_reg_value", text=f"0x{self.cpu['B']:02X}")
        self.canvas.itemconfig("output_value", text=f"0x{self.cpu['output']:02X}")
        
        for i in range(MEMORY_SIZE):
            self.canvas.itemconfig(f"mem_text_{i}", text=f"{self.cpu['memory'][i]:02X}")
        
        for i in range(MEMORY_SIZE):
            self.canvas.itemconfig(f"mem_{i}", fill="white")
            self.canvas.itemconfig(f"mem_addr_{i}", fill="gray")
        if 0 <= self.cpu['MAR'] < MEMORY_SIZE:
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ffff99")
            self.canvas.itemconfig(f"mem_addr_{self.cpu['MAR']}", fill="red")

        output_val = self.cpu['output']
        for i in range(8):
            if (output_val >> i) & 1: 
                self.canvas.itemconfig(self.led_rects[7-i], fill="red")
            else:
                self.canvas.itemconfig(self.led_rects[7-i], fill="lightgray")

    def animate_main_bus_transfer(self, source_comp_tag, target_comp_tag, duration=0.3):
        """
        Anima a transferência de dados pelo Barramento W.
        Referência: Fig. 10-1, Fig. 10-3, 10-4, 10-6, 10-8 do artigo.
        """
        active_color = "#ff9999"
        original_bus_color = "#666666"
        original_reg_color = "#e6f3ff"

        source_conn_tag = f"{source_comp_tag}_to_bus_main" if source_comp_tag not in ["mem_block", "output_reg", "alu"] else (f"{source_comp_tag[:-5]}_to_bus_main" if source_comp_tag.endswith("_block") else f"{source_comp_tag}_to_bus_main")
        target_conn_tag = f"{target_comp_tag}_to_bus_main" if target_comp_tag not in ["mem_block", "output_reg", "alu"] else (f"{target_comp_tag[:-5]}_to_bus_main" if target_comp_tag.endswith("_block") else f"{target_comp_tag}_to_bus_main")
        
        if source_comp_tag == "alu":
            source_conn_tag = "alu_to_bus_main"
        if target_comp_tag == "alu":
            target_conn_tag = "alu_to_bus_main"

        try:
            target_obj_color = self.canvas.itemcget(target_comp_tag, "fill")
        except:
            target_obj_color = original_reg_color

        self.canvas.itemconfig(source_comp_tag, fill=active_color)
        if source_conn_tag and self.canvas.find_withtag(source_conn_tag):
            self.canvas.itemconfig(source_conn_tag, fill="red", width=3)
        self.canvas.update()
        time.sleep(duration / (3 * self.clock_speed))

        self.canvas.itemconfig("main_bus", fill="red", width=5)
        self.canvas.update()
        time.sleep(duration / (3 * self.clock_speed))

        if target_conn_tag and self.canvas.find_withtag(target_conn_tag):
            self.canvas.itemconfig(target_conn_tag, fill="red", width=3)
        self.canvas.itemconfig(target_comp_tag, fill=active_color)
        self.canvas.update()
        time.sleep(duration / (3 * self.clock_speed))

        self.canvas.itemconfig(source_comp_tag, fill=original_reg_color)
        if source_conn_tag and self.canvas.find_withtag(source_conn_tag):
            self.canvas.itemconfig(source_conn_tag, fill=original_bus_color, width=2)
        self.canvas.itemconfig("main_bus", fill=original_bus_color, width=4)
        if target_conn_tag and self.canvas.find_withtag(target_conn_tag):
            self.canvas.itemconfig(target_conn_tag, fill=original_bus_color, width=2)
        self.canvas.itemconfig(target_comp_tag, fill=target_obj_color)
        self.canvas.update()
        time.sleep(0.1 / self.clock_speed)

    def animate_direct_transfer(self, source_comp_tag, target_comp_tag, line_tag, duration=0.3):
        """
        Anima a transferência de dados direta entre dois componentes (sem o barramento principal).
        """
        active_color = "#ff9999"
        original_bus_color = "#666666"
        original_reg_color = "#e6f3ff"

        try:
            target_obj_color = self.canvas.itemcget(target_comp_tag, "fill")
        except:
            target_obj_color = original_reg_color

        self.canvas.itemconfig(source_comp_tag, fill=active_color)
        self.canvas.itemconfig(line_tag, fill="red", width=3)
        self.canvas.itemconfig(target_comp_tag, fill=active_color)
        self.canvas.update()
        time.sleep(duration / self.clock_speed)

        self.canvas.itemconfig(source_comp_tag, fill=original_reg_color)
        self.canvas.itemconfig(line_tag, fill=original_bus_color, width=2)
        self.canvas.itemconfig(target_comp_tag, fill=target_obj_color)
        self.canvas.update()
        time.sleep(0.1 / self.clock_speed)

    def animate_clock(self):
        """
        Anima o pulso do clock.
        Referência: Fig. 10-2b e Exemplo 10.6 do artigo.
        """
        for _ in range(2):
            self.canvas.itemconfig("clock", fill="#ff9999")
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
            self.canvas.itemconfig("clock", fill="#f0f0f0")
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
    
    def highlight_component(self, component_tag, duration=0.5):
        """
        Destaca visualmente um componente da CPU.
        """
        original_reg_color = "#e6f3ff"
        original_text_color = "black"
        
        try:
            original_fill = self.canvas.itemcget(component_tag, "fill")
        except:
            original_fill = original_reg_color

        self.canvas.itemconfig(component_tag, fill="#ff9999")
        text_tag = component_tag.replace("_reg", "") + "_text" if "_reg" in component_tag else component_tag + "_text"
        try:
             self.canvas.itemconfig(text_tag, fill="red")
        except:
             pass

        self.canvas.update()
        time.sleep(duration / self.clock_speed)
        
        self.canvas.itemconfig(component_tag, fill=original_fill)
        try:
            self.canvas.itemconfig(text_tag, fill=original_text_color)
        except:
            pass
        self.canvas.update()

    def highlight_assembly_line(self, line_num):
        """
        Destaca a linha de código Assembly que está sendo executada no editor.
        """
        if self.current_assembly_line != -1:
            self.editor.tag_remove("current_line", f"{self.current_assembly_line}.0", f"{self.current_assembly_line}.end")
        
        self.editor.tag_add("current_line", f"{line_num}.0", f"{line_num}.end")
        self.current_assembly_line = line_num
        self.editor.see(f"{line_num}.0")

    def clear_assembly_highlight(self):
        """
        Remove todos os destaques do editor Assembly.
        """
        if self.current_assembly_line != -1:
            self.editor.tag_remove("current_line", f"{self.current_assembly_line}.0", f"{self.current_assembly_line}.end")
            self.current_assembly_line = -1
        self.editor.tag_remove("error_line", "1.0", tk.END)


    def load_example(self):
        """
        Carrega um programa Assembly de exemplo no editor.
        O programa soma 5 + 3, projetado para caber na memória de 16 bytes.
        """
        example_code = """; Exemplo SAP-1: Soma 5 + 3
; Conforme descrito no Capítulo 10 do livro de Malvino.
; Programa ocupa endereços 00-03 (4 bytes de instruções).
; Dados ocupam endereços 0E-0F (2 bytes de dados).

LDA 0E   ; Carrega o valor do endereço 0E (5 decimal) para o Acumulador (ACC).
ADD 0F   ; Soma o valor do endereço 0F (3 decimal) ao ACC.
OUT      ; Transfere o resultado do ACC para o Registrador de Saída.
HLT      ; Finaliza a execução do programa (Seção 10.2).

ORG 0E   ; Diretiva para o montador: Inicia a área de dados no endereço 0E.
DB 5     ; Define Byte: Armazena o valor 5 no endereço 0E.
DB 3     ; Define Byte: Armazena o valor 3 no endereço 0F.
"""
        self.editor.delete(1.0, tk.END)
        self.editor.insert(1.0, example_code)
        self.status_var.set("Exemplo carregado: Soma 5 + 3")
        self.clear_assembly_highlight()

    def assemble(self):
        """
        Monta o código Assembly para código de máquina.
        Referência: Seção 10.3 (Programação do SAP-1) e Tabela 10-2 (Código Op do SAP-1).
        """
        code = self.editor.get(1.0, tk.END)
        lines = code.split('\n')
        
        assembled_memory = [0] * MEMORY_SIZE
        
        instruction_ptr = 0
        data_ptr = None
        
        self.editor.tag_remove("error_line", "1.0", tk.END)

        try:
            for line_num, line in enumerate(lines, 1):
                original_line_content = line
                line = line.strip()
                if not line:
                    continue
                
                comment_start = line.find(';')
                if comment_start != -1:
                    line = line[:comment_start].strip()
                
                if not line:
                    continue

                parts = line.split()
                mnemonic = parts[0].upper()

                if mnemonic == "ORG":
                    if len(parts) < 2:
                        raise ValueError(f"ORG requer um endereço. Linha {line_num}.")
                    addr = int(parts[1], 16)
                    if not (0 <= addr < MEMORY_SIZE):
                        raise ValueError(f"Endereço ORG fora do range (00-{MEMORY_SIZE-1:01X}). Linha {line_num}.")
                    data_ptr = addr
                    continue
                
                elif mnemonic == "DB":
                    if data_ptr is None:
                        raise ValueError(f"DB requer um ORG antes. Linha {line_num}.")
                    if len(parts) < 2:
                        raise ValueError(f"DB requer um valor. Linha {line_num}.")
                    
                    value = int(parts[1])
                    if not (0 <= value <= 255):
                        raise ValueError(f"Valor DB deve ser entre 0 e 255. Linha {line_num}.")
                    
                    if data_ptr >= MEMORY_SIZE:
                        raise ValueError(f"Memória insuficiente para DB (máx. {MEMORY_SIZE} bytes, endereço {MEMORY_SIZE-1:01X}). Linha {line_num}.")
                    
                    assembled_memory[data_ptr] = value
                    data_ptr += 1
                    continue
                
                if instruction_ptr >= MEMORY_SIZE:
                    raise ValueError(f"Programa muito grande para memória (máx. {MEMORY_SIZE} bytes, endereço {MEMORY_SIZE-1:01X}). Linha {line_num}.")

                if mnemonic not in ["LDA", "ADD", "SUB", "OUT", "HLT"]:
                    raise ValueError(f"Instrução inválida: {mnemonic}. Linha {line_num}.")
                
                opcode = {
                    "LDA": 0b0000,
                    "ADD": 0b0001,
                    "SUB": 0b0010,
                    "OUT": 0b1110,
                    "HLT": 0b1111
                }[mnemonic]
                
                operand = 0
                if mnemonic in ["LDA", "ADD", "SUB"]:
                    if len(parts) < 2:
                        raise ValueError(f"Falta operando para {mnemonic}. Linha {line_num}.")
                    try:
                        operand = int(parts[1], 16)
                    except ValueError:
                        raise ValueError(f"Operando inválido para {mnemonic}. Esperado hexadecimal. Linha {line_num}.")

                    if not (0 <= operand < MEMORY_SIZE):
                        raise ValueError(f"Operando {mnemonic} deve ser entre 00 e {MEMORY_SIZE-1:01X}. Linha {line_num}.")
                elif len(parts) > 1:
                     raise ValueError(f"Instrução {mnemonic} não aceita operando. Linha {line_num}.")
                
                assembled_memory[instruction_ptr] = (opcode << 4) | operand
                instruction_ptr += 1
            
            self.cpu['memory'] = assembled_memory
            self.cpu['PC'] = 0
            self.update_visualization()
            self.status_var.set("Montagem concluída com sucesso!")
            self.clear_assembly_highlight()
            return True
            
        except Exception as e:
            self.editor.tag_add("error_line", f"{line_num}.0", f"{line_num}.end")
            messagebox.showerror("Erro na montagem", f"Erro na linha {line_num}: {str(e)}")
            self.status_var.set(f"Erro na montagem: linha {line_num}")
            return False
    
    def run_program(self):
        """
        Executa o programa em modo contínuo até HLT ou o fim da memória.
        """
        if self.running:
            return
            
        self.cpu['PC'] = 0
        self.update_visualization()
        self.clear_assembly_highlight()
            
        def run_thread():
            self.running = True
            self.status_var.set("Executando programa...")
            
            while self.running and self.cpu['PC'] < MEMORY_SIZE:
                current_editor_line = 1
                prog_counter = 0
                for i, line_content in enumerate(self.editor.get("1.0", tk.END).split('\n')):
                    stripped_line = line_content.strip()
                    if stripped_line and not stripped_line.startswith(';'):
                        if prog_counter == self.cpu['PC']:
                            self.highlight_assembly_line(i + 1)
                            break
                        prog_counter += 1
                    current_editor_line += 1

                if not self.step():
                    break
                time.sleep(0.5 / self.clock_speed)
            
            self.running = False
            self.clear_assembly_highlight()
            if self.cpu['PC'] >= MEMORY_SIZE:
                self.status_var.set("Execução concluída (PC fora do limite de memória)")
            else:
                self.status_var.set("Execução concluída (HLT encontrado)")
        
        import threading
        threading.Thread(target=run_thread).start()
    
    def step(self):
        """
        Executa uma única instrução (passo a passo).
        Referência: Ciclo Fetch-Execute (Seção 10.4 e 10.5 do artigo).
        """
        if self.cpu['PC'] >= MEMORY_SIZE:
            self.status_var.set("PC fora do limite de memória. Reset necessário.")
            self.running = False
            self.clear_assembly_highlight()
            return False
        
        current_editor_line = 1
        prog_counter = 0
        for i, line_content in enumerate(self.editor.get("1.0", tk.END).split('\n')):
            stripped_line = line_content.strip()
            if stripped_line and not stripped_line.startswith(';'):
                if prog_counter == self.cpu['PC']:
                    self.highlight_assembly_line(i + 1)
                    break
                prog_counter += 1
            current_editor_line += 1
            
        self.animate_clock()
        
        # 1. CICLO DE BUSCA (FETCH) - Estados T1, T2, T3 - Seção 10.4
        
        # T1: Estado de Endereço (PC -> MAR) - Fig. 10-3a
        self.status_var.set(f"Busca (Fetch) - T1: PC ({self.cpu['PC']:01X}) -> MAR")
        self.animate_main_bus_transfer("pc", "mar")
        self.cpu['MAR'] = self.cpu['PC']
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # T2: Estado de Incremento (PC++) - Fig. 10-3b
        self.status_var.set(f"Busca (Fetch) - T2: Incrementa PC ({self.cpu['PC']:01X} -> {self.cpu['PC']+1:01X})")
        self.highlight_component("pc")
        self.cpu['PC'] += 1
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # T3: Estado de Memória (Memória[MAR] -> IR) - Fig. 10-3c
        self.status_var.set(f"Busca (Fetch) - T3: Memória[{self.cpu['MAR']:01X}] -> IR")
        if 0 <= self.cpu['MAR'] < MEMORY_SIZE:
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ff9999") 
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
            self.animate_main_bus_transfer("mem_block", "ir")
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ffff99") 
        
        self.cpu['IR'] = self.cpu['memory'][self.cpu['MAR']]
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # 2. CICLO DE EXECUÇÃO - Estados T4, T5, T6 - Seção 10.5
        opcode = self.cpu['IR'] >> 4
        operand = self.cpu['IR'] & 0x0F
        
        if opcode in self.instructions:
            instr_name, instr_func = self.instructions[opcode]
            self.status_var.set(f"Executando: {instr_name} 0x{operand:01X}")
            
            halted = instr_func(operand)
            self.update_visualization()
            return not halted
        else:
            messagebox.showerror("Erro", f"Opcode inválido: {opcode:04b} na instrução 0x{self.cpu['IR']:02X} no endereço 0x{self.cpu['MAR']:01X}.")
            self.running = False
            self.clear_assembly_highlight()
            return False 
    
    def reset_cpu(self):
        """
        Reseta registradores e memória para o estado inicial.
        """
        self.running = False
        self.initialize_cpu()
        self.status_var.set("CPU resetada. Carregue e monte um programa.")
        self.clear_assembly_highlight()
        for i in range(MEMORY_SIZE):
            self.canvas.itemconfig(f"mem_{i}", fill="white")
            self.canvas.itemconfig(f"mem_addr_{i}", fill="gray")
        self.canvas.itemconfig("alu_value", text="")


    def update_speed(self, value):
        """
        Atualiza a velocidade da simulação do clock.
        """
        self.clock_speed = float(value)
    
    # Implementação das instruções básicas do SAP-1 (Macroinstruções) - Seção 10.2
    
    def lda(self, operand):
        """
        Instrução LDA (Load Accumulator) - Carrega o Acumulador.
        Referência: Seção 10.2 (LDA) e Rotina LDA (Seção 10.5, Fig. 10-4, Fig. 10-5).
        """
        self.status_var.set(f"Execução LDA: Carrega Mem[{operand:01X}] para ACC")
        # T4: Operando do IR -> MAR
        self.highlight_component("ir")
        self.animate_main_bus_transfer("ir", "mar")
        self.cpu['MAR'] = operand
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # T5: Memória[MAR] -> ACC
        self.status_var.set(f"Execução LDA: Memória[{self.cpu['MAR']:01X}] -> ACC")
        if 0 <= self.cpu['MAR'] < MEMORY_SIZE:
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ff9999") 
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
            self.animate_main_bus_transfer("mem_block", "acc")
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ffff99") 
        self.cpu['ACC'] = self.cpu['memory'][self.cpu['MAR']]
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # T6: NOP (No Operation) - Seção 10.5 (Rotina LDA)
        self.canvas.itemconfig("alu_value", text="")
        return False
    
    def add(self, operand):
        """
        Instrução ADD - Soma ao Acumulador.
        Referência: Seção 10.2 (ADD) e Rotina ADD (Seção 10.5, Fig. 10-6, Fig. 10-7).
        """
        self.status_var.set(f"Execução ADD: Soma Mem[{operand:01X}] ao ACC")
        # T4: Operando do IR -> MAR
        self.highlight_component("ir")
        self.animate_main_bus_transfer("ir", "mar")
        self.cpu['MAR'] = operand
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # T5: Memória[MAR] -> Reg B
        self.status_var.set(f"Execução ADD: Memória[{self.cpu['MAR']:01X}] -> Reg B")
        if 0 <= self.cpu['MAR'] < MEMORY_SIZE:
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ff9999") 
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
            self.animate_main_bus_transfer("mem_block", "b_reg")
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ffff99") 
        self.cpu['B'] = self.cpu['memory'][self.cpu['MAR']]
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # T6: ACC + Reg B -> ULA -> ACC
        self.status_var.set("Execução ADD: ACC + Reg B -> ULA -> ACC")
        self.animate_direct_transfer("acc", "alu", "acc_to_alu_direct")
        self.animate_direct_transfer("b_reg", "alu", "b_reg_to_alu_direct")

        alu_result = (self.cpu['ACC'] + self.cpu['B']) & 0xFF
        self.canvas.itemconfig("alu_value", text=f"0x{alu_result:02X}", font=('Courier', 12))
        self.highlight_component("alu")
        self.animate_main_bus_transfer("alu", "acc")
        
        self.cpu['ACC'] = alu_result
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        self.canvas.itemconfig("alu_value", text="")
        
        return False
    
    def sub(self, operand):
        """
        Instrução SUB - Subtrai do Acumulador.
        Referência: Seção 10.2 (SUB) e Rotina SUB (Seção 10.5, Fig. 10-6, Fig. 10-7).
        """
        self.status_var.set(f"Execução SUB: Subtrai Mem[{operand:01X}] do ACC")
        self.highlight_component("ir")
        self.animate_main_bus_transfer("ir", "mar")
        self.cpu['MAR'] = operand
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # T5: Memória[MAR] -> Reg B
        self.status_var.set(f"Execução SUB: Memória[{self.cpu['MAR']:01X}] -> Reg B")
        if 0 <= self.cpu['MAR'] < MEMORY_SIZE:
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ff9999") 
            self.canvas.update()
            time.sleep(0.2 / self.clock_speed)
            self.animate_main_bus_transfer("mem_block", "b_reg")
            self.canvas.itemconfig(f"mem_{self.cpu['MAR']}", fill="#ffff99") 
        self.cpu['B'] = self.cpu['memory'][self.cpu['MAR']]
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # T6: ACC - Reg B -> ULA -> ACC
        self.status_var.set("Execução SUB: ACC - Reg B -> ULA -> ACC")
        self.animate_direct_transfer("acc", "alu", "acc_to_alu_direct")
        self.animate_direct_transfer("b_reg", "alu", "b_reg_to_alu_direct")

        alu_result = (self.cpu['ACC'] - self.cpu['B']) & 0xFF
        self.canvas.itemconfig("alu_value", text=f"0x{alu_result:02X}", font=('Courier', 12))
        self.highlight_component("alu")
        self.animate_main_bus_transfer("alu", "acc")
        
        self.cpu['ACC'] = alu_result
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        self.canvas.itemconfig("alu_value", text="")
        
        return False
    
    def out(self, _):
        """
        Instrução OUT - Saída do Acumulador.
        Referência: Seção 10.2 (OUT) e Rotina OUT (Seção 10.5, Fig. 10-8, Fig. 10-9).
        """
        self.status_var.set("Execução OUT: ACC -> Saída")
        # T4: ACC -> Registrador de Saída
        self.highlight_component("acc")
        self.animate_main_bus_transfer("acc", "output_reg")
        
        self.cpu['output'] = self.cpu['ACC']
        self.update_visualization()
        time.sleep(0.5 / self.clock_speed)
        
        # T5 e T6: NOP (No Operation) - Seção 10.5 (Rotina OUT)
        self.canvas.itemconfig("alu_value", text="")
        return False
    
    def hlt(self, _):
        """
        Instrução HLT (Halt) - Parada.
        Referência: Seção 10.2 (HLT) e HLT (Seção 10.5).
        """
        self.status_var.set("Execução interrompida (HLT)")
        self.highlight_component("ir")
        self.running = False
        self.canvas.itemconfig("alu_value", text="")
        return True

# Ponto de entrada principal do programa.
if __name__ == "__main__":
    root = tk.Tk()
    app = SAP1Emulator(root)
    root.mainloop()
