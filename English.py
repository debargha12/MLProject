#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np

import random

import numpy as np

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

def smooth(loss, cur_loss):
    return loss * 0.999 + cur_loss * 0.001

def print_sample(sample_ix, ix_to_char):
    txt = ''.join(ix_to_char[ix] for ix in sample_ix)
    txt = txt[0].upper() + txt[1:]  # capitalize first character 
    print ('%s' % (txt, ), end='')

def get_initial_loss(vocab_size, seq_length):
    return -np.log(1.0/vocab_size)*seq_length

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0)

def initialize_parameters(n_a, n_x, n_y):
    
    np.random.seed(1)
    Wax = np.random.randn(n_a, n_x)*0.01 # input to hidden
    Waa = np.random.randn(n_a, n_a)*0.01 # hidden to hidden
    Wya = np.random.randn(n_y, n_a)*0.01 # hidden to output
    b = np.zeros((n_a, 1)) # hidden bias
    by = np.zeros((n_y, 1)) # output bias
    
    parameters = {"Wax": Wax, "Waa": Waa, "Wya": Wya, "b": b,"by": by}
    
    return parameters

def rnn_step_forward(parameters, a_prev, x):
    
    Waa, Wax, Wya, by, b = parameters['Waa'], parameters['Wax'], parameters['Wya'], parameters['by'], parameters['b']
    a_next = np.tanh(np.dot(Wax, x) + np.dot(Waa, a_prev) + b) # hidden state
    p_t = softmax(np.dot(Wya, a_next) + by) # unnormalized log probabilities for next chars # probabilities for next chars 
    
    return a_next, p_t

def rnn_step_backward(dy, gradients, parameters, x, a, a_prev):
    
    gradients['dWya'] += np.dot(dy, a.T)
    gradients['dby'] += dy
    da = np.dot(parameters['Wya'].T, dy) + gradients['da_next'] # backprop into h
    daraw = (1 - a * a) * da # backprop through tanh nonlinearity
    gradients['db'] += daraw
    gradients['dWax'] += np.dot(daraw, x.T)
    gradients['dWaa'] += np.dot(daraw, a_prev.T)
    gradients['da_next'] = np.dot(parameters['Waa'].T, daraw)
    return gradients

def update_parameters(parameters, gradients, lr):

    parameters['Wax'] += -lr * gradients['dWax']
    parameters['Waa'] += -lr * gradients['dWaa']
    parameters['Wya'] += -lr * gradients['dWya']
    parameters['b']  += -lr * gradients['db']
    parameters['by']  += -lr * gradients['dby']
    return parameters

def rnn_forward(X, Y, a0, parameters, vocab_size):
    
    x, a, y_hat = {}, {}, {}
    
    a[-1] = np.copy(a0)
    

    loss = 0
    
    for t in range(len(X)):
        
       
        x[t] = np.zeros((vocab_size,1)) 
        if (X[t] != None):
            x[t][X[t]] = 1
        

        a[t], y_hat[t] = rnn_step_forward(parameters, a[t-1], x[t])
        
        loss -= np.log(y_hat[t][Y[t],0])
        
    cache = (y_hat, a, x)
        
    return loss, cache

def rnn_backward(X, Y, parameters, cache):
 
    gradients = {}

    (y_hat, a, x) = cache
    Waa, Wax, Wya, by, b = parameters['Waa'], parameters['Wax'], parameters['Wya'], parameters['by'], parameters['b']

    gradients['dWax'], gradients['dWaa'], gradients['dWya'] = np.zeros_like(Wax), np.zeros_like(Waa), np.zeros_like(Wya)
    gradients['db'], gradients['dby'] = np.zeros_like(b), np.zeros_like(by)
    gradients['da_next'] = np.zeros_like(a[0])
    
    
    for t in reversed(range(len(X))):
        dy = np.copy(y_hat[t])
        dy[Y[t]] -= 1
        gradients = rnn_step_backward(dy, gradients, parameters, x[t], a[t], a[t-1])
    
    
    return gradients, a



# In[2]:


data = open('English.txt', 'r').read()
data= data.lower()
chars = list(set(data))
data_size, vocab_size = len(data), len(chars)
#finding the unique characters in the string
print('There are %d total characters and %d unique characters in the data.' % (data_size, vocab_size))
#print(chars)


# In[3]:


#mapping charters to numbers and numbers to the characters
char_to_ix = { ch:i for i,ch in enumerate(sorted(chars)) }
ix_to_char = { i:ch for i,ch in enumerate(sorted(chars)) }
#print(ix_to_char)
#print(char_to_ix)


# In[4]:



def clip(gradients, maxValue):
    
    
    dWaa, dWax, dWya, db, dby = gradients['dWaa'], gradients['dWax'], gradients['dWya'], gradients['db'], gradients['dby']
    for gradient in [dWax, dWaa, dWya, db, dby]:
        np.clip(gradient,-maxValue , maxValue, out=gradient)
    gradients = {"dWaa": dWaa, "dWax": dWax, "dWya": dWya, "db": db, "dby": dby}
    return gradients


# In[5]:


np.random.seed(3)
dWax = np.random.randn(5,3)*10
dWaa = np.random.randn(5,5)*10
dWya = np.random.randn(2,5)*10
db = np.random.randn(5,1)*10
dby = np.random.randn(2,1)*10
gradients = {"dWax": dWax, "dWaa": dWaa, "dWya": dWya, "db": db, "dby": dby}


# In[6]:


def sample(parameters, char_to_ix, seed):
    Waa, Wax, Wya, by, b = parameters['Waa'], parameters['Wax'], parameters['Wya'], parameters['by'], parameters['b']
    vocab_size = by.shape[0]
    n_a = Waa.shape[1]
    x = np.zeros([vocab_size,1])
    a_prev = np.zeros([n_a,1])
    indices = []
    idx = -1 
    counter = 0
    newline_character = char_to_ix['\n']
    
    while (idx != newline_character and counter != 50):
        a = np.tanh(np.dot(Wax,x)+np.dot(Waa,a_prev)+b)
        z = np.dot(Wya,a)+by
        y = softmax(z)
        np.random.seed(counter+seed) 
        idx = np.random.choice(range(len(y)),p=y.ravel())
        indices.append(idx)
        x = np.zeros((vocab_size,1))
        x[idx] = 1
        a_prev = a
        seed += 1
        counter +=1
    if (counter == 50):
        indices.append(char_to_ix['\n'])
    
    return indices


# In[7]:


np.random.seed(2)
_, n_a = 20, 100
Wax, Waa, Wya = np.random.randn(n_a, vocab_size), np.random.randn(n_a, n_a), np.random.randn(vocab_size, n_a)
b, by = np.random.randn(n_a, 1), np.random.randn(vocab_size, 1)
parameters = {"Wax": Wax, "Waa": Waa, "Wya": Wya, "b": b, "by": by}
indices = sample(parameters, char_to_ix, 0)


# In[8]:


def optimize(X, Y, a_prev, parameters, learning_rate = 0.01):
    
    
    loss, cache = rnn_forward(X, Y, a_prev, parameters, vocab_size)
  
    gradients, a = rnn_backward(X, Y, parameters, cache)

    gradients = clip(gradients, 5)
    
    parameters = update_parameters(parameters, gradients, learning_rate)

    
    return loss, gradients, a[len(X)-1]


# In[9]:


np.random.seed(1)
vocab_size, n_a = vocab_size, 100
a_prev = np.random.randn(n_a, 1)
Wax, Waa, Wya = np.random.randn(n_a, vocab_size), np.random.randn(n_a, n_a), np.random.randn(vocab_size, n_a)
b, by = np.random.randn(n_a, 1), np.random.randn(vocab_size, 1)
parameters = {"Wax": Wax, "Waa": Waa, "Wya": Wya, "b": b, "by": by}
X = [12,3,5,11,22,3]
Y = [4,14,11,14,18, 21]

loss, gradients, a_last = optimize(X, Y, a_prev, parameters, learning_rate = 0.01)


# In[10]:


def model(data, ix_to_char, char_to_ix, vocab_size, num_iterations = 100000, n_a = 50, dino_names = 7):

    n_x, n_y = vocab_size, vocab_size

    parameters = initialize_parameters(n_a, n_x, n_y)
    

    loss = get_initial_loss(vocab_size, dino_names)
    

    with open("English.txt") as f:
        examples = f.readlines()
    examples = [x.lower().strip() for x in examples]
    

    np.random.seed(0)
    np.random.shuffle(examples)
    

    a_prev = np.zeros((n_a, 1))

    for j in range(num_iterations):
        

        index = j % len(examples)
        X = [None] + [char_to_ix[ch] for ch in examples[index]] 
        Y = X[1:] + [char_to_ix["\n"]]
        
        

        curr_loss, gradients, a_prev = optimize(X,Y,a_prev,parameters,learning_rate=0.01)

        loss = smooth(loss, curr_loss)

        if j % 2000 == 0:
            
            print('Iteration executed: %d, Loss: %f' % (j, loss) + '\n')
            

            seed = 0
            for name in range(dino_names):
                

                sampled_indices = sample(parameters, char_to_ix, seed)
                print_sample(sampled_indices, ix_to_char)
                
                seed += 1  
      
            print('\n')
        
    return parameters


# In[11]:


parameters = model(data, ix_to_char, char_to_ix,vocab_size)


# In[ ]:




