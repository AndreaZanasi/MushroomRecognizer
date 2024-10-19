import torch
import torchvision.transforms as transforms
from PIL import Image
import torchvision.models as models
import torch.nn as nn

# Define the predict_image function
def predict(image_path, class_names):
    preprocess = transforms.Compose([
        transforms.Resize([350, 350]),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.2787, 0.2223, 0.1592], std=[0.2433, 0.2235, 0.2131])
    ])

    image = Image.open(image_path).convert('RGB')
    image = preprocess(image)
    image = image.unsqueeze(0)
    model = load_model()
    
    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)
        return class_names[predicted.item()]
    
def load_model():
    model = models.resnet18(weights=None)
    num_ftrs = model.fc.in_features
    number_of_classes = 9
    model.fc = nn.Linear(num_ftrs, number_of_classes)

    model.load_state_dict(torch.load(r'weights\model_weights(lr=0.01,mom=0.9,wd=0.003,pretr=Yes,bs=32,ep=50,size=350,trainacc=98.07864164432529,testacc=98.8978254393804).pth', map_location=torch.device('cpu'), weights_only=True))
    model.eval()
    return model