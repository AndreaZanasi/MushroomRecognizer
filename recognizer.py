# This script defines a function to predict the class of a mushroom image using a pre-trained ResNet-18 model.
# It includes functions to preprocess the image, load the model, and make predictions with confidence scores.

import torch
import torchvision.transforms as transforms
from PIL import Image
import torchvision.models as models
from torchvision.models import ResNet18_Weights
import torch.nn as nn
import torch.nn.functional as F

def predict(image_path, class_names):
    preprocess = transforms.Compose([
        transforms.Resize([400, 400]),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.4639, 0.6601, 0.5745], std=[0.9625, 0.9623, 0.9794])
    ])

    image = Image.open(image_path).convert('RGB')
    image = preprocess(image)
    image = image.unsqueeze(0)
    model = load_model()
    
    with torch.no_grad():
        outputs = model(image)
        probabilities = F.softmax(outputs, dim=1) * 100
        _, predicted = torch.max(probabilities, 1)
        predicted_name = class_names[predicted.item()]
        confidence = probabilities[0][predicted.item()]
        
        return predicted_name, round(float(confidence),1)
    
def load_model():
    model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1) 
    num_ftrs = model.fc.in_features
    number_of_classes = 9
    model.fc = nn.Linear(num_ftrs, number_of_classes)

    model.load_state_dict(torch.load(r'weights/model_weights(lr=0.01,mom=0.9,wd=0.003,pretr=Yes,bs=32,ep=50,size=400,trainacc=97.58713136729223,testacc=99.38933571641347).pth', 
                                     map_location=torch.device('cpu'), 
                                     weights_only=True))
    model.eval()
    return model