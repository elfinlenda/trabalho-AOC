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
        self.title("🚀 Simulador MIPS")
        self.geometry("1200x800")
        self.configure(bg='#f0f0f0')
        
        # Definir estilo moderno
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Arial', 10), padding=6)
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.map('TButton', 
                      foreground=[('active', 'white'), ('disabled', 'gray')],
                      background=[('active', '#45a049'), ('disabled', '#cccccc')])
        
        self.instructions = []
        self.current_line = 0
        self.registers = {}
        self.memory = {}
        self.create_widgets()
        self.init_registers()
    
    def init_registers(self):
        """Inicializa todos os registradores com 0"""
        for i in range(32):
            reg_name = register_name(i)
            self.registers[reg_name] = 0
    
    def create_widgets(self):
        # Controles superiores
        self.dark_bg = '#2c3e50'
        self.light_bg = '#ecf0f1'
        self.highlight_color = '#3498db'

        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill=tk.X)

        button_style = {'style': 'TButton', 'padding': 8}
        self.load_btn = ttk.Button(control_frame, text="📂 Carregar", command=self.load_file, **button_style)
        self.step_btn = ttk.Button(control_frame, text="⏭ Passo", command=self.next_step, state=tk.DISABLED, **button_style)
        self.run_all_btn = ttk.Button(control_frame, text="⚡ Executar Tudo", command=self.run_all, state=tk.DISABLED, **button_style)
        self.reset_btn = ttk.Button(control_frame, text="🔄 Reset", command=self.reset_simulator, state=tk.DISABLED, **button_style)
        
        # Layout dos botões
        self.load_btn.pack(side=tk.LEFT, padx=5)
        self.step_btn.pack(side=tk.LEFT, padx=5)
        self.run_all_btn.pack(side=tk.LEFT, padx=5)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Área de código binário
        code_frame = ttk.Frame(self.notebook)
        self.notebook.add(code_frame, text='📝 Código Binário')
        code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Área de código com scroll
        self.code_text = tk.Text(code_frame, wrap=tk.NONE, font=('Consolas', 11), 
                                bg=self.dark_bg, fg='white', insertbackground='white')
        vsb = ttk.Scrollbar(code_frame, orient="vertical", command=self.code_text.yview)
        hsb = ttk.Scrollbar(code_frame, orient="horizontal", command=self.code_text.xview)
        self.code_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.code_text.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        code_frame.grid_rowconfigure(0, weight=1)
        code_frame.grid_columnconfigure(0, weight=1)
        
        self.code_text = tk.Text(code_frame, wrap=tk.NONE, font=('Courier', 10))
        vsb = tk.Scrollbar(code_frame, command=self.code_text.yview)
        hsb = tk.Scrollbar(code_frame, orient=tk.HORIZONTAL, command=self.code_text.xview)
        self.code_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.code_text.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
       
        
        # Painel de registradores
        register_frame = ttk.Frame(self.notebook)
        self.notebook.add(register_frame, text='🧮 Registradores')
        
        self.register_labels = {}
        for i in range(32):
            reg_name = register_name(i)
            row = i // 4
            col = (i % 4) * 2
            
            lbl_frame = ttk.Frame(register_frame, padding=5)
            lbl_frame.grid(row=row, column=col, padx=5, pady=2, sticky='w')
            
            ttk.Label(lbl_frame, text=f"{reg_name}:", 
                     font=('Arial', 10, 'bold'), 
                     foreground='#2c3e50').pack(side=tk.LEFT)
            
            lbl_value = ttk.Label(lbl_frame, text="0", 
                                font=('Consolas', 10), 
                                foreground='#e74c3c',
                                width=12)
            lbl_value.pack(side=tk.LEFT)
            self.register_labels[reg_name] = lbl_value

         # Painel de informações
        info_frame = ttk.Frame(self, padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.translation_label = ttk.Label(
            info_frame, 
            text="📋 Instrução Traduzida:",
            font=('Arial', 11, 'bold'),
            foreground='#27ae60'
        )
        self.translation_label.pack(anchor=tk.W)
        
        self.details_label = ttk.Label(
            info_frame,
            text="🔍 Detalhes:",
            font=('Arial', 10),
            foreground='#7f8c8d'
        )
        self.details_label.pack(anchor=tk.W)
        
        # Configurar tags para realce
        self.code_text.tag_configure('current', background='yellow', foreground='black')
        self.code_text.tag_configure('executed', background='#e0e0e0')
    
    def reset_simulator(self):
        """Reseta todo o estado da simulação"""
        self.current_line = 0
        self.init_registers()
        self.memory = {}
        self.update_register_display()
        self.clear_highlights()
        self.highlight_current_line()
        self.translation_label.config(text="Instrução Traduzida:")
        self.details_label.config(text="Detalhes da Decodificação:")
        # Mantém o botão Reset habilitado se houver código
        if self.instructions:
            self.step_btn.config(state=tk.NORMAL)
            self.run_all_btn.config(state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)
        else:
            self.reset_btn.config(state=tk.DISABLED)
    
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Arquivos de texto", "*.txt")])
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as file:
                self.instructions = [line.strip() for line in file]
                self.current_line = 0
                # Habilitar todos os botões relevantes
                self.step_btn.config(state=tk.NORMAL)
                self.run_all_btn.config(state=tk.NORMAL)
                self.reset_btn.config(state=tk.NORMAL)  # essa linha tava faltando tb
                self.init_registers()
                self.update_register_display()
                self.show_code()
                self.clear_highlights()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler arquivo:\n{str(e)}")
    
    def show_code(self):
        self.code_text.config(state=tk.NORMAL)
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(tk.END, '\n'.join(self.instructions))
        self.code_text.config(state=tk.DISABLED)
        self.highlight_current_line()
    
    def highlight_current_line(self):
        self.code_text.tag_remove('current', 1.0, tk.END)
        if self.current_line < len(self.instructions):
            line_start = f"{self.current_line + 1}.0"
            line_end = f"{self.current_line + 1}.end"
            self.code_text.tag_add('current', line_start, line_end)
            self.code_text.see(line_start)
    
    def clear_highlights(self):
        self.code_text.tag_remove('executed', 1.0, tk.END)
    
    def next_step(self):
        if self.current_line >= len(self.instructions):
            self.show_register_report()
            messagebox.showinfo("Fim", "Execução concluída!")
            self.step_btn.config(state=tk.DISABLED)
            return
        
        bin_instr = self.instructions[self.current_line]
        assembly, parsed = bin_to_assembly(bin_instr)
        
        if parsed is None:
            messagebox.showinfo("Completo", " Execução concluída! ")
            return
        
        self.translation_label.config(text=f"Instrução Traduzida: {assembly}")
        self.details_label.config(text=f"Decodificando: {bin_instr}")
        self.highlight_current_line()
        
        self.execute_instruction(parsed)
        self.update_register_display()
        self.update()  # Força a atualização imediata da interface gráfica
        
        line_start = f"{self.current_line + 1}.0"
        line_end = f"{self.current_line + 1}.end"
        self.code_text.tag_add('executed', line_start, line_end)
        
        self.current_line += 1

    def run_all(self):
        if not self.instructions:
            messagebox.showwarning("Aviso", "Nenhum código carregado!")
            return
        
        self.reset_simulator()
        
        assembly_code = []
        for bin_instr in self.instructions:
            instr, _ = bin_to_assembly(bin_instr)
            assembly_code.append(instr)
        self.show_assembly(assembly_code)

        # Executar todas as instruções
        self.current_line = 0
        while self.current_line < len(self.instructions):
            bin_instr = self.instructions[self.current_line]
            parsed = parse_instruction(bin_instr)
            if parsed:
                self.execute_instruction(parsed)
            self.current_line += 1

        # Forçar atualização imediata da interface
        self.update_register_display()
        self.update_idletasks()
        
        # Mostrar relatório
        self.highlight_current_line()
        self.code_text.tag_add('executed', '1.0', tk.END)
        self.show_register_report()
        messagebox.showinfo("Concluído", "Execução completa!")

    def show_register_report(self):
        """Exibe relatório completo dos registradores em nova janela"""

        report_window = tk.Toplevel(self)
        report_window.title("📊 Relatório de Registradores")
        report_window.geometry("800x500")
        
        # Frame principal com scroll
        main_frame = tk.Frame(report_window)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas e scrollbar
        canvas = tk.Canvas(main_frame)
        scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)
        
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
        
        # Cabeçalho
        tk.Label(scrollable_frame, 
                text="Registrador".ljust(15) + "Valor Decimal".ljust(20) + "Valor Hexadecimal",
                font=('Courier', 10, 'bold')).pack(anchor='w')
        
        # Conteúdo dos registradores
        for reg_name in sorted(self.registers.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
            value = self.registers[reg_name]
            # Converter para signed 32-bit
            if value > 0x7FFFFFFF:
                value -= 0x100000000
            hex_value = f"{value & 0xFFFFFFFF:08x}"
            
            line = f"{reg_name.ljust(15)}{str(value).ljust(20)}0x{hex_value}"
            tk.Label(scrollable_frame, 
                    text=line,
                    font=('Courier', 10)).pack(anchor='w')

    def show_assembly(self, assembly_code):
        # Criar nova janela para exibir o assembly
        asm_window = tk.Toplevel(self)
        asm_window.title("📜 Código Assembly")
        
        text_frame = ttk.Frame(asm_window)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        asm_text = tk.Text(text_frame, wrap=tk.NONE, font=('Consolas', 11), 
                          bg=self.dark_bg, fg='white')
        vsb = ttk.Scrollbar(text_frame, orient="vertical", command=asm_text.yview)
        hsb = ttk.Scrollbar(text_frame, orient="horizontal", command=asm_text.xview)
        
        asm_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        asm_text.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        asm_text.insert(tk.END, '\n'.join(assembly_code))
        asm_text.config(state=tk.DISABLED)
    
    def execute_instruction(self, parsed):
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
                set_register_value(32, (result >> 32) & 0xFFFFFFFF)  # HI
                set_register_value(33, result & 0xFFFFFFFF)           # LO

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
        for reg_name in self.register_labels:
            value = self.registers[reg_name]
            self.register_labels[reg_name].config(text=str(value))

if __name__ == "__main__":
    simulator = MIPSSimulator()
    simulator.mainloop() 
