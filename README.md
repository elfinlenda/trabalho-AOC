
# Simulador MIPS

Este projeto é um simulador do processador MIPS, implementado em Python e com uma interface gráfica baseada na biblioteca Tkinter.

## Recursos disponíveis

- Execução de instruções fundamentais da arquitetura MIPS
- Interface visual que exibe o estado dos registradores e da memória
- Simulação interativa com execução passo a passo

## Capturas de Tela

1. **img_mips1.png**  
   Tela principal da aplicação, com tradução para assembly e visualização dos registradores. Também permite carregar arquivos, executar instruções uma por uma ou de forma contínua.

![Image](https://github.com/user-attachments/assets/708be90f-7475-4a5f-81f8-448cef7ca7a3)


2. **img_mips2.png**  
   Demonstração da leitura do código binário, com destaque nos registradores utilizados em cada operação.

![image](https://github.com/user-attachments/assets/32215b1e-32bf-49df-ad08-157ea7128f61)


3. **img_mips3.png**  
   Exemplo da conversão completa do binário para código assembly.

![Image](https://github.com/user-attachments/assets/311cded4-55ea-4ec1-817b-5c4e065a4be6)


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
   python SimuladorMips.py
   ```
