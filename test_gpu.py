#!/usr/bin/env python3
"""
测试GPU加速
"""

def test_gpu():
    print("🧪 测试GPU加速...")
    
    try:
        import torch
        print(f"PyTorch版本: {torch.__version__}")
        
        # 检查GPU
        if torch.backends.mps.is_available():
            print("✅ Apple Silicon GPU (MPS) 可用")
            device = "mps"
        elif torch.cuda.is_available():
            print("✅ NVIDIA GPU (CUDA) 可用")
            device = "cuda"
        else:
            print("❌ 没有可用的GPU")
            return
        
        # 测试GPU
        print(f"使用设备: {device}")
        x = torch.randn(100, 100).to(device)
        y = torch.randn(100, 100).to(device)
        z = torch.mm(x, y)
        print(f"✅ GPU计算测试成功，结果形状: {z.shape}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_gpu()
