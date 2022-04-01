import torch.optim
import copy
from torchvision import transforms
from modules.focus.mutual_gaze.focus_detection.MARIADataset import MARIAData
from modules.focus.mutual_gaze.focus_detection.model import MutualGazeDetector
from tqdm import tqdm
import cv2

LOG_EVERY = 10

if __name__ == "__main__":
    valid_data = MARIAData("D:/datasets/focus_dataset", mode="valid")
    valid_loader = torch.utils.data.DataLoader(valid_data, batch_size=32, num_workers=2)

    model = MutualGazeDetector()
    model.load_state_dict(torch.load('modules/focus/mutual_gaze/focus_detection/checkpoints/acc_0.98_loss_0.07.pth'))
    model.cuda()
    model.eval()

    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])

    # EVAL
    losses = []
    accuracies = []
    model.eval()
    for x, y in tqdm(valid_loader):

        imgs = copy.deepcopy(x)
        x = x.permute(0, 3, 1, 2)
        x = x / 255.
        x = normalize(x)
        x = x.cuda()
        y = y.cuda()

        out = model(x)

        for i in range(len(imgs)):
            img = imgs[i].detach().cpu().numpy()

            print("Real: {:.2f}, pred: {:.2f}", y[i].int().item(), out[i].item())
            cv2.imshow("", img)

            cv2.waitKey(0)
