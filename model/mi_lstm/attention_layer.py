import torch
import torch.nn as nn
from torch.autograd import Variable


class Attention_layer():
    def __init__(self, seq_len, input_size, attention_size=None):
        if attention_size == None:
            attention_size = input_size
        self.o_size = attention_size
        self.h_size = input_size
        self.t_size = seq_len

        self.beta_weight = Variable(torch.randn(size=(self.h_size, self.o_size)))
        self.beta_bias = Variable(torch.zeros(self.o_size))
        self.v = Variable(torch.randn(size=(self.o_size, 1)))

    # inputs (batchsize, seq_len, hidden_size)
    def __call__(self, inputs):
        '''
		shape of output will be (batch_size, 1, input_hidden_unit_size).
		'''
        temp = torch.matmul(inputs.reshape(-1, self.h_size), self.beta_weight)

        print('temp size: ', temp.size())
        temp = nn.Tanh()(temp + self.beta_bias)

        j = torch.matmul(temp, self.v).reshape(-1, self.t_size, 1)

        beta = nn.Softmax()(j)  # temporal attention vector
        print('beta: ', beta.size())
        output = beta * inputs

        output = torch.sum(output, dim=1)

        return output
