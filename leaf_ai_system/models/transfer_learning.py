"""
Transfer Learning & Model Factory
Supports MobileNetV2, ResNet18, and custom LeafNet.
"""

import torch
import torch.nn as nn
from torchvision import models

from .leaf_net import LeafNet

def build_model(
    backbone: str = "mobilenet_v2",
    num_classes: int = 4,
    pretrained: bool = True,
    dropout: float = 0.2
) -> nn.Module:
    """
    Factory function to instantiate models for leaf classification.
    Options: 'mobilenet_v2', 'resnet18', 'leaf_net'
    """
    backbone = backbone.lower()

    if backbone == "mobilenet_v2":
        weights = models.MobileNet_V2_Weights.DEFAULT if pretrained else None
        model = models.mobilenet_v2(weights=weights)
        in_features = model.classifier[1].in_features
        model.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, num_classes)
        )
        return model

    elif backbone == "resnet18":
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        model = models.resnet18(weights=weights)
        in_features = model.fc.in_features
        model.fc = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(in_features, num_classes)
        )
        return model

    elif backbone == "leaf_net":
        model = LeafNet(num_classes=num_classes, dropout=dropout)
        return model

    else:
        raise ValueError(
            f"Unsupported backbone: '{backbone}'. "
            f"Choose from: 'mobilenet_v2', 'resnet18', 'leaf_net'"
        )
