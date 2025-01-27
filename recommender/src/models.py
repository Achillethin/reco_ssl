import numpy as np
import torch
import torch.nn as nn
from scipy.stats import truncnorm

from kernels import HMC_our, HMC_vanilla, Reverse_kernel


def truncated_normal(size, std=1):
    values = truncnorm.rvs(-2. * std, 2. * std, size=size)
    return values


def make_linear_network(dims, encoder=False):
    layer_list = nn.ModuleList([])
    for i in range(len(dims) - 1):
        if i == len(dims) - 2 and encoder:
            layer_list.append(nn.Linear(dims[i], 2 * dims[i + 1]))
        else:
            layer_list.append(nn.Linear(dims[i], dims[i + 1]))
        layer_list[-1].weight = nn.init.xavier_uniform_(layer_list[-1].weight)
        layer_list[-1].bias = nn.Parameter(
            torch.tensor(truncated_normal(layer_list[-1].bias.shape, 0.001), dtype=torch.float32))
        layer_list.append(nn.Tanh())
    layer_list = layer_list[:-1]
    model = nn.Sequential(*layer_list)
    return model


class MultiDAE(nn.Module):
    def __init__(self, p_dims, q_dims=None, args=None):
        super(MultiDAE, self).__init__()
        self.p_dims = p_dims
        if q_dims is None:
            self.q_dims = p_dims[::-1]
        else:
            assert q_dims[0] == p_dims[-1], "Input and output dimension must equal each other for autoencoders."
            assert q_dims[-1] == p_dims[0], "Latent dimension for p- and q-network mismatches."
            self.q_dims = q_dims
        dims = self.q_dims + self.p_dims[1:]

        self.model = make_linear_network(dims)
        self.dropout = nn.Dropout()
        print(self.model)

    def forward(self, x_initial, is_training_ph=1.):
        l2 = torch.sum(x_initial ** 2, 1)[..., None]
        x_normed = x_initial / torch.sqrt(torch.max(l2, torch.ones_like(l2) * 1e-12))
        x = self.dropout(x_normed)
        logits = self.model(x)
        return logits, 0.


class MultiVAE(nn.Module):
    def __init__(self, p_dims, q_dims=None, args=None):
        super(MultiVAE, self).__init__()

        self.p_dims = p_dims
        if q_dims is None:
            self.q_dims = p_dims[::-1]
            q_dims = self.q_dims
        else:
            assert q_dims[0] == p_dims[-1], "Input and output dimension must equal each other for autoencoders."
            assert q_dims[-1] == p_dims[0], "Latent dimension for p- and q-network mismatches."
            self.q_dims = q_dims

        self.encoder = make_linear_network(q_dims, encoder=True)
        print(self.encoder)

        self.decoder = make_linear_network(p_dims)
        print(self.decoder)

        self.dropout = nn.Dropout()

        device_zero = torch.tensor(0., dtype=torch.float32, device=args.device)
        device_one = torch.tensor(1., dtype=torch.float32, device=args.device)
        self.std_normal = torch.distributions.Normal(loc=device_zero, scale=device_one)

    def forward(self, x_initial, is_training_ph=1.):
        l2 = torch.sum(x_initial ** 2, 1)[..., None]
        x_normed = x_initial / torch.sqrt(torch.max(l2, torch.ones_like(l2) * 1e-12))
        x = self.dropout(x_normed)

        enc_out = self.encoder(x)
        mu, logvar = enc_out[:, :self.q_dims[-1]], enc_out[:, self.q_dims[-1]:]
        std = torch.exp(0.5 * logvar)

        u = self.std_normal.sample(mu.shape)
        z = mu + is_training_ph * u * std

        KL = torch.mean(torch.sum(0.5 * (-logvar + torch.exp(logvar) + mu ** 2 - 1), dim=1))
        # sum_log_sigma = torch.log(std).sum(1)
        # log_q = self.std_normal.log_prob(u).sum(1) - sum_log_sigma
        # log_prior = self.std_normal.log_prob(z).sum(1)
        # KL = torch.mean(log_q - log_prior)

        logits = self.decoder(z)

        return logits, KL


class Target(nn.Module):
    def __init__(self, dec):
        super(Target, self).__init__()
        self.decoder = dec

    def get_logdensity(self, x, z, prior=None, args=None, prior_flow=None):
        """
        The method returns target logdensity
        Input:
        x - datapoint
        z - latent vaiable
        Output:
        log_density - log p(x, z)
        """
        logits = self.decoder(z)
        log_softmax_var = nn.LogSoftmax(dim=-1)(logits)
        log_density = torch.mean(torch.sum(log_softmax_var * x, dim=1))
        return log_density


class Multi_our_VAE(nn.Module):
    def __init__(self, p_dims, q_dims=None, args=None):
        super(Multi_our_VAE, self).__init__()

        self.p_dims = p_dims
        if q_dims is None:
            self.q_dims = p_dims[::-1]
            q_dims = self.q_dims
        else:
            assert q_dims[0] == p_dims[-1], "Input and output dimension must equal each other for autoencoders."
            assert q_dims[-1] == p_dims[0], "Latent dimension for p- and q-network mismatches."
            self.q_dims = q_dims

        ## Define encoder
        self.encoder = make_linear_network(q_dims, encoder=True)
        print(self.encoder)

        ## Define target(decoder)
        decoder = make_linear_network(p_dims)
        print(decoder)
        self.target = Target(dec=decoder)

        ## Define transitions
        self.K = args.K
        self.transitions = nn.ModuleList([HMC_our(kwargs=args).to(args.device) for _ in range(args['K'])])

        ## Define reverse kernel (if it is needed)
        self.learnable_reverse = args.learnable_reverse
        if args.learnable_reverse:
            self.reverse_kernel = Reverse_kernel(kwargs=args).to(args.device)

        self.dropout = nn.Dropout()

        device_zero = torch.tensor(0., dtype=torch.float32, device=args.device)
        device_one = torch.tensor(1., dtype=torch.float32, device=args.device)
        self.std_normal = torch.distributions.Normal(loc=device_zero, scale=device_one)
        self.torch_log_2 = torch.tensor(np.log(2), device=args.device, dtype=args.torchType)

    def forward(self, x_initial, is_training_ph=1.):
        l2 = torch.sum(x_initial ** 2, 1)[..., None]
        x_normed = x_initial / torch.sqrt(torch.max(l2, torch.ones_like(l2) * 1e-12))
        x = self.dropout(x_normed)

        enc_out = self.encoder(x)
        mu, logvar = enc_out[:, :self.q_dims[-1]], enc_out[:, self.q_dims[-1]:]
        std = torch.exp(0.5 * logvar)
        sum_log_sigma = torch.log(std).sum(1)
        sum_log_alpha = torch.zeros_like(mu[:, 0])
        sum_log_jacobian = torch.zeros_like(mu[:, 0])

        u = self.std_normal.sample(mu.shape)
        z = mu + is_training_ph * u * std

        p_old = self.std_normal.sample(z.shape)
        p_ = p_old.detach()

        if self.learnable_reverse:
            all_directions = torch.tensor([], device=x.device)
        else:
            all_directions = None

        for i in range(self.K):
            cond_vector = self.std_normal.sample(p_.shape)
            z, p_, log_jac, current_log_alphas, directions, _ = self.transitions[i].make_transition(q_old=z, x=x,
                                                                                                    p_old=p_,
                                                                                                    k=cond_vector,
                                                                                                    target_distr=self.target)
            sum_log_alpha = sum_log_alpha + current_log_alphas
            sum_log_jacobian = sum_log_jacobian + log_jac
            if self.learnable_reverse:
                all_directions = torch.cat([all_directions, directions.view(-1, 1)], dim=1)

        ## logdensity of Variational family
        log_q = self.std_normal.log_prob(u).sum(1) + self.std_normal.log_prob(p_old).sum(
            1) - sum_log_jacobian - sum_log_sigma + sum_log_alpha

        ## logdensity of prior
        log_priors = self.std_normal.log_prob(z).sum(1) + self.std_normal.log_prob(p_).sum(1)

        ## logits
        logits = self.target.decoder(z)

        ## logdensity of reverse (if needed)
        if self.learnable_reverse:
            log_r = self.reverse_kernel(z_fin=z.detach(), h=mu.detach(), a=all_directions)
        else:
            log_r = -self.K * self.torch_log_2

        return logits, log_q, log_priors, log_r, sum_log_alpha


class MultiHoffmanVAE(nn.Module):
    def __init__(self, p_dims, q_dims=None, args=None):
        super(MultiHoffmanVAE, self).__init__()

        self.p_dims = p_dims
        if q_dims is None:
            self.q_dims = p_dims[::-1]
            q_dims = self.q_dims
        else:
            assert q_dims[0] == p_dims[-1], "Input and output dimension must equal each other for autoencoders."
            assert q_dims[-1] == p_dims[0], "Latent dimension for p- and q-network mismatches."
            self.q_dims = q_dims

        # Define encoder
        self.encoder = make_linear_network(q_dims, encoder=True)
        print(self.encoder)

        ## Define target(decoder)
        decoder = make_linear_network(p_dims)
        print(decoder)
        self.target = Target(dec=decoder)

        ## Define transitions
        self.K = args.K
        self.transitions = HMC_vanilla(kwargs=args).to(args.device)

        self.dropout = nn.Dropout()

        device_zero = torch.tensor(0., dtype=torch.float32, device=args.device)
        device_one = torch.tensor(1., dtype=torch.float32, device=args.device)
        self.std_normal = torch.distributions.Normal(loc=device_zero, scale=device_one)

    def forward(self, x_initial, is_training_ph=1.):
        l2 = torch.sum(x_initial ** 2, 1)[..., None]
        x_normed = x_initial / torch.sqrt(torch.max(l2, torch.ones_like(l2) * 1e-12))
        x = self.dropout(x_normed)

        ## Compute the first objective
        enc_out = self.encoder(x)
        mu, logvar = enc_out[:, :self.q_dims[-1]], enc_out[:, self.q_dims[-1]:]
        std = torch.exp(0.5 * logvar)

        u = self.std_normal.sample(mu.shape)
        z = mu + is_training_ph * u * std

        KL = torch.mean(torch.sum(0.5 * (-logvar + torch.exp(logvar) + mu ** 2 - 1), dim=1))
        logits_pre = self.target.decoder(z)

        ## Compute the second objective
        p_ = self.std_normal.sample(z.shape)
        z = z.detach()
        for _ in range(self.K):
            cond_vector = self.std_normal.sample(p_.shape)
            z, p_, _, _, _, _ = self.transitions.make_transition(q_old=z, x=x,
                                                                 p_old=p_,
                                                                 k=cond_vector,
                                                                 target_distr=self.target)
        logits = self.target.decoder(z)

        return logits, KL, logits_pre


class Multi_ourHoffman_VAE(nn.Module):
    def __init__(self, p_dims, q_dims=None, args=None):
        super(Multi_ourHoffman_VAE, self).__init__()

        self.p_dims = p_dims
        if q_dims is None:
            self.q_dims = p_dims[::-1]
            q_dims = self.q_dims
        else:
            assert q_dims[0] == p_dims[-1], "Input and output dimension must equal each other for autoencoders."
            assert q_dims[-1] == p_dims[0], "Latent dimension for p- and q-network mismatches."
            self.q_dims = q_dims

        ## Define encoder
        self.encoder = make_linear_network(q_dims, encoder=True)
        print(self.encoder)

        ## Define target(decoder)
        decoder = make_linear_network(p_dims)
        print(decoder)
        self.target = Target(dec=decoder)

        ## Define transitions
        self.K = args.K
        self.transitions = nn.ModuleList([HMC_our(kwargs=args).to(args.device) for _ in range(args['K'])])

        ## Define reverse kernel (if it is needed)
        self.learnable_reverse = args.learnable_reverse
        if args.learnable_reverse:
            self.reverse_kernel = Reverse_kernel(kwargs=args).to(args.device)

        self.dropout = nn.Dropout()

        device_zero = torch.tensor(0., dtype=torch.float32, device=args.device)
        device_one = torch.tensor(1., dtype=torch.float32, device=args.device)
        self.std_normal = torch.distributions.Normal(loc=device_zero, scale=device_one)
        self.torch_log_2 = torch.tensor(np.log(2), device=args.device, dtype=args.torchType)

    def forward(self, x_initial, is_training_ph=1.):
        l2 = torch.sum(x_initial ** 2, 1)[..., None]
        x_normed = x_initial / torch.sqrt(torch.max(l2, torch.ones_like(l2) * 1e-12))
        x = self.dropout(x_normed)

        enc_out = self.encoder(x)
        mu, logvar = enc_out[:, :self.q_dims[-1]], enc_out[:, self.q_dims[-1]:]
        std = torch.exp(0.5 * logvar)
        sum_log_sigma = torch.log(std).sum(1)
        sum_log_alpha = torch.zeros_like(mu[:, 0])
        sum_log_jacobian = torch.zeros_like(mu[:, 0])

        u = self.std_normal.sample(mu.shape)
        z = mu + is_training_ph * u * std

        p_old = self.std_normal.sample(z.shape)
        p_ = p_old.detach()

        if self.learnable_reverse:
            all_directions = torch.tensor([], device=x.device)
        else:
            all_directions = None

        for i in range(self.K):
            cond_vector = self.std_normal.sample(p_.shape)
            z, p_, log_jac, current_log_alphas, directions, _ = self.transitions[i].make_transition(q_old=z, x=x,
                                                                                                    p_old=p_,
                                                                                                    k=cond_vector,
                                                                                                    target_distr=self.target)
            sum_log_alpha = sum_log_alpha + current_log_alphas
            sum_log_jacobian = sum_log_jacobian + log_jac
            if self.learnable_reverse:
                all_directions = torch.cat([all_directions, directions.view(-1, 1)], dim=1)

        ## logdensity of Variational family
        log_q = self.std_normal.log_prob(u).sum(1) + self.std_normal.log_prob(p_old).sum(
            1) - sum_log_jacobian - sum_log_sigma + sum_log_alpha

        ## logdensity of prior
        log_priors = self.std_normal.log_prob(z).sum(1) + self.std_normal.log_prob(p_).sum(1)

        ## logits
        logits_pre = self.target.decoder(z)
        logits = self.target.decoder(z.detach())

        ## logdensity of reverse (if needed)
        if self.learnable_reverse:
            log_r = self.reverse_kernel(z_fin=z.detach(), h=mu.detach(), a=all_directions)
        else:
            log_r = -self.K * self.torch_log_2

        return logits, log_q, log_priors, log_r, sum_log_alpha, logits_pre
