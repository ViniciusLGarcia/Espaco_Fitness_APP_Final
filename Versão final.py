import flet as ft
import json
import os
import time
import asyncio
from flet import Icons

# ===================================================================
# 1. CONSTANTES GLOBAIS
# Define valores fixos usados em todo o aplicativo.
# ===================================================================

NUMERO_WHATSAPP = "5511939222617"
ARQUIVO_USUARIOS = "users.json"

# ===================================================================
# 2. FUNÇÕES DE PERSISTÊNCIA DE DADOS
# Funções responsáveis por ler e salvar os dados dos usuários
# em um arquivo JSON local.
# ===================================================================

# Carrega a lista de usuários do arquivo JSON. Se o arquivo não
# existir, cria um novo com uma lista vazia.
def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "w") as f:
            json.dump([], f)
    with open(ARQUIVO_USUARIOS, "r") as f:
        return json.load(f)

# Salva a lista atual de usuários de volta no arquivo JSON.
def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w") as f:
        json.dump(usuarios, f, indent=4)

# ===================================================================
#CLASSE PRINCIPAL DA APLICAÇÃO (LÓGICA DE LOGIN E NAVEGAÇÃO)
# Gerencia todo o estado, lógica de negócios e construção de
# telas (Views) do aplicativo.
# ===================================================================

class AcademiaApp:
    # -----------------------------------------------------------
    # INICIALIZAÇÃO
    # -----------------------------------------------------------
    # Método construtor: configura a página e chama a construção dos componentes.
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Espaço Fitness Academia"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 20
        self.page.scroll = ft.ScrollMode.AUTO

        self.usuario_logado = False
        self.usuario_atual = None
        self.usuarios = carregar_usuarios()

        self._build_components()

    # -----------------------------------------------------------
    #MÉTODOS DE CONSTRUÇÃO DE UI (HELPERS)
    # -----------------------------------------------------------

    # Esta é uma função "helper" (auxiliar) reutilizável.
    # Ela constrói a ESTRUTURA base das telas de Login e Registro.
    # Recebe os controles específicos (campos e botões) e os
    # insere em um layout padrão com o logo e o título.
    def _build_auth_view(self, route: str, controls: list) -> ft.View:
        return ft.View(
            route=route,
            controls=[
                ft.Container(
                    content=ft.ListView(
                        [
                            ft.Column(
                                [
                                    ft.Image(src="assets/logfit.png", width=200, height=200),
                                    ft.Text("Espaço Fitness Academia", size=30, weight=ft.FontWeight.BOLD),
                                ] + controls + [],
                                spacing=10,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER
                            )
                        ],
                        expand=True,
                        auto_scroll=True
                    ),
                    alignment=ft.alignment.center,
                    expand=True
                )
            ]
        )

    # Esta é outra função "helper" (auxiliar) reutilizável.
    # Ela constrói a ESTRUTURA principal do app (pós-login),
    # que inclui o menu lateral (barra_navegacao) e o cabeçalho.
    # Ela recebe o 'conteúdo' específico da tela (Home ou Cronômetro)
    # e o insere no local correto.
    def _build_main_view(self, route: str, content: ft.Control) -> ft.View:
        return ft.View(
            route=route,
            controls=[
                ft.Row(
                    [
                        self.barra_navegacao,
                        ft.VerticalDivider(width=1),
                        ft.Container(
                            content=ft.ListView(
                                [self.cabecalho, content],
                                spacing=20,
                                padding=20,
                                expand=True,
                                auto_scroll=True
                            ),
                            expand=True,
                        )
                    ],
                    expand=True
                )
            ]
        )
        
    # -----------------------------------------------------------
    #CONSTRUTOR PRINCIPAL DE COMPONENTES
    # -----------------------------------------------------------

    # Cria e armazena todas as "peças" reutilizáveis da UI (campos, botões, etc).
    def _build_components(self):
        # --- Definição dos campos de autenticação ---
        self.email_campo = ft.TextField(label="Email", width=300)
        self.senha_campo = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
        self.campo_nome_reg = ft.TextField(label="Nome Completo", width=300)
        self.campo_email_reg = ft.TextField(label="Email", width=300)
        self.campo_senha_reg = ft.TextField(label="Senha", password=True, can_reveal_password=True, width=300)
        self.campo_confirmar_senha_reg = ft.TextField(label="Confirmar Senha", password=True, can_reveal_password=True, width=300)

        # --- Definição dos componentes principais (reutilizados) ---
        self.cabecalho = ft.Row(
            [
                ft.Text("Espaço Fitness Academia", size=24, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("Sair", on_click=self.logout, icon=ft.Icons.LOGOUT)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        self.barra_navegacao = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            destinations=[
                ft.NavigationRailDestination(icon=ft.Icons.HOME_OUTLINED, selected_icon=ft.Icons.HOME, label="Início"),
                ft.NavigationRailDestination(icon=ft.Icons.TIMER_OUTLINED, selected_icon=ft.Icons.TIMER, label="Cronômetro"),
            ],
            on_change=lambda e: self.navegar_para(["home", "cronome"][e.control.selected_index])
        )

        # --- Definição do CONTEÚDO da tela Home ---
        # (Os campos de texto são salvos em 'self' para serem atualizados no login)
        self.texto_usuario_home = ft.Text(f"Usuário: Convidado")
        self.conteudo_home = ft.Column(
            [
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Bem-vindo de volta!", size=20, weight=ft.FontWeight.BOLD),
                            self.texto_usuario_home,
                        ], spacing=10),
                        padding=20
                    )
                ),
                ft.Text("Não Perca Nada!!!", size=20, weight=ft.FontWeight.BOLD),
                
                ft.ResponsiveRow(
                    controls=[
                        # Coluna 1 (Wrapper para o Card 1)
                        ft.Column(
                            col={"sm": 12, "md": 6, "lg": 4},
                            controls=[
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Image(src="assets/turma_malhando.jpeg", width=300, height=200, border_radius=ft.border_radius.all(10)),
                                            ft.Text("Novas turmas abertas!", weight=ft.FontWeight.BOLD),
                                            ft.Text("Confira nossas novas aulas em grupo")
                                        ]),
                                        padding=10,
                                        width=320,
                                        on_click=self.abrir_whatsapp,
                                        ink=True
                                    )
                                )
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        
                        # Coluna 2 (Wrapper para o Card 2)
                        ft.Column(
                            col={"sm": 12, "md": 6, "lg": 4},
                            controls=[
                                ft.Card(
                                    content=ft.Container(
                                        content=ft.Column([
                                            ft.Image(src="assets/andreia.jpeg", width=300, height=200, border_radius=ft.border_radius.all(10)),
                                            ft.Text("Personal Trainer", weight=ft.FontWeight.BOLD),
                                            ft.Text("Agende sua avaliação gratuita")
                                        ]),
                                        padding=10,
                                        width=320,
                                        on_click=self.abrir_whatsapp,
                                        ink=True
                                    )
                                )
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    run_spacing=10
                )
            ], 
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        # -----------------------------------------------------------
        # INÍCIO DAS DEFINIÇÕES DE TELAS (VIEWS)
        # -----------------------------------------------------------

        # --- TELA 1: LOGIN ---
        self.visual_login = self._build_auth_view(
            route="/login",
            controls=[
                ft.Text("Entre na sua conta", size=16),
                self.email_campo,
                self.senha_campo,
                ft.ElevatedButton("Entrar", on_click=self.login, width=300),
                ft.TextButton("Criar uma conta", on_click=self.ir_para_registro),
            ]
        )
        
        # --- TELA 2: REGISTRO ---
        self.visual_registro = self._build_auth_view(
            route="/register",
            controls=[
                ft.Text("Crie sua conta", size=16),
                self.campo_nome_reg,
                self.campo_email_reg,
                self.campo_senha_reg,
                self.campo_confirmar_senha_reg,
                ft.ElevatedButton("Cadastrar", on_click=self.registrar, width=300),
                ft.TextButton("Já tem uma conta? Entre", on_click=self.ir_para_login),
            ]
        )

        # --- TELA 3: HOME ---
        self.visual_home = self._build_main_view("/home", self.conteudo_home)

    # -----------------------------------------------------------
    #MÉTODOS DE LÓGICA E CONTROLE (EVENT HANDLERS)
    # -----------------------------------------------------------

    # Ponto de entrada do app: exibe a tela de login inicial.
    def start(self):
        self.page.views.clear()
        self.page.views.append(self.visual_login)
        self.page.update()

    # Valida as credenciais e faz o login do usuário.
    def login(self, e):
        self.email_campo.error_text = None
        self.senha_campo.error_text = None
        self.page.update()
        email = self.email_campo.value.strip()
        senha = self.senha_campo.value.strip()
        if not email:
            self.email_campo.error_text = "O campo de email não pode estar vazio"
        if not senha:
            self.senha_campo.error_text = "O campo de senha não pode estar vazio"
        self.page.update()
        if self.email_campo.error_text or self.senha_campo.error_text:
            return
        
        usuario = next((u for u in self.usuarios if u["email"] == email and u["password"] == senha), None)
        
        if usuario:
            self.usuario_logado = True
            self.usuario_atual = usuario
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Bem-vindo, {usuario['nome']}!", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN_700)
            self.page.snack_bar.open = True
            self.atualizar_interface()
        else:
            self.email_campo.error_text = "Email ou senha incorretos."
            self.senha_campo.error_text = "Email ou senha incorretos."
            self.page.update()

    # Desconecta o usuário e o envia para a tela de login.
    def logout(self, e):
        self.usuario_logado = False
        self.usuario_atual = None
        self.page.snack_bar = ft.SnackBar(ft.Text("Logout realizado com sucesso!", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN_700)
        self.page.snack_bar.open = True
        self.atualizar_interface()

    # Valida os dados e cria um novo usuário.
    def registrar(self, e):
        self.campo_nome_reg.error_text = None
        self.campo_email_reg.error_text = None
        self.campo_senha_reg.error_text = None
        self.campo_confirmar_senha_reg.error_text = None
        self.page.update()

        nome = self.campo_nome_reg.value.strip()
        email = self.campo_email_reg.value.strip()
        senha = self.campo_senha_reg.value.strip()
        confirmar_senha = self.campo_confirmar_senha_reg.value.strip()
        erro = False

        if not nome:
            self.campo_nome_reg.error_text = "O campo de nome não pode estar vazio."
            erro = True
        if not email:
            self.campo_email_reg.error_text = "O campo de email não pode estar vazio."
            erro = True
        elif any(u["email"] == email for u in self.usuarios):
            self.campo_email_reg.error_text = "Email já cadastrado."
            erro = True
        if not senha:
            self.campo_senha_reg.error_text = "O campo de senha não pode estar vazio."
            erro = True
        if not confirmar_senha:
            self.campo_confirmar_senha_reg.error_text = "Confirme sua senha."
            erro = True
        elif senha != confirmar_senha:
            self.campo_confirmar_senha_reg.error_text = "As senhas não coincidem."
            erro = True
        
        self.page.update()
        if erro:
            return

        self.usuarios.append({"nome": nome, "email": email, "password": senha})
        salvar_usuarios(self.usuarios)
        self.page.snack_bar = ft.SnackBar(ft.Text("Cadastro realizado com sucesso! Faça login.", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN_700)
        self.page.snack_bar.open = True

        self.campo_nome_reg.value = ""
        self.campo_email_reg.value = ""
        self.campo_senha_reg.value = ""
        self.campo_confirmar_senha_reg.value = ""
        
        self.page.views.clear()
        self.page.views.append(self.visual_login)
        self.page.update()

    # Navega para a tela de Registro.
    def ir_para_registro(self, e):
        self.page.views.clear()
        self.page.views.append(self.visual_registro)
        self.page.update()

    # Navega para a tela de Login.
    def ir_para_login(self, e):
        self.page.views.clear()
        self.page.views.append(self.visual_login)
        self.page.update()

    # Abre o link do WhatsApp no navegador.
    def abrir_whatsapp(self, e: ft.ControlEvent):
        link = f"https://wa.me/{NUMERO_WHATSAPP}"
        self.page.launch_url(link)

    # Controla a navegação principal, exibindo a tela correta com base no destino.
    def navegar_para(self, destino: str):
        self.page.views.clear()
        if destino == "home":
            self.page.views.append(self.visual_home)
        
        elif destino == "cronome":
            cronometro_app = CronometroApp(self.page)
            conteudo_cronometro = ft.Column([
                ft.Text("Cronômetro", size=24, weight=ft.FontWeight.BOLD),
                cronometro_app.build()
            ], spacing=20)
            visual_cronometro = self._build_main_view("/cronometro", conteudo_cronometro)
            self.page.views.append(visual_cronometro)
            
        self.page.update()

    # Atualiza a UI inteira com base no estado de login (logado ou deslogado).
    def atualizar_interface(self):
        self.page.views.clear()
        if self.usuario_logado:
            self.texto_usuario_home.value = f"Usuário: {self.usuario_atual['nome']}"
            self.barra_navegacao.selected_index = 0
            self.page.views.append(self.visual_home)
        else:
            self.texto_usuario_home.value = "Usuário: Convidado"
            self.email_campo.value = ""
            self.senha_campo.value = ""
            self.page.views.append(self.visual_login)
        self.page.update()

# ===================================================================
# CLASSE DO COMPONENTE CRONÔMETRO 
# Gerencia a lógica e a interface de usuário (UI) do cronômetro
# e do contador de repetições.
# ===================================================================

class CronometroApp:
    def __init__(self, page):
        self.page = page
        self.tempo_inicial = None
        self.rodando = False
        self.repeticao_atual = 0

        self.texto_tempo = ft.Text("Tempo Decorrido: 00:00.00", size=18, weight=ft.FontWeight.BOLD)
        self.btn_iniciar = ft.ElevatedButton("Iniciar/Reiniciar", icon=ft.Icons.PLAY_ARROW, on_click=self.iniciar_cronometro)
        self.btn_parar = ft.ElevatedButton("Parar", icon=ft.Icons.STOP, on_click=self.parar_cronometro)
        self.texto_repeticao = ft.Text(f"Repetição: {self.repeticao_atual}", size=16)
        self.btn_adicionar = ft.ElevatedButton("+", on_click=self.adc_repeticao)
        self.btn_remover = ft.ElevatedButton("-", on_click=self.sub_repeticao)

    def build(self):
        conteudo = ft.Column(
            [
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Icon(ft.Icons.TIMER, size=60, color=ft.Colors.BLUE),
                                ft.Text("Treino em andamento", size=18, weight=ft.FontWeight.BOLD),
                                self.texto_tempo,
                                ft.Divider(),
                                ft.Text("Controles", size=16, weight=ft.FontWeight.BOLD),
                                ft.Row(
                                    [self.btn_iniciar, self.btn_parar],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=20
                                ),
                                ft.Divider(),
                                ft.Text("Gerenciar Repetições", size=16, weight=ft.FontWeight.BOLD),
                                self.texto_repeticao,
                                ft.Row(
                                    [self.btn_adicionar, self.btn_remover],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=20
                                ),
                            ],
                            spacing=15,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=20,
                        width=400,
                    ),
                ),
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        #Centraliza tudo no meio da tela
        return ft.Container(
            content=conteudo,
            expand=True,
            alignment=ft.alignment.center,
        )

    def iniciar_cronometro(self, e):
        if not self.rodando:
            self.tempo_inicial = time.time()
            self.rodando = True
            self.page.run_task(self.atualizar_loop)

    def parar_cronometro(self, e):
        if self.rodando:
            self.rodando = False
            self.adc_repeticao(None)

    async def atualizar_loop(self):
        while self.rodando:
            tempo_decorrido = time.time() - self.tempo_inicial
            minutos = int(tempo_decorrido // 60)
            segundos = tempo_decorrido % 60
            self.texto_tempo.value = f"Tempo Decorrido: {minutos:02d}:{segundos:05.2f}"
            self.page.update()
            await asyncio.sleep(0.01)

    def adc_repeticao(self, e):
        self.repeticao_atual += 1
        self.texto_repeticao.value = f"Repetição: {self.repeticao_atual}"
        self.page.update()

    def sub_repeticao(self, e):
        if self.repeticao_atual > 0:
            self.repeticao_atual -= 1
            self.texto_repeticao.value = f"Repetição: {self.repeticao_atual}"
            self.page.update()

# Função 'main' que o Flet usará como ponto de entrada.
def main(page: ft.Page):
    app = AcademiaApp(page)
    app.start()

# Inicia o aplicativo Flet.
ft.app(target=main)