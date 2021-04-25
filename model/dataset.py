from torch.utils.data import Dataset
import torch


class stockDataset(Dataset):
    def __init__(self, dataset, seq_len=3, label_idx=3, transforms=None):
        self.dataset = torch.tensor(dataset, dtype=torch.float)
        self.seq_len = seq_len
        self.transforms = transforms
        self.features_len = len(dataset[0])
        self.label_idx = label_idx

    def __len__(self):
        return len(self.dataset) - self.seq_len

    def __getitem__(self, idx):
        # if idx + self.seq_len > self.__len__():
        #  return
        if self.transforms is not None:
            # seq_features = torch.zeros(self.seq_len, self.features_len)
            seq_feature = self.transforms(self.dataset[idx:idx + self.seq_len])
            label = self.transforms(self.dataset[idx + self.seq_len][self.label_idx])
            return seq_feature, label
        else:
            # print(idx)
            return self.dataset[idx:idx + self.seq_len], self.dataset[idx + self.seq_len][self.label_idx]
