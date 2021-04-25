import torch
import torch.nn as nn
import numpy as np
from lstm_cell import Mi_LSTM_cell
from attention_layer import Attention_layer


# lstmModel=model.LSTM_Model(
#     sess,
#     name,
#     timesize,
#     positive_correlation_stock_num,
#     negative_correlation_sotck_num
#     )

class LSTM_Model(nn.Module):
    def __init__(self, hidden_size, seq_len, n_pos, n_neg):
        super(LSTM_Model, self).__init__()
        self.hidden_size = hidden_size
        self.T = seq_len
        self.P = n_pos
        self.N = n_neg

    # self.build_net()
    # forward input :y, Xp, Xn, Xi, target
    # now just for testing so no input given
    def forward(self, batch_size=32):

        self.Y = torch.rand(size=(batch_size, self.T, 1), dtype=torch.float)
        self.Xp = torch.rand(size=(batch_size, self.P, self.T, 1), dtype=torch.float)
        self.Xn = torch.rand(size=(batch_size, self.N, self.T, 1), dtype=torch.float)
        self.Xi = torch.rand(size=(batch_size, self.T, 1), dtype=torch.float)
        self.Target = torch.rand(size=(batch_size, 1), dtype=torch.float)

        Xps = torch.chunk(self.Xp, chunks=self.P, dim=1)
        Xns = torch.chunk(self.Xn, self.N, dim=1)
        print(Xps[0].size())  # (batchsize, seq_len, 1)

        Xp_list = []
        Xn_list = []

        # 有seq_len 長度的lstm cell組成
        lstm = nn.LSTM(input_size=1, hidden_size=self.hidden_size, batch_first=True)

        # (batch_size, seq_len, hidden_size)
        Y_1, _ = lstm(self.Y)
        Xi_1, _ = lstm(self.Xi)

        for i in range(len(Xps)):
            o, _ = lstm(torch.squeeze(Xps[i], dim=1))  # o : (batchsize, seq_len, hidden_dim)
            Xp_list.append(o)

        for i in range(len(Xns)):
            o, _ = lstm(torch.squeeze(Xns[i], dim=1))
            Xn_list.append(o)

        assert (len(Xp_list) > 0) & (len(Xn_list) > 0), 'list len == 0'

        # 多一個維度以供算平均
        Xp_list = [p_out.unsqueeze(dim=0) for p_out in Xp_list]
        Xn_list = [n_out.unsqueeze(dim=0) for n_out in Xn_list]

        Xp = torch.cat(Xp_list)
        Xn = torch.cat(Xn_list)

        print(Xp.size())

        Xp_1 = torch.mean(Xp, dim=0)
        Xn_1 = torch.mean(Xn, dim=0)

        assert (Y_1.size() == Xi_1.size() == Xp_1.size() == Xn_1.size()), 'Y_1 size: {}, Xp_1 size: {}'.format(
            Y_1.size(), Xp_1.size())

        result = torch.cat([Y_1, Xp_1, Xn_1, Xi_1], dim=2)
        # (batc_size, seq_len, 4*hidden_size)

        # iterate through lstm cell
        cell = Mi_LSTM_cell(input_size=result.size(-1), hidden_size=self.hidden_size, num_input=4)
        init_hidden = (
        torch.rand(size=(result.size(0), self.hidden_size)), torch.rand(size=(result.size(0), self.hidden_size)))

        out = []
        for t in range(result.size(1)):
            input_t = torch.squeeze(result[:, t, :], dim=1)
            if t == 0:
                _, (new_c, new_h) = cell(inputs=input_t, state=init_hidden)
                out.append(new_h.unsqueeze(dim=1))
            else:
                _, (new_c, new_h) = cell(inputs=input_t, state=(new_c, new_h))
                out.append(new_h.unsqueeze(dim=1))

        out = torch.cat(out, dim=1)

        print('lstm last out size: ', out.size())
        Y_2 = out  # (batchsize, hidden_size)

        # attention_layer
        attention_layer = Attention_layer(seq_len=self.T, input_size=self.hidden_size)
        Y_3 = attention_layer(Y_2)
        print('attention output size: ', Y_3.size())
        # Y_3 = torch.flatten(Y_3)

        layers = nn.Sequential(
            nn.Linear(Y_3.size(-1), self.hidden_size),
            nn.ReLU(),
            nn.Linear(self.hidden_size, self.hidden_size),
            nn.ReLU(),
            nn.Linear(self.hidden_size, 1))

        out = layers(Y_3)
        print('last out size: ', out.size())

        loss = nn.MSELoss()(input=out, target=self.Target)

        return out, loss


if __name__ == '__main__':
    model = LSTM_Model(hidden_size=64, seq_len=10, n_pos=5, n_neg=5)
    out, loss = model()

    print(out)
    print(loss)
