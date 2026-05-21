import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
from torchvision import transforms, models
from PIL import Image
import matplotlib.pyplot as plt
from tqdm import tqdm
import time
from sklearn.metrics import classification_report

class PetDataset(Dataset):
    def __init__(self, dog_root, cat_root, transform=None):
        self.transform = transform
        self.samples = []
        self.classes = []
        class_to_idx = {}
        
        dog_classes = sorted([d for d in os.listdir(dog_root) if os.path.isdir(os.path.join(dog_root, d))])
        for cls in dog_classes:
            cls_dir = os.path.join(dog_root, cls)
            idx = len(self.classes)
            class_to_idx[cls] = idx
            self.classes.append(cls)
            for img_name in os.listdir(cls_dir):
                if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                    self.samples.append((os.path.join(cls_dir, img_name), idx))

        cat_label_path = os.path.join(cat_root, 'label.txt')
        cat_class_mapping = {}  # 英文目录名 -> 中文类别名
        if os.path.exists(cat_label_path):
            with open(cat_label_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        parts = line.split(' ')
                        if len(parts) >= 2:
                            # 获取英文目录名（原目录名）和中文类别名
                            cat_class_mapping[parts[1]] = parts[2] if len(parts) >= 3 else parts[1]
        
        cat_images_dir = os.path.join(cat_root, 'images', 'train')
        # 获取所有英文目录名
        if os.path.exists(cat_images_dir):
            for dir_name in os.listdir(cat_images_dir):
                dir_path = os.path.join(cat_images_dir, dir_name)
                if os.path.isdir(dir_path):
                    # 使用中文类别名，如果没有映射则使用原目录名
                    cls_name = cat_class_mapping.get(dir_name, dir_name)
                    idx = len(self.classes)
                    class_to_idx[cls_name] = idx
                    self.classes.append(cls_name)
                    for img_name in os.listdir(dir_path):
                        if img_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                            self.samples.append((os.path.join(dir_path, img_name), idx))

        self.class_to_idx = class_to_idx

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = Image.open(img_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image, label

    def get_class_name(self, idx):
        return self.classes[idx]

def get_data_loaders(dog_dir, cat_dir, batch_size=32, num_workers=0):
    train_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.RandomGrayscale(p=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    full_dataset = PetDataset(dog_dir, cat_dir, transform=None)
    print(f"Total samples: {len(full_dataset)}")
    print(f"Total classes: {len(full_dataset.classes)}")
    print(f"Classes: {full_dataset.classes}")

    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

    train_dataset.dataset.transform = train_transform
    val_dataset.dataset.transform = val_transform

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers, pin_memory=True)

    print(f"Training samples: {len(train_dataset)}")
    print(f"Validation samples: {len(val_dataset)}")

    return train_loader, val_loader, full_dataset.classes

def create_model(num_classes):
    model = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.IMAGENET1K_V1)
    num_features = model.classifier[1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.3, inplace=True),
        nn.Linear(num_features, 512),
        nn.ReLU(inplace=True),
        nn.Dropout(p=0.2),
        nn.Linear(512, num_classes)
    )
    return model

def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0
    pbar = tqdm(loader, desc='Training')
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item() * images.size(0)
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        pbar.set_postfix({'loss': f'{loss.item():.4f}', 'acc': f'{100.*correct/total:.2f}%'})
    return running_loss / total, 100. * correct / total

def validate(model, loader, criterion, device):
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for images, labels in tqdm(loader, desc='Validating'):
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    return running_loss / total, 100. * correct / total, all_preds, all_labels

def main():
    DOG_DIR = os.path.join(os.path.dirname(__file__), 'data', 'pet')
    CAT_DIR = os.path.join(os.path.dirname(__file__), 'data', 'cat')
    MODEL_SAVE_PATH = os.path.join(os.path.dirname(__file__), 'best_pet_model.pth')

    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {DEVICE}")

    BATCH_SIZE = 32
    NUM_WORKERS = 0
    NUM_EPOCHS = 50

    print("Loading dataset...")
    train_loader, val_loader, classes = get_data_loaders(DOG_DIR, CAT_DIR, BATCH_SIZE, NUM_WORKERS)

    model = create_model(len(classes)).to(DEVICE)
    print(f"Model created with {len(classes)} classes")

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS, eta_min=1e-6)

    best_val_acc = 0.0
    patience = 10
    patience_counter = 0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    print("\nStarting training...")
    start_time = time.time()

    for epoch in range(NUM_EPOCHS):
        print(f"\nEpoch {epoch+1}/{NUM_EPOCHS}")
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, DEVICE)
        val_loss, val_acc, val_preds, val_labels = validate(model, val_loader, criterion, DEVICE)
        scheduler.step()

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        print(f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.2f}%")
        print(f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.2f}%")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_acc': val_acc,
                'classes': classes
            }, MODEL_SAVE_PATH)
            print(f"Model saved with validation accuracy: {val_acc:.2f}%")
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping triggered after {epoch+1} epochs")
                break

    total_time = time.time() - start_time
    print(f"\nTraining completed in {total_time/60:.2f} minutes")
    print(f"Best validation accuracy: {best_val_acc:.2f}%")

    checkpoint = torch.load(MODEL_SAVE_PATH)
    model.load_state_dict(checkpoint['model_state_dict'])
    _, final_acc, final_preds, final_labels = validate(model, val_loader, criterion, DEVICE)

    print("\n" + "="*50)
    print("Final Classification Report:")
    print("="*50)
    print(classification_report(final_labels, final_preds, target_names=classes))

    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.title('Training and Validation Loss')

    plt.subplot(1, 2, 2)
    plt.plot(history['train_acc'], label='Train Acc')
    plt.plot(history['val_acc'], label='Val Acc')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy (%)')
    plt.legend()
    plt.title('Training and Validation Accuracy')
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(__file__), 'training_history.png'), dpi=150)
    plt.close()
    print("\nTraining history plot saved to training_history.png")

if __name__ == '__main__':
    main()