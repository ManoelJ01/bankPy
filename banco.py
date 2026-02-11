import customtkinter as ctk
from tkinter import messagebox
import os
import json
from datetime import datetime, timedelta
import random

# --- Configurações Visuais ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

class Cores:
    ROXO_PRINCIPAL = "#820AD1"
    ROXO_HOVER = "#6A05A8"
    BRANCO = "#FFFFFF"
    CINZA_CLARO = "#F5F5F5"
    CINZA_ESCURO = "#E0E0E0"
    PRETO = "#111111"
    CINZA_TEXTO = "#666666"
    VERDE_SUCESSO = "#2ECC71"
    VERMELHO_ERRO = "#E74C3C"

# --- Simulação de API e Backend ---
class MarketAPI:
    EMPRESAS = {
        "PETR4": {"nome": "Petrobras", "preco_base": 35.50},
        "VALE3": {"nome": "Vale", "preco_base": 68.20},
        "ITUB4": {"nome": "Itaú Unibanco", "preco_base": 32.10},
        "AAPL34": {"nome": "Apple BDR", "preco_base": 45.80},
        "WEGE3": {"nome": "WEG", "preco_base": 40.00}
    }
    CALENDARIO_DIVIDENDOS = {
        "PETR4": {"valor_acao": 1.45, "offset_dias": 0},
        "VALE3": {"valor_acao": 0.90, "offset_dias": 5},
        "ITUB4": {"valor_acao": 0.35, "offset_dias": 15},
        "WEGE3": {"valor_acao": 0.20, "offset_dias": 30},
    }

    @staticmethod
    def get_prices():
        cotacoes = {}
        for ticker, dados in MarketAPI.EMPRESAS.items():
            variacao = random.uniform(-0.02, 0.02)
            preco_atual = dados["preco_base"] * (1 + variacao)
            cotacoes[ticker] = {
                "nome": dados["nome"],
                "preco": round(preco_atual, 2),
                "variacao": round(variacao * 100, 2)
            }
        return cotacoes

    @staticmethod
    def get_info_dividendos():
        hoje = datetime.now()
        info = {}
        for ticker, dados in MarketAPI.CALENDARIO_DIVIDENDOS.items():
            data_pag = hoje + timedelta(days=dados["offset_dias"])
            info[ticker] = {
                "valor": dados["valor_acao"],
                "data": data_pag.strftime("%d/%m/%Y"),
                "data_obj": data_pag.date(),
                "status": "Hoje" if dados["offset_dias"] == 0 else f"Em {dados['offset_dias']} dias"
            }
        return info

class BancoBackend:
    def __init__(self, arquivo="bank_data.json"):
        self.arquivo = arquivo
        if not os.path.exists(self.arquivo):
            self._salvar([])

    def _ler(self):
        try:
            with open(self.arquivo, "r", encoding='utf-8') as f: return json.load(f)
        except: return []

    def _salvar(self, dados):
        with open(self.arquivo, "w", encoding='utf-8') as f: json.dump(dados, f, indent=4, ensure_ascii=False)

    def _get_timestamp(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M")

    # --- NOVA FUNÇÃO DE VALIDAÇÃO DE CPF ---
    def _validar_cpf_real(self, cpf):
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))

        # Verifica tamanho e se todos os números são iguais
        if len(cpf) != 11 or cpf == cpf[0] * 11:
            return False

        # Cálculo do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        dv1 = 0 if resto < 2 else 11 - resto
        if dv1 != int(cpf[9]):
            return False

        # Cálculo do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        dv2 = 0 if resto < 2 else 11 - resto
        if dv2 != int(cpf[10]):
            return False

        return True

    def login(self, cpf, senha):
        # Limpa o CPF para login também
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        users = self._ler()
        for u in users:
            # Compara com o CPF limpo do banco
            if u["cpf"] == cpf_limpo and u["senha"] == senha:
                if "extrato" not in u: u["extrato"] = []
                if "investimentos" not in u: u["investimentos"] = {}
                if "dividendos_recebidos" not in u: u["dividendos_recebidos"] = {}
                return True, u
        return False, "Credenciais inválidas."

    def cadastrar(self, nome, cpf, senha):
        # Limpa o CPF recebido (remove pontos e traços)
        cpf_limpo = ''.join(filter(str.isdigit, cpf))

        # 1. Validação do Algoritmo de CPF
        if not self._validar_cpf_real(cpf_limpo):
            return False, "CPF inválido! Verifique os números."

        dados = self._ler()
        # Verifica duplicidade usando CPF limpo
        if any(u['cpf'] == cpf_limpo for u in dados): 
            return False, "CPF já cadastrado."
        
        # Salva apenas os números no banco
        novo_usuario = {
            "nome": nome, 
            "cpf": cpf_limpo, 
            "senha": senha, 
            "saldo": 0.0, 
            "extrato": [], 
            "investimentos": {}, 
            "dividendos_recebidos": {}
        }
        dados.append(novo_usuario)
        self._salvar(dados)
        return True, "Conta criada com sucesso."

    def registrar_transacao(self, usuario, tipo, valor, detalhe=""):
        transacao = {"data": self._get_timestamp(), "tipo": tipo, "valor": valor, "detalhe": detalhe}
        usuario["extrato"].insert(0, transacao)

    def deposito_saque(self, cpf, valor, tipo):
        dados = self._ler()
        for u in dados:
            if u["cpf"] == cpf:
                u["saldo"] += valor
                self.registrar_transacao(u, tipo, valor)
                self._salvar(dados)
                return u["saldo"], u["extrato"]
        return None, None

    def realizar_pix(self, cpf_remetente, cpf_destinatario, valor):
        # Limpa o CPF de destino caso o usuário digite com pontos
        cpf_dest_limpo = ''.join(filter(str.isdigit, cpf_destinatario))
        
        dados = self._ler()
        remetente = next((u for u in dados if u["cpf"] == cpf_remetente), None)
        destinatario = next((u for u in dados if u["cpf"] == cpf_dest_limpo), None)
        
        if not destinatario: return False, "Chave Pix (CPF) não encontrada."
        if remetente["cpf"] == destinatario["cpf"]: return False, "Pix para mesma conta."
        if remetente["saldo"] < valor: return False, "Saldo insuficiente."
        
        remetente["saldo"] -= valor
        destinatario["saldo"] += valor
        self.registrar_transacao(remetente, "Pix Enviado", -valor, f"Para: {destinatario['nome']}")
        self.registrar_transacao(destinatario, "Pix Recebido", valor, f"De: {remetente['nome']}")
        self._salvar(dados)
        return True, remetente["saldo"]

    def investir(self, cpf, ticker, qtd, preco_unitario, tipo="compra"):
        dados = self._ler()
        user = next((u for u in dados if u["cpf"] == cpf), None)
        valor_total = qtd * preco_unitario
        if tipo == "compra":
            if user["saldo"] < valor_total: return False, "Saldo insuficiente."
            user["saldo"] -= valor_total
            if ticker not in user["investimentos"]: user["investimentos"][ticker] = {"qtd": 0, "preco_medio": 0}
            cart = user["investimentos"][ticker]
            cart["preco_medio"] = ((cart["qtd"] * cart["preco_medio"]) + valor_total) / (cart["qtd"] + qtd)
            cart["qtd"] += qtd
            self.registrar_transacao(user, "Investimento", -valor_total, f"Compra {qtd}x {ticker}")
        elif tipo == "venda":
            if ticker not in user["investimentos"] or user["investimentos"][ticker]["qtd"] < qtd: return False, "Qtd insuficiente."
            user["saldo"] += valor_total
            user["investimentos"][ticker]["qtd"] -= qtd
            if user["investimentos"][ticker]["qtd"] == 0: del user["investimentos"][ticker]
            self.registrar_transacao(user, "Resgate Inv.", valor_total, f"Venda {qtd}x {ticker}")
        self._salvar(dados)
        return True, user

    def processar_pagamentos_dividendos(self, cpf):
        dados = self._ler()
        user = next((u for u in dados if u["cpf"] == cpf), None)
        info_div = MarketAPI.get_info_dividendos()
        hoje = datetime.now().date()
        total_pago = 0
        lista = []
        for ticker, d_mercado in info_div.items():
            if ticker in user["investimentos"] and user["investimentos"][ticker]["qtd"] > 0:
                chave = f"{ticker}_{d_mercado['data']}"
                if d_mercado["data_obj"] <= hoje and chave not in user.get("dividendos_recebidos", {}):
                    val = d_mercado["valor"] * user["investimentos"][ticker]["qtd"]
                    user["saldo"] += val
                    total_pago += val
                    if "dividendos_recebidos" not in user: user["dividendos_recebidos"] = {}
                    user["dividendos_recebidos"][chave] = True
                    self.registrar_transacao(user, "Dividendos", val, ticker)
                    lista.append(f"{ticker}: R$ {val:.2f}")
        if total_pago > 0:
            self._salvar(dados)
            return True, total_pago, lista, user
        return False, 0, [], user

# --- Interfaces Gráficas ---

class LoginFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Cores.CINZA_CLARO, corner_radius=15)
        self.controller = controller
        self.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self, text="BankPY", font=("Roboto Medium", 30), text_color=Cores.ROXO_PRINCIPAL).pack(pady=(40,10), padx=100)
        self.entry_cpf = ctk.CTkEntry(self, placeholder_text="CPF", width=250, border_width=0, fg_color=Cores.BRANCO)
        self.entry_cpf.pack(pady=10)
        self.entry_senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*", width=250, border_width=0, fg_color=Cores.BRANCO)
        self.entry_senha.pack(pady=10)
        ctk.CTkButton(self, text="ENTRAR", width=250, fg_color=Cores.ROXO_PRINCIPAL, hover_color=Cores.ROXO_HOVER, command=self._fazer_login).pack(pady=20)
        ctk.CTkButton(self, text="Criar conta", fg_color="transparent", text_color=Cores.ROXO_PRINCIPAL, hover_color=Cores.BRANCO, command=lambda: controller.trocar_tela("cadastro")).pack(pady=(0, 40))

    def _fazer_login(self):
        cpf = self.entry_cpf.get()
        senha = self.entry_senha.get()
        sucesso, resposta = self.controller.backend.login(cpf, senha)
        if sucesso:
            self.controller.usuario_atual = resposta
            self.controller.trocar_tela("dashboard")
        else: messagebox.showerror("Erro", resposta)

class CadastroFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=Cores.CINZA_CLARO, corner_radius=15)
        self.controller = controller
        self.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(self, text="Nova Conta", font=("Roboto Medium", 24), text_color=Cores.ROXO_PRINCIPAL).pack(pady=30, padx=100)
        self.nome = ctk.CTkEntry(self, placeholder_text="Nome", width=250, border_width=0, fg_color=Cores.BRANCO)
        self.nome.pack(pady=5)
        self.cpf = ctk.CTkEntry(self, placeholder_text="CPF", width=250, border_width=0, fg_color=Cores.BRANCO)
        self.cpf.pack(pady=5)
        self.senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*", width=250, border_width=0, fg_color=Cores.BRANCO)
        self.senha.pack(pady=5)
        ctk.CTkButton(self, text="CADASTRAR", width=250, fg_color=Cores.ROXO_PRINCIPAL, hover_color=Cores.ROXO_HOVER, command=self._registrar).pack(pady=20)
        ctk.CTkButton(self, text="Voltar", fg_color="transparent", text_color=Cores.CINZA_TEXTO, hover_color=Cores.BRANCO, command=lambda: controller.trocar_tela("login")).pack(pady=5)

    def _registrar(self):
        sucesso, msg = self.controller.backend.cadastrar(self.nome.get(), self.cpf.get(), self.senha.get())
        if sucesso:
            messagebox.showinfo("Sucesso", msg)
            self.controller.trocar_tela("login")
        else: messagebox.showerror("Erro", msg)

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(fill="both", expand=True)

        self._verificar_dividendos()

        # Layout Principal: Sidebar (Col 0) | Conteúdo (Col 1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar (Esquerda)
        self._criar_sidebar()

        # 2. Área Principal (Direita)
        self.area_principal = ctk.CTkFrame(self, fg_color="transparent")
        self.area_principal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Inicia na tela Home
        self._trocar_conteudo("inicio")

    def _verificar_dividendos(self):
        pagou, total, lista, user_att = self.controller.backend.processar_pagamentos_dividendos(self.controller.usuario_atual['cpf'])
        if pagou:
            self.controller.usuario_atual = user_att
            messagebox.showinfo("Dividendos", f"Recebido: R$ {total:.2f}")

    def _criar_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=Cores.CINZA_CLARO)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False) # Mantém largura fixa

        # Título e Usuário
        ctk.CTkLabel(sidebar, text="BankPY", font=("Roboto Medium", 24), text_color=Cores.ROXO_PRINCIPAL).pack(pady=(40, 20))
        nome = self.controller.usuario_atual['nome'].split()[0]
        ctk.CTkLabel(sidebar, text=f"Olá, {nome}", font=("Roboto", 16), text_color=Cores.CINZA_TEXTO).pack(pady=(0, 30))

        # Botões de Navegação (Menu Lateral)
        self._criar_botao_menu(sidebar, "Início", "inicio")
        self._criar_botao_menu(sidebar, "Pix", "pix")
        self._criar_botao_menu(sidebar, "Investimentos", "investimentos")
        self._criar_botao_menu(sidebar, "Extrato", "extrato")

        # Botão Sair (Lá em baixo)
        ctk.CTkButton(sidebar, text="SAIR", fg_color="transparent", text_color=Cores.VERMELHO_ERRO, 
                      hover_color="#FFEEEE", border_width=1, border_color=Cores.VERMELHO_ERRO,
                      command=self._logout).pack(side="bottom", pady=20, padx=20, fill="x")

    def _criar_botao_menu(self, parent, texto, chave):
        ctk.CTkButton(parent, text=texto, fg_color="transparent", text_color=Cores.PRETO, 
                      anchor="w", hover_color=Cores.BRANCO, height=40, font=("Roboto Medium", 14),
                      command=lambda: self._trocar_conteudo(chave)).pack(fill="x", padx=10, pady=5)

    def _trocar_conteudo(self, tela):
        # Limpa a área principal
        for widget in self.area_principal.winfo_children():
            widget.destroy()

        if tela == "inicio": self._montar_inicio()
        elif tela == "pix": self._montar_pix()
        elif tela == "investimentos": self._montar_investimentos()
        elif tela == "extrato": self._montar_extrato()

    # --- TELA: INÍCIO (Modificada: Mais Larga e Proporcional) ---
    def _montar_inicio(self):
        # Container principal centralizado que ocupa 80% da largura (relwidth=0.8)
        container = ctk.CTkFrame(self.area_principal, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8)

        # Card de Saldo (Esticado)
        card = ctk.CTkFrame(container, height=180, corner_radius=20, fg_color=Cores.ROXO_PRINCIPAL)
        card.pack(fill="x", pady=(0, 20)) # fill="x" faz esticar horizontalmente
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="Saldo Disponível", text_color="#E0E0E0", font=("Roboto", 16)).pack(pady=(45, 5))
        self.lbl_saldo = ctk.CTkLabel(card, text=f"R$ {self.controller.usuario_atual['saldo']:.2f}", font=("Roboto", 48, "bold"), text_color="white")
        self.lbl_saldo.pack()

        # Botões de Ação (Container que estica)
        frame_acoes = ctk.CTkFrame(container, fg_color="transparent")
        frame_acoes.pack(fill="x") # Estica o container dos botões

        # Botões ocupam todo o espaço disponível dividindo meio a meio (expand=True)
        btn_dep = ctk.CTkButton(frame_acoes, text="Depositar (+)", height=70,
                                font=("Roboto Medium", 18), fg_color=Cores.CINZA_CLARO, 
                                text_color=Cores.ROXO_PRINCIPAL, hover_color=Cores.CINZA_ESCURO,
                                command=lambda: self._transacao_simples("deposito"))
        btn_dep.pack(side="left", padx=(0, 10), fill="x", expand=True)

        btn_sac = ctk.CTkButton(frame_acoes, text="Sacar (-)", height=70,
                                font=("Roboto Medium", 18), fg_color=Cores.CINZA_CLARO, 
                                text_color=Cores.ROXO_PRINCIPAL, hover_color=Cores.CINZA_ESCURO,
                                command=lambda: self._transacao_simples("saque"))
        btn_sac.pack(side="right", padx=(10, 0), fill="x", expand=True)

    # --- TELA: PIX (Modificada: Centralizada e Proporcional) ---
    def _montar_pix(self):
        # Container centralizado para alinhar o título
        main_container = ctk.CTkFrame(self.area_principal, fg_color="transparent")
        main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6) # Ocupa 60% da tela

        ctk.CTkLabel(main_container, text="Área Pix", font=("Roboto Medium", 32), text_color=Cores.PRETO).pack(pady=(0, 30))
        
        # Card do Formulário (Ocupa toda a largura do main_container)
        frame = ctk.CTkFrame(main_container, fg_color=Cores.CINZA_CLARO, corner_radius=20)
        frame.pack(fill="x", pady=10) # fill="x" para esticar
        
        # Inputs esticados dentro do card
        self.pix_cpf = ctk.CTkEntry(frame, placeholder_text="Chave Pix (CPF)", height=50, border_width=0, fg_color=Cores.BRANCO)
        self.pix_cpf.pack(pady=30, padx=40, fill="x")
        
        self.pix_valor = ctk.CTkEntry(frame, placeholder_text="Valor (R$)", height=50, border_width=0, fg_color=Cores.BRANCO)
        self.pix_valor.pack(pady=(0, 30), padx=40, fill="x")
        
        ctk.CTkButton(frame, text="ENVIAR PIX", height=55, fg_color=Cores.ROXO_PRINCIPAL, 
                      hover_color=Cores.ROXO_HOVER, font=("Roboto Medium", 16),
                      command=self._enviar_pix).pack(pady=(0, 40), padx=40, fill="x")

    def _montar_investimentos(self):
        self.area_principal.grid_columnconfigure(0, weight=1)
        self.area_principal.grid_columnconfigure(1, weight=1)
        self.area_principal.grid_rowconfigure(0, weight=1)

        # Coluna 1: Mercado
        frame_mercado = ctk.CTkScrollableFrame(self.area_principal, label_text="Mercado", height=500)
        frame_mercado.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        cotacoes = MarketAPI.get_prices()
        for ticker, dados in cotacoes.items():
            cor = Cores.VERDE_SUCESSO if dados["variacao"] >= 0 else Cores.VERMELHO_ERRO
            card = ctk.CTkFrame(frame_mercado, fg_color=Cores.CINZA_CLARO)
            card.pack(fill="x", pady=5)
            
            ctk.CTkLabel(card, text=f"{ticker}\nR$ {dados['preco']:.2f}", text_color=Cores.PRETO, 
                         font=("Roboto", 14, "bold"), justify="left").pack(side="left", padx=10, pady=10)
            ctk.CTkLabel(card, text=f"{dados['variacao']}%", text_color=cor, font=("Roboto", 12)).pack(side="left", padx=5)
            ctk.CTkButton(card, text="Comprar", width=60, height=25, fg_color=Cores.ROXO_PRINCIPAL, 
                          command=lambda t=ticker, p=dados['preco']: self._comprar_acao(t, p)).pack(side="right", padx=10)

        # Coluna 2: Carteira
        direita_frame = ctk.CTkFrame(self.area_principal, fg_color="transparent")
        direita_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        ctk.CTkLabel(direita_frame, text="Minha Carteira", font=("Roboto Medium", 18), text_color=Cores.PRETO).pack(anchor="w", pady=(0, 10))
        
        self.carteira_container = ctk.CTkScrollableFrame(direita_frame, height=250)
        self.carteira_container.pack(fill="x", pady=(0, 20))
        self._atualizar_carteira_ui()

        ctk.CTkLabel(direita_frame, text="Proventos Futuros", font=("Roboto Medium", 18), text_color=Cores.PRETO).pack(anchor="w", pady=(0, 10))
        self.proventos_container = ctk.CTkScrollableFrame(direita_frame, height=200)
        self.proventos_container.pack(fill="both", expand=True)
        self._atualizar_calendario_ui()

    def _montar_extrato(self):
        ctk.CTkLabel(self.area_principal, text="Histórico de Transações", font=("Roboto Medium", 22), text_color=Cores.PRETO).pack(anchor="w", pady=(0, 20))
        self.frame_extrato = ctk.CTkScrollableFrame(self.area_principal, fg_color="transparent")
        self.frame_extrato.pack(fill="both", expand=True)
        self._atualizar_extrato_ui()

    # --- Atualizações de UI ---
    def _atualizar_carteira_ui(self):
        for widget in self.carteira_container.winfo_children(): widget.destroy()
        investimentos = self.controller.usuario_atual.get("investimentos", {})
        if not investimentos: ctk.CTkLabel(self.carteira_container, text="Carteira vazia.").pack(pady=10)
        for ticker, dados in investimentos.items():
            if dados['qtd'] > 0:
                card = ctk.CTkFrame(self.carteira_container, fg_color=Cores.BRANCO)
                card.pack(fill="x", pady=2)
                ctk.CTkLabel(card, text=f"{ticker} (x{dados['qtd']})", text_color=Cores.PRETO).pack(side="left", padx=10, pady=10)
                ctk.CTkButton(card, text="Vender", width=60, fg_color=Cores.VERMELHO_ERRO, height=25,
                              command=lambda t=ticker: self._vender_acao(t)).pack(side="right", padx=10)

    def _atualizar_calendario_ui(self):
        for widget in self.proventos_container.winfo_children(): widget.destroy()
        info = MarketAPI.get_info_dividendos()
        user_invest = self.controller.usuario_atual.get("investimentos", {})
        for ticker, dados in info.items():
            if ticker in user_invest and user_invest[ticker]["qtd"] > 0:
                qtd = user_invest[ticker]["qtd"]
                card = ctk.CTkFrame(self.proventos_container, fg_color=Cores.BRANCO)
                card.pack(fill="x", pady=5)
                ctk.CTkLabel(card, text=f"{ticker} - {dados['data']}", font=("Roboto", 12, "bold"), text_color=Cores.ROXO_PRINCIPAL).pack(anchor="w", padx=10, pady=5)
                ctk.CTkLabel(card, text=f"Previsto: R$ {(dados['valor']*qtd):.2f}", font=("Roboto", 12), text_color=Cores.VERDE_SUCESSO).pack(anchor="e", padx=10, pady=5)

    def _atualizar_extrato_ui(self):
        for widget in self.frame_extrato.winfo_children(): widget.destroy()
        extrato = self.controller.usuario_atual.get("extrato", [])
        for item in extrato:
            cor = Cores.VERDE_SUCESSO if item["valor"] > 0 else Cores.VERMELHO_ERRO
            card = ctk.CTkFrame(self.frame_extrato, fg_color=Cores.BRANCO, height=50)
            card.pack(fill="x", pady=3)
            ctk.CTkLabel(card, text=f"{item['data']} - {item['tipo']}", text_color=Cores.CINZA_TEXTO).pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(card, text=f"R$ {abs(item['valor']):.2f}", text_color=cor, font=("Roboto", 12, "bold")).pack(side="right", padx=15)

    def _atualizar_saldo_visual(self):
        # Atualiza apenas se o label existir (estiver na tela Home)
        if hasattr(self, 'lbl_saldo') and self.lbl_saldo.winfo_exists():
            self.lbl_saldo.configure(text=f"R$ {self.controller.usuario_atual['saldo']:.2f}")

    # --- Lógica de Negócio (Calls) ---
    def _transacao_simples(self, tipo):
        dialog = ctk.CTkInputDialog(text="Valor:", title=tipo.capitalize())
        v = dialog.get_input()
        if v:
            try:
                val = float(v)
                
                # Se for saque, inverte o sinal para negativo E verifica saldo
                if tipo == "saque": 
                    if val > self.controller.usuario_atual['saldo']:
                        messagebox.showwarning("Ops", "Saldo insuficiente")
                        return
                    val = -val # Torna negativo para o backend
                
                # Envia o valor (já negativo se for saque) para o backend
                ns, _ = self.controller.backend.deposito_saque(self.controller.usuario_atual['cpf'], val, tipo.capitalize())
                
                self.controller.usuario_atual['saldo'] = ns
                self._atualizar_saldo_visual()
                
                if tipo == "saque": 
                    self._trocar_conteudo("inicio") # Refresh
                else: 
                    self._atualizar_saldo_visual()
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido")

    def _enviar_pix(self):
        try:
            val = float(self.pix_valor.get())
            ok, res = self.controller.backend.realizar_pix(self.controller.usuario_atual['cpf'], self.pix_cpf.get(), val)
            if ok: 
                self.controller.usuario_atual['saldo'] = res
                messagebox.showinfo("Sucesso", "Pix enviado!")
                self._trocar_conteudo("inicio")
            else: messagebox.showerror("Erro", res)
        except: pass

    def _comprar_acao(self, ticker, preco):
        d = ctk.CTkInputDialog(text="Qtd:", title="Comprar")
        q = d.get_input()
        if q:
            ok, res = self.controller.backend.investir(self.controller.usuario_atual['cpf'], ticker, int(q), preco, "compra")
            if ok:
                self.controller.usuario_atual = res
                messagebox.showinfo("Sucesso", "Ação comprada!")
                self._trocar_conteudo("investimentos") # Refresh
            else: messagebox.showerror("Erro", res)

    def _vender_acao(self, ticker):
        d = ctk.CTkInputDialog(text="Qtd:", title="Vender")
        q = d.get_input()
        if q:
            # Preço aproximado de venda (pega da API)
            preco = MarketAPI.EMPRESAS[ticker]["preco_base"] 
            ok, res = self.controller.backend.investir(self.controller.usuario_atual['cpf'], ticker, int(q), preco, "venda")
            if ok:
                self.controller.usuario_atual = res
                messagebox.showinfo("Sucesso", "Venda realizada!")
                self._trocar_conteudo("investimentos") # Refresh
            else: messagebox.showerror("Erro", res)

    def _logout(self):
        self.controller.usuario_atual = None
        self.controller.trocar_tela("login")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.backend = BancoBackend()
        self.usuario_atual = None
        self.title("BankPY - Sistema Financeiro")
        self.geometry("1100x700")
        self.configure(fg_color=Cores.BRANCO)
        self.tela_atual = None
        self.trocar_tela("login")

    def trocar_tela(self, nome_tela):
        if self.tela_atual: self.tela_atual.destroy()
        if nome_tela == "login": self.tela_atual = LoginFrame(self, self)
        elif nome_tela == "cadastro": self.tela_atual = CadastroFrame(self, self)
        elif nome_tela == "dashboard": self.tela_atual = DashboardFrame(self, self)

if __name__ == "__main__":
    app = App()
    app.mainloop()