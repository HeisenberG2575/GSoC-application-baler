import torch
from torch import nn
from torch.nn import functional as F

class VarAutoEnc(nn.Module):
    def __init__(self, device, n_features, z_dim):
        super(VarAutoEnc, self).__init__()
        self.device = device
        self.enc_nn = nn.Sequential(
            nn.Linear(n_features, 256, dtype=torch.float64,device=device),
            nn.LeakyReLU(),
            nn.BatchNorm1d(256, dtype=torch.float64,device=device),
            nn.Linear(256, 128, dtype=torch.float64,device=device),
            nn.LeakyReLU(),
            nn.BatchNorm1d(128, dtype=torch.float64,device=device),
            nn.Linear(128, 64, dtype=torch.float64,device=device),
            nn.LeakyReLU(),
            nn.BatchNorm1d(64, dtype=torch.float64,device=device),
            # nn.Linear(64, z_dim, dtype=torch.float64,device=device),
            # nn.LeakyReLU(),
            # nn.BatchNorm1d(z_dim, dtype=torch.float64,device=device),
        )
        self.mu_layer = nn.Linear(64,z_dim,dtype=torch.float64,device=device)
        self.logvar_layer = nn.Linear(64,z_dim,dtype=torch.float64,device=device)
        self.dec_nn = nn.Sequential(
            nn.Linear(z_dim, 64, dtype=torch.float64,device=device),
            nn.LeakyReLU(),
            nn.Linear(64, 128, dtype=torch.float64,device=device),
            nn.LeakyReLU(),
            nn.Linear(128, 256, dtype=torch.float64,device=device),
            nn.LeakyReLU(),
            nn.Linear(256, n_features, dtype=torch.float64,device=device),
            nn.ReLU(),
        )

        self.n_features = n_features
        self.z_dim = z_dim

    def reparameterise(self, mu, logvar):
        if self.training:
            std = logvar.mul(0.5).exp_()
            eps = std.data.new(std.size()).normal_()
            return eps.mul(std).add_(mu)
        else:
            return mu

    def encode(self, x):
        pre_final = self.enc_nn(x)
        mu = self.mu_layer(pre_final)
        logvar = self.logvar_layer(pre_final)
        return mu, logvar        

    def decode(self, z):
        out = self.dec_nn(z)
        return out

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterise(mu, logvar)
        x_hat = self.decode(z)
        return x_hat, mu, logvar


class george_SAE(nn.Module):
    def __init__(self, device, n_features, z_dim, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.device = device

        # encoder
        self.en1 = nn.Linear(n_features, 256, dtype=torch.float64, device=device)
        self.en2 = nn.Linear(256, 128, dtype=torch.float64, device=device)
        self.en3 = nn.Linear(128, 64, dtype=torch.float64, device=device)
        self.en4 = nn.Linear(64, z_dim, dtype=torch.float64, device=device)
        # decoder
        self.de1 = nn.Linear(z_dim, 64, dtype=torch.float64, device=device)
        self.de2 = nn.Linear(64, 128, dtype=torch.float64, device=device)
        self.de3 = nn.Linear(128, 256, dtype=torch.float64, device=device)
        self.de4 = nn.Linear(256, n_features, dtype=torch.float64, device=device)

        self.n_features = n_features
        self.z_dim = z_dim

    def encode(self, x):
        h1 = F.leaky_relu(self.en1(x))
        h2 = F.leaky_relu(self.en2(h1))
        h3 = F.leaky_relu(self.en3(h2))
        return self.en4(h3)

    def decode(self, z):
        h4 = F.leaky_relu(self.de1(z))
        h5 = F.leaky_relu(self.de2(h4))
        h6 = F.leaky_relu(self.de3(h5))
        out = self.de4(h6)
        return out

    def forward(self, x):
        z = self.encode(x)
        return self.decode(z)


class george_SAE_BN(nn.Module):
    def __init__(self, device, n_features, z_dim):
        super(george_SAE_BN, self).__init__()
        self.device = device
        # encoder
        self.enc_nn = nn.Sequential(
            nn.Linear(n_features, 200, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.5),
            nn.LeakyReLU(),
            nn.BatchNorm1d(200, dtype=torch.float64,device=device),
            nn.Linear(200, 100, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.4),
            nn.LeakyReLU(),
            nn.BatchNorm1d(100, dtype=torch.float64,device=device),
            nn.Linear(100, 50, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.3),
            nn.LeakyReLU(),
            nn.BatchNorm1d(50, dtype=torch.float64,device=device),
            nn.Linear(50, z_dim, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.2),
            nn.LeakyReLU(),
            nn.BatchNorm1d(z_dim, dtype=torch.float64,device=device),
        )

        # decoder
        self.dec_nn = nn.Sequential(
            nn.Linear(z_dim, 50, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.2),
            nn.LeakyReLU(),
            # nn.BatchNorm1d(50,dtype=torch.float64),
            nn.Linear(50, 100, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.3),
            nn.LeakyReLU(),
            # nn.BatchNorm1d(100,dtype=torch.float64),
            nn.Linear(100, 200, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.4),
            nn.LeakyReLU(),
            # nn.BatchNorm1d(200,dtype=torch.float64),
            nn.Linear(200, n_features, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.5),
            # nn.BatchNorm1d(n_features,dtype=torch.float64),
            nn.ReLU(),
        )

        self.n_features = n_features
        self.z_dim = z_dim

    def encode(self, x):
        out = self.enc_nn(x)
        return out

    def decode(self, z):
        out = self.dec_nn(z)
        return out

    def forward(self, x):
        z = self.encode(x)
        return self.decode(z)


class george_SAE_Dropout_BN(nn.Module):
    def __init__(self, device, n_features, z_dim):
        super(george_SAE_Dropout_BN, self).__init__()
        self.device = device
        print(device)
        # encoder
        self.enc_nn = nn.Sequential(
            nn.Linear(n_features, 200, dtype=torch.float64,device=device),
            nn.Dropout(p=0.3),
            nn.LeakyReLU(),
            # nn.BatchNorm1d(200,dtype=torch.float64),
            nn.Linear(200, 100, dtype=torch.float64,device=device),
            nn.Dropout(p=0.3),
            nn.LeakyReLU(),
            # nn.BatchNorm1d(100,dtype=torch.float64),
            nn.Linear(100, 50, dtype=torch.float64,device=device),
            nn.Dropout(p=0.2),
            nn.LeakyReLU(),
            # nn.BatchNorm1d(50,dtype=torch.float64),
            nn.Linear(50, z_dim, dtype=torch.float64,device=device),
            nn.Dropout(p=0.1),
            nn.LeakyReLU(),
            # nn.BatchNorm1d(z_dim,dtype=torch.float64)
        )

        # decoder
        self.dec_nn = nn.Sequential(
            nn.Linear(z_dim, 50, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.2),
            nn.LeakyReLU(),
            nn.BatchNorm1d(50, dtype=torch.float64,device=device),
            nn.Linear(50, 100, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.3),
            nn.LeakyReLU(),
            nn.BatchNorm1d(100, dtype=torch.float64,device=device),
            nn.Linear(100, 200, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.4),
            nn.LeakyReLU(),
            nn.BatchNorm1d(200, dtype=torch.float64,device=device),
            nn.Linear(200, n_features, dtype=torch.float64,device=device),
            # nn.Dropout(p=0.5),
            nn.BatchNorm1d(n_features, dtype=torch.float64,device=device),
            nn.ReLU(),
        )

        self.n_features = n_features
        self.z_dim = z_dim

    def encode(self, x):
        out = self.enc_nn(x)
        return out

    def decode(self, z):
        out = self.dec_nn(z)
        return out

    def forward(self, x):
        z = self.encode(x)
        return self.decode(z)


class george_SAE_Dropout(nn.Module):
    def __init__(self, device, n_features, z_dim):
        super(george_SAE_Dropout, self).__init__()
        self.device=device
        # encoder
        self.enc_nn = nn.Sequential(
            nn.Linear(n_features, 200, dtype=torch.float64,device=device),
            nn.Dropout(p=0.3),
            nn.LeakyReLU(),
            nn.Linear(200, 100, dtype=torch.float64,device=device),
            nn.Dropout(p=0.3),
            nn.LeakyReLU(),
            nn.Linear(100, 50, dtype=torch.float64,device=device),
            nn.Dropout(p=0.2),
            nn.LeakyReLU(),
            nn.Linear(50, z_dim, dtype=torch.float64,device=device),
            nn.Dropout(p=0.1),
            nn.LeakyReLU(),
        )

        # decoder
        self.dec_nn = nn.Sequential(
            nn.Linear(z_dim, 50, dtype=torch.float64,device=device),
            nn.Dropout(p=0.1),
            nn.LeakyReLU(),
            nn.Linear(50, 100, dtype=torch.float64,device=device),
            nn.Dropout(p=0.2),
            nn.LeakyReLU(),
            nn.Linear(100, 200, dtype=torch.float64,device=device),
            nn.Dropout(p=0.3),
            nn.LeakyReLU(),
            nn.Linear(200, n_features, dtype=torch.float64,device=device),
            nn.Dropout(p=0.3),
            nn.ReLU(),
        )

        self.n_features = n_features
        self.z_dim = z_dim

    def encode(self, x):
        out = self.enc_nn(x)
        return out

    def decode(self, z):
        out = self.dec_nn(z)
        return out

    def forward(self, x):
        x = self.encode(x)
        return self.decode(x)

    def loss(self, model_children, true_data, reconstructed_data, reg_param):
        mse = nn.MSELoss()
        mse_loss = mse(reconstructed_data, true_data)
        l1_loss = 0
        values = true_data
        for i in range(len(model_children)):
            values = F.relu((model_children[i](values)))
            l1_loss += torch.mean(torch.abs(values))
        loss = mse_loss + reg_param * l1_loss
        return loss
