import torch
import torch.nn as nn


class Net(nn.Module):
    def __init__(self, in_features, hidden_dim=512, n_classes=1, num_layers=2, drop_prob=0.5):
        super(Net, self).__init__()
        self.n_classes = n_classes
        self.in_features = in_features
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size=in_features, hidden_size=hidden_dim, num_layers=num_layers, dropout=drop_prob,
                            batch_first=True)
        # 原本lstm 的規定input (timesteps, (batch_size, features))
        # 若batch = first 則input為 (batchsize, timesteps, features) # timesteps為seq len 就是sliding window的長度 features則可以看成 stock df的columns數
        # self.fc = nn.Linear(-1, n_classes)
        self.linear = nn.Linear(in_features=hidden_dim, out_features=n_classes)
        self.fc = nn.Sequential(
            nn.Dropout(drop_prob),
            nn.ReLU(),
            nn.Linear(hidden_dim, n_classes))

    def forward(self, x):
        # h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim)
        # c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim)

        x, _ = self.lstm(x)
        # print('lstm batch output:',x.size())
        x = x[:, -1, :]
        # print('batch size before linear:',x.size())
        x = self.linear(x)

        return torch.squeeze(x)
