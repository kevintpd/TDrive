import torch
from torchvision import transforms
from PIL import Image
import torchvision

def AutoLabelProcess(imgPath):
    #图片转换
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    #导入模型
    # model = torch.load("autolabel/modelAndLabel/AutoLabel3.pkl")
    model = torchvision.models.quantization.mobilenet_v3_large(weights=torchvision.models.quantization.MobileNet_V3_Large_QuantizedWeights.IMAGENET1K_QNNPACK_V1, quantize=True)
    #导入并处理图片
    img = Image.open(imgPath)
    img_t = transform(img)
    batch_t = torch.unsqueeze(img_t, 0)
    out = model(batch_t)
    #打开标签文件
    with open('autolabel/modelAndLabel/label.txt', encoding='utf-8', errors='ignore') as f:
        classes = [line.strip() for line in f.readlines()]

    _, indices = torch.sort(out, descending=True)
    percentage = torch.nn.functional.softmax(out, dim=1)[0] * 100
    #结果处理
    results = []
    for idx in indices[0][:5]:
        results.append((classes[idx], percentage[idx].item()))
    return results
if __name__ == '__main__':
    result = AutoLabelProcess("测试/猴子.jpg")
    print(result)