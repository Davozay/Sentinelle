import torch
import torch.nn as nn
import torch.optim as optim
# from torchtext.data.utils import get_tokenizer
import pickle


texts = [
    "verify your account",
    "click the link",
    "update your password",
    "your account has been suspended",
    "hello how are you",
    "i love you",
    "i am a man",
    "good morning",
    "congratulations you won",
    "urgent update needed",
    "please confirm your identity", 
    "who made you",
    "how does this work",
    "you are a scammer",
    "this message looks suspicious",
    "reset your password immediately",
    "limited time offer just for you",
    "hi there can i help you",
    "i need your login details",
    "my account was hacked",
    "click here to claim your prize",
    "do not share this code with anyone",
    "ht tp",
    "h t t p",
    "h ttp",
    ". com",
    ". org",
    ". ng",
    "htt p",
    "http s"
]


def tokenizer(text):
    return text.lower().split()


# Build vocab
tokens = [word for sentence in texts for word in tokenizer(sentence)]
vocab = {word: idx+1 for idx, word in enumerate(set(tokens))}  # idx+1 so padding = 0
vocab['<PAD>'] = 0
inv_vocab = {idx: word for word, idx in vocab.items()}

# Save vocab for later
with open("pytorch_vocab.pkl", "wb") as f:
    pickle.dump(vocab, f)
with open("pytorch_inv_vocab.pkl", "wb") as f:
    pickle.dump(inv_vocab, f)

# Build sequences
sequences = []
for sentence in texts:
    words = tokenizer(sentence)
    for i in range(1, len(words)):
        input_seq = [vocab[w] for w in words[:i]]
        target = vocab[words[i]]
        sequences.append((input_seq, target))

# Pad sequences
def pad(seq, length):
    return [0]*(length - len(seq)) + seq

max_len = max(len(seq[0]) for seq in sequences)
X = torch.tensor([pad(seq, max_len) for seq, _ in sequences])
y = torch.tensor([target for _, target in sequences])

# Model
class RNNPredictor(nn.Module):
    def __init__(self, vocab_size, embed_size, hidden_size):
        super(RNNPredictor, self).__init__()
        self.embed = nn.Embedding(vocab_size, embed_size, padding_idx=0)
        self.rnn = nn.LSTM(embed_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)

    def forward(self, x):
        x = self.embed(x)
        _, (h, _) = self.rnn(x)
        out = self.fc(h[-1])
        return out

model = RNNPredictor(len(vocab), 64, 128)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Training
for epoch in range(120):
    optimizer.zero_grad()
    output = model(X)
    loss = criterion(output, y)
    loss.backward()
    optimizer.step()
    if epoch % 10 == 0:
        print(f"Epoch {epoch}: Loss = {loss.item():.4f}")

# Savedd model
torch.save(model.state_dict(), "pytorch_rnn_model.pth")
print("✅ Model and vocab saved.")
