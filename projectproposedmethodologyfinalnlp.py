# -*- coding: utf-8 -*-
"""projectproposedmethodologyfinalnlp.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YNXj5t-MzzNoKQ13u89isWagISYLuwz2
"""

#



import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.optim import rmsprop
import sklearn.metrics as metrics
from tensorflow.keras import activations
from tensorflow.keras import layers
from sklearn.metrics import roc_auc_score
#from mxnet import autograd, np
#from d2l import mxnet as d2l
import torch.nn.functional as F
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
from collections import Counter
import string
import re
import seaborn as sns
from tqdm import tqdm
import matplotlib.pyplot as plt
from torch.utils.data import TensorDataset, DataLoader
from sklearn.model_selection import train_test_split
from google.colab import drive
drive.mount('/content/drive')
is_cuda = torch.cuda.is_available()
if is_cuda:
  device = torch.device("cuda")
  print("GPU is available")
else:
      device = torch.device("cpu")
      print("GPU not available, CPU used")
base_csv = '/content/drive/MyDrive/IMDB Dataset.csv'
df = pd.read_csv(base_csv)
df.head()
X,y = df['review'].values,df['sentiment'].values
#x_train,x_test,y_train,y_test = train_test_split(X,y,stratify=y)
#This line split data in 80% 20% ratio
x_train,x_test,y_train,y_test = train_test_split(X,y,test_size=0.20,stratify=y)
print(f'shape of train data is  {x_train.shape}')
print(f'shape of test data is {x_test.shape}')
dd = pd.Series(y_train).value_counts()
sns.barplot(x=np.array(['negative','positive']),y=dd.values)
plt.show()
def preprocess_string(s):
  #remove all non word characters
  s = re.sub(r"[^\w\s]",'',s)
  #replace all runs of whitespaces with no space
  s = re.sub(r"\s+",'', s)
  #replace digits wiyh no space
  s = re.sub(r"\d",'',s)
  return s
#end of the def block
def tockenize(x_train,y_train,x_val,y_val):
  word_list = []
  stop_words = set(stopwords.words('english'))
  for sent in x_train:
    for word in sent.lower().split():
      word = preprocess_string(word)
      if word not in stop_words and word !='':
        word_list.append(word)
  corpus = Counter(word_list)
  #sorting on the basis of most common words
  corpus_ = sorted(corpus,key=corpus.get,reverse=True)[:3000]
  #creating dictionary
  onehot_dict = {w:i+1 for i,w in enumerate(corpus_)}
  #tockenize
  final_list_train,final_list_test =  [],[]
  for sent in x_train:
    final_list_train.append([onehot_dict[preprocess_string(word)]
     for word in sent.lower().split()
      if preprocess_string(word) in onehot_dict.keys()])
  for sent in x_val:
    final_list_test.append([onehot_dict[preprocess_string(word)]
      for word in sent.lower().split()
        if preprocess_string(word) in onehot_dict.keys()])
  encoded_train = [1 if label == 'positive' else 0 for label in y_train]
  encoded_test = [1 if label =='positive' else 0 for label in y_val]
 # (pd.Series(nltk.ngrams(word, 3)).value_counts())
 # bigrams_series.sort_values().plot.barh(color='blue', width=0.9, figsize(10,8))
  return np.array(final_list_train), np.array(encoded_train),np.array(final_list_test),np.array(encoded_test),onehot_dict
  
#end of the def block
x_train,y_train,x_test,y_test,vocab = tockenize(x_train,y_train,x_test,y_test)
print(f'Length of vocabulary is {len(vocab)}')
rev_len = [len(i) for i in x_train]
pd.Series(rev_len).hist()
#pd.Series(nltk.ngrams(word, 3)).value_counts()
plt.show()
pd.Series(rev_len).describe()
def padding_(sentences, seq_len):
  features = np.zeros((len(sentences), seq_len),dtype=int)
  for ii, review in enumerate(sentences):
    if len(review) != 0:
      features[ii, -len(review):] = np.array(review)[:seq_len]
  return features
  #end of the def block
x_train_pad = padding_(x_train,500)
x_test_pad = padding_(x_test,500)
# create tensor datasets
train_data = TensorDataset(torch.from_numpy(x_train_pad), torch.from_numpy(y_train))
valid_data = TensorDataset(torch.from_numpy(x_test_pad), torch.from_numpy(y_test))
#dataloaders
batch_size = 50

train_loader = DataLoader(train_data, shuffle=True, batch_size=batch_size)
valid_loader = DataLoader(valid_data, shuffle=True, batch_size=batch_size)

dataiter = iter(train_loader)
sample_x, sample_y = dataiter.next()

print('sample input size:', sample_x.size())
print('sample input: \n', sample_x)
print('sample input: \n', sample_y)

from google.colab import drive
drive.mount('/content/drive')

class SentimentRNN(nn.Module):
   def __init__(self,no_layers,vocab_size,hidden_dim,embedding_dim,drop_prob=0.3):
        super(SentimentRNN,self).__init__()
 
        self.output_dim = output_dim
        self.hidden_dim = hidden_dim
 
        self.no_layers = no_layers
        self.vocab_size = vocab_size
    
        # embedding and LSTM layers
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        
        #lstm
        self.lstm = nn.LSTM(input_size=embedding_dim,hidden_size=self.hidden_dim,
                           num_layers=no_layers, batch_first=True)
        
        
        # dropout layer
        self.dropout = nn.Dropout(0.3)
     #   self.fc = nn.Linear(self.hidden_dim, output_dim)
    
      
         # linear and sigmoid layer
        self.fc = nn.Linear(self.hidden_dim, output_dim)
       
       # Exponential Linear Unit which helps to improve accuracy better than base code activation function sigmoid. its parameters are alpha and inplace.
        self.ELU = nn.ELU(alpha=1.04, inplace=False) 
        
        
      


        

        
        
        
   def forward(self,x,hidden):
        batch_size = x.size(0)
        # embeddings and lstm_out
        embeds = self.embedding(x)  # shape: B x S x Feature   since batch = True
        #print(embeds.shape)  #[50, 500, 1000]
        lstm_out, hidden = self.lstm(embeds, hidden)
        
        lstm_out = lstm_out.contiguous().view(-1, self.hidden_dim) 
        
        # dropout and fully connected layer
        out = self.dropout(lstm_out)
        out = self.fc(out)


        
        # ELU activation function instead function
        
        elu_out = self.ELU(out)
      
        # reshape to be batch_size first
        #sig_out = sig_out.view(batch_size, -1)
        #sig_out = sig_out[:, -1] 
        #relu_out = relu_out.view(batch_size, -1)
        #relu_out = relu_out[:, -1]
        # this change is for ELU 
        elu_out = elu_out.view(batch_size, -1)
        elu_out = elu_out[:, -1]

        # return last sigmoid output and hidden state
        #return sig_out, hidden
        #return relu_out, hidden
        return elu_out, hidden

        
        
   def init_hidden(self, batch_size):
        ''' Initializes hidden state '''
        # Create two new tensors with sizes n_layers x batch_size x hidden_dim,
        # initialized to zero, for hidden state and cell state of LSTM
        h0 = torch.zeros((self.no_layers,batch_size,self.hidden_dim)).to(device)
        c0 = torch.zeros((self.no_layers,batch_size,self.hidden_dim)).to(device)
        hidden = (h0,c0)
        return hidden

#class NgramModel(nn.Module):
 # def __init__(self, vocab_size, context)

no_layers = 2
vocab_size = len(vocab) + 1 #extra 1 for padding
embedding_dim = 64
output_dim = 1
hidden_dim = 256


model = SentimentRNN(no_layers,vocab_size,hidden_dim,embedding_dim,drop_prob=0.3)

#moving to gpu
model.to(device)

print(model)

#loss and optimization functions
lr=0.001

#criterion = nn.BCELoss()
#criterion = nn.L1Loss()
criterion = nn.MSELoss()
#optimizer = torch.optim.Adam(model.parameters(), lr=lr)
#optimizer = torch.optim.Adadelta(model.parameters(), lr=lr, rho=0.9, eps=1e-06, weight_decay=0)
#optimizer = torch.optim.Adam(model.parameters(), lr=lr)
#optimizer = torch.optim.RMSprop(model.parameters(),)
#optimizer = torch.optim.Adadelta(model.parameters(), lr=lr)
#optimizer = torch.optim.Adamax(model.parameters(), lr=lr, betas=(0.9, 0.999), eps=1e-08, weight_decay=0)
#optimizer = torch.optim.SGD(model.parameters(), lr=lr)
#optimizer = torch.optim.AdamW(model.parameters(), lr=lr, betas=(0.9, 0.999), eps=1e-08, weight_decay=0, amsgrad=False)
#RMSProp optimization function gives better accuracy than Adam optimizer.
optimizer = torch.optim.RMSprop(model.parameters(), lr=lr, alpha=0.99, eps=1e-08, weight_decay=0, momentum=0, centered=False)
#optimizer = torch.optim.Rprop(model.parameters(), lr=lr, etas=(0.5, 1.2), step_sizes=(1e-06, 50))
#low output
#optimizer = torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)
#optimizer = torch.optim.Adadelta(model.parameters(), lr=lr, rho=0.9, eps=1e-06)
#optimizer = torch.optim.RMSprop(model.parameters(), lr=lr, alpha=0.99)


def acc(pred,label):
    pred = torch.round(pred.squeeze())
    return torch.sum(pred == label.squeeze()).item()



clip = 5
epochs = 5
valid_loss_min = np.Inf
# train for some number of epochs
epoch_tr_loss,epoch_vl_loss = [],[]
epoch_tr_acc,epoch_vl_acc = [],[]

for epoch in range(epochs):
    train_losses = []
    train_acc = 0.0
    model.train()
    # initialize hidden state 
    h = model.init_hidden(batch_size)
    for inputs, labels in train_loader:
        
        inputs, labels = inputs.to(device), labels.to(device)   
        # Creating new variables for the hidden state, otherwise
        # we'd backprop through the entire training history
        h = tuple([each.data for each in h])
        
        model.zero_grad()

        if(len(inputs)==batch_size):
          output,h = model(inputs,h)
         # calculate the loss and perform backprop
          loss = criterion(output.squeeze(), labels.float())
          loss.backward()
          train_losses.append(loss.item())
        # calculating accuracy
          accuracy = acc(output,labels)
          train_acc += accuracy
        #`clip_grad_norm` helps prevent the exploding gradient problem in RNNs / LSTMs.
        nn.utils.clip_grad_norm_(model.parameters(), clip)
        optimizer.step()
 
    
        
    val_h = model.init_hidden(batch_size)
    val_losses = []
    val_acc = 0.0
    model.eval()
    for inputs, labels in valid_loader:
            val_h = tuple([each.data for each in val_h])
            inputs, labels = inputs.to(device), labels.to(device)

            output, val_h = model(inputs, val_h)
            val_loss = criterion(output.squeeze(), labels.float())

            val_losses.append(val_loss.item())
            
            accuracy = acc(output,labels)
            val_acc += accuracy
            
    epoch_train_loss = np.mean(train_losses)
    epoch_val_loss = np.mean(val_losses)
    epoch_train_acc = train_acc/len(train_loader.dataset)
    epoch_val_acc = val_acc/len(valid_loader.dataset)
    epoch_tr_loss.append(epoch_train_loss)
    epoch_vl_loss.append(epoch_val_loss)
    epoch_tr_acc.append(epoch_train_acc)
    epoch_vl_acc.append(epoch_val_acc)
    print(f'Epoch {epoch+1}')   
    print(f'train_loss : {epoch_train_loss} val_loss : {epoch_val_loss}')
    print(f'train_accuracy : {epoch_train_acc*100} val_accuracy : {epoch_val_acc*100}')
    if epoch_val_loss <= valid_loss_min:
      torch.save(model.state_dict(), '/content/drive/MyDrive/Colab Notebooks/torch_save.pt')
      print('Validation loss decreased ({:.6f} --> {:.6f}).  Saving model ...'.format(valid_loss_min,epoch_val_loss))
      valid_loss_min = epoch_val_loss
    print(25*'==')

fig = plt.figure(figsize = (20, 6))
plt.subplot(1, 2, 1)
plt.plot(epoch_tr_acc, label='Train Acc')
plt.plot(epoch_vl_acc, label='Validation Acc')
plt.title("Accuracy")
plt.legend()
plt.grid()
plt.subplot(1, 2, 2)
plt.plot(epoch_tr_loss, label='Train loss')
plt.plot(epoch_vl_loss, label='Validation loss')
plt.title("Loss")
plt.legend()
plt.grid()

plt.show()

import sklearn.metrics as metrics
from sklearn.metrics import roc_auc_score
def plot_auc_roc(model,valid_loader, version='title', threshold=0.5):
    y_pred = []
    y_true = []
    val_h = model.init_hidden(batch_size)
    model.eval()
    with torch.no_grad():
        for inputs, labels in valid_loader :
            
            val_h = tuple([each.data for each in val_h])

            inputs, labels = inputs.to(device), labels.to(device)

            output, val_h = model(inputs, val_h)

            output = (output > threshold).int()
            y_pred.extend(output.tolist())
            y_true.extend(labels.tolist())
    
    print('AUC ROC :')
    fpr, tpr, threshold = metrics.roc_curve(y_true, y_pred)
    roc_auc = metrics.auc(fpr, tpr)
    
    print(roc_auc)
    print('----------------------------------------------------------')
    
    plt.title('Receiver Operating Characteristic')
    plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % roc_auc)
    plt.legend(loc = 'lower right')
    plt.plot([0, 1], [0, 1],'r--')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.ylabel('True Positive Rate')
    plt.xlabel('False Positive Rate')
    plt.show()
plot_auc_roc(model, valid_loader)

def predict_text(text):
      word_seq = np.array([vocab[preprocess_string(word)] for word in text.split()
         if preprocess_string(word) in vocab.keys()])
      word_seq = np.expand_dims(word_seq,axis=0)
      pad = torch.from_numpy(padding_(word_seq,500))
      inputs = pad.to(device)
      batch_size = 1
      h = model.init_hidden(batch_size)
      h = tuple([each.data for each in h])
      output, h = model(inputs, h)
      return(output.item())

index = 30
print(df['review'][index])
print('='*70)
print(f'Actual sentiment is : {df["sentiment"][index]}')
print('='*70)
pro = predict_text(df['review'][index])
status = "positive" if pro>0.5 else "negative"
pro = (1 - pro) if status == "negative" else pro
print(f'predicted sentiment is {status} with a probability of {pro}')