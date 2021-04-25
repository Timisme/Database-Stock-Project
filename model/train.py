import torch
import matplotlib.pyplot as plt


def train_test(model, optimizer, criterion, scheduler, train_dataloader, num_epochs, device):
    train_loss = {}
    test_loss = {}
    model.to(device)

    for epoch in range(num_epochs):

        model.train()
        t_loss = 0
        t_iter = 0

        for idx, (batch, labels) in enumerate(train_dataloader):
            batch = batch.to(device)
            labels = labels.to(device)
            # print('batch shape', batch.size())
            # print('')
            optimizer.zero_grad()
            outputs = model(batch)
            # print('output size:',outputs.size())
            #             print('outputs: ',outputs.data)
            # print('labels:', labels)
            # print('label shape', labels.size())

            loss = criterion(outputs.float(), labels)
            loss.backward()
            optimizer.step()

            t_loss += loss
            t_iter += 1

        print('average loss for epoch {} = {}'.format(epoch + 1, t_loss / t_iter), end='\r')
        scheduler.step()
        train_loss[epoch + 1] = t_loss / t_iter

        t_loss = 0
        t_iter = 0

        # model.eval()

        # for idx, (batch, labels) in enumerate(test_dataloader):
        #     batch = batch.to(device)
        #     labels = labels.to(device) 

        #     with torch.no_grad():
        #         outputs = model(batch)

        #     loss = criterion(outputs.float(), labels)
        #     t_loss += loss
        #     t_iter += 1

        # test_loss[epoch+1] = t_loss/t_iter

    # plt.figure(figsize=(8, 5))
    # plt.plot(list(train_loss.keys()), list(train_loss.values()), label='training loss')
    # plt.plot(list(test_loss.keys()), list(test_loss.values()), label = 'test loss')
    # plt.legend()
    # plt.show()
    print(" " * 100, end='\r')
    return model
