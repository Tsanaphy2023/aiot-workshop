"""
LeafNet: Compact & Efficient Custom CNN Architecture
Designed specifically for agricultural leaf classification,
educational workshops, and low-latency Edge AI deployment.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class ConvBlock(nn.Module):
    """Convolution + BatchNorm + LeakyReLU + MaxPool block"""
    def __init__(self, in_channels, out_channels, pool=True):
        super().__init__()
        layers = [
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.LeakyReLU(0.1, inplace=True)
        ]
        if pool:
            layers.append(nn.MaxPool2d(2, 2))
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)

class LeafNet(nn.Module):
    """
    Lightweight 4-stage convolutional neural network.
    Parameter count: ~1.2M parameters.
    Fast training on standard CPU or GPU.
    """
    def __init__(self, num_classes: int = 4, in_channels: int = 3, dropout: float = 0.3):
        super().__init__()
        self.num_classes = num_classes

        self.features = nn.Sequential(
            ConvBlock(in_channels, 32, pool=True),    # 224 -> 112
            ConvBlock(32, 64, pool=True),             # 112 -> 56
            ConvBlock(64, 128, pool=True),            # 56 -> 28
            ConvBlock(128, 256, pool=True),           # 28 -> 14
        )

        self.gap = nn.AdaptiveAvgPool2d((1, 1))

        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(256, 128),
            nn.LeakyReLU(0.1, inplace=True),
            nn.Dropout(dropout / 2),
            nn.Linear(128, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.gap(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
