
# Simulador MIPS

Este projeto é um simulador do processador MIPS, implementado em Python e com uma interface gráfica baseada na biblioteca Tkinter.

## Recursos disponíveis

- Execução de instruções fundamentais da arquitetura MIPS
- Interface visual que exibe o estado dos registradores e da memória
- Simulação interativa com execução passo a passo

## Capturas de Tela

1. **img_mips1.png**  
   Tela principal da aplicação, com tradução para assembly e visualização dos registradores. Também permite carregar arquivos, executar instruções uma por uma ou de forma contínua.

![image](https://github.com/user-attachments/assets/2639fc59-d055-46d5-b034-f1d68d22d997)


2. **img_mips2.png**  
   Demonstração da leitura do código binário, com destaque nos registradores utilizados em cada operação.

   ![image](https://github.com/user-attachments/assets/05b9033b-5a99-4c4f-b645-747f60643f7b)


3. **img_mips3.png**  
   Exemplo da conversão completa do binário para código assembly.

   ![image](https://github.com/user-attachments/assets/8f5774e0-d46e-48af-b4cc-482e120a3c10)


## Como executar o simulador

### Pré-requisitos:
- Python devidamente instalado
- Suporte à biblioteca Tkinter (normalmente já incluída nas instalações padrão)

### Etapas para execução:
1. Abra o projeto no Visual Studio Code (ou editor de sua preferência)
2. Certifique-se de que o Tkinter está funcionando  
   - **No Windows:** `python app.py`  
   - **No Linux:** `python3 app.py`
3. Execute o simulador via terminal com:

   ```bash
   python mips_simulator.py
   ```
