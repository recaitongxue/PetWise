# PetWise 宠物识别模型

## 概述

PetWise 宠物识别模型是一个基于 **EfficientNet-B3** 深度学习架构构建的宠物品种识别系统，支持识别 **23种宠物品种**（11种狗 + 12种猫）。

---

## 📊 模型架构

### 骨架网络：EfficientNet-B3

本模型采用 **EfficientNet-B3** 作为基础骨架，这是一种通过复合缩放（Compound Scaling）策略优化的高效卷积神经网络。

#### EfficientNet 核心特点

| 特性 | 说明 |
|------|------|
| **复合缩放** | 同时优化深度、宽度和分辨率 |
| **MBConv模块** | Mobile Inverted Residual Bottleneck |
| **深度可分离卷积** | 高效的计算方式 |
| **注意力机制** | SE (Squeeze-and-Excitation) 模块 |

#### 模型结构

```
输入 (224x224x3)
    ↓
┌───────────────────────────────────────┐
│        EfficientNet-B3 Backbone       │
│  ┌─────────────────────────────────┐  │
│  │  Stem: 3x3 Conv, 2x2 MaxPool   │  │
│  └─────────────────────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │  MBConv Blocks (1-7 stages)    │  │
│  │  - Stage 1: 1 block            │  │
│  │  - Stage 2: 2 blocks           │  │
│  │  - Stage 3: 3 blocks           │  │
│  │  - Stage 4: 5 blocks           │  │
│  │  - Stage 5: 8 blocks           │  │
│  │  - Stage 6: 10 blocks          │  │
│  │  - Stage 7: 1 blocks           │  │
│  └─────────────────────────────────┘  │
│  ┌─────────────────────────────────┐  │
│  │  Head: Global AvgPool + 1280    │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│         自定义分类器头部              │
│  ┌─────────────────────────────────┐  │
│  │  Dropout(0.3)                   │  │
│  │       ↓                         │  │
│  │  Linear(1280 → 512)            │  │
│  │       ↓                         │  │
│  │  ReLU                           │  │
│  │       ↓                         │  │
│  │  Dropout(0.2)                   │  │
│  │       ↓                         │  │
│  │  Linear(512 → 23)               │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
    ↓
输出 (23个类别的概率分布)
```

#### 分类器详细结构

| 层级 | 类型 | 输入维度 | 输出维度 | 参数 |
|------|------|----------|----------|------|
| Layer 1 | Dropout | 1280 | 1280 | p=0.3 |
| Layer 2 | Linear | 1280 | 512 | 1280×512 |
| Layer 3 | ReLU | 512 | 512 | - |
| Layer 4 | Dropout | 512 | 512 | p=0.2 |
| Layer 5 | Linear | 512 | 23 | 512×23 |

---

## 📁 数据集

### 数据结构

```
data/
├── dog/                    # 狗类数据集 (按目录分类)
│   ├── 中华田园犬/
│   ├── 吉娃娃/
│   ├── 哈士奇/
│   ├── 德牧/
│   ├── 拉布拉多/
│   ├── 杜宾/
│   ├── 柴犬/
│   ├── 法国斗牛/
│   ├── 萨摩耶/
│   ├── 藏獒/
│   └── 金毛/
└── cat/                    # 猫类数据集
    ├── label.txt           # 英文->中文类别映射
    ├── train.txt           # 训练文件列表
    ├── val.txt             # 验证文件列表
    └── images/
        └── train/          # 按英文目录名分类
            ├── Abyssinian/
            ├── Egyptian/
            ├── Bengal/
            ├── Ragdoll/
            ├── Persian/
            ├── Burmese/
            ├── Russian_Blue/
            ├── Bombay/
            ├── Maine_Coon/
            ├── Sphynx/
            ├── Siamese/
            └── British_Shorthair/
```

### 类别列表

#### 🐕 犬类 (11种)
1. 中华田园犬
2. 吉娃娃
3. 哈士奇
4. 德牧
5. 拉布拉多
6. 杜宾
7. 柴犬
8. 法国斗牛
9. 萨摩耶
10. 藏獒
11. 金毛

#### 🐱 猫类 (12种)
1. 阿比西尼亚猫
2. 埃及猫
3. 豹猫
4. 布偶猫
5. 波斯猫
6. 缅甸猫
7. 俄罗斯蓝猫
8. 孟买猫
9. 缅因猫
10. 无毛猫
11. 暹罗猫
12. 英国短毛猫

### 数据增强策略

训练阶段采用以下数据增强技术：

| 增强方式 | 参数 | 作用 |
|----------|------|------|
| RandomResizedCrop | 224x224 | 随机裁剪，增加样本多样性 |
| RandomHorizontalFlip | p=0.5 | 随机水平翻转 |
| RandomRotation | 15° | 随机旋转 |
| ColorJitter | brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1 | 颜色扰动 |
| RandomGrayscale | p=0.1 | 随机灰度化 |

### 归一化参数

使用 ImageNet 预训练的均值和标准差：
- **均值**: `[0.485, 0.456, 0.406]`
- **标准差**: `[0.229, 0.224, 0.225]`

---

## 🚀 训练配置

### 训练超参数

| 参数 | 值 | 说明 |
|------|-----|------|
| Batch Size | 32 | 每批次样本数 |
| Epochs | 50 | 训练轮数 |
| Learning Rate | 1e-4 | 初始学习率 |
| Weight Decay | 1e-4 | L2正则化系数 |
| Optimizer | AdamW | 优化器 |
| Scheduler | CosineAnnealingLR | 学习率调度器 |
| Early Stopping | patience=10 | 早停机制 |

### 优化器配置

```python
optimizer = optim.AdamW(
    model.parameters(),
    lr=1e-4,
    weight_decay=1e-4
)
```

### 学习率调度

```python
scheduler = optim.lr_scheduler.CosineAnnealingLR(
    optimizer,
    T_max=NUM_EPOCHS,
    eta_min=1e-6
)
```

---

## 📈 训练结果

### 性能指标

| 指标 | 值 |
|------|-----|
| 训练准确率 | ~99% |
| 验证准确率 | ~95.85% |
| 训练时间 | ~30分钟 (GPU) |
| 模型大小 | ~120MB |

### 训练曲线

训练过程中自动生成 `training_history.png`，包含：
- 训练/验证损失曲线
- 训练/验证准确率曲线

---

## 🔧 使用方法

### 环境依赖

```bash
# 必要依赖
pip install torch torchvision matplotlib tqdm scikit-learn pillow
```

### 训练模型

```bash
cd e:\PetWise\model
python train.py
```

### 预测单张图片

```bash
python predict.py --image path/to/image.jpg
```

### 模型文件

训练完成后，模型权重保存在 `best_pet_model.pth`，包含：

```python
{
    'epoch': 训练轮数,
    'model_state_dict': 模型参数,
    'optimizer_state_dict': 优化器参数,
    'val_acc': 最佳验证准确率,
    'classes': 类别名称列表
}
```

---

## 🔍 推理流程

### 单张图片推理步骤

```python
# 1. 加载模型
model = create_model(num_classes=23)
checkpoint = torch.load('best_pet_model.pth')
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# 2. 预处理图片
transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 3. 推理
with torch.no_grad():
    outputs = model(img_tensor)
    probs = torch.nn.functional.softmax(outputs, dim=1)
    top5_probs, top5_indices = torch.topk(probs, 5)
```

---

## 📚 文件说明

| 文件 | 描述 |
|------|------|
| `train.py` | 完整的训练脚本 |
| `predict.py` | 预测脚本 |
| `data/dog/` | 狗类数据集 |
| `data/cat/` | 猫类数据集 |
| `best_pet_model.pth` | 训练好的模型权重 |
| `training_history.png` | 训练曲线图 |
| `README.md` | 本说明文档 |

---

## 🎯 技术亮点

1. **迁移学习**: 使用 ImageNet 预训练权重初始化，加速收敛
2. **数据增强**: 多种增强策略提升模型泛化能力
3. **早停机制**: 防止过拟合，保留最佳模型
4. **余弦退火**: 学习率动态调整，优化训练过程
5. **AdamW优化**: 改进的Adam优化器，更好的权重衰减

---

## 📝 License

MIT License