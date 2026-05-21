import os
import torch
from torchvision import transforms, models
from PIL import Image
import sys

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'best_pet_model.pth')
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

def load_model():
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
    classes = checkpoint['classes']

    model = models.efficientnet_b3(weights=None)
    num_features = model.classifier[1].in_features
    model.classifier = torch.nn.Sequential(
        torch.nn.Dropout(p=0.3, inplace=True),
        torch.nn.Linear(num_features, 512),
        torch.nn.ReLU(inplace=True),
        torch.nn.Dropout(p=0.2),
        torch.nn.Linear(512, len(classes))
    )
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(DEVICE)
    model.eval()

    return model, classes

def predict_image(image_path, model, classes):
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probabilities, 1)

    predicted_class = classes[predicted_idx.item()]
    confidence_score = confidence.item()

    return predicted_class, confidence_score

def main():
    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
        print("Or use predict_batch() function in Python code")
        sys.exit(1)

    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        sys.exit(1)

    print(f"Loading model from {MODEL_PATH}...")
    model, classes = load_model()
    print(f"Model loaded successfully. Classes: {classes}")

    predicted_class, confidence = predict_image(image_path, model, classes)
    print(f"\nPrediction: {predicted_class}")
    print(f"Confidence: {confidence * 100:.2f}%")

    return predicted_class, confidence

if __name__ == "__main__":
    main()