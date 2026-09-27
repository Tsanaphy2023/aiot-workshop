"""
Hardware Device Detection Utility
Detects Apple Silicon MPS, NVIDIA CUDA, or CPU fallback.
"""

import torch

def select_device(preferred: str = None) -> torch.device:
    """
    Detects and returns the optimal torch.device.
    Can be overridden with 'cuda', 'mps', or 'cpu'.
    """
    if preferred:
        return torch.device(preferred)

    if torch.cuda.is_available():
        print(f"🚀 Using NVIDIA CUDA GPU: {torch.cuda.get_device_name(0)}")
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        print("🍎 Using Apple Silicon GPU via Metal Performance Shaders (MPS)")
        return torch.device("mps")
    else:
        print("💻 Using Standard CPU")
        return torch.device("cpu")
