#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版GUI测试 - 用于诊断显示问题
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class SimpleTestGUI:
    """简化版测试GUI"""
    
    COLORS = {
        'bg': '#EDEDED',
        'top_bar': '#393A3F',
        'user_bubble': '#95EC69',
        'aer_bubble': '#FFD4E5',
        'cer_bubble': '#D4E5FF',
        'system_bubble': '#FFFFFF',
        'text': '#000000',
        'send_btn': '#07C160',
    }
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_test_ui()
        
    def setup_window(self):
        """设置窗口"""
        self.root.title("GUI测试 - 颜色和布局检查")
        
        # 窗口尺寸和居中
        window_width = 900
        window_height = 1000
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.configure(bg=self.COLORS['bg'])
        self.root.minsize(700, 800)
        
        print(f"窗口尺寸: {window_width}x{window_height}")
        print(f"窗口位置: ({x}, {y})")
        print(f"屏幕尺寸: {screen_width}x{screen_height}")
        
    def create_test_ui(self):
        """创建测试UI"""
        # 顶部栏
        top_frame = tk.Frame(self.root, bg=self.COLORS['top_bar'], height=60)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        top_frame.pack_propagate(False)
        
        title = tk.Label(
            top_frame,
            text="🎨 GUI 颜色测试",
            bg=self.COLORS['top_bar'],
            fg='white',
            font=('Microsoft YaHei UI', 16, 'bold')
        )
        title.pack(pady=15)
        
        # 主内容区域
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 说明文字
        info = tk.Label(
            main_frame,
            text="如果你能看到下面的彩色气泡，说明GUI显示正常",
            bg=self.COLORS['bg'],
            fg=self.COLORS['text'],
            font=('Microsoft YaHei UI', 12)
        )
        info.pack(pady=10)
        
        # 测试各种颜色的气泡
        self.add_test_bubble(main_frame, "👤 用户消息（绿色）", self.COLORS['user_bubble'], "right")
        self.add_test_bubble(main_frame, "💖 AER消息（粉色）", self.COLORS['aer_bubble'], "left")
        self.add_test_bubble(main_frame, "🧠 CER消息（蓝色）", self.COLORS['cer_bubble'], "left")
        self.add_test_bubble(main_frame, "🤖 系统消息（白色）", self.COLORS['system_bubble'], "left")
        
        # 底部按钮区
        button_frame = tk.Frame(self.root, bg=self.COLORS['bg'], height=80)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=10)
        button_frame.pack_propagate(False)
        
        test_btn = tk.Button(
            button_frame,
            text="✅ 颜色显示正常",
            command=self.show_success,
            bg=self.COLORS['send_btn'],
            fg='white',
            font=('Microsoft YaHei UI', 12, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        test_btn.pack(side=tk.LEFT, padx=10)
        
        problem_btn = tk.Button(
            button_frame,
            text="❌ 有显示问题",
            command=self.show_problem,
            bg='#FF6B6B',
            fg='white',
            font=('Microsoft YaHei UI', 12, 'bold'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=10
        )
        problem_btn.pack(side=tk.LEFT, padx=10)
        
        # 信息显示区
        self.info_text = tk.Text(
            button_frame,
            height=3,
            width=50,
            font=('Microsoft YaHei UI', 10),
            wrap=tk.WORD
        )
        self.info_text.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)
        
        # 显示初始信息
        self.info_text.insert('1.0', 
            "窗口已加载完成\n"
            "请检查上方是否能看到4种不同颜色的气泡\n"
            f"当前时间: {datetime.now().strftime('%H:%M:%S')}"
        )
        
    def add_test_bubble(self, parent, text, color, align):
        """添加测试气泡"""
        container = tk.Frame(parent, bg=self.COLORS['bg'])
        container.pack(fill=tk.X, pady=10)
        
        bubble = tk.Label(
            container,
            text=text,
            bg=color,
            fg=self.COLORS['text'],
            font=('Microsoft YaHei UI', 12),
            padx=20,
            pady=15,
            relief=tk.FLAT,
            borderwidth=2
        )
        
        if align == "right":
            bubble.pack(side=tk.RIGHT, padx=20)
        else:
            bubble.pack(side=tk.LEFT, padx=20)
            
    def show_success(self):
        """显示成功信息"""
        self.info_text.delete('1.0', tk.END)
        self.info_text.insert('1.0',
            "✅ 太好了！GUI显示正常\n"
            "现在可以关闭这个测试窗口\n"
            "运行主GUI: python gui_chat.py --lang zh"
        )
        
    def show_problem(self):
        """显示问题诊断"""
        self.info_text.delete('1.0', tk.END)
        problems = []
        
        # 检查屏幕分辨率
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        if w < 1024 or h < 768:
            problems.append(f"⚠️ 屏幕分辨率较低: {w}x{h}")
        
        # 检查窗口
        if self.root.winfo_width() < 700:
            problems.append(f"⚠️ 窗口宽度不足: {self.root.winfo_width()}px")
            
        if not problems:
            problems.append("请描述具体问题：")
            problems.append("1. 看不到颜色？")
            problems.append("2. 窗口太小？")
            problems.append("3. 布局错乱？")
        
        self.info_text.insert('1.0', '\n'.join(problems))


def main():
    """主函数"""
    print("="*60)
    print("GUI 测试程序启动")
    print("="*60)
    
    root = tk.Tk()
    app = SimpleTestGUI(root)
    
    print("\n窗口已创建，应该可以看到测试界面")
    print("如果看不到窗口，请检查任务栏")
    print("\n按 Ctrl+C 或关闭窗口退出\n")
    
    root.mainloop()


if __name__ == "__main__":
    main()
