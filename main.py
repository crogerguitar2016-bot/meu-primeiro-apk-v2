from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock

import os
import shutil
import subprocess
import urllib.parse


EXTENSOES = {
    ".pdf",
    ".doc",
    ".docx",
    ".htm",
    ".html",
    ".ppt",
    ".pptx",
    ".txt",
    ".epub",
}


def nome_legivel(nome):
    base, extensao = os.path.splitext(nome)

    base = base.replace("_", " ")
    base = base.replace("-", " - ")
    base = " ".join(base.split())

    return base


def abrir_documento(caminho):
    try:
        app = App.get_running_app()

        pasta_cache = os.path.join(
            app.user_data_dir,
            "documents"
        )

        os.makedirs(
            pasta_cache,
            exist_ok=True
        )

        destino = os.path.join(
            pasta_cache,
            os.path.basename(caminho)
        )

        shutil.copy2(
            caminho,
            destino
        )

        extensao = os.path.splitext(
            destino
        )[1].lower()

        tipos = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".ppt": "application/vnd.ms-powerpoint",
            ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            ".htm": "text/html",
            ".html": "text/html",
            ".txt": "text/plain",
            ".epub": "application/epub+zip",
        }

        mime = tipos.get(
            extensao,
            "*/*"
        )

        try:
            from jnius import autoclass

            PythonActivity = autoclass(
                "org.kivy.android.PythonActivity"
            )

            Intent = autoclass(
                "android.content.Intent"
            )

            File = autoclass(
                "java.io.File"
            )

            FileProvider = autoclass(
                "androidx.core.content.FileProvider"
            )

            activity = PythonActivity.mActivity

            arquivo_java = File(
                destino
            )

            uri = FileProvider.getUriForFile(
                activity,
                activity.getPackageName()
                + ".fileprovider",
                arquivo_java
            )

            intent = Intent(
                Intent.ACTION_VIEW
            )

            intent.setDataAndType(
                uri,
                mime
            )

            intent.addFlags(
                Intent.FLAG_GRANT_READ_URI_PERMISSION
            )

            intent.addFlags(
                Intent.FLAG_ACTIVITY_NEW_TASK
            )

            activity.startActivity(
                intent
            )

            return

        except Exception as erro_android:
            print(
                "Erro FileProvider:",
                erro_android
            )

            subprocess.Popen(
                [
                    "am",
                    "start",
                    "-a",
                    "android.intent.action.VIEW",
                    "-d",
                    "file://"
                    + urllib.parse.quote(
                        destino
                    ),
                ]
            )

    except Exception as erro:
        print(
            "Erro ao abrir documento:",
            erro
        )


class BibliotecaCasais(App):

    def build(self):

        self.title = (
            "Biblioteca de Casais"
        )

        self.documentos = []
        self.principais = []
        self.complementares = []

        raiz = BoxLayout(
            orientation="vertical",
            padding=dp(8),
            spacing=dp(6),
        )

        titulo = Label(
            text="BIBLIOTECA DE CASAIS",
            size_hint_y=None,
            height=dp(48),
            font_size="21sp",
            bold=True,
        )

        raiz.add_widget(
            titulo
        )

        self.status = Label(
            text="Localizando biblioteca interna...",
            size_hint_y=None,
            height=dp(32),
            font_size="14sp",
        )

        raiz.add_widget(
            self.status
        )

        self.pesquisar = TextInput(
            hint_text="Pesquisar pelo nome do livro...",
            multiline=False,
            size_hint_y=None,
            height=dp(44),
            font_size="16sp",
        )

        self.pesquisar.bind(
            text=self.filtrar
        )

        raiz.add_widget(
            self.pesquisar
        )

        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
        )

        self.lista = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(5),
            padding=(0, dp(4)),
        )

        self.lista.bind(
            minimum_height=
            self.lista.setter("height")
        )

        self.scroll.add_widget(
            self.lista
        )

        raiz.add_widget(
            self.scroll
        )

        Clock.schedule_once(
            self.carregar_biblioteca,
            0.2
        )

        return raiz

    def localizar_biblioteca(self):

        locais = []

        diretorio_codigo = os.path.dirname(
            os.path.abspath(__file__)
        )

        locais.append(
            os.path.join(
                diretorio_codigo,
                "biblioteca"
            )
        )

        locais.append(
            os.path.join(
                os.path.dirname(
                    diretorio_codigo
                ),
                "biblioteca"
            )
        )

        for local in locais:

            if os.path.isdir(local):
                return local

        return None

    def carregar_biblioteca(self, *args):

        self.documentos = []
        self.principais = []
        self.complementares = []

        base = self.localizar_biblioteca()

        if not base:

            self.status.text = (
                "ERRO: biblioteca interna "
                "não encontrada no APK."
            )

            self.mostrar_mensagem(
                "A pasta 'biblioteca' não foi "
                "encontrada dentro do aplicativo."
            )

            return

        for diretorio, pastas, arquivos in os.walk(
            base
        ):

            for arquivo in arquivos:

                extensao = os.path.splitext(
                    arquivo
                )[1].lower()

                if extensao not in EXTENSOES:
                    continue

                caminho = os.path.join(
                    diretorio,
                    arquivo
                )

                relativo = os.path.relpath(
                    caminho,
                    base
                )

                partes = relativo.split(
                    os.sep
                )

                if (
                    partes
                    and partes[0].lower()
                    == "principais"
                ):

                    categoria = "principal"

                    self.principais.append(
                        caminho
                    )

                elif (
                    partes
                    and partes[0].lower()
                    == "complementares"
                ):

                    categoria = "complementar"

                    self.complementares.append(
                        caminho
                    )

                else:

                    categoria = "outro"

                self.documentos.append(
                    {
                        "caminho": caminho,
                        "nome": nome_legivel(
                            arquivo
                        ),
                        "arquivo": arquivo,
                        "categoria": categoria,
                    }
                )

        self.principais.sort(
            key=lambda caminho:
            nome_legivel(
                os.path.basename(
                    caminho
                )
            ).lower()
        )

        self.complementares.sort(
            key=lambda caminho:
            nome_legivel(
                os.path.basename(
                    caminho
                )
            ).lower()
        )

        self.documentos.sort(
            key=lambda documento:
            documento["nome"].lower()
        )

        self.status.text = (
            "Biblioteca interna: "
            f"{len(self.documentos)} "
            "documento(s)"
        )

        self.mostrar_documentos(
            self.documentos,
            mostrar_categorias=True
        )

    def limpar_lista(self):

        self.lista.clear_widgets()

    def adicionar_titulo_secao(
        self,
        texto
    ):

        titulo = Label(
            text=texto,
            size_hint_y=None,
            height=dp(42),
            font_size="18sp",
            bold=True,
        )

        self.lista.add_widget(
            titulo
        )

    def adicionar_documento(
        self,
        documento
    ):

        botao = Button(
            text=documento["nome"],
            size_hint_y=None,
            height=dp(52),
            font_size="15sp",
            halign="left",
            valign="middle",
        )

        botao.bind(
            on_press=lambda btn,
            d=documento:
            abrir_documento(
                d["caminho"]
            )
        )

        self.lista.add_widget(
            botao
        )

    def mostrar_documentos(
        self,
        documentos,
        mostrar_categorias=False
    ):

        self.limpar_lista()

        if not documentos:

            self.lista.add_widget(
                Label(
                    text=(
                        "Nenhum documento "
                        "encontrado."
                    ),
                    size_hint_y=None,
                    height=dp(50),
                    font_size="16sp",
                )
            )

            return

        if mostrar_categorias:

            if self.principais:

                self.adicionar_titulo_secao(
                    "BIBLIOTECA PRINCIPAL "
                    f"({len(self.principais)})"
                )

                documentos_principais = [
                    documento
                    for documento in self.documentos
                    if documento["categoria"]
                    == "principal"
                ]

                for documento in (
                    documentos_principais
                ):

                    self.adicionar_documento(
                        documento
                    )

            if self.complementares:

                self.adicionar_titulo_secao(
                    "MATERIAIS COMPLEMENTARES "
                    f"({len(self.complementares)})"
                )

                documentos_complementares = [
                    documento
                    for documento in self.documentos
                    if documento["categoria"]
                    == "complementares"
                ]

                for documento in (
                    documentos_complementares
                ):

                    self.adicionar_documento(
                        documento
                    )

        else:

            for documento in documentos:

                self.adicionar_documento(
                    documento
                )

    def filtrar(
        self,
        instance,
        texto
    ):

        termo = texto.strip().lower()

        if not termo:

            self.status.text = (
                "Biblioteca interna: "
                f"{len(self.documentos)} "
                "documento(s)"
            )

            self.mostrar_documentos(
                self.documentos,
                mostrar_categorias=True
            )

            return

        encontrados = [
            documento
            for documento
            in self.documentos
            if (
                termo
                in documento["nome"].lower()
                or termo
                in documento["arquivo"].lower()
            )
        ]

        self.status.text = (
            f"{len(encontrados)} "
            "documento(s) encontrado(s)"
        )

        self.mostrar_documentos(
            encontrados,
            mostrar_categorias=False
        )

    def mostrar_mensagem(
        self,
        mensagem
    ):

        self.lista.clear_widgets()

        self.lista.add_widget(
            Label(
                text=mensagem,
                size_hint_y=None,
                height=dp(80),
                font_size="16sp",
            )
        )


if __name__ == "__main__":

    BibliotecaCasais().run()
