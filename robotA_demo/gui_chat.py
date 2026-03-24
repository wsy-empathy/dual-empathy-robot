"""
微信风格的双共情机器人对话界面
WeChat-style GUI for Dual Empathy Robot System
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
import threading
from datetime import datetime
from typing import Optional

from core.session_manager import SessionManager
from core.agents.aer_agent import AERAgent
from core.agents.cer_agent import CERAgent
from core.llm_gemini import GeminiLLM
from core.emo_wrime_luke_onnx import get_onnx_wrime_luke_recognizer
from core.rag_v2_retriever import RAGV2Retriever
from core.topics import get_topic_list, get_subtopic_list, get_topic_name, get_subtopic_name
from core.i18n import get_message


class WeChatStyleGUI:
    """微信风格的对话界面"""
    
    # 微信配色方案 + AER/CER区分色
    COLORS = {
        'bg': '#EDEDED',              # 背景灰色
        'top_bar': '#393A3F',         # 顶部栏深灰
        'user_bubble': '#95EC69',     # 用户气泡（微信绿）
        'aer_bubble': '#FFD4E5',      # AER气泡（粉色 - 情感共情）
        'cer_bubble': '#D4E5FF',      # CER气泡（蓝色 - 认知共情）
        'system_bubble': '#FFFFFF',   # 系统气泡（白色）
        'text': '#000000',            # 文本黑色
        'timestamp': '#999999',       # 时间戳灰色
        'send_btn': '#07C160',        # 发送按钮（微信绿）
        'input_bg': '#F7F7F7',        # 输入框背景
        'emotion_tag': '#FF6B6B'      # 情绪标签红色
    }
    
    # 机器人头像
    AVATARS = {
        'AER': '💖',  # 心形 - 情感共情
        'CER': '🧠',  # 脑形 - 认知共情
        'system': '🤖',  # 机器人 - 系统
        'user': '👤'  # 用户
    }
    
    def __init__(self, root, language='ja'):
        """初始化GUI"""
        self.root = root
        self.language = language
        self.session_id = None
        self.session = None
        
        # 初始化后端组件
        self.init_backend()
        
        # 设置窗口
        self.setup_window()
        
        # 创建UI组件
        self.create_widgets()
        
        # 显示欢迎消息
        self.show_welcome()
    
    def init_backend(self):
        """初始化后端组件"""
        print("[GUI] 初始化后端组件...")
        self.session_manager = SessionManager()
        self.aer_agent = AERAgent()
        self.cer_agent = CERAgent()
        self.llm = GeminiLLM()
        
        try:
            self.emotion_recognizer = get_onnx_wrime_luke_recognizer()
        except Exception as e:
            print(f"[GUI] 情绪识别器初始化失败: {e}")
            self.emotion_recognizer = None
        
        self.rag_retriever = RAGV2Retriever()
        print("[GUI] 后端组件初始化完成")
    
    def setup_window(self):
        """设置窗口样式"""
        self.root.title("双共情机器人 | Dual Empathy Robot")
        
        # 设置窗口尺寸（增大到更容易查看）
        window_width = 900
        window_height = 1000
        
        # 获取屏幕尺寸并居中显示
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg=self.COLORS['bg'])
        
        # 设置最小尺寸
        self.root.minsize(700, 800)
        
        # 确保窗口显示在最前面
        self.root.lift()
        self.root.focus_force()
        
        print(f"[GUI] 窗口初始化: {window_width}x{window_height} 位置: ({x}, {y})")
    
    def create_widgets(self):
        """创建所有UI组件"""
        # 顶部栏
        self.create_top_bar()
        
        # 主聊天区域
        self.create_chat_area()
        
        # 底部输入区
        self.create_input_area()
        
        # 侧边栏（话题选择）
        self.create_sidebar()
    
    def create_top_bar(self):
        """创建顶部栏"""
        top_frame = tk.Frame(self.root, bg=self.COLORS['top_bar'], height=60)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        top_frame.pack_propagate(False)
        
        # 标题
        title_text = "AER & CER 共情对话" if self.language == 'zh' else "AER & CER 共感対話"
        title_label = tk.Label(
            top_frame,
            text=title_text,
            bg=self.COLORS['top_bar'],
            fg='white',
            font=('Microsoft YaHei UI', 16, 'bold')
        )
        title_label.pack(pady=15)
        
        # 状态指示器
        self.status_label = tk.Label(
            top_frame,
            text="● 等待开始" if self.language == 'zh' else "● 開始を待っています",
            bg=self.COLORS['top_bar'],
            fg='#00D976',
            font=('Microsoft YaHei UI', 10)
        )
        self.status_label.place(relx=0.02, rely=0.3)
    
    def create_chat_area(self):
        """创建聊天区域"""
        # 聊天容器
        chat_container = tk.Frame(self.root, bg=self.COLORS['bg'])
        chat_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 使用Canvas和Scrollbar实现滚动
        self.canvas = tk.Canvas(chat_container, bg=self.COLORS['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.canvas.yview)
        
        self.chat_frame = tk.Frame(self.canvas, bg=self.COLORS['bg'])
        self.chat_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw", width=860)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定鼠标滚轮
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        print("[GUI] 聊天区域创建完成")
    
    def create_input_area(self):
        """创建输入区域"""
        input_container = tk.Frame(self.root, bg=self.COLORS['input_bg'], height=100)
        input_container.pack(fill=tk.X, side=tk.BOTTOM)
        input_container.pack_propagate(False)
        
        # 输入框
        input_frame = tk.Frame(input_container, bg=self.COLORS['input_bg'])
        input_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        self.input_text = tk.Text(
            input_frame,
            height=3,
            font=('Microsoft YaHei UI', 11),
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg='white',
            fg=self.COLORS['text']
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 发送按钮
        send_text = "发送" if self.language == 'zh' else "送信"
        self.send_button = tk.Button(
            input_frame,
            text=send_text,
            command=self.send_message,
            bg=self.COLORS['send_btn'],
            fg='white',
            font=('Microsoft YaHei UI', 12, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            width=8,
            height=2
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # 绑定Enter键
        self.input_text.bind('<Return>', lambda e: self.send_message() if not e.state & 0x1 else None)
        self.input_text.bind('<Shift-Return>', lambda e: self.input_text.insert(tk.INSERT, '\n'))
    
    def create_sidebar(self):
        """创建侧边栏（话题选择）"""
        self.sidebar = tk.Toplevel(self.root)
        self.sidebar.title("选择话题" if self.language == 'zh' else "トピックを選択")
        self.sidebar.geometry("350x500")
        self.sidebar.configure(bg='white')
        self.sidebar.withdraw()  # 初始隐藏
    
    def add_message(self, sender, text, emotion=None, timestamp=None):
        """添加消息气泡"""
        if timestamp is None:
            timestamp = datetime.now().strftime('%H:%M')
        
        # 创建消息容器
        msg_container = tk.Frame(self.chat_frame, bg=self.COLORS['bg'])
        msg_container.pack(fill=tk.X, pady=8, padx=10)
        
        if sender == 'user':
            # 用户消息（右对齐，绿色气泡）
            self._create_user_bubble(msg_container, text, timestamp)
        else:
            # 机器人消息（左对齐，白色气泡）
            self._create_bot_bubble(msg_container, sender, text, emotion, timestamp)
        
        # 滚动到底部
        self.root.after(100, self._scroll_to_bottom)
    
    def _create_user_bubble(self, container, text, timestamp):
        """创建用户气泡"""
        # 右侧布局
        right_frame = tk.Frame(container, bg=self.COLORS['bg'])
        right_frame.pack(side=tk.RIGHT, anchor='n')
        
        # 头像和气泡行
        content_frame = tk.Frame(right_frame, bg=self.COLORS['bg'])
        content_frame.pack(anchor='e')
        
        # 气泡
        bubble = tk.Label(
            content_frame,
            text=text,
            bg=self.COLORS['user_bubble'],
            fg=self.COLORS['text'],
            font=('Microsoft YaHei UI', 11),
            wraplength=400,
            justify=tk.LEFT,
            padx=15,
            pady=10,
            relief=tk.FLAT,
            cursor='hand2'
        )
        bubble.pack(side=tk.LEFT, padx=(0, 8))
        
        # 绑定右键菜单
        bubble.bind('<Button-3>', lambda e: self._show_copy_menu(e, text))
        
        # 用户头像
        avatar_label = tk.Label(
            content_frame,
            text=self.AVATARS['user'],
            bg=self.COLORS['bg'],
            font=('Segoe UI Emoji', 20)
        )
        avatar_label.pack(side=tk.LEFT)
        
        # 时间戳
        time_label = tk.Label(
            right_frame,
            text=timestamp,
            fg=self.COLORS['timestamp'],
            bg=self.COLORS['bg'],
            font=('Microsoft YaHei UI', 9)
        )
        time_label.pack(anchor='e', pady=(2, 0), padx=(0, 28))
    
    def _create_bot_bubble(self, container, sender, text, emotion, timestamp):
        """创建机器人气泡"""
        # 左侧布局
        left_frame = tk.Frame(container, bg=self.COLORS['bg'])
        left_frame.pack(side=tk.LEFT, anchor='n')
        
        # 确定气泡颜色
        if sender == 'AER':
            bubble_color = self.COLORS['aer_bubble']
            avatar = self.AVATARS['AER']
            name_display = 'AER - 情感共情' if self.language == 'zh' else 'AER - 感情的共感'
        elif sender == 'CER':
            bubble_color = self.COLORS['cer_bubble']
            avatar = self.AVATARS['CER']
            name_display = 'CER - 认知共情' if self.language == 'zh' else 'CER - 認知的共感'
        else:
            bubble_color = self.COLORS['system_bubble']
            avatar = self.AVATARS['system']
            name_display = '系统' if self.language == 'zh' else 'システム'
        
        # 头像和名称行
        header_frame = tk.Frame(left_frame, bg=self.COLORS['bg'])
        header_frame.pack(anchor='w', pady=(0, 5))
        
        # 头像
        avatar_label = tk.Label(
            header_frame,
            text=avatar,
            bg=self.COLORS['bg'],
            font=('Segoe UI Emoji', 20)
        )
        avatar_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # 名称
        name_label = tk.Label(
            header_frame,
            text=name_display,
            fg=self.COLORS['text'],
            bg=self.COLORS['bg'],
            font=('Microsoft YaHei UI', 10, 'bold')
        )
        name_label.pack(side=tk.LEFT, anchor='center')
        
        # 气泡容器
        bubble_container = tk.Frame(left_frame, bg=self.COLORS['bg'])
        bubble_container.pack(anchor='w', padx=(28, 0))  # 对齐到头像右侧
        
        # 气泡
        bubble = tk.Label(
            bubble_container,
            text=text,
            bg=bubble_color,
            fg=self.COLORS['text'],
            font=('Microsoft YaHei UI', 11),
            wraplength=400,
            justify=tk.LEFT,
            padx=15,
            pady=10,
            relief=tk.FLAT,
            borderwidth=1,
            cursor='hand2'
        )
        bubble.pack()
        
        # 绑定右键菜单
        bubble.bind('<Button-3>', lambda e: self._show_copy_menu(e, text))
        
        # 情绪标签（如果有）
        if emotion and sender == 'AER':  # 只有AER显示情绪标签
            emotion_label = tk.Label(
                bubble_container,
                text=f"😊 {emotion}",
                bg=self.COLORS['emotion_tag'],
                fg='white',
                font=('Microsoft YaHei UI', 9),
                padx=8,
                pady=2
            )
            emotion_label.pack(anchor='w', pady=(5, 0))
        
        # 时间戳
        time_label = tk.Label(
            left_frame,
            text=timestamp,
            fg=self.COLORS['timestamp'],
            bg=self.COLORS['bg'],
            font=('Microsoft YaHei UI', 9)
        )
        time_label.pack(anchor='w', padx=(28, 0), pady=(2, 0))
    
    def show_welcome(self):
        """显示欢迎消息"""
        welcome_msg = get_message(self.language, 'session_start')
        self.add_message('system', welcome_msg)
        
        # 显示话题选择
        self.show_topic_selection()
        
        # 强制刷新显示
        self.root.update_idletasks()
        self.root.update()
        print("[GUI] 欢迎消息显示完成")
    
    def show_topic_selection(self):
        """显示话题选择界面"""
        topics = get_topic_list()
        
        selection_text = "请选择一个话题：\n\n" if self.language == 'zh' else "トピックを選択してください：\n\n"
        
        for idx, (key, ja, zh) in enumerate(topics, 1):
            topic_name = zh if self.language == 'zh' else ja
            selection_text += f"{idx}. {topic_name}\n"
        
        self.add_message('system', selection_text)
        self.awaiting_topic = True
        self.topics_list = topics
    
    def send_message(self):
        """发送消息"""
        user_input = self.input_text.get("1.0", tk.END).strip()
        
        if not user_input:
            return
        
        # 清空输入框
        self.input_text.delete("1.0", tk.END)
        
        # 显示用户消息
        self.add_message('user', user_input)
        
        # 禁用输入
        self.send_button.config(state=tk.DISABLED)
        self.input_text.config(state=tk.DISABLED)
        
        # 在新线程中处理
        threading.Thread(target=self.process_message, args=(user_input,), daemon=True).start()
    
    def process_message(self, user_input):
        """处理用户消息（后台线程）"""
        try:
            if hasattr(self, 'awaiting_topic') and self.awaiting_topic:
                self.handle_topic_selection(user_input)
            elif hasattr(self, 'awaiting_subtopic') and self.awaiting_subtopic:
                self.handle_subtopic_selection(user_input)
            else:
                self.handle_dialogue(user_input)
        except Exception as e:
            error_msg = f"错误: {str(e)}" if self.language == 'zh' else f"エラー: {str(e)}"
            self.root.after(0, lambda: self.add_message('system', error_msg))
        finally:
            # 重新启用输入
            self.root.after(0, lambda: self.send_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.input_text.config(state=tk.NORMAL))
    
    def handle_topic_selection(self, user_input):
        """处理话题选择"""
        try:
            idx = int(user_input) - 1
            if 0 <= idx < len(self.topics_list):
                topic_key, ja, zh = self.topics_list[idx]
                topic_name = zh if self.language == 'zh' else ja
                
                # 创建会话
                if not self.session:
                    self.session_id = f"gui_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    self.session = self.session_manager.create_session(self.session_id, self.language)
                
                self.session.set_topic(topic_key, topic_name)
                
                # 显示子话题
                subtopics = get_subtopic_list(topic_key)
                self.show_subtopic_selection(topic_name, subtopics)
                
                self.awaiting_topic = False
                self.awaiting_subtopic = True
                self.subtopics_list = subtopics
                self.current_topic_key = topic_key
            else:
                raise ValueError("无效的选择")
        except:
            hint = "请输入数字编号" if self.language == 'zh' else "数字を入力してください"
            self.root.after(0, lambda: self.add_message('system', hint))
    
    def show_subtopic_selection(self, topic_name, subtopics):
        """显示子话题选择"""
        msg = get_message(self.language, 'topic_selected', topic=topic_name) + "\n\n"
        
        for idx, (key, ja, zh) in enumerate(subtopics, 1):
            subtopic_name = zh if self.language == 'zh' else ja
            msg += f"{idx}. {subtopic_name}\n"
        
        self.root.after(0, lambda: self.add_message('system', msg))
    
    def handle_subtopic_selection(self, user_input):
        """处理子话题选择"""
        try:
            idx = int(user_input) - 1
            if 0 <= idx < len(self.subtopics_list):
                subtopic_key, ja, zh = self.subtopics_list[idx]
                subtopic_name = zh if self.language == 'zh' else ja
                
                self.session.set_subtopic(subtopic_key, subtopic_name)
                self.session.advance_stage()  # 进入aer_1
                
                # 显示开始消息
                start_msg = get_message(
                    self.language,
                    'subtopic_selected',
                    topic=self.session.topic_name,
                    subtopic=subtopic_name
                )
                self.root.after(0, lambda: self.add_message('system', start_msg))
                
                self.awaiting_subtopic = False
                self.update_status("对话中" if self.language == 'zh' else "対話中")
            else:
                raise ValueError("无效的选择")
        except:
            hint = "请输入数字编号" if self.language == 'zh' else "数字を入力してください"
            self.root.after(0, lambda: self.add_message('system', hint))
    
    def handle_dialogue(self, user_input):
        """处理对话"""
        if not self.session:
            return
        
        # 情绪检测
        emotion = None
        if self.emotion_recognizer:
            try:
                result = self.emotion_recognizer.predict(user_input)
                emotion = result['emo_top']
                self.session.set_emotion(emotion, result['emo_conf'])
            except Exception as e:
                print(f"[GUI] 情绪检测失败: {e}")
        
        # RAG检索
        rag_content = ""
        try:
            rag_content = self.rag_retriever.retrieve(
                self.session.topic_key,
                self.session.subtopic_key,
                self.session.current_stage
            )
        except Exception as e:
            print(f"[GUI] RAG检索失败: {e}")
        
        # 确定当前Agent
        agent_type = self.session.get_current_agent()
        
        # 构建prompt并生成
        if agent_type == "AER":
            messages = self.aer_agent.format_prompt(
                language=self.language,
                stage=self.session.current_stage,
                user_input=user_input,
                emotion=emotion,
                rag_content=rag_content,
                dialogue_history=self.session.dialogue_history
            )
        elif agent_type == "CER":
            messages = self.cer_agent.format_prompt(
                language=self.language,
                stage=self.session.current_stage,
                user_input=user_input,
                rag_content=rag_content,
                dialogue_history=self.session.dialogue_history
            )
        else:
            return
        
        # LLM生成
        response = self.llm.generate(messages=messages)
        
        # 记录对话
        self.session.add_turn("user", user_input, self.session.current_stage)
        self.session.add_turn(agent_type, response, self.session.current_stage)
        
        # 显示机器人回复
        self.root.after(0, lambda: self.add_message(agent_type, response, emotion))
        
        # 前进到下一阶段
        self.session.advance_stage()
        
        # 更新状态
        stage_name = self.session.current_stage
        self.update_status(f"{agent_type} - {stage_name}")
        
        # 检查是否完成
        if self.session.is_completed():
            complete_msg = get_message(self.language, 'stage_complete')
            self.root.after(0, lambda: self.add_message('system', complete_msg))
            self.session.save_to_file()
    
    def update_status(self, text):
        """更新状态"""
        self.root.after(0, lambda: self.status_label.config(text=f"● {text}"))
    
    def _scroll_to_bottom(self):
        """滚动到底部"""
        self.canvas.yview_moveto(1.0)
    
    def _on_mousewheel(self, event):
        """鼠标滚轮事件"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        # 显示提示（可选）
        # print(f"[GUI] 已复制: {text[:20]}...")
    
    def _show_copy_menu(self, event, text):
        """显示右键复制菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        copy_text = "复制" if self.language == 'zh' else "コピー"
        menu.add_command(label=copy_text, command=lambda: self._copy_to_clipboard(text))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='双共情机器人GUI')
    parser.add_argument('--lang', type=str, default='ja', choices=['ja', 'zh'],
                        help='界面语言: ja(日语) or zh(中文)')
    
    args = parser.parse_args()
    
    root = tk.Tk()
    app = WeChatStyleGUI(root, language=args.lang)
    root.mainloop()


if __name__ == "__main__":
    main()
