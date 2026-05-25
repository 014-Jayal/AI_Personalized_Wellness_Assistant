import torch
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import torchvision.transforms as transforms

device = torch.device("cpu")

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])


def generate_gradcam(model, image):

    img_tensor = transform(image).unsqueeze(0).to(device)
    img_tensor.requires_grad = True

    features = []
    gradients = []

    def forward_hook(module, input, output):
        features.append(output)

    def backward_hook(module, grad_in, grad_out):
        gradients.append(grad_out[0])

    layer = model.features[-1]

    forward_handle = layer.register_forward_hook(forward_hook)
    backward_handle = layer.register_backward_hook(backward_hook)

    output = model(img_tensor)
    pred = output.argmax()

    model.zero_grad()
    output[0, pred].backward()

    grads = gradients[0]
    fmap = features[0]

    weights = torch.mean(grads, dim=(2, 3), keepdim=True)

    cam = torch.sum(weights * fmap, dim=1).squeeze()

    cam = torch.relu(cam)
    cam = cam / cam.max()

    cam = cam.detach().cpu().numpy()

    cam = cv2.resize(cam, (224, 224))

    heatmap = cv2.applyColorMap(
        np.uint8(255 * cam),
        cv2.COLORMAP_JET
    )

    img_np = np.array(image.resize((224, 224)))

    overlay = cv2.addWeighted(img_np, 0.6, heatmap, 0.4, 0)

    overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

    img = Image.fromarray(overlay)

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    encoded = base64.b64encode(buffer.getvalue()).decode()

    forward_handle.remove()
    backward_handle.remove()

    return encoded