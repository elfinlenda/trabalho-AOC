# MIPS Simulator
#
# Aluno: FABIO EMANUEL M. S. C. COIMRBA       RA: 2669978
# Aluno: FELIPE KENZO HIGASHI                 RA: 2669986
#
# Descrição: Simulador de um processador MIPS desenvolvido em Python com Tkinter.

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def register_name(num):
    """Mapeia números de registradores para nomes convencionais"""
    if num == 0:
        return "$zero"
    elif num == 1:
        return "$at"
    elif 2 <= num <= 3:
        return f"$v{num-2}"
    elif 4 <= num <= 7:
        return f"$a{num-4}"
    elif 8 <= num <= 15:
        return f"$t{num-8}"
    elif 16 <= num <= 23:
        return f"$s{num-16}"
    elif 24 <= num <= 25:  
        return f"$t{num-8 + 8}" 
        return f"$t{num - 24 + 8}" if num <= 25 else f"${num}"
    elif 26 <= num <= 27:
        return f"$k{num-26}"
    elif num == 28:
        return "$gp"
    elif num == 29:
        return "$sp"
    elif num == 30:
        return "$fp"
    elif num == 31:
        return "$ra"
    return f"${num}"

def parse_instruction(bin_instr):
    """Analisa a instrução binária e retorna um dicionário com os campos parseados"""
    if len(bin_instr) != 32:
        return None
    
    parsed = {
        'opcode': bin_instr[:6],
        'rs': bin_instr[6:11],
        'rt': bin_instr[11:16],
        'rd': bin_instr[16:21],
        'shamt': bin_instr[21:26],
        'funct': bin_instr[26:],
        'immediate': bin_instr[16:],
        'address': bin_instr[6:]
    }
    
    # Converter campos binários para inteiros
    parsed['rs_num'] = int(parsed['rs'], 2)
    parsed['rt_num'] = int(parsed['rt'], 2)
    parsed['rd_num'] = int(parsed['rd'], 2)
    parsed['shamt_num'] = int(parsed['shamt'], 2)
    parsed['funct_num'] = int(parsed['funct'], 2)
    
    # Tratar immediate (sinalizado)
    immediate_bin = parsed['immediate']
    if immediate_bin[0] == '1':
        parsed['immediate_num'] = -(65536 - int(immediate_bin, 2))
    else:
        parsed['immediate_num'] = int(immediate_bin, 2)
    
    # Tratar endereço J-type
    parsed['address_num'] = int(parsed['address'], 2)
    
    return parsed

def bin_to_assembly(bin_instr):
    """Traduz instrução binária para assembly e retorna dados parseados"""
    if len(bin_instr) != 32:
        return "   ", None
    
    parsed = parse_instruction(bin_instr)
    if not parsed:
        return "  ", None
    
    rs = register_name(parsed['rs_num'])
    rt = register_name(parsed['rt_num'])
    rd = register_name(parsed['rd_num'])
    shamt = parsed['shamt_num']
    funct = parsed['funct']
    immediate = parsed['immediate_num']
    address = parsed['address_num']
    
    try:
        # Instruções Tipo R
        if parsed['opcode'] == '000000':
            if funct == '100000':   # ADD
                return f"add {rd}, {rs}, {rt}", parsed
            elif funct == '100010':  # SUB
                return f"sub {rd}, {rs}, {rt}", parsed
            elif funct == '011000':  # MULT
                return f"mult {rs}, {rt}", parsed
            elif funct == '100100':  # AND
                return f"and {rd}, {rs}, {rt}", parsed
            elif funct == '100101':  # OR
                return f"or {rd}, {rs}, {rt}", parsed
            elif funct == '000000':  # SLL
                return f"sll {rd}, {rt}, {shamt}", parsed
            elif funct == '101010':  # SLT
                return f"slt {rd}, {rs}, {rt}", parsed
            elif funct == '001100':  # SYSCALL
                return "syscall", parsed
        
        # Instruções Tipo I
        elif parsed['opcode'] == '001000':  # ADDI
            return f"addi {rt}, {rs}, {immediate}", parsed
        elif parsed['opcode'] == '001010':  # SLTI
            return f"slti {rt}, {rs}, {immediate}", parsed
        elif parsed['opcode'] == '100011':  # LW
            return f"lw {rt}, {immediate}({rs})", parsed
        elif parsed['opcode'] == '101011':  # SW
            return f"sw {rt}, {immediate}({rs})", parsed
        elif parsed['opcode'] == '001111':  # LUI
            return f"lui {rt}, {immediate}", parsed
        
        # Instruções Tipo J
        elif parsed['opcode'] == '000010':  # J
            return f"j {address}", parsed
        
        # Chamadas de sistema (exemplo não padrão)
        elif parsed['opcode'] == '000001':  # IMPRIMIR INTEIRO
            return f"print_int {rt}", parsed
        elif parsed['opcode'] == '000011':  # IMPRIMIR STRING
            return f"print_str {rt}", parsed
        elif parsed['opcode'] == '000100':  # SAIR
            return "exit", parsed
        
        else:
            return f"Instrução não implementada (OPCODE: {parsed['opcode']})", parsed
    
    except:
        return "Erro na tradução da instrução", parsed

class MIPSSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuração do tema e estilo
        self.setup_theme()
        self.setup_window()
        
        self.instructions = []
        self.current_line = 0
        self.registers = {}
        self.memory = {}
        self.create_widgets()
        self.init_registers()
    
    def setup_theme(self):
        """Configura o tema visual da aplicação"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Paleta de cores moderna
        self.colors = {
            'dark_bg': '#2c3e50',
            'light_bg': '#ecf0f1',
            'highlight': '#3498db',
            'text_dark': '#2c3e50',
            'text_light': '#ecf0f1',
            'accent': '#e74c3c',
            'success': '#27ae60'
        }
        
        # Configurar estilos
        self.style.configure('TButton', 
                           font=('Segoe UI', 10, 'bold'),
                           padding=8,
                           background=self.colors['highlight'],
                           foreground=self.colors['text_light'])
        
        self.style.map('TButton',
                      background=[('active', '#2980b9'), 
                                ('disabled', '#bdc3c7')],
                      foreground=[('active', self.colors['text_light']),
                                ('disabled', '#7f8c8d')])
        
        self.style.configure('TFrame', background=self.colors['light_bg'])
        self.style.configure('TLabel', 
                           font=('Segoe UI', 10),
                           background=self.colors['light_bg'],
                           foreground=self.colors['text_dark'])
        
        self.style.configure('TNotebook', background=self.colors['light_bg'])
        self.style.configure('TNotebook.Tab', 
                           font=('Segoe UI', 10, 'bold'),
                           padding=[15, 5])
        
        self.style.configure('Highlight.TLabel', 
                           foreground=self.colors['accent'],
                           font=('Consolas', 10, 'bold'))
    
    def setup_window(self):
        """Configura a janela principal"""
        self.title("🚀 Simulador MIPS Avançado")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(bg=self.colors['light_bg'])
        
        # Ícone da aplicação
        try:
            self.iconbitmap('mips_icon.ico')  # Substitua pelo caminho do seu ícone
        except:
            pass
    
    def init_registers(self):
        """Inicializa todos os registradores com 0"""
        for i in range(32):
            reg_name = register_name(i)
            self.registers[reg_name] = 0
        # Registradores especiais
        self.registers['$hi'] = 0
        self.registers['$lo'] = 0
    
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        self.create_control_panel()
        self.create_notebook()
        self.create_info_panel()
    
    def create_control_panel(self):
        """Cria o painel de controles superiores"""
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botões com ícones e estilo moderno
        buttons = [
            ("📂 Carregar", self.load_file, 'success.TButton'),
            ("⏭ Passo", self.next_step, None),
            ("⚡ Executar Tudo", self.run_all, None),
            ("🔄 Reset", self.reset_simulator, 'danger.TButton'),
            ("ℹ️ Sobre", self.show_about, None)
        ]
        
        for text, command, style in buttons:
            btn = ttk.Button(control_frame, 
                           text=text,
                           command=command,
                           style=style)
            btn.pack(side=tk.LEFT, padx=5)
            
            # Guardar referência aos botões importantes
            if text == "⏭ Passo":
                self.step_btn = btn
            elif text == "⚡ Executar Tudo":
                self.run_all_btn = btn
            elif text == "🔄 Reset":
                self.reset_btn = btn
        
        # Configurar estados iniciais
        self.step_btn.config(state=tk.DISABLED)
        self.run_all_btn.config(state=tk.DISABLED)
        self.reset_btn.config(state=tk.DISABLED)
        
        # Estilo especial para botões
        self.style.configure('success.TButton', 
                           background=self.colors['success'])
        self.style.configure('danger.TButton', 
                           background=self.colors['accent'])
    
    def create_notebook(self):
        """Cria o notebook com abas para código e registradores"""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Aba do código binário
        self.create_code_tab()
        
        # Aba dos registradores
        self.create_register_tab()
        
        # Aba da memória (opcional)
        self.create_memory_tab()
    
    def create_code_tab(self):
        """Cria a aba de visualização do código binário"""
        code_frame = ttk.Frame(self.notebook)
        self.notebook.add(code_frame, text='📝 Código Binário')
        
        # Configurar grid
        code_frame.grid_rowconfigure(0, weight=1)
        code_frame.grid_columnconfigure(0, weight=1)
        
        # Área de texto com scroll
        self.code_text = tk.Text(code_frame, 
                               wrap=tk.NONE, 
                               font=('Consolas', 11),
                               bg=self.colors['dark_bg'],
                               fg=self.colors['text_light'],
                               insertbackground='white',
                               selectbackground=self.colors['highlight'],
                               padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(code_frame, orient="vertical", command=self.code_text.yview)
        hsb = ttk.Scrollbar(code_frame, orient="horizontal", command=self.code_text.xview)
        self.code_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Layout
        self.code_text.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configurar tags para realce de código
        self.code_text.tag_configure('current', 
                                   background=self.colors['highlight'],
                                   foreground='black')
        self.code_text.tag_configure('executed', 
                                   background='#34495e',
                                   foreground='white')
    
    def create_register_tab(self):
        """Cria a aba de visualização dos registradores"""
        register_frame = ttk.Frame(self.notebook)
        self.notebook.add(register_frame, text='🧮 Registradores')
        
        # Frame com scroll para registradores
        canvas = tk.Canvas(register_frame, bg=self.colors['light_bg'])
        scrollbar = ttk.Scrollbar(register_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Dicionário para armazenar os labels dos registradores
        self.register_labels = {}
        
        # Organizar registradores em 4 colunas
        for i in range(32):
            reg_name = register_name(i)
            row = i // 4
            col = (i % 4) * 2
            
            lbl_frame = ttk.Frame(scrollable_frame, padding=5)
            lbl_frame.grid(row=row, column=col, padx=5, pady=2, sticky='w')
            
            # Nome do registrador
            ttk.Label(lbl_frame, 
                     text=f"{reg_name}:", 
                     font=('Segoe UI', 10, 'bold'),
                     foreground=self.colors['text_dark']).pack(side=tk.LEFT)
            
            # Valor do registrador
            lbl_value = ttk.Label(lbl_frame, 
                                text="0", 
                                style='Highlight.TLabel',
                                width=12)
            lbl_value.pack(side=tk.LEFT)
            self.register_labels[reg_name] = lbl_value
        
        # Adicionar registradores especiais (HI e LO)
        lbl_frame = ttk.Frame(scrollable_frame, padding=5)
        lbl_frame.grid(row=8, column=0, columnspan=8, pady=10, sticky='w')
        
        ttk.Label(lbl_frame, 
                 text="Registradores Especiais:", 
                 font=('Segoe UI', 10, 'bold'),
                 foreground=self.colors['text_dark']).pack(side=tk.LEFT)
        
        for reg in ['$hi', '$lo']:
            lbl_frame = ttk.Frame(scrollable_frame, padding=5)
            lbl_frame.grid(row=9 if reg == '$hi' else 10, column=0, columnspan=8, sticky='w')
            
            ttk.Label(lbl_frame, 
                     text=f"{reg}:", 
                     font=('Segoe UI', 10, 'bold'),
                     foreground=self.colors['text_dark']).pack(side=tk.LEFT)
            
            lbl_value = ttk.Label(lbl_frame, 
                                text="0", 
                                style='Highlight.TLabel',
                                width=12)
            lbl_value.pack(side=tk.LEFT)
            self.register_labels[reg] = lbl_value
    
    def create_memory_tab(self):
        """Cria a aba de visualização da memória (opcional)"""
        memory_frame = ttk.Frame(self.notebook)
        self.notebook.add(memory_frame, text='💾 Memória')
        
        # Adicione aqui a implementação da visualização da memória
        ttk.Label(memory_frame, 
                 text="Visualização da Memória (implementação futura)",
                 font=('Segoe UI', 10),
                 foreground=self.colors['text_dark']).pack(pady=20)
    
    def create_info_panel(self):
        """Cria o painel de informações na parte inferior"""
        info_frame = ttk.Frame(self, padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Label da instrução traduzida
        self.translation_label = ttk.Label(
            info_frame, 
            text="📋 Instrução Traduzida: Aguardando...",
            font=('Segoe UI', 11, 'bold'),
            foreground=self.colors['success']
        )
        self.translation_label.pack(anchor=tk.W)
        
        # Label de detalhes da decodificação
        self.details_label = ttk.Label(
            info_frame,
            text="🔍 Detalhes: Nenhuma instrução carregada",
            font=('Segoe UI', 10),
            foreground=self.colors['text_dark']
        )
        self.details_label.pack(anchor=tk.W)
        
        # Barra de status
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        
        status_bar = ttk.Label(
            info_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Segoe UI', 9),
            foreground=self.colors['text_dark']
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def show_about(self):
        """Mostra a janela 'Sobre'"""
        about_window = tk.Toplevel(self)
        about_window.title("ℹ️ Sobre o Simulador MIPS")
        about_window.geometry("500x300")
        about_window.resizable(False, False)
        
        # Centralizar a janela
        window_width = about_window.winfo_reqwidth()
        window_height = about_window.winfo_reqheight()
        position_right = int(self.winfo_screenwidth()/2 - window_width/2)
        position_down = int(self.winfo_screenheight()/2 - window_height/2)
        about_window.geometry(f"+{position_right}+{position_down}")
        
        # Conteúdo
        ttk.Label(about_window, 
                 text="Simulador MIPS", 
                 font=('Segoe UI', 16, 'bold'),
                 foreground=self.colors['highlight']).pack(pady=10)
        
        ttk.Label(about_window, 
                 text="Desenvolvido por:\nFABIO EMANUEL M. S. C. COIMBRA (RA: 2669978)\nFELIPE KENZO HIGASHI (RA: 2669986)",
                 font=('Segoe UI', 11),
                 justify=tk.CENTER).pack(pady=5)
        
        ttk.Label(about_window, 
                 text="Este simulador foi desenvolvido como parte de um projeto\npara a disciplina de Arquitetura de Computadores.",
                 font=('Segoe UI', 10),
                 justify=tk.CENTER).pack(pady=10)
        
        ttk.Button(about_window, 
                  text="Fechar", 
                  command=about_window.destroy).pack(pady=10)
    
    def reset_simulator(self):
        """Reseta todo o estado da simulação"""
        self.current_line = 0
        self.init_registers()
        self.memory = {}
        self.update_register_display()
        self.clear_highlights()
        self.highlight_current_line()
        self.translation_label.config(text="📋 Instrução Traduzida: Aguardando...")
        self.details_label.config(text="🔍 Detalhes: Simulador reiniciado")
        self.status_var.set("Pronto - Simulador reiniciado")
        
        # Atualizar estados dos botões
        if self.instructions:
            self.step_btn.config(state=tk.NORMAL)
            self.run_all_btn.config(state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)
        else:
            self.reset_btn.config(state=tk.DISABLED)
    
    def load_file(self):
        """Carrega um arquivo com instruções binárias"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")],
            title="Selecione um arquivo com instruções MIPS"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as file:
                self.instructions = [line.strip() for line in file if line.strip()]
                self.current_line = 0
                
                # Habilitar controles
                self.step_btn.config(state=tk.NORMAL)
                self.run_all_btn.config(state=tk.NORMAL)
                self.reset_btn.config(state=tk.NORMAL)
                
                # Atualizar interface
                self.init_registers()
                self.update_register_display()
                self.show_code()
                self.clear_highlights()
                self.status_var.set(f"Arquivo carregado: {file_path}")
                
                messagebox.showinfo(
                    "Sucesso",
                    f"Arquivo carregado com sucesso!\n{len(self.instructions)} instruções encontradas."
                )
                
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Não foi possível ler o arquivo:\n{str(e)}"
            )
            self.status_var.set("Erro ao carregar arquivo")
    
    def show_code(self):
        """Mostra o código binário na área de texto"""
        self.code_text.config(state=tk.NORMAL)
        self.code_text.delete(1.0, tk.END)
        
        # Adicionar números de linha e o código
        for i, instr in enumerate(self.instructions, 1):
            self.code_text.insert(tk.END, f"{i:4d}: {instr}\n")
        
        self.code_text.config(state=tk.DISABLED)
        self.highlight_current_line()
    
    def highlight_current_line(self):
        """Destaca a linha atual sendo executada"""
        self.code_text.tag_remove('current', 1.0, tk.END)
        
        if self.current_line < len(self.instructions):
            line_start = f"{self.current_line + 1}.0"
            line_end = f"{self.current_line + 1}.end"
            
            # Aplicar tag e rolar para a linha
            self.code_text.tag_add('current', line_start, line_end)
            self.code_text.see(line_start)
    
    def clear_highlights(self):
        """Remove todos os realces de execução"""
        self.code_text.tag_remove('executed', 1.0, tk.END)
    
    def next_step(self):
        """Executa o próximo passo da simulação"""
        if self.current_line >= len(self.instructions):
            self.show_register_report()
            messagebox.showinfo(
                "Execução concluída",
                "Todas as instruções foram executadas!"
            )
            self.step_btn.config(state=tk.DISABLED)
            self.status_var.set("Execução concluída")
            return
        
        bin_instr = self.instructions[self.current_line]
        assembly, parsed = bin_to_assembly(bin_instr)
        
        if parsed is None:
            messagebox.showwarning(
                "Instrução inválida",
                f"A instrução na linha {self.current_line + 1} é inválida!"
            )
            self.status_var.set(f"Erro: Instrução inválida na linha {self.current_line + 1}")
            return
        
        # Atualizar informações na interface
        self.translation_label.config(text=f"📋 Instrução Traduzida: {assembly}")
        self.details_label.config(text=f"🔍 Decodificando: {bin_instr}")
        self.status_var.set(f"Executando linha {self.current_line + 1}/{len(self.instructions)}")
        self.highlight_current_line()
        
        # Executar instrução
        self.execute_instruction(parsed)
        self.update_register_display()
        self.update()  # Forçar atualização imediata da interface
        
        # Marcar linha como executada
        line_start = f"{self.current_line + 1}.0"
        line_end = f"{self.current_line + 1}.end"
        self.code_text.tag_add('executed', line_start, line_end)
        
        # Avançar para próxima linha
        self.current_line += 1
        
        # Verificar se terminou
        if self.current_line >= len(self.instructions):
            self.step_btn.config(state=tk.DISABLED)
            self.status_var.set("Execução concluída")
            self.show_register_report()
    
    def run_all(self):
        """Executa todas as instruções de uma vez"""
        if not self.instructions:
            messagebox.showwarning(
                "Nenhum código",
                "Nenhum código foi carregado para execução!"
            )
            return
        
        # Resetar simulador
        self.reset_simulator()
        
        # Traduzir para assembly
        assembly_code = []
        for bin_instr in self.instructions:
            instr, _ = bin_to_assembly(bin_instr)
            assembly_code.append(instr)
        
        # Mostrar código assembly em uma janela separada
        self.show_assembly(assembly_code)
        
        # Executar todas as instruções
        self.status_var.set("Executando todas as instruções...")
        self.update()
        
        self.current_line = 0
        while self.current_line < len(self.instructions):
            bin_instr = self.instructions[self.current_line]
            parsed = parse_instruction(bin_instr)
            
            if parsed:
                self.execute_instruction(parsed)
            
            # Marcar linha como executada
            line_start = f"{self.current_line + 1}.0"
            line_end = f"{self.current_line + 1}.end"
            self.code_text.tag_add('executed', line_start, line_end)
            
            self.current_line += 1
        
        # Atualizar interface
        self.update_register_display()
        self.update_idletasks()
        self.highlight_current_line()
        self.code_text.tag_add('executed', '1.0', tk.END)
        
        # Mostrar relatório
        self.show_register_report()
        messagebox.showinfo(
            "Concluído",
            "Execução completa de todas as instruções!"
        )
        self.status_var.set("Execução completa")
    
    def show_register_report(self):
        """Exibe relatório completo dos registradores em nova janela"""
        report_window = tk.Toplevel(self)
        report_window.title("📊 Relatório de Registradores - Execução Completa")
        report_window.geometry("800x600")
        
        # Centralizar a janela
        window_width = report_window.winfo_reqwidth()
        window_height = report_window.winfo_reqheight()
        position_right = int(self.winfo_screenwidth()/2 - window_width/2)
        position_down = int(self.winfo_screenheight()/2 - window_height/2)
        report_window.geometry(f"+{position_right}+{position_down}")
        
        # Frame principal com scroll
        main_frame = ttk.Frame(report_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(main_frame, bg=self.colors['light_bg'])
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configurar scroll
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Título
        ttk.Label(scrollable_frame, 
                 text="Estado Final dos Registradores",
                 font=('Segoe UI', 14, 'bold'),
                 foreground=self.colors['highlight']).pack(pady=(0, 10))
        
        # Cabeçalho da tabela
        header_frame = ttk.Frame(scrollable_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, 
                 text="Registrador".ljust(15),
                 font=('Courier', 10, 'bold'),
                 width=15).pack(side=tk.LEFT)
        
        ttk.Label(header_frame, 
                 text="Valor Decimal".ljust(20),
                 font=('Courier', 10, 'bold'),
                 width=20).pack(side=tk.LEFT)
        
        ttk.Label(header_frame, 
                 text="Valor Hexadecimal",
                 font=('Courier', 10, 'bold')).pack(side=tk.LEFT)
        
        # Linha separadora
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Conteúdo dos registradores
        for reg_name in sorted(self.registers.keys(), key=lambda x: (not x.startswith('$'), x)):
            value = self.registers[reg_name]
            
            # Converter para signed 32-bit
            if value > 0x7FFFFFFF:
                value -= 0x100000000
            
            hex_value = f"{value & 0xFFFFFFFF:08x}"
            
            # Frame para cada linha
            line_frame = ttk.Frame(scrollable_frame)
            line_frame.pack(fill=tk.X, pady=2)
            
            # Nome do registrador
            ttk.Label(line_frame, 
                     text=reg_name.ljust(15),
                     font=('Courier', 10),
                     width=15).pack(side=tk.LEFT)
            
            # Valor decimal
            ttk.Label(line_frame, 
                     text=str(value).ljust(20),
                     font=('Courier', 10),
                     width=20).pack(side=tk.LEFT)
            
            # Valor hexadecimal
            ttk.Label(line_frame, 
                     text=f"0x{hex_value}",
                     font=('Courier', 10)).pack(side=tk.LEFT)
        
        # Botão de fechar
        ttk.Button(scrollable_frame,
                  text="Fechar Relatório",
                  command=report_window.destroy).pack(pady=10)
    
    def show_assembly(self, assembly_code):
        """Mostra o código assembly traduzido em uma nova janela"""
        asm_window = tk.Toplevel(self)
        asm_window.title("📜 Código Assembly Traduzido")
        asm_window.geometry("600x800")
        
        # Frame principal
        main_frame = ttk.Frame(asm_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra de título
        ttk.Label(main_frame,
                 text="Código Assembly Traduzido",
                 font=('Segoe UI', 12, 'bold'),
                 foreground=self.colors['highlight']).pack(pady=(0, 10))
        
        # Área de texto com scroll
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        asm_text = tk.Text(text_frame,
                          wrap=tk.NONE,
                          font=('Consolas', 11),
                          bg=self.colors['dark_bg'],
                          fg=self.colors['text_light'],
                          padx=10, pady=10)
        
        vsb = ttk.Scrollbar(text_frame, orient="vertical", command=asm_text.yview)
        hsb = ttk.Scrollbar(text_frame, orient="horizontal", command=asm_text.xview)
        
        asm_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        asm_text.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Adicionar código assembly com numeração de linhas
        for i, line in enumerate(assembly_code, 1):
            asm_text.insert(tk.END, f"{i:4d}: {line}\n")
        
        asm_text.config(state=tk.DISABLED)
        
        # Botão de fechar
        ttk.Button(main_frame,
                  text="Fechar",
                  command=asm_window.destroy).pack(pady=10)
    
    def execute_instruction(self, parsed):
        """Executa a instrução parseada"""
        opcode = parsed['opcode']
        funct = parsed['funct']

        def get_register_value(reg_num):
            return self.registers[register_name(reg_num)]
        
        def set_register_value(reg_num, value):
            reg_name = register_name(reg_num)
            if reg_name != "$zero":
                self.registers[reg_name] = value & 0xFFFFFFFF
        
        if opcode == '000000':  # Tipo R
            rs_num = parsed['rs_num']
            rt_num = parsed['rt_num']
            rd_num = parsed['rd_num']
            shamt = parsed['shamt_num']
            
            rs_val = get_register_value(rs_num)
            rt_val = get_register_value(rt_num)

            if funct == '100000':  # ADD
                result = rs_val + rt_val
                set_register_value(rd_num, result)
            elif funct == '100010':  # SUB
                result = rs_val - rt_val
                set_register_value(rd_num, result)
            elif funct == '100100':  # AND
                result = rs_val & rt_val
                set_register_value(rd_num, result)
            elif funct == '100101':  # OR
                result = rs_val | rt_val
                set_register_value(rd_num, result)
            elif funct == '000000':  # SLL
                result = rt_val << shamt
                set_register_value(rd_num, result)
            elif funct == '011000':  # MULT
                result = rs_val * rt_val
                # Implementação simplificada (armazena em registradores temporários)
                self.registers['$hi'] = (result >> 32) & 0xFFFFFFFF
                self.registers['$lo'] = result & 0xFFFFFFFF

        elif opcode == '001000':  # ADDI
            rs_num = parsed['rs_num']
            rt_num = parsed['rt_num']
            immediate = parsed['immediate_num']
            rs_val = get_register_value(rs_num)
            result = rs_val + immediate
            set_register_value(rt_num, result)

        elif opcode == '100011':  # LW
            base_num = parsed['rs_num']
            rt_num = parsed['rt_num']
            offset = parsed['immediate_num']
            base_val = get_register_value(base_num)
            eff_address = base_val + offset
            self.memory[eff_address] = self.memory.get(eff_address, 0)
            set_register_value(rt_num, self.memory[eff_address])

        elif opcode == '101011':  # SW
            base_num = parsed['rs_num']
            rt_num = parsed['rt_num']
            offset = parsed['immediate_num']
            base_val = get_register_value(base_num)
            eff_address = base_val + offset
            rt_val = get_register_value(rt_num)
            self.memory[eff_address] = rt_val

        elif opcode == '001111':  # LUI
            rt_num = parsed['rt_num']
            immediate = parsed['immediate_num']
            # Tratar immediate como valor não sinalizado
            immediate_unsigned = immediate & 0xFFFF
            result = immediate_unsigned << 16
            set_register_value(rt_num, result)
    
    def update_register_display(self):
        """Atualiza a exibição dos valores dos registradores na interface"""
        for reg_name in self.register_labels:
            value = self.registers[reg_name]
            
            # Converter para signed 32-bit se necessário
            if value > 0x7FFFFFFF:
                value -= 0x100000000
            
            self.register_labels[reg_name].config(text=str(value))

if __name__ == "__main__":
    app = MIPSSimulator()
    app.mainloop()
