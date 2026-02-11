<div align="center">

# 🏦 BankPY

**Simulação de Banking Core & Investimentos com Python**

<p align="center">
  <a href="#-funcionalidades">Funcionalidades</a> •
  <a href="#-como-executar">Instalação</a> •
  <a href="#-tecnologias">Tecnologias</a> •
  <a href="#-autor">Autor</a>
</p>

![Python Version](https://img.shields.io/badge/python-3.10%2B-820AD1?style=flat&logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/interface-CustomTkinter-820AD1?style=flat&logo=tcl&logoColor=white)
![Size](https://img.shields.io/github/repo-size/SEU-USUARIO/BankPY?color=820AD1&label=tamanho)
![License](https://img.shields.io/badge/license-MIT-820AD1?style=flat)

</div>

---

---

> Uma aplicação desktop robusta para simulação de operações financeiras, trading e gestão de carteira, desenvolvida com Python e CustomTkinter.

---

## 📋 Visão Geral

O **BankPY** é uma solução de software que simula o ecossistema de um banco digital (Fintech). O projeto foi arquitetado para demonstrar a implementação de lógica de negócios complexa aliada a uma interface gráfica moderna.

Diferente de sistemas básicos, o BankPY implementa um **motor de mercado financeiro** (`MarketAPI`), simulando volatilidade de ativos em tempo real e gerenciamento de dividendos baseado em datas, além de validação rigorosa de dados cadastrais (algoritmo de CPF).

---

## 🚀 Funcionalidades Principais

### 🔐 Segurança e Autenticação
- **Validação Algorítmica:** Implementação do algoritmo oficial de verificação de CPF (cálculo de dígitos verificadores) para impedir registros inválidos.
- **Persistência Segura:** Sistema de login com verificação de credenciais armazenadas localmente.
- **Prevenção de Duplicidade:** Verificação de unicidade de chaves (CPF) no banco de dados.

### 💸 Core Banking
- **Dashboard Financeiro:** Visualização consolidada de saldo e atalhos rápidos.
- **Sistema Pix:** Transferências peer-to-peer (P2P) entre usuários cadastrados com atualização atômica de saldos.
- **Ledger de Transações:** Registro imutável de todas as operações (Input/Output) com timestamp para auditoria (Extrato).

### 📈 Módulo de Investimentos (Mock Market)
- **Simulação de Volatilidade:** Variação dinâmica de preços de ativos (ex: PETR4, VALE3) a cada sessão.
- **Gestão de Portfólio:** Compra e venda de ativos com cálculo automático de **Preço Médio**.
- **Motor de Proventos:** Sistema que verifica datas de corte (Data Com) e executa o pagamento automático de dividendos na conta do usuário.

---

## 🛠️ Arquitetura e Tecnologias

O projeto segue princípios de **Programação Orientada a Objetos (POO)** e separação de responsabilidades:

| Componente | Responsabilidade |
|:--- |:--- |
| **Frontend (View)** | Desenvolvido com `CustomTkinter` para uma UI moderna, responsiva e com suporte a temas (Light/Dark). |
| **Backend (Controller/Model)** | Classe `BancoBackend` gerencia a lógica de negócios, validações e regras de transação. |
| **Data Layer** | Persistência em arquivo JSON (`bank_data.json`), simulando um banco de dados NoSQL documental. |
| **Mock API** | Classe estática `MarketAPI` que atua como um serviço externo de cotações e calendário corporativo. |

---

