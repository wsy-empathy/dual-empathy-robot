"""
WRIME-LUKE 情感识别 - ONNX Runtime 版本
使用 Mizuiro-sakura/luke-japanese-large-sentiment-analysis-wrime
支持 RTX 5070 GPU (ONNX Runtime 规避 sm_120 问题)
输出: WRIME 8类情感标签
"""

import time
import numpy as np
from typing import Dict, Tuple
from pathlib import Path

try:
    import onnxruntime as ort
    from transformers import AutoTokenizer
    HAS_ONNX = True
except ImportError:
    HAS_ONNX = False
    ort = None

# WRIME 8种情感标签
WRIME_LABELS = ["joy", "sadness", "anticipation", "surprise", "anger", "fear", "disgust", "trust"]


class ONNXWRIMELukeRecognizer:
    """
    使用 ONNX Runtime 的 WRIME-LUKE 情感识别器
    模型: Mizuiro-sakura/luke-japanese-large-sentiment-analysis-wrime
    输出: WRIME 8类情感
    """
    
    def __init__(
        self,
        model_name: str = "Mizuiro-sakura/luke-japanese-large-sentiment-analysis-wrime",
        use_gpu: bool = True
    ):
        """
        初始化 WRIME-LUKE 情感识别器
        
        Args:
            model_name: HuggingFace 模型名称
            use_gpu: 是否使用 GPU
        """
        if not HAS_ONNX:
            raise ImportError("需要安装 onnxruntime-gpu 和 transformers")
        
        self.model_name = model_name
        self.use_gpu = use_gpu
        self.labels = WRIME_LABELS
        
        # ONNX 模型路径
        model_dir = Path("models/onnx")
        model_dir.mkdir(parents=True, exist_ok=True)
        safe_model_name = model_name.replace('/', '_').replace('-', '_')
        self.onnx_path = model_dir / f"{safe_model_name}_wrime.onnx"
        
        print(f"初始化 ONNX WRIME-LUKE 情感识别器: {model_name}")
        
        # 加载 tokenizer
        print(f"  加载 tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # 检查或转换 ONNX 模型
        if not self.onnx_path.exists():
            print(f"  未找到 ONNX 模型，开始转换...")
            self._convert_to_onnx()
        else:
            print(f"  ✓ 找到已有 ONNX 模型: {self.onnx_path}")
        
        # 创建 ONNX Runtime 会话
        print(f"  创建 ONNX Runtime 会话...")
        providers = []
        if self.use_gpu:
            try:
                # 尝试使用GPU
                test_providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
                test_session = ort.InferenceSession(str(self.onnx_path), providers=test_providers)
                if 'CUDAExecutionProvider' in test_session.get_providers():
                    providers.append('CUDAExecutionProvider')
                    print(f"    [OK] Using CUDAExecutionProvider (GPU)")
                else:
                    print(f"    [WARNING] CUDA not available, falling back to CPU")
            except Exception as e:
                print(f"    [WARNING] GPU initialization failed ({type(e).__name__}), using CPU")
                print(f"              Error: {str(e)[:100]}")
        providers.append('CPUExecutionProvider')
        
        self.session = ort.InferenceSession(str(self.onnx_path), providers=providers)
        
        # 获取输入输出信息
        self.input_names = [inp.name for inp in self.session.get_inputs()]
        self.output_names = [out.name for out in self.session.get_outputs()]
        
        device = "cuda" if self.use_gpu else "cpu"
        print(f"    ✓ 会话创建成功")
        print(f"    使用的 providers: {self.session.get_providers()}")
        print(f"    输入: {self.input_names}")
        print(f"    输出: {self.output_names}")
        print(f"✓ 加载成功，设备: {device}")
    
    def _convert_to_onnx(self):
        """转换 PyTorch 模型到 ONNX 格式"""
        import torch
        from transformers import AutoModelForSequenceClassification
        
        print(f"    下载 PyTorch 模型...")
        model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        model.eval()
        
        # 准备示例输入
        dummy_text = "テスト用のテキストです。"
        inputs = self.tokenizer(
            dummy_text,
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=128
        )
        
        # 动态轴配置
        dynamic_axes = {
            'input_ids': {0: 'batch', 1: 'sequence'},
            'attention_mask': {0: 'batch', 1: 'sequence'},
            'logits': {0: 'batch'}
        }
        
        print(f"    导出到 ONNX...")
        with torch.no_grad():
            torch.onnx.export(
                model,
                (inputs['input_ids'], inputs['attention_mask']),
                str(self.onnx_path),
                input_names=['input_ids', 'attention_mask'],
                output_names=['logits'],
                dynamic_axes=dynamic_axes,
                opset_version=14,
                do_constant_folding=True
            )
        
        print(f"    ✓ ONNX 模型已保存: {self.onnx_path}")
    
    def predict(self, text: str) -> Dict:
        """
        预测文本情感
        
        Args:
            text: 输入文本（日语）
            
        Returns:
            结果字典:
                - emo8_dist: 8类情感概率分布 (list)
                - emo_top: 最高情感标签 (str)
                - emo_conf: 最高情感置信度 (float)
                - emo_score: 最高情感得分（别名，与emo_conf相同）
                - elapsed_time: 处理耗时 (float)
        """
        if not text or not text.strip():
            # 空文本返回中性结果
            return {
                "emo8_dist": [0.125] * 8,
                "emo_top": "trust",
                "emo_conf": 0.125,
                "emo_score": 0.125,
                "elapsed_time": 0.0
            }
        
        start_time = time.time()
        
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="np",
                padding="max_length",
                truncation=True,
                max_length=128
            )
            
            # 准备 ONNX 输入
            onnx_inputs = {
                'input_ids': inputs['input_ids'].astype(np.int64),
                'attention_mask': inputs['attention_mask'].astype(np.int64)
            }
            
            # 推理
            outputs = self.session.run(self.output_names, onnx_inputs)
            logits = outputs[0][0]  # shape: (8,)
            
            # Softmax
            exp_logits = np.exp(logits - np.max(logits))
            probs = exp_logits / exp_logits.sum()
            
            # 获取最高情感
            top_idx = int(np.argmax(probs))
            top_label = self.labels[top_idx]
            top_conf = float(probs[top_idx])
            
            elapsed_time = time.time() - start_time
            
            result = {
                "emo8_dist": probs.tolist(),
                "emo_top": top_label,
                "emo_conf": top_conf,
                "emo_score": top_conf,  # 兼容性别名，确保与emo_conf相同
                "elapsed_time": elapsed_time
            }
            
            return result
        except Exception as e:
            print(f"情感识别失败: {e}")
            # 返回中性结果而不是抛出异常
            return {
                "emo8_dist": [0.125] * 8,
                "emo_top": "trust",
                "emo_conf": 0.125,
                "emo_score": 0.125,
                "elapsed_time": time.time() - start_time
            }
    
    def predict_with_distribution(self, text: str) -> Tuple[np.ndarray, str, float]:
        """
        预测情感并返回分布、标签和置信度
        
        Args:
            text: 输入文本
            
        Returns:
            (distribution, top_label, confidence)
        """
        result = self.predict(text)
        return (
            np.array(result["emo8_dist"]),
            result["emo_top"],
            result["emo_conf"]
        )


# Singleton instance
_recognizer = None

def get_onnx_wrime_luke_recognizer(use_gpu: bool = True) -> ONNXWRIMELukeRecognizer:
    """获取 ONNX WRIME-LUKE 识别器单例"""
    global _recognizer
    if _recognizer is None:
        _recognizer = ONNXWRIMELukeRecognizer(use_gpu=use_gpu)
    return _recognizer


def recognize_emotion(text: str) -> Dict:
    """
    便捷函数：识别文本情感
    
    Args:
        text: 输入文本
        
    Returns:
        情感识别结果字典
    """
    recognizer = get_onnx_wrime_luke_recognizer(use_gpu=True)
    return recognizer.predict(text)


if __name__ == "__main__":
    # 测试
    print("\n" + "=" * 70)
    print("ONNX WRIME-LUKE 情感识别测试")
    print("=" * 70)
    
    recognizer = get_onnx_wrime_luke_recognizer(use_gpu=True)
    
    # 测试文本
    test_texts = [
        "今日はとても嬉しいです！",
        "悲しくて泣きそうです。",
        "明日が楽しみです。",
        "びっくりしました！",
        "怒っています。",
        "怖いです。"
    ]
    
    print("\n测试结果:")
    for text in test_texts:
        result = recognizer.predict(text)
        print(f"\n  文本: {text}")
        print(f"  情感: {result['emo_top']} (置信度: {result['emo_conf']:.3f})")
        print(f"  耗时: {result['elapsed_time']*1000:.2f}ms")
        
        # 显示 top-3 情感
        dist = result['emo8_dist']
        top3_idx = np.argsort(dist)[-3:][::-1]
        print(f"  Top-3: ", end="")
        for idx in top3_idx:
            print(f"{WRIME_LABELS[idx]}({dist[idx]:.2f}) ", end="")
        print()
    
    print("\n" + "=" * 70)
