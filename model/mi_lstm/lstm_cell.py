import torch 
import torch.nn as nn 
from torch.autograd import Variable

# a single cell at time t (no seq_len)

class Mi_LSTM_cell(nn.LSTMCell):
	def __init__(self, input_size, hidden_size, num_input):
		super(Mi_LSTM_cell, self).__init__(input_size, hidden_size)

		if (type(num_input) is not int):
			raise ValueError('num_input should be int')
		elif num_input < 1:
			raise ValueError('num_input should be > 0')

		self.num_input = num_input
		self.hidden_size = hidden_size
		self.alpha_weight = Variable(torch.randn((hidden_size, hidden_size), requires_grad= True))
		self.alpha_bias= []

		for i in range(self.num_input):
			self.alpha_bias.append(torch.zeros(1, requires_grad= True))

	
	# inputs : [batch, 4*hidden_dim]
    # 0 = forget_gate, 1 = output_gate, 2= main_new_input, 3 = main_input_gate, 4~ = input_gate_for_auxiliary

	def __call__(self, inputs, state): #將class當作函數調用 __call__()。

		# cell, hidden state at t- 1

		c, h = state # state is tuple

		#input_list :
		input_list = torch.chunk(inputs, chunks= self.num_input, dim= 1)
		print(input_list[0].size())
		# [batchsize, hidden_dim]

		'''If split_size_or_sections is an integer type, 
		then tensor will be split into equally sized chunks (if possible). 
		Last chunk will be smaller if the tensor size along the given dimension dim 
		is not divisible by split_size.'''

		# ms : main_stream
		# out : why？
		ms = torch.cat([input_list[0], h], dim= 1)
		n_out = (3 + self.num_input) * self.hidden_size
		concat = nn.Linear(in_features= ms.size(-1), out_features= n_out)(ms)

		main_list = concat.chunk((3+self.num_input), dim= 1)
		# print(len(main_list))
		# print(main_list[0])

		#new_input_gate= list of all new_input
		new_input_gate= [nn.Tanh()(main_list[2])]

		#linear layer for auxiliary inputs

		##怪怪的

		# it = (Wi[ht􀀀1; ~Yt] + bi) (24)
		# ipt = (Wip[ht􀀀1; ~Yt] + bip) (25)
		# int = (Win[ht􀀀1; ~Yt] + bin) (26)
		# iit = (Wii[ht􀀀1; ~Yt] + bii)

		for i in range(1, self.num_input):

			nn_input_size=  torch.cat([input_list[i], h], dim= 1).size(-1)
			
			layer = nn.Sequential(
				nn.Linear(nn_input_size, self.hidden_size),
				nn.Tanh())

			y = layer(input= torch.cat([input_list[i], h], dim= 1))

			new_input_gate.append(y)

		# making list of 1.1 = sigmoid(input_gate) * tanh(new_input)

		'''
		lt = ~Ct  it (28)
		lpt = ~Cpt  ipt (29)
		lnt = ~Cnt  int (30)
		lit = ~Cit  iit (31)
		'''

		# final cell state input at time t.
		new_l= []
		for i, new_input in enumerate(new_input_gate, 3):
			new_l.append(nn.Sigmoid()(main_list[i]) * new_input)

		# list of u 

		u = []

		for i, l in enumerate(new_l):
			u_temp = torch.matmul(l, self.alpha_weight)
			u_temp = torch.unsqueeze(u_temp, dim=1)
			u_temp = torch.matmul(u_temp, torch.unsqueeze(c, dim= 2))
			u.append(nn.Tanh()(torch.squeeze(u_temp+self.alpha_bias[i], dim= 2)))

		u = torch.cat(u, dim= 0)

		alpha = nn.Softmax(dim= 0)(u)

		#the final cell state inputat time t.
		L= []

		for i, l in enumerate(new_l):
			L.append(alpha[i]*l)

		L = torch.cat(L, dim= 0) # 從list轉成tensor matrix

		L= torch.sum(L, dim= 0)

		#new state = c(t-1) * f + L. new h = tanh(c) + sigmoid(o)
		# the update vector of cell state Lt 
		# ft = (Wf [ht􀀀1; ~Yt] + bf )
		# forget gate and output gate are ft; ot
		# ht = tanh(Ct)  ot

		# self._forget_bias
		new_c = (c * nn.Sigmoid()(main_list[0] + 1)+L)
		new_h = nn.Tanh()(new_c) * nn.Sigmoid()(main_list[1])

		new_state= (new_c, new_h) # LSTMstatetuple
		return new_h, new_state

#Attention layer. Receives LSTM output of (None, TimeWindow, hidden_unit_size) 
# shape as input and outputs tensor of (None, 1, hidden_unit_size)
"""
        Setting parameter for attention layer.
        args:
            timewindow_size = time window size of previous lstm layer.
            input_hidden_unit_size = hidden unit number of previous lstm layer.
            attention_size = size of this attention. 
                default = input_hidden_unit_size.
"""


'''
jt = vb
>tanh(Wb(~Y0t)> + bb) (43)
 = Softmax([j1; j2; :::; jT ]>)
'''

if __name__ == '__main__':


	
	batch_size=  10
	input_size= 3
	hidden_dim = 64
	num_input = 4
	seq_len= 5

	# Y = torch.randn(size= (batch_size, seq_len, 1), dtype=torch.float32)
	# lstm = nn.LSTM(input_size= 1, hidden_size= hidden_dim)
	# Y_1, _= lstm(Y)

	# print(Y_1.size())

	cell =Mi_LSTM_cell(input_size= input_size, hidden_size= hidden_dim, num_input= num_input)



	# (batch, input_size)
	input_ = torch.randn(size= (batch_size, 4*hidden_dim))
	hidden_state = torch.randn(size= (batch_size, hidden_dim))
	cell_state = torch.randn(size= (batch_size, hidden_dim))

	new_h, new_state= cell(inputs= input_, state= (cell_state, hidden_state))
	print(new_h.size())

	# a = torch.rand(size= (batch_size, num_input*hidden_dim))
	# b = a.chunk(chunks= num_input, dim= 1)
	# print(b[0].size())

	# print(torch.chunk(a, chunks= num_input, dim= 1)[0].size())









		


