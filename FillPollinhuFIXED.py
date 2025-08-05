#BY GABBLEZZ :P
import tkinter as tk
from tkinter import colorchooser, messagebox
from typing import List, Tuple, Dict, Optional

class Ponto:
    """representa um ponto 2D com coordenadas x e y"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def para_tupla(self) -> Tuple[float, float]:
        return (self.x, self.y)

class Poligono:
    """representa um polígono com vértices, cor e estado de preenchimento"""
    def __init__(self, vertices: List[Tuple[float, float]]):
        self._vertices = [Ponto(x, y) for x, y in vertices]
        self._cor_rgb = (255, 0, 0)  # vermelho como a cor padrão
        self._preenchimento_ativado = False
        self._esta_selecionado = False

    @property
    def vertices(self) -> List[Tuple[float, float]]:
        return [p.para_tupla() for p in self._vertices]

    @property
    def cor_rgb(self) -> Tuple[int, int, int]:
        return self._cor_rgb

    @cor_rgb.setter
    def cor_rgb(self, valor: Tuple[int, int, int]):
        self._cor_rgb = valor

    @property
    def preenchimento_ativado(self) -> bool:
        return self._preenchimento_ativado

    @preenchimento_ativado.setter
    def preenchimento_ativado(self, valor: bool):
        self._preenchimento_ativado = valor

    @property
    def esta_selecionado(self) -> bool:
        return self._esta_selecionado

    @esta_selecionado.setter
    def esta_selecionado(self, valor: bool):
        self._esta_selecionado = valor

    def contem_ponto(self, x: float, y: float, tolerancia: float = 2.0) -> bool:
        """implementação do algoritmo ray-casting com tratamento de arestas"""
        # verificação de proximidade com as arestas
        for i in range(len(self._vertices)):
            p1 = self._vertices[i]
            p2 = self._vertices[(i + 1) % len(self._vertices)]
            if self._calcular_distancia_ponto_segmento(x, y, p1, p2) < tolerancia:
                return True

        # algoritmo ray-casting
        dentro = False
        n = len(self._vertices)
        
        for i in range(n):
            p1 = self._vertices[i]
            p2 = self._vertices[(i + 1) % n]
            
            if ((p1.y > y) != (p2.y > y)):
                x_intersecao = (y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y) + p1.x
                if x <= x_intersecao:
                    dentro = not dentro
                    
        return dentro

    def _calcular_distancia_ponto_segmento(self, x: float, y: float, p1: Ponto, p2: Ponto) -> float:
        """calcula distância euclidiana entre ponto e segmento de reta"""
        if p1.x == p2.x and p1.y == p2.y:
            return ((x - p1.x)**2 + (y - p1.y)**2)**0.5
            
        l2 = (p1.x - p2.x)**2 + (p1.y - p2.y)**2
        t = max(0, min(1, ((x - p1.x) * (p2.x - p1.x) + (y - p1.y) * (p2.y - p1.y)) / l2))
        
        proj_x = p1.x + t * (p2.x - p1.x)
        proj_y = p1.y + t * (p2.y - p1.y)
        
        return ((x - proj_x)**2 + (y - proj_y)**2)**0.5

class GerenciadorPoligonos:
    """gerencia a coleção de polígonos na cena"""
    def __init__(self):
        self._poligonos: List[Poligono] = []
        self._poligono_selecionado: Optional[Poligono] = None

    @property
    def poligonos(self) -> List[Poligono]:
        return self._poligonos

    @property
    def poligono_selecionado(self) -> Optional[Poligono]:
        return self._poligono_selecionado

    def adicionar_poligono(self, vertices: List[Tuple[float, float]]) -> Poligono:
        """adiciona um novo polígono à cena"""
        novo_poligono = Poligono(vertices)
        self._poligonos.append(novo_poligono)
        return novo_poligono

    def selecionar_poligono_por_posicao(self, x: float, y: float) -> bool:
        """seleciona polígono contendo as coordenadas especificadas"""
        for poligono in reversed(self._poligonos):
            if poligono.contem_ponto(x, y):
                if self._poligono_selecionado:
                    self._poligono_selecionado.esta_selecionado = False
                self._poligono_selecionado = poligono
                poligono.esta_selecionado = True
                return True
        return False

    def remover_poligono_selecionado(self) -> bool:
        """remove o polígono atualmente selecionado"""
        if self._poligono_selecionado:
            self._poligonos.remove(self._poligono_selecionado)
            self._poligono_selecionado = None
            return True
        return False

class AplicacaoRenderizacao:
    """classe principal da aplicação gráfica"""
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("FillPoly - CG 2025")
        
        # Modelo
        self._gerenciador_poligonos = GerenciadorPoligonos()
        self._vertices_temporarios: List[Tuple[float, float]] = []
        self._cor_preenchimento_atual = (255, 0, 0)  # Vermelho
        self._mostrar_arestas = True
        self._modo_interacao = "desenho"  # ou "selecao"

        # View
        self._configurar_interface_grafica()
        self._configurar_eventos_mouse()
        self.renderizar_cena()

    def _configurar_interface_grafica(self):
        """configura os componentes visuais da aplicação"""
        # Toolbar
        self._frame_toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self._frame_toolbar.pack(side=tk.TOP, fill=tk.X)

        # Canvas
        self._canvas = tk.Canvas(self.root, width=800, height=600, bg="white")
        self._canvas.pack(expand=tk.YES, fill=tk.BOTH)

        # Controles
        self._criar_botoes_toolbar()
        self._criar_labels_status()

    def _criar_botoes_toolbar(self):
        """cria os botões da barra de ferramentas"""
        botoes = [
            ("Modo Desenho/Seleção", self._alternar_modo_interacao),
            ("Limpar Cena", self._limpar_cena),
            ("Remover Polígono", self._remover_poligono_selecionado),
            ("Definir Cor", self._exibir_dialogo_cor),
            ("Preencher Polígono", self._aplicar_preenchimento_poligono),
        ]
        
        for texto, comando in botoes:
            tk.Button(self._frame_toolbar, text=texto, command=comando).pack(side=tk.LEFT)

        # checkbutton para as arestas
        self._var_mostrar_arestas = tk.BooleanVar(value=True)
        tk.Checkbutton(
            self._frame_toolbar, 
            text="Exibir Arestas", 
            variable=self._var_mostrar_arestas,
            command=self.renderizar_cena
        ).pack(side=tk.LEFT)

    def _criar_labels_status(self):
        """cria os labels informativos"""
        self._label_status = tk.Label(self.root, text="Modo Desenho: Clique para adicionar vértices")
        self._label_status.pack()
        
        self._label_coordenadas = tk.Label(self.root, text="Coordenadas: (0, 0)")
        self._label_coordenadas.pack()

    def _configurar_eventos_mouse(self):
        """configura os handlers de eventos de mouse"""
        self._canvas.bind("<Button-1>", self._tratar_clique_esquerdo)
        self._canvas.bind("<Button-3>", self._tratar_clique_direito)
        self._canvas.bind("<Motion>", self._atualizar_coordenadas_ponteiro)

    def renderizar_cena(self):
        """renderiza todos os elementos gráficos na cena"""
        self._limpar_viewport()
        self._renderizar_poligonos()
        self._renderizar_poligono_em_construcao()

    def _limpar_viewport(self):
        """limpa o canvas de desenho"""
        self._canvas.delete("all")

    def _renderizar_poligonos(self):
        """renderiza todos os polígonos da cena"""
        for poligono in self._gerenciador_poligonos.poligonos:
            if poligono.preenchimento_ativado:
                self._aplicar_algoritmo_scanline(poligono)
            
            cor_aresta = "red" if poligono.esta_selecionado else "black"
            if self._var_mostrar_arestas.get():
                self._canvas.create_polygon(
                    poligono.vertices, 
                    outline=cor_aresta, 
                    fill="", 
                    width=2
                )

    def _renderizar_poligono_em_construcao(self):
        """renderiza o polígono que está sendo construído"""
        if len(self._vertices_temporarios) > 1:
            self._canvas.create_line(
                self._vertices_temporarios, 
                fill="blue", 
                width=1
            )
            # mostra os pontos temporários
            for x, y in self._vertices_temporarios:
                self._canvas.create_oval(x-3, y-3, x+3, y+3, fill="blue")

    def _aplicar_algoritmo_scanline(self, poligono: Poligono):
        """implementação otimizada do algoritmo scanline para preenchimento"""
        vertices = poligono.vertices
        if len(vertices) < 3:
            return

        # 1. encontra os limites verticais
        y_min = min(y for x, y in vertices)
        y_max = max(y for x, y in vertices)

        # 2. cria a Edge Table (ET)
        et = {}
        for i in range(len(vertices)):
            x1, y1 = vertices[i]
            x2, y2 = vertices[(i + 1) % len(vertices)]

            if y1 == y2:  # ignora as arestas horizontais
                continue
                
            if y1 > y2:  # Garantir y1 < y2
                x1, y1, x2, y2 = x2, y2, x1, y1

            m_inverso = (x2 - x1) / (y2 - y1) if (y2 - y1) != 0 else 0
            y_min_aresta = int(y1)
            
            if y_min_aresta not in et:
                et[y_min_aresta] = []
                
            et[y_min_aresta].append({
                'y_max': y2,
                'x_inicial': x1,
                'm_inverso': m_inverso
            })

        # 3. processamento por scanline
        aet = []
        for y in range(int(y_min), int(y_max) + 1):
            # adiciona as novas arestas
            if y in et:
                aet.extend(et[y])
            
            # remove as arestas concluídas
            aet = [edge for edge in aet if edge['y_max'] > y]
            
            # ordena por x_inicial
            aet.sort(key=lambda edge: edge['x_inicial'])
            
            # preenche entre pares de arestas
            for i in range(0, len(aet), 2):
                if i + 1 < len(aet):
                    x_inicio = int(aet[i]['x_inicial'])
                    x_fim = int(aet[i + 1]['x_inicial'])
                    # garante a ordem correta
                    if x_inicio > x_fim:
                        x_inicio, x_fim = x_fim, x_inicio
                    # desenha a linha horizontal de preenchimento
                    self._canvas.create_line(
                        x_inicio, y, x_fim, y,
                        fill="#%02x%02x%02x" % poligono.cor_rgb,
                        width=1
                    )
            
            # atualiza x_inicial para próxima linha
            for edge in aet:
                edge['x_inicial'] += edge['m_inverso']

    # métodos de interação
    def _tratar_clique_esquerdo(self, event):
        """handler para clique esquerdo do mouse"""
        if self._modo_interacao == "desenho":
            self._vertices_temporarios.append((event.x, event.y))
        else:
            self._gerenciador_poligonos.selecionar_poligono_por_posicao(event.x, event.y)
        self.renderizar_cena()

    def _tratar_clique_direito(self, event):
        """handler para clique direito do mouse"""
        if self._modo_interacao == "desenho" and len(self._vertices_temporarios) >= 3:
            novo_poligono = self._gerenciador_poligonos.adicionar_poligono(self._vertices_temporarios)
            novo_poligono.cor_rgb = self._cor_preenchimento_atual
            self._vertices_temporarios = []
            self.renderizar_cena()
        else:
            messagebox.showerror("Erro", "São necessários pelo menos 3 vértices para formar um polígono")

    def _atualizar_coordenadas_ponteiro(self, event):
        """atualiza a posição do cursor na interface"""
        self._label_coordenadas.config(text=f"Coordenadas: ({event.x}, {event.y})")

    # métodos de controle
    def _alternar_modo_interacao(self):
        """alterna entre os modos de desenho e seleção"""
        self._modo_interacao = "selecao" if self._modo_interacao == "desenho" else "desenho"
        status = "Modo Seleção: Clique para selecionar polígonos" if self._modo_interacao == "selecao" else "Modo Desenho: Clique para adicionar vértices"
        self._label_status.config(text=status)
        self._vertices_temporarios = []
        self.renderizar_cena()

    def _limpar_cena(self):
        """remove todos os polígonos da cena"""
        self._gerenciador_poligonos = GerenciadorPoligonos()
        self._vertices_temporarios = []
        self.renderizar_cena()

    def _exibir_dialogo_cor(self):
        """exibe o seletor de cores e aplica ao polígono selecionado"""
        cor = colorchooser.askcolor()[0]
        if cor and self._gerenciador_poligonos.poligono_selecionado:
            self._gerenciador_poligonos.poligono_selecionado.cor_rgb = tuple(int(c) for c in cor)
            self.renderizar_cena()

    def _aplicar_preenchimento_poligono(self):
        """ativa o preenchimento para o polígono selecionado"""
        if self._gerenciador_poligonos.poligono_selecionado:
            self._gerenciador_poligonos.poligono_selecionado.preenchimento_ativado = True
            self.renderizar_cena()

    def _remover_poligono_selecionado(self):
        """remove o polígono atualmente selecionado"""
        if self._gerenciador_poligonos.remover_poligono_selecionado():
            self.renderizar_cena()

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacaoRenderizacao(root)
    root.mainloop()