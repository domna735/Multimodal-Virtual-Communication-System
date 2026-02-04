# FER Module (Emotion Analysis)

This folder contains the first module of the Multimodal Virtual Communication System: **Facial Expression Recognition (FER)**.

## What you get
- Teacher ensemble wrappers (ResNet18 / EfficientNet-B3 / ConvNeXt) and a ViT-Tiny student.
- Training with CE + ArcFace head (optional) + Knowledge Distillation (KD) and Decoupled KD (DKD).
- Evaluation metrics: accuracy, macro-F1, ECE, Brier score.
- Stress testing: class imbalance, image degradation, and simple domain shift simulations.

## Quick start
1. Create a Python environment (recommended: Python 3.10+).
2. Install deps:
   - `pip install -r requirements.txt`
3. Prepare a dataset in ImageFolder format:
   - `data/your_dataset/train/<class_name>/*.jpg`
   - `data/your_dataset/val/<class_name>/*.jpg`
4. Train:
   - `python -m fer_system.cli.train --config configs/fer_vit_tiny_kd.yaml`

## Dataset format
The training code supports:
- ImageFolder directory layout (preferred)
- A CSV manifest (path,label) (optional; can be added later)

## Notes
- This is a scaffold intended to be extended to AffectNet/RAF-DB once you point it at the dataset root and class mapping.
