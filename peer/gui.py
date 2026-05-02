#!/usr/bin/env python3
"""
GUI - Interface Gráfica para o Peer P2P
Interface moderna com tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import queue
import time
from datetime import datetime
import os


class PeerGUI:
    def __init__(self, peer):
        self.peer = peer
        self.root = tk.Tk()
        self.root.title(f"Sistema P2P - {self.peer.peer_id}")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Fila para comunicação thread-safe com a GUI
        self.message_queue = queue.Queue()
        
        # Configurar estilo
        self.setup_style()
        
        # Criar interface
        self.create_widgets()
        
        # Configurar fechamento da janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Iniciar thread de atualização
        self.running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        # Processar mensagens da fila
        self.root.after(100, self.process_message_queue)
    
    def setup_style(self):
        """Configura o estilo da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores
        bg_color = '#2b2b2b'
        fg_color = '#ffffff'
        accent_color = '#0078d4'
        
        # Configurar cores
        self.root.configure(bg=bg_color)
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=accent_color, foreground=fg_color)
        style.configure('Header.TLabel', font=('Arial', 14, 'bold'), 
                       background=bg_color, foreground=accent_color)
        style.configure('Info.TLabel', font=('Arial', 10), 
                       background=bg_color, foreground='#a0a0a0')
    
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        self.create_header(main_frame)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Criar aba de logs primeiro (para que log_text exista)
        # mas adicionaremos ao notebook depois
        self.create_logs_tab()
        
        # Criar demais abas
        self.create_publish_tab()
        self.create_search_tab()
        self.create_local_files_tab()
        self.create_peers_tab()
        
        # Selecionar a primeira aba (Publicar) como padrão
        self.notebook.select(1)
        
        # Barra de status
        self.create_status_bar(main_frame)
        
        # Fazer refresh inicial das abas após tudo estar criado
        self.root.after(100, self.initial_refresh)
    
    def create_header(self, parent):
        """Cria o cabeçalho da aplicação"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, 
                               text="📁 Sistema P2P de Compartilhamento de Arquivos",
                               style='Header.TLabel')
        title_label.pack(side=tk.LEFT)
        
        info_frame = ttk.Frame(header_frame)
        info_frame.pack(side=tk.RIGHT)
        
        peer_info = f"Peer ID: {self.peer.peer_id}  |  {self.peer.peer_ip}:{self.peer.peer_port}"
        info_label = ttk.Label(info_frame, text=peer_info, style='Info.TLabel')
        info_label.pack()
    
    def create_publish_tab(self):
        """Cria a aba de publicar arquivos"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📤 Publicar Arquivo")
        
        # Frame central
        content_frame = ttk.Frame(tab, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instruções
        ttk.Label(content_frame, 
                 text="Selecione um arquivo para compartilhar na rede P2P",
                 font=('Arial', 11)).pack(pady=20)
        
        # Arquivo selecionado
        self.selected_file_var = tk.StringVar(value="Nenhum arquivo selecionado")
        file_label = ttk.Label(content_frame, textvariable=self.selected_file_var,
                              font=('Arial', 10), foreground='#a0a0a0')
        file_label.pack(pady=10)
        
        # Botões
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(pady=20)
        
        select_btn = tk.Button(button_frame, text="Selecionar Arquivo", 
                              command=self.select_file_to_publish,
                              bg='#0078d4', fg='white', font=('Arial', 10),
                              padx=20, pady=10, cursor='hand2')
        select_btn.pack(side=tk.LEFT, padx=5)
        
        publish_btn = tk.Button(button_frame, text="Publicar na Rede", 
                               command=self.publish_selected_file,
                               bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                               padx=20, pady=10, cursor='hand2')
        publish_btn.pack(side=tk.LEFT, padx=5)
    
    def create_search_tab(self):
        """Cria a aba de buscar/baixar arquivos"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🔍 Buscar Arquivos")
        
        # Frame de busca
        search_frame = ttk.Frame(tab, padding="10")
        search_frame.pack(fill=tk.X)
        
        ttk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=('Arial', 10), width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.search_entry.bind('<Return>', lambda e: self.search_files())
        
        search_btn = tk.Button(search_frame, text="Buscar", 
                              command=self.search_files,
                              bg='#0078d4', fg='white', font=('Arial', 10),
                              padx=15, pady=5, cursor='hand2')
        search_btn.pack(side=tk.LEFT, padx=5)
        
        list_all_btn = tk.Button(search_frame, text="Listar Todos", 
                                command=self.list_all_files,
                                bg='#6c757d', fg='white', font=('Arial', 10),
                                padx=15, pady=5, cursor='hand2')
        list_all_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame da tabela
        table_frame = ttk.Frame(tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Criar Treeview para resultados
        columns = ('filename', 'replicas', 'hash')
        self.search_tree = ttk.Treeview(table_frame, columns=columns, 
                                       show='tree headings', height=15)
        
        self.search_tree.heading('#0', text='#')
        self.search_tree.heading('filename', text='Nome do Arquivo')
        self.search_tree.heading('replicas', text='Réplicas')
        self.search_tree.heading('hash', text='Hash')
        
        self.search_tree.column('#0', width=50, anchor='center')
        self.search_tree.column('filename', width=300)
        self.search_tree.column('replicas', width=100, anchor='center')
        self.search_tree.column('hash', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, 
                                 command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)
        
        self.search_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botão de download
        download_frame = ttk.Frame(tab, padding="10")
        download_frame.pack(fill=tk.X)
        
        download_btn = tk.Button(download_frame, text="⬇ Baixar Arquivo Selecionado", 
                                command=self.download_selected_file,
                                bg='#28a745', fg='white', font=('Arial', 10, 'bold'),
                                padx=20, pady=8, cursor='hand2')
        download_btn.pack()
    
    def create_local_files_tab(self):
        """Cria a aba de arquivos locais"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💾 Arquivos Locais")
        
        # Botão de atualizar
        button_frame = ttk.Frame(tab, padding="10")
        button_frame.pack(fill=tk.X)
        
        refresh_btn = tk.Button(button_frame, text="🔄 Atualizar Lista", 
                               command=self.refresh_local_files,
                               bg='#0078d4', fg='white', font=('Arial', 10),
                               padx=15, pady=5, cursor='hand2')
        refresh_btn.pack(side=tk.LEFT)
        
        # Frame da tabela
        table_frame = ttk.Frame(tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Criar Treeview
        columns = ('filename', 'size', 'hash')
        self.local_tree = ttk.Treeview(table_frame, columns=columns, 
                                      show='tree headings', height=15)
        
        self.local_tree.heading('#0', text='#')
        self.local_tree.heading('filename', text='Nome do Arquivo')
        self.local_tree.heading('size', text='Tamanho')
        self.local_tree.heading('hash', text='Hash')
        
        self.local_tree.column('#0', width=50, anchor='center')
        self.local_tree.column('filename', width=300)
        self.local_tree.column('size', width=150, anchor='center')
        self.local_tree.column('hash', width=200)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, 
                                 command=self.local_tree.yview)
        self.local_tree.configure(yscrollcommand=scrollbar.set)
        
        self.local_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Não carregar arquivos aqui, será feito após inicialização completa
    
    def create_peers_tab(self):
        """Cria a aba de peers ativos"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🌐 Peers Ativos")
        
        # Botão de atualizar
        button_frame = ttk.Frame(tab, padding="10")
        button_frame.pack(fill=tk.X)
        
        refresh_btn = tk.Button(button_frame, text="🔄 Atualizar Lista", 
                               command=self.refresh_peers,
                               bg='#0078d4', fg='white', font=('Arial', 10),
                               padx=15, pady=5, cursor='hand2')
        refresh_btn.pack(side=tk.LEFT)
        
        # Frame da tabela
        table_frame = ttk.Frame(tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Criar Treeview
        columns = ('peer_id', 'ip', 'port', 'files')
        self.peers_tree = ttk.Treeview(table_frame, columns=columns, 
                                      show='tree headings', height=15)
        
        self.peers_tree.heading('#0', text='#')
        self.peers_tree.heading('peer_id', text='Peer ID')
        self.peers_tree.heading('ip', text='IP')
        self.peers_tree.heading('port', text='Porta')
        self.peers_tree.heading('files', text='Arquivos')
        
        self.peers_tree.column('#0', width=50, anchor='center')
        self.peers_tree.column('peer_id', width=250)
        self.peers_tree.column('ip', width=150)
        self.peers_tree.column('port', width=100, anchor='center')
        self.peers_tree.column('files', width=100, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, 
                                 command=self.peers_tree.yview)
        self.peers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.peers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Não carregar peers aqui, será feito após inicialização completa
    
    def create_logs_tab(self):
        """Cria a aba de logs"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 Logs")
        
        # Botões
        button_frame = ttk.Frame(tab, padding="10")
        button_frame.pack(fill=tk.X)
        
        clear_btn = tk.Button(button_frame, text="🗑 Limpar Logs", 
                             command=self.clear_logs,
                             bg='#dc3545', fg='white', font=('Arial', 10),
                             padx=15, pady=5, cursor='hand2')
        clear_btn.pack(side=tk.LEFT)
        
        # Área de texto para logs
        log_frame = ttk.Frame(tab)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                  font=('Consolas', 9),
                                                  bg='#1e1e1e', fg='#d4d4d4',
                                                  wrap=tk.WORD, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Adicionar log inicial
        self.add_log("Sistema iniciado")
        self.add_log(f"Peer ID: {self.peer.peer_id}")
        self.add_log(f"Endereço: {self.peer.peer_ip}:{self.peer.peer_port}")
    
    def create_status_bar(self, parent):
        """Cria a barra de status"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="✓ Conectado ao tracker")
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                style='Info.TLabel')
        status_label.pack(side=tk.LEFT)
        
        self.stats_var = tk.StringVar(value="Arquivos: 0 | Peers: 0")
        stats_label = ttk.Label(status_frame, textvariable=self.stats_var,
                               style='Info.TLabel')
        stats_label.pack(side=tk.RIGHT)
    
    def initial_refresh(self):
        """Faz o refresh inicial das abas após tudo estar criado"""
        self.refresh_local_files()
        self.refresh_peers()
    
    # Métodos de ação
    
    def select_file_to_publish(self):
        """Seleciona um arquivo para publicar"""
        filename = filedialog.askopenfilename(
            title="Selecione um arquivo para compartilhar",
            filetypes=[("Todos os arquivos", "*.*")]
        )
        if filename:
            self.selected_file_var.set(filename)
            self.add_log(f"Arquivo selecionado: {os.path.basename(filename)}")
    
    def publish_selected_file(self):
        """Publica o arquivo selecionado"""
        file_path = self.selected_file_var.get()
        
        if file_path == "Nenhum arquivo selecionado":
            messagebox.showwarning("Aviso", "Selecione um arquivo primeiro!")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("Erro", "Arquivo não encontrado!")
            return
        
        self.add_log(f"Publicando arquivo: {os.path.basename(file_path)}")
        
        # Executar em thread separada
        def publish_thread():
            success = self.peer.publish_file(file_path)
            if success:
                self.message_queue.put(('success', 'Arquivo publicado com sucesso!'))
                self.message_queue.put(('refresh_local', None))
            else:
                self.message_queue.put(('error', 'Erro ao publicar arquivo'))
        
        threading.Thread(target=publish_thread, daemon=True).start()
    
    def search_files(self):
        """Busca arquivos na rede"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            messagebox.showwarning("Aviso", "Digite um termo de busca!")
            return
        
        self.add_log(f"Buscando: {search_term}")
        
        def search_thread():
            results = self.peer.search_files(search_term)
            self.message_queue.put(('search_results', results))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def list_all_files(self):
        """Lista todos os arquivos da rede"""
        self.add_log("Listando todos os arquivos da rede")
        
        def list_thread():
            response = self.peer.network.list_files()
            if response.get('status') == 'success':
                files = response.get('files', [])
                self.message_queue.put(('search_results', files))
            else:
                self.message_queue.put(('error', 'Erro ao listar arquivos'))
        
        threading.Thread(target=list_thread, daemon=True).start()
    
    def download_selected_file(self):
        """Baixa o arquivo selecionado"""
        selection = self.search_tree.selection()
        
        if not selection:
            messagebox.showwarning("Aviso", "Selecione um arquivo para baixar!")
            return
        
        item = self.search_tree.item(selection[0])
        filename = item['values'][0]
        
        self.add_log(f"Iniciando download: {filename}")
        
        def download_thread():
            success = self.peer.download_file(filename)
            if success:
                self.message_queue.put(('success', f'Arquivo "{filename}" baixado com sucesso!'))
                self.message_queue.put(('refresh_local', None))
            else:
                self.message_queue.put(('error', f'Erro ao baixar "{filename}"'))
        
        threading.Thread(target=download_thread, daemon=True).start()
    
    def refresh_local_files(self):
        """Atualiza a lista de arquivos locais"""
        # Limpar tabela
        for item in self.local_tree.get_children():
            self.local_tree.delete(item)
        
        # Obter arquivos locais
        files = self.peer.file_manager.list_files()
        
        for idx, file_info in enumerate(files, 1):
            filename = file_info['filename']
            size = self.format_file_size(file_info['size'])
            file_hash = file_info['hash'][:16] + "..."
            
            self.local_tree.insert('', 'end', text=str(idx),
                                  values=(filename, size, file_hash))
        
        self.add_log(f"Arquivos locais atualizados: {len(files)} arquivo(s)")
    
    def refresh_peers(self):
        """Atualiza a lista de peers"""
        def refresh_thread():
            response = self.peer.network.list_peers()
            if response.get('status') == 'success':
                peers = response.get('peers', [])
                self.message_queue.put(('peers_list', peers))
            else:
                self.message_queue.put(('error', 'Erro ao listar peers'))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def update_search_results(self, results):
        """Atualiza os resultados de busca"""
        # Limpar tabela
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
        
        # Adicionar resultados
        for idx, file_info in enumerate(results, 1):
            filename = file_info.get('filename', 'N/A')
            replicas = file_info.get('peer_count', file_info.get('replicas', 0))
            file_hash = file_info.get('hash', 'N/A')[:16] + "..."
            
            self.search_tree.insert('', 'end', text=str(idx),
                                   values=(filename, replicas, file_hash))
        
        self.add_log(f"Busca concluída: {len(results)} resultado(s)")
    
    def update_peers_list(self, peers):
        """Atualiza a lista de peers"""
        # Limpar tabela
        for item in self.peers_tree.get_children():
            self.peers_tree.delete(item)
        
        # Adicionar peers
        for idx, peer_info in enumerate(peers, 1):
            peer_id = peer_info.get('peer_id', 'N/A')
            peer_ip = peer_info.get('ip', 'N/A')
            peer_port = peer_info.get('port', 'N/A')
            file_count = peer_info.get('file_count', 0)
            
            self.peers_tree.insert('', 'end', text=str(idx),
                                  values=(peer_id, peer_ip, peer_port, file_count))
        
        self.add_log(f"Peers ativos: {len(peers)}")
        self.stats_var.set(f"Arquivos: {len(self.peer.file_manager.list_files())} | Peers: {len(peers)}")
    
    def add_log(self, message):
        """Adiciona uma mensagem ao log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        # Verificar se log_text já foi criado
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
        else:
            # Se ainda não foi criado, apenas imprimir no console
            print(log_message.strip())
    
    def clear_logs(self):
        """Limpa os logs"""
        self.log_text.delete(1.0, tk.END)
        self.add_log("Logs limpos")
    
    def format_file_size(self, size_bytes):
        """Formata o tamanho do arquivo"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def process_message_queue(self):
        """Processa mensagens da fila"""
        try:
            while True:
                msg_type, data = self.message_queue.get_nowait()
                
                if msg_type == 'success':
                    messagebox.showinfo("Sucesso", data)
                    self.add_log(data)
                elif msg_type == 'error':
                    messagebox.showerror("Erro", data)
                    self.add_log(f"ERRO: {data}")
                elif msg_type == 'search_results':
                    self.update_search_results(data)
                elif msg_type == 'peers_list':
                    self.update_peers_list(data)
                elif msg_type == 'refresh_local':
                    self.refresh_local_files()
                elif msg_type == 'log':
                    self.add_log(data)
        except queue.Empty:
            pass
        
        # Agendar próxima verificação
        if self.running:
            self.root.after(100, self.process_message_queue)
    
    def update_loop(self):
        """Loop de atualização automática"""
        while self.running:
            time.sleep(10)  # Atualizar a cada 10 segundos
            if self.running:
                # Atualizar estatísticas
                self.message_queue.put(('log', 'Atualizando estatísticas...'))
    
    def on_closing(self):
        """Tratamento do fechamento da janela"""
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.running = False
            self.add_log("Encerrando aplicação...")
            self.root.destroy()
            self.peer.stop()
    
    def run(self):
        """Inicia a interface gráfica"""
        self.root.mainloop()
