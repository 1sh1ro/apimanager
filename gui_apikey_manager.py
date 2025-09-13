#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import json
import threading
from tkinter.scrolledtext import ScrolledText
from model_fetcher import model_fetcher

# 数据库文件
DB_FILE = "apikeys.db"

# 厂商和模型配置 - 自动更新于 2025-09-13
VENDOR_MODELS = {
    "OpenAI": ["gpt-4", "gpt-4-turbo", "gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "text-embedding-ada-002", "dall-e-3"],
    "Google": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro", "gemini-pro-vision", "palm-2", "text-bison", "chat-bison", "embedding-gecko"],
    "Anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-2.1", "claude-2.0", "claude-instant-1.2"],
    "Cohere": ["command", "command-r", "command-r-plus", "command-light", "embed-english", "embed-multilingual"],
    "Groq": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"],
    "DeepSeek": ["deepseek-chat", "deepseek-coder", "deepseek-math", "deepseek-v2", "deepseek-v2-chat"],
    "Moonshot": ["moonshot-v1-8k", "moonshot-v1-32k", "moonshot-v1-128k"],
    "智谱AI": ["glm-4", "glm-4v", "glm-3-turbo", "chatglm3-6b", "chatglm2-6b"],
    "百度文心": ["ernie-bot-4.0", "ernie-bot-turbo", "ernie-bot", "ernie-speed", "ernie-lite"],
    "阿里通义": ["qwen-turbo", "qwen-plus", "qwen-max", "qwen-max-longcontext", "qwen-vl-plus"],
    "字节豆包": ["doubao-lite-4k", "doubao-pro-4k", "doubao-pro-32k", "doubao-pro-128k"],
    "腾讯混元": ["hunyuan-lite", "hunyuan-standard", "hunyuan-pro"],
    "讯飞星火": ["spark-v3.5", "spark-v3.0", "spark-v2.0", "spark-lite"],
    "Microsoft Azure": ["gpt-4", "gpt-4-turbo", "gpt-35-turbo", "gpt-35-turbo-16k", "text-embedding-ada-002"],
    "Hugging Face": ["llama-2-7b", "llama-2-13b", "llama-2-70b", "mistral-7b", "codellama"],
    "Perplexity": ["llama-3-sonar-small-32k-chat", "llama-3-sonar-large-32k-chat", "mixtral-8x7b-instruct"],
    "Together AI": ["meta-llama/Llama-2-7b-chat-hf", "meta-llama/Llama-2-13b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
    "自定义": []
}

DEFAULT_API_URLS = {
    "OpenAI": "https://api.openai.com/v1",
    "Google": "https://generativelanguage.googleapis.com/v1beta",
    "Anthropic": "https://api.anthropic.com/v1",
    "Microsoft Azure": "https://your-resource.openai.azure.com",
    "Cohere": "https://api.cohere.ai/v1",
    "DeepSeek": "https://api.deepseek.com/v1",
    "Moonshot": "https://api.moonshot.cn/v1",
    "智谱AI": "https://open.bigmodel.cn/api/paas/v4",
    "百度文心": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1",
    "阿里通义": "https://dashscope.aliyuncs.com/api/v1",
    "字节豆包": "https://ark.cn-beijing.volces.com/api/v3",
    "腾讯混元": "https://hunyuan.tencentcloudapi.com",
    "讯飞星火": "https://spark-api.xf-yun.com/v1.1",
    "Hugging Face": "https://api-inference.huggingface.co/models",
    "Groq": "https://api.groq.com/openai/v1",
    "Perplexity": "https://api.perplexity.ai",
    "Together AI": "https://api.together.xyz/v1",
    "自定义": ""
}

class ClickableField(tk.Frame):
    """支持双击编辑的字段组件"""
    
    def __init__(self, parent, label_text, field_type="entry", options=None, is_password=False, change_callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.label_text = label_text
        self.field_type = field_type  # "entry", "combobox", "text"
        self.options = options or []
        self.is_password = is_password
        self.change_callback = change_callback
        self.value = ""
        self.is_editing = False
        
        # 配置样式
        self.configure(bg="#2d2d2d", relief="groove", bd=2, padx=5, pady=5)
        
        # 创建界面
        self.setup_ui()
        
        # 绑定事件
        if self.field_type == "combobox":
            self.bind("<Button-1>", self.on_single_click)
            self.display_label.bind("<Button-1>", self.on_single_click)
        else:
            self.bind("<Double-Button-1>", self.on_double_click)
            self.display_label.bind("<Double-Button-1>", self.on_double_click)
        
    def setup_ui(self):
        """创建用户界面"""
        # 创建主容器
        main_container = tk.Frame(self, bg="#2d2d2d")
        main_container.pack(fill="both", expand=True)
        
        # 标签和按钮容器
        header_frame = tk.Frame(main_container, bg="#2d2d2d")
        header_frame.pack(fill="x", pady=(0, 5))
        
        # 标签
        self.label = tk.Label(header_frame, text=self.label_text, 
                             bg="#2d2d2d", fg="#007acc", 
                             font=("Arial", 10, "bold"))
        self.label.pack(side="left")
        
        # 为文本类型字段添加复制按钮
        if self.field_type == "text":
            self.copy_btn_display = tk.Button(header_frame, text="📋", bg="#9b59b6", fg="white",
                                             relief="flat", padx=8, pady=2, font=("Arial", 8),
                                             command=self.copy_display_text)
            self.copy_btn_display.pack(side="right")
        
        # 显示区域（非编辑状态）
        self.display_var = tk.StringVar()
        self.display_label = tk.Label(main_container, textvariable=self.display_var,
                                     bg="#404040", fg="#e8e8e8",
                                     relief="flat", padx=5, pady=5,
                                     anchor="w", justify="left")
        self.display_label.pack(fill="both", expand=True)
        self.display_label.bind("<Double-Button-1>", self.on_double_click)
        
        # 设置初始显示
        self.update_display()
        
    def update_display(self):
        """更新显示内容"""
        if self.is_editing:
            return
            
        if self.value:
            if self.is_password:
                display_text = "••••••••"
            elif self.field_type == "text" and len(self.value) > 50:
                display_text = self.value[:50] + "..."
            else:
                display_text = self.value
        else:
            if self.field_type == "combobox":
                display_text = f"点击选择 {self.label_text}..."
            else:
                display_text = f"双击编辑 {self.label_text}..."
            
        self.display_var.set(display_text)
        
    def on_single_click(self, event=None):
        """单击进入编辑模式（用于combobox）"""
        if self.is_editing:
            return
        self.enter_edit_mode()
        
    def on_double_click(self, event=None):
        """双击进入编辑模式"""
        if self.is_editing:
            return
            
        self.enter_edit_mode()
        
    def enter_edit_mode(self):
        """进入编辑模式"""
        self.is_editing = True
        
        # 清除现有UI
        for widget in self.winfo_children():
            widget.destroy()
        
        # 创建标签
        self.label = tk.Label(self, text=self.label_text, 
                             bg="#2d2d2d", fg="#007acc", 
                             font=("Arial", 10, "bold"))
        self.label.pack(anchor="w", pady=(0, 5))
        
        # 创建编辑控件
        if self.field_type == "entry":
            self.edit_widget = tk.Entry(self, bg="#1a1a1a", fg="#e8e8e8",
                                       relief="flat", show="*" if self.is_password else "")
            self.edit_widget.insert(0, self.value)
            self.edit_widget.bind("<Return>", self.save_and_exit)
            self.edit_widget.bind("<Escape>", self.cancel_edit)
            
        elif self.field_type == "combobox":
            self.edit_widget = ttk.Combobox(self, values=self.options, state="readonly")
            if self.value and self.value in self.options:
                self.edit_widget.set(self.value)
            elif self.options:
                self.edit_widget.current(0)  # 默认选择第一个选项
            self.edit_widget.bind("<<ComboboxSelected>>", self.on_combobox_select)
            self.edit_widget.bind("<Escape>", self.cancel_edit)
            
        elif self.field_type == "text":
            self.edit_widget = ScrolledText(self, height=4, bg="#1a1a1a", fg="#e8e8e8",
                                          wrap=tk.WORD, relief="flat")
            self.edit_widget.insert("1.0", self.value)
            self.edit_widget.bind("<Control-Return>", self.save_and_exit)
            self.edit_widget.bind("<Escape>", self.cancel_edit)
            
        self.edit_widget.pack(fill="both", expand=True, pady=(0, 5))
        self.edit_widget.focus_set()
        
        # 添加保存/取消按钮
        button_frame = tk.Frame(self, bg="#2d2d2d")
        button_frame.pack(fill="x")
        
        save_btn = tk.Button(button_frame, text="✓", bg="#27ae60", fg="white",
                           relief="flat", padx=10, command=self.save_and_exit)
        save_btn.pack(side="left", padx=(0, 5))
        
        # 为文本字段添加复制按钮
        if self.field_type == "text":
            copy_btn = tk.Button(button_frame, text="📋 复制", bg="#9b59b6", fg="white",
                               relief="flat", padx=10, command=self.copy_text)
            copy_btn.pack(side="left", padx=(0, 5))
        
        cancel_btn = tk.Button(button_frame, text="✗", bg="#e74c3c", fg="white",
                             relief="flat", padx=10, command=self.cancel_edit)
        cancel_btn.pack(side="left")
        
    def on_combobox_select(self, event=None):
        """下拉框选择事件"""
        # 保存当前值
        self.value = self.edit_widget.get()
        
        # 触发父级的更新事件
        if hasattr(self, 'change_callback') and self.change_callback:
            self.change_callback(self.value)
        
        # 自动退出编辑模式
        self.exit_edit_mode()
            
    def save_and_exit(self, event=None):
        """保存并退出编辑模式"""
        if self.field_type == "text":
            self.value = self.edit_widget.get("1.0", "end-1c")
        else:
            self.value = self.edit_widget.get()
            
        self.exit_edit_mode()
        
    def cancel_edit(self, event=None):
        """取消编辑"""
        self.exit_edit_mode()
        
    def exit_edit_mode(self):
        """退出编辑模式"""
        self.is_editing = False
        
        # 清除所有子组件
        for widget in self.winfo_children():
            widget.destroy()
        
        # 重新创建UI
        self.setup_ui()
        
    def update_options(self, new_options):
        """更新下拉框选项"""
        self.options = new_options
        if self.is_editing and hasattr(self, 'edit_widget') and isinstance(self.edit_widget, ttk.Combobox):
            self.edit_widget['values'] = new_options
            
    def set_value(self, value):
        """设置字段值"""
        self.value = str(value) if value is not None else ""
        self.update_display()
        
    def get_value(self):
        """获取当前值"""
        if self.is_editing:
            if self.field_type == "text":
                return self.edit_widget.get("1.0", "end-1c")
            else:
                return self.edit_widget.get()
        return self.value
    
    def set_value(self, value):
        """设置值"""
        self.value = value
        self.update_display()
        
    def set_options(self, options):
        """设置下拉框选项"""
        self.options = options
        if self.is_editing and self.field_type == "combobox":
            self.edit_widget.configure(values=options)
    
    def update_options(self, new_options):
        """更新下拉框选项"""
        self.options = new_options or []
        # 如果当前正在编辑且是combobox，更新选项
        if self.is_editing and self.field_type == "combobox" and hasattr(self, 'edit_widget'):
            current_value = self.edit_widget.get()
            self.edit_widget['values'] = self.options
            # 如果当前值不在新选项中，保持当前值（允许自定义）
            self.edit_widget.set(current_value)

    def copy_display_text(self):
        """复制显示的文本到剪贴板"""
        if self.value:
            try:
                # 复制到剪贴板
                self.clipboard_clear()
                self.clipboard_append(self.value)
                self.update()  # 确保剪贴板更新
                
                # 显示提示
                messagebox.showinfo("成功", "示例代码已复制到剪贴板！")
            except Exception as e:
                messagebox.showerror("错误", f"复制失败: {str(e)}")
        else:
            messagebox.showwarning("警告", "没有内容可复制")
    
    def copy_text(self):
        """复制文本到剪贴板"""
        if self.field_type == "text" and hasattr(self, 'edit_widget'):
            try:
                # 获取文本内容
                text_content = self.edit_widget.get("1.0", "end-1c")
                
                # 复制到剪贴板
                self.clipboard_clear()
                self.clipboard_append(text_content)
                self.update()  # 确保剪贴板更新
                
                # 显示提示
                messagebox.showinfo("成功", "示例代码已复制到剪贴板！")
            except Exception as e:
                messagebox.showerror("错误", f"复制失败: {str(e)}")

class APIKeyManager:
    """API密钥管理器主窗口"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔑 API Key Manager - 现代化密钥管理工具")
        self.root.geometry("1200x700")
        self.root.configure(bg="#0f0f0f")
        self.root.minsize(800, 500)
        
        # 设置窗口图标（如果有的话）
        try:
            # 可以添加ico文件路径
            pass
        except:
            pass
        
        # 初始化数据库
        self.init_database()
        
        # 创建界面
        self.setup_ui()
        
        # 加载数据
        self.refresh_data()
    
    def darken_color(self, color):
        """让颜色变暗，用于悬停效果"""
        color_map = {
            "#00d4ff": "#0099cc",
            "#ff9500": "#cc7700", 
            "#ff3b30": "#cc2e25",
            "#af52de": "#8a42b8",
            "#34c759": "#2ba047"
        }
        return color_map.get(color, color)
    
    def init_database(self):
        """初始化数据库"""
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY,
                vendor TEXT NOT NULL,
                api_key TEXT NOT NULL,
                api_url TEXT,
                model TEXT,
                notes TEXT,
                example_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 添加示例数据
        cur.execute("SELECT COUNT(*) FROM api_keys")
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO api_keys (vendor, api_key, api_url, model, notes, example_code) VALUES (?, ?, ?, ?, ?, ?)",
                ("OpenAI", "sk-1234567890", "https://api.openai.com/v1", "gpt-4", "Personal Account",
                 "import openai\nclient = openai.OpenAI(api_key='YOUR_KEY')\nresponse = client.chat.completions.create(...)")
            )
            
        con.commit()
        con.close()
        
    def setup_ui(self):
        """创建用户界面"""
        # 创建主容器，带有渐变效果
        main_container = tk.Frame(self.root, bg="#0f0f0f")
        main_container.pack(fill="both", expand=True)
        
        # 顶部标题栏
        header_frame = tk.Frame(main_container, bg="#1a1a1a", height=80)
        header_frame.pack(fill="x", padx=2, pady=(2, 0))
        header_frame.pack_propagate(False)
        
        # 标题容器，居中显示
        title_container = tk.Frame(header_frame, bg="#1a1a1a")
        title_container.pack(expand=True, fill="both")
        
        # 主标题
        title_label = tk.Label(title_container, text="🔑 API Key Manager", 
                              bg="#1a1a1a", fg="#00d4ff", 
                              font=("Microsoft YaHei UI", 24, "bold"))
        title_label.pack(expand=True)
        
        # 副标题
        subtitle_label = tk.Label(title_container, text="现代化AI密钥管理工具", 
                                 bg="#1a1a1a", fg="#8a8a8a", 
                                 font=("Microsoft YaHei UI", 10))
        subtitle_label.pack()
        
        # 主内容区域
        content_frame = tk.Frame(main_container, bg="#0f0f0f")
        content_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # 工具栏区域（按钮）
        toolbar_frame = tk.Frame(content_frame, bg="#1e1e1e", height=60)
        toolbar_frame.pack(fill="x", pady=(0, 15))
        toolbar_frame.pack_propagate(False)
        
        # 按钮容器，居中显示
        button_container = tk.Frame(toolbar_frame, bg="#1e1e1e")
        button_container.pack(expand=True, fill="y", pady=10)
        
        # 现代化按钮样式
        button_style = {
            "font": ("Microsoft YaHei UI", 11, "bold"),
            "relief": "flat",
            "bd": 0,
            "padx": 25,
            "pady": 8,
            "cursor": "hand2"
        }
        
        # 按钮定义
        buttons = [
            ("➕ 添加", "#00d4ff", self.add_key),
            ("✏ 编辑", "#ff9500", self.edit_key),
            ("🗑 删除", "#ff3b30", self.delete_key),
            ("📋 复制", "#af52de", self.copy_api_key),
            ("🔄 刷新", "#34c759", self.refresh_data)
        ]
        
        # 创建按钮
        for text, color, command in buttons:
            btn = tk.Button(button_container, text=text, bg=color, fg="white",
                          command=command, **button_style)
            btn.pack(side="left", padx=8)
            
            # 添加悬停效果
            def on_enter(e, btn=btn, original_color=color):
                btn.configure(bg=self.darken_color(original_color))
            
            def on_leave(e, btn=btn, original_color=color):
                btn.configure(bg=original_color)
            
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # 表格框架，现代化设计
        table_frame = tk.Frame(content_frame, bg="#1e1e1e", relief="flat", bd=1)
        table_frame.pack(fill="both", expand=True)
        
        # 创建现代化表格样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置Treeview样式
        style.configure("Modern.Treeview",
                       background="#2a2a2a",
                       foreground="#e8e8e8",
                       rowheight=35,
                       fieldbackground="#2a2a2a",
                       bordercolor="#404040",
                       borderwidth=1)
        
        style.configure("Modern.Treeview.Heading",
                       background="#1a1a1a",
                       foreground="#00d4ff",
                       font=("Microsoft YaHei UI", 11, "bold"),
                       borderwidth=1)
        
        style.map("Modern.Treeview",
                 background=[('selected', '#00d4ff')],
                 foreground=[('selected', '#ffffff')])
        
        style.map("Modern.Treeview.Heading",
                 background=[('active', '#404040')])
        
        # 创建Treeview
        columns = ("ID", "厂商", "模型", "备注", "API URL", "示例代码")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", 
                               height=15, style="Modern.Treeview")
        
        # 配置列标题
        column_configs = {
            "ID": ("ID", 60),
            "厂商": ("🏢 厂商", 130),
            "模型": ("🤖 模型", 160),
            "备注": ("📝 备注", 200), 
            "API URL": ("🌐 API URL", 280),
            "示例代码": ("💻 代码", 120)
        }
        
        for col_id, (text, width) in column_configs.items():
            self.tree.heading(col_id, text=text)
            self.tree.column(col_id, width=width, minwidth=50)
        
        # 现代化滚动条
        scrollbar_frame = tk.Frame(table_frame, bg="#1e1e1e", width=15)
        scrollbar = ttk.Scrollbar(scrollbar_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局表格和滚动条
        self.tree.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=15)
        scrollbar_frame.pack(side="right", fill="y", pady=15)
        scrollbar.pack(fill="y", padx=(5, 10))
        
        # 添加表格交互效果
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-1>", self.on_item_click)
        
        # 底部状态栏
        status_frame = tk.Frame(main_container, bg="#1a1a1a", height=30)
        status_frame.pack(fill="x", padx=2, pady=(0, 2))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="准备就绪", 
                                   bg="#1a1a1a", fg="#8a8a8a",
                                   font=("Microsoft YaHei UI", 9))
        self.status_label.pack(side="left", padx=15, pady=5)
        
    def refresh_data(self):
        """刷新数据"""
        self.update_status("正在刷新数据...")
        
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # 从数据库加载数据
        try:
            con = sqlite3.connect(DB_FILE)
            cur = con.cursor()
            cur.execute("SELECT id, vendor, model, notes, api_url, example_code FROM api_keys ORDER BY id")
            
            row_count = 0
            for row in cur.fetchall():
                item_id, vendor, model, notes, api_url, example_code = row
                
                # 处理显示文本，防止None值
                notes = notes or ""
                api_url = api_url or ""
                example_code = example_code or ""
                
                notes_display = notes[:30] + "..." if notes and len(notes) > 30 else notes
                url_display = api_url[:40] + "..." if api_url and len(api_url) > 40 else api_url
                code_display = "✓ 有代码" if example_code.strip() else "○ 无代码"
                
                # 插入数据，交替行颜色
                tags = ('evenrow',) if row_count % 2 == 0 else ('oddrow',)
                self.tree.insert("", "end", values=(
                    item_id, vendor, model, notes_display, url_display, code_display
                ), tags=tags)
                row_count += 1
                
            con.close()
            
            # 配置行颜色
            self.tree.tag_configure('evenrow', background='#2a2a2a')
            self.tree.tag_configure('oddrow', background='#323232')
            
            self.update_status(f"共加载 {row_count} 条记录")
            
        except Exception as e:
            self.update_status(f"刷新失败: {str(e)}")
            messagebox.showerror("错误", f"刷新数据失败: {str(e)}")
    
    def on_item_click(self, event):
        """单击表格项时的处理"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item)["values"]
            if values:
                self.update_status(f"已选择: {values[1]} - {values[2]}")
        else:
            self.update_status("准备就绪")
    
    def update_status(self, message):
        """更新状态栏信息"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
    
    def add_key(self):
        """添加新密钥"""
        AddEditDialog(self.root, self, title="添加新的 API 密钥")
        
    def edit_key(self):
        """编辑选中的密钥"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要编辑的项目")
            return
            
        item = selection[0]
        key_id = self.tree.item(item)["values"][0]
        
        # 从数据库获取完整数据
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("SELECT * FROM api_keys WHERE id = ?", (key_id,))
        data = cur.fetchone()
        con.close()
        
        if data:
            AddEditDialog(self.root, self, title="编辑 API 密钥", edit_data=data)
            
    def delete_key(self):
        """删除选中的密钥"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的项目")
            return
            
        if messagebox.askyesno("确认删除", "确定要删除选中的API密钥吗？"):
            item = selection[0]
            key_id = self.tree.item(item)["values"][0]
            
            con = sqlite3.connect(DB_FILE)
            cur = con.cursor()
            cur.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
            con.commit()
            con.close()
            
            self.refresh_data()
            messagebox.showinfo("成功", "API密钥已删除")
            
    def copy_api_key(self):
        """复制选中密钥的API Key到剪贴板"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要复制API密钥的项目")
            return
            
        item = selection[0]
        key_id = self.tree.item(item)["values"][0]
        
        # 从数据库获取API密钥
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        cur.execute("SELECT api_key FROM api_keys WHERE id = ?", (key_id,))
        result = cur.fetchone()
        con.close()
        
        if result:
            api_key = result[0]
            # 复制到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(api_key)
            self.root.update()  # 确保剪贴板更新
            messagebox.showinfo("成功", f"API密钥已复制到剪贴板！\n\n前缀: {api_key[:10]}...")
        else:
            messagebox.showerror("错误", "无法获取API密钥")

    def on_item_double_click(self, event):
        """双击表格项"""
        self.edit_key()
        
    def run(self):
        """运行应用"""
        self.root.mainloop()

class AddEditDialog:
    """添加/编辑对话框"""
    
    def __init__(self, parent, main_app, title="添加 API 密钥", edit_data=None):
        self.main_app = main_app
        self.edit_data = edit_data
        
        # 创建现代化对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("650x750")
        self.dialog.configure(bg="#0f0f0f")
        self.dialog.resizable(False, False)
        
        # 模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建界面
        self.setup_ui()
        
        # 如果是编辑模式，填充数据
        if edit_data:
            self.load_edit_data()
            
        # 居中显示
        self.center_dialog()
    
    def setup_ui(self):
        """创建现代化用户界面"""
        # 主容器
        main_container = tk.Frame(self.dialog, bg="#0f0f0f")
        main_container.pack(fill="both", expand=True)
        
        # 顶部标题区域
        header_frame = tk.Frame(main_container, bg="#1a1a1a", height=70)
        header_frame.pack(fill="x", padx=2, pady=(2, 0))
        header_frame.pack_propagate(False)
        
        title_text = "✏ 编辑 API 密钥" if self.edit_data else "➕ 添加新的 API 密钥"
        title_label = tk.Label(header_frame, text=title_text,
                              bg="#1a1a1a", fg="#00d4ff",
                              font=("Microsoft YaHei UI", 16, "bold"))
        title_label.pack(expand=True)
        
        # 内容区域
        content_frame = tk.Frame(main_container, bg="#0f0f0f")
        content_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # 字段容器
        fields_frame = tk.Frame(content_frame, bg="#1e1e1e", relief="flat", bd=1)
        fields_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # 内部填充
        inner_frame = tk.Frame(fields_frame, bg="#1e1e1e")
        inner_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 创建现代化字段
        self.vendor_field = ClickableField(inner_frame, "🏢 厂商名称", 
                                          field_type="combobox", 
                                          options=list(VENDOR_MODELS.keys()),
                                          change_callback=self.on_vendor_change)
        self.vendor_field.pack(fill="x", pady=(0, 15))
        
        self.api_key_field = ClickableField(inner_frame, "🔐 API 密钥",
                                           field_type="entry", is_password=True)
        self.api_key_field.pack(fill="x", pady=(0, 15))
        
        self.api_url_field = ClickableField(inner_frame, "🌐 API URL", 
                                           field_type="entry")
        self.api_url_field.pack(fill="x", pady=(0, 15))
        
        self.model_field = ClickableField(inner_frame, "🤖 模型名称",
                                         field_type="combobox", options=[])
        self.model_field.pack(fill="x", pady=(0, 10))
        
        # 获取模型按钮区域
        model_button_frame = tk.Frame(inner_frame, bg="#1e1e1e")
        model_button_frame.pack(fill="x", pady=(0, 15))
        
        self.fetch_models_btn = tk.Button(model_button_frame, text="🔄 获取模型", 
                                         bg="#6c5ce7", fg="white",
                                         font=("Microsoft YaHei UI", 10, "bold"), 
                                         relief="flat", padx=20, pady=8,
                                         cursor="hand2",
                                         command=self.fetch_models)
        self.fetch_models_btn.pack(side="left")
        
        self.model_status_label = tk.Label(model_button_frame, text="", 
                                          bg="#1e1e1e", fg="#8a8a8a",
                                          font=("Microsoft YaHei UI", 9))
        self.model_status_label.pack(side="left", padx=(15, 0))
        
        self.notes_field = ClickableField(inner_frame, "📝 备注信息",
                                         field_type="entry")
        self.notes_field.pack(fill="x", pady=(0, 15))
        
        self.code_field = ClickableField(inner_frame, "💻 示例代码",
                                        field_type="text")
        self.code_field.pack(fill="both", expand=True, pady=(0, 20))
        
        # 底部按钮区域
        button_container = tk.Frame(content_frame, bg="#1a1a1a", height=60)
        button_container.pack(fill="x")
        button_container.pack_propagate(False)
        
        button_frame = tk.Frame(button_container, bg="#1a1a1a")
        button_frame.pack(expand=True, fill="both", pady=10)
        
        # 现代化按钮
        button_style = {
            "font": ("Microsoft YaHei UI", 11, "bold"),
            "relief": "flat",
            "bd": 0,
            "padx": 25,
            "pady": 8,
            "cursor": "hand2"
        }
        
        # 按钮定义
        buttons = [
            ("💾 保存", "#34c759", self.save),
            ("🔄 重置", "#ff9500", self.reset),
            ("❌ 取消", "#ff3b30", self.cancel)
        ]
        
        # 左侧按钮（保存、重置）
        for text, color, command in buttons[:2]:
            btn = tk.Button(button_frame, text=text, bg=color, fg="white",
                          command=command, **button_style)
            btn.pack(side="left", padx=8)
        
        # 右侧按钮（取消）
        cancel_btn = tk.Button(button_frame, text=buttons[2][0], bg=buttons[2][1], 
                              fg="white", command=buttons[2][2], **button_style)
        cancel_btn.pack(side="right", padx=8)
        
        # 居中显示对话框
        self.center_dialog()
    
    def fetch_models(self):
        """获取模型列表"""
        vendor = self.vendor_field.get_value().strip()
        api_key = self.api_key_field.get_value().strip()
        api_url = self.api_url_field.get_value().strip()
        
        if not vendor:
            messagebox.showwarning("警告", "请先选择厂商")
            return
        
        if not api_key and vendor not in ["智谱AI", "百度文心", "阿里通义", "字节豆包", "腾讯混元", "讯飞星火", "自定义"]:
            messagebox.showwarning("警告", "请先输入API密钥")
            return
        
        # 更新状态
        self.model_status_label.config(text="⟳ 正在获取模型列表...", fg="#f39c12")
        self.fetch_models_btn.config(state="disabled", text="⟳ 获取中...")
        self.dialog.update()
        
        # 在后台线程中获取模型
        def fetch_in_background():
            try:
                models = model_fetcher.get_models_for_vendor(vendor, api_key, api_url)
                
                # 在主线程中更新UI
                def update_ui():
                    if models and not any(model.startswith("错误:") for model in models):
                        self.model_field.update_options(models)
                        if models:
                            self.model_field.set_value(models[0])
                        self.model_status_label.config(text=f"✅ 获取到 {len(models)} 个模型", fg="#27ae60")
                    else:
                        error_msg = models[0] if models else "未知错误"
                        self.model_status_label.config(text=f"❌ {error_msg}", fg="#e74c3c")
                        
                        # 如果API Key错误，提供预设模型列表
                        if "无效" in error_msg or "错误" in error_msg:
                            if vendor in VENDOR_MODELS:
                                fallback_models = VENDOR_MODELS[vendor].copy()
                                if fallback_models:
                                    fallback_models.append("自定义模型")
                                    self.model_field.update_options(fallback_models)
                                    self.model_field.set_value(fallback_models[0])
                                    self.model_status_label.config(text="⚠ 使用预设模型列表", fg="#f39c12")
                    
                    self.fetch_models_btn.config(state="normal", text="⟳ 获取模型列表")
                
                self.dialog.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    self.model_status_label.config(text=f"❌ 获取失败: {str(e)}", fg="#e74c3c")
                    self.fetch_models_btn.config(state="normal", text="⟳ 获取模型列表")
                
                self.dialog.after(0, show_error)
        
        # 启动后台线程
        thread = threading.Thread(target=fetch_in_background, daemon=True)
        thread.start()
    
    def on_vendor_change(self, vendor):
        """厂商变化时更新API URL和模型选项"""
        if not vendor:
            return
        
        # 清空之前的状态信息
        self.model_status_label.config(text="", fg="#b3b3b3")
        
        # 自动填充API URL
        if vendor in DEFAULT_API_URLS:
            self.api_url_field.set_value(DEFAULT_API_URLS[vendor])
        
        # 提供预设模型选项（用户可以选择手动获取或使用预设）
        if vendor in VENDOR_MODELS:
            preset_models = VENDOR_MODELS[vendor].copy()
            if preset_models and vendor != "自定义":
                preset_models.append("🔄 点击上方按钮获取最新模型")
                self.model_field.update_options(preset_models)
                self.model_field.set_value(preset_models[0])
                self.model_status_label.config(text="💡 建议点击上方按钮获取最新模型", fg="#6c5ce7")
            else:
                self.model_field.update_options([])
                self.model_field.set_value("")
                if vendor == "自定义":
                    self.model_status_label.config(text="💡 请手动输入模型名称", fg="#6c5ce7")
                else:
                    self.model_status_label.config(text="💡 请点击上方按钮获取模型列表", fg="#6c5ce7")
                    
        # 生成示例代码
        self.update_example_code(vendor)
                
    def load_edit_data(self):
        """加载编辑数据"""
        if not self.edit_data:
            return
            
        data = self.edit_data
        vendor = data[1] or ""
        
        # 设置字段值
        self.vendor_field.set_value(vendor)
        self.api_key_field.set_value(data[2] or "")  # api_key
        self.api_url_field.set_value(data[3] or "")  # api_url
        self.model_field.set_value(data[4] or "")  # model
        self.notes_field.set_value(data[5] or "")  # notes
        self.code_field.set_value(data[6] or "")  # example_code
        
        # 触发厂商变化事件以更新模型选项
        if vendor:
            self.on_vendor_change(vendor)
            
    def save(self):
        """保存数据"""
        vendor = self.vendor_field.get_value().strip()
        api_key = self.api_key_field.get_value().strip()
        api_url = self.api_url_field.get_value().strip()
        model = self.model_field.get_value().strip()
        notes = self.notes_field.get_value().strip()
        example_code = self.code_field.get_value().strip()
        
        if not vendor or not api_key:
            messagebox.showerror("错误", "厂商名称和API密钥不能为空！")
            return
            
        con = sqlite3.connect(DB_FILE)
        cur = con.cursor()
        
        if self.edit_data:
            # 更新现有记录
            cur.execute("""
                UPDATE api_keys 
                SET vendor=?, api_key=?, api_url=?, model=?, notes=?, example_code=?
                WHERE id=?
            """, (vendor, api_key, api_url, model, notes, example_code, self.edit_data[0]))
            messagebox.showinfo("成功", "API密钥已更新！")
        else:
            # 插入新记录
            cur.execute("""
                INSERT INTO api_keys (vendor, api_key, api_url, model, notes, example_code)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (vendor, api_key, api_url, model, notes, example_code))
            messagebox.showinfo("成功", "API密钥已添加！")
            
        con.commit()
        con.close()
        
        self.main_app.refresh_data()
        self.dialog.destroy()
        
    def reset(self):
        """重置表单"""
        if messagebox.askyesno("确认", "确定要重置所有字段吗？"):
            self.vendor_field.set_value("")
            self.api_key_field.set_value("")
            self.api_url_field.set_value("")
            self.model_field.set_value("")
            self.notes_field.set_value("")
            self.code_field.set_value("")
            
    def cancel(self):
        """取消并关闭对话框"""
        self.dialog.destroy()
        
    def center_dialog(self):
        """居中显示对话框"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
    def update_example_code(self, vendor):
        """根据厂商更新示例代码"""
        # 如果已有自定义代码，不覆盖
        current_code = self.code_field.get_value().strip()
        if current_code and current_code != "":
            return
            
        code_templates = {
            "OpenAI": '''import openai

client = openai.OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.openai.com/v1"
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)''',

            "Google": '''import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-1.5-pro')

response = model.generate_content("Hello!")
print(response.text)''',

            "Anthropic": '''import anthropic

client = anthropic.Anthropic(
    api_key="YOUR_API_KEY"
)

message = client.messages.create(
    model="claude-3-sonnet",
    max_tokens=1000,
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(message.content[0].text)''',

            "智谱AI": '''from zhipuai import ZhipuAI

client = ZhipuAI(api_key="YOUR_API_KEY")

response = client.chat.completions.create(
    model="glm-4",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)''',

            "百度文心": '''import requests

def call_ernie_api(prompt):
    # 先获取access_token
    token_url = "https://aip.baidubce.com/oauth/2.0/token"
    token_params = {
        "grant_type": "client_credentials",
        "client_id": "YOUR_API_KEY",
        "client_secret": "YOUR_SECRET_KEY"
    }
    
    token_response = requests.post(token_url, params=token_params)
    access_token = token_response.json()["access_token"]
    
    # 调用API
    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"
    
    payload = {
        "messages": [{"role": "user", "content": prompt}]
    }
    
    response = requests.post(url, json=payload)
    return response.json()["result"]

print(call_ernie_api("Hello!"))''',

            "DeepSeek": '''import openai

client = openai.OpenAI(
    api_key="YOUR_API_KEY",
    base_url="https://api.deepseek.com/v1"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)

print(response.choices[0].message.content)'''
        }
        
        if vendor in code_templates:
            self.code_field.set_value(code_templates[vendor])
        elif vendor == "自定义":
            self.code_field.set_value("# 请在此处编写您的自定义API调用代码\n")
        else:
            # 通用OpenAI兼容格式
            template = f'''import openai

client = openai.OpenAI(
    api_key="YOUR_API_KEY",
    base_url="YOUR_API_URL"  # 请填入{vendor}的API地址
)

response = client.chat.completions.create(
    model="YOUR_MODEL",  # 请填入{vendor}的模型名称
    messages=[
        {{"role": "user", "content": "Hello!"}}
    ]
)

print(response.choices[0].message.content)'''
            self.code_field.set_value(template)


if __name__ == "__main__":
    app = APIKeyManager()
    app.run()
