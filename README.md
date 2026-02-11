# 🏦 BankPY - Sistema Bancário e de Investimentos

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Concluído-success?style=for-the-badge)

## 📄 Sobre o Projeto

O **BankPY** é uma aplicação desktop de simulação bancária desenvolvida em Python. O projeto utiliza a biblioteca **CustomTkinter** para criar uma interface gráfica moderna e responsiva (modo Light/Dark). 

O objetivo do sistema é simular as operações essenciais de um banco digital, incluindo transações financeiras em tempo real e um módulo de investimentos com variação de preços e pagamento de dividendos simulados.

## 🚀 Funcionalidades

### 🔐 Autenticação e Segurança
* **Login e Cadastro:** Sistema de criação de contas com persistência de dados.
* **Validação de CPF:** Algoritmo real de validação de CPF (cálculo dos dígitos verificadores) para impedir cadastros inválidos.
* **Proteção:** Verificação de duplicidade de contas.

### 💸 Serviços Bancários
* **Dashboard Interativo:** Visão geral do saldo e menu lateral de navegação.
* **Transações:** Depósitos e Saques com atualização imediata do saldo.
* **Sistema Pix:** Transferência de valores entre contas cadastradas utilizando o CPF como chave.
* **Extrato:** Histórico detalhado de todas as operações (entradas e saídas) com data e hora.

### 📈 Módulo de Investimentos (MarketAPI)
* **Simulação de Bolsa:** Cotações de ações (ex: PETR4, VALE3) com variação aleatória de preços simulada a cada execução.
* **Carteira de Ativos:** Compra e venda de ações, com cálculo de preço médio.
* **Dividendos:** Sistema automatizado que verifica datas e "paga" proventos aos acionistas baseados em um calendário simulado.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** [Python](https://www.python.org/)
* **Interface Gráfica:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Wrapper moderno do Tkinter).
* **Persistência de Dados:** JSON (Armazenamento local em `bank_data.json` simulando um banco NoSQL).
* **Bibliotecas Nativas:**
    * `os` e `json`: Manipulação de arquivos e dados.
    * `datetime`: Controle de timestamps e datas de dividendos.
    * `random`: Simulação de volatilidade do mercado financeiro.

---

## ⚙️ Estrutura do Código

O projeto foi estruturado seguindo princípios de orientação a objetos, separando a lógica de negócios da interface gráfica:

* **`BancoBackend`**: Classe responsável por toda a lógica "server-side" (CRUD de usuários, validações, transações e manipulação do JSON).
* **`MarketAPI`**: Classe estática que simula uma API externa de bolsa de valores e calendário de proventos.
* **`App` & Frames**: Classes que herdam de `ctk.CTk` e `ctk.CTkFrame` para renderizar as telas (Login, Cadastro, Dashboard, Pix, Investimentos).

---

## 📦 Como Executar

### Pré-requisitos
* Python 3.x instalado.
* Gerenciador de pacotes `pip`.

### Passo a passo

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/SEU-USUARIO/BankPY.git](https://github.com/SEU-USUARIO/BankPY.git)
   cd BankPY
