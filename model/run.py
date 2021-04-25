from model.dataset import stockDataset
from model.stock_feature import feature_add
from model.model import Net
from model.train import train_test
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from pandas_datareader import data as pdr


def stock_predict(stock, seq_len=3, drop_prob=0.3, lr=1e-3, num_epochs=15, batch_size=32, step_size=10):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    df = pdr.get_data_yahoo(stock)
    df.columns = [col.lower() for col in df.columns]
    data, [max_price, min_price] = feature_add(df)
    dataset = stockDataset(data)

    in_features = len(data[0])

    model = Net(in_features=in_features).to(device)

    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=step_size, gamma=0.1)
    criterion = nn.MSELoss(reduction='mean')

    dataloader = DataLoader(dataset=dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    model = train_test(model=model, optimizer=optimizer, criterion=criterion, scheduler=scheduler,
                       train_dataloader=dataloader, num_epochs=15, device=device)

    input_feats = torch.tensor(data[-seq_len:], dtype=torch.float).unsqueeze(0).to(device)
    pred_price_normalized = model(input_feats)

    pred_price = pred_price_normalized.item() * (max_price - min_price) + min_price
    return pred_price


if __name__ == '__main__':
    preds = stock_predict(['2330.TW', '2317.TW'])
    print(preds)
