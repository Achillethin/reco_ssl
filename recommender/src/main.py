import argparse
import random

import numpy as np
import torch
from models import MultiVAE, MultiDAE, Multi_our_VAE, MultiHoffmanVAE, Multi_ourHoffman_VAE
from training import train_model, train_met_model, train_hoffman_model, train_methoffman_model

from args import get_args
from data import Dataset

parser = argparse.ArgumentParser(
    description='VAE for CF')

parser.add_argument('-data', type=str, choices=['ml20m', 'foursquare', 'gowalla', 'ml25m', 'ml100k'],
                    help='Specify, which data to use', required=True)
parser.add_argument('-model', type=str,
                    choices=['MultiVAE', 'MultiDAE', 'Multi_our_VAE', 'MultiHoffmanVAE', 'Multi_ourHoffman_VAE'],
                    help='Specify, which model to use', required=True)
parser.add_argument('-K', type=int, help='Number of transitions (MH)', required=False)
parser.add_argument('-N', type=int, help='Number of leapfrogs', required=False)
parser.add_argument('-learnable_reverse', type=str, choices=['True', 'False'],
                    help='If we use learnable reverse or not', default='False')
parser.add_argument('-annealing', type=str, choices=['True', 'False'],
                    help='If we use annealing or not', default='True')
parser.add_argument('-gpu', type=int, help='If >=0 - id of device, -1 means cpu', default=-1)

parser.add_argument('-lrdec', type=float, help='Learning rate for decoder', default=1e-3)
parser.add_argument('-lrenc', type=float, help='Learning rate for inference part', default=None)


args = parser.parse_args()


def set_seeds(rand_seed):
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.manual_seed(rand_seed)
    np.random.seed(rand_seed)
    random.seed(rand_seed)
    torch.cuda.manual_seed_all(rand_seed)


def main(args):
    set_seeds(322)
    args = get_args(args)
    dataset = Dataset(args)
    layers = [200, 600, dataset.n_items]
    args.z_dim = layers[0]
    args.l2_coeff = 0.

    if args.model == 'MultiVAE':
        model = MultiVAE(layers, args=args).to(args.device)
        metric_values = train_model(model, dataset, args)
    elif args.model == 'MultiDAE':
        args.l2_coeff = 0.01 / args.train_batch_size
        model = MultiDAE([200, dataset.n_items], args=args).to(args.device)
        metric_values = train_model(model, dataset, args)
    elif args.model == 'Multi_our_VAE':
        model = Multi_our_VAE(layers, args=args).to(args.device)
        metric_values = train_met_model(model, dataset, args)
    elif args.model == 'MultiHoffmanVAE':
        model = MultiHoffmanVAE(layers, args=args).to(args.device)
        metric_values = train_hoffman_model(model, dataset, args)
    elif args.model == 'Multi_ourHoffman_VAE':
        model = Multi_ourHoffman_VAE(layers, args=args).to(args.device)
        metric_values = train_methoffman_model(model, dataset, args)

    np.savetxt(
        "../logs/metrics_{}_{}_K_{}_N_{}_learnreverse_{}_anneal_{}_lrdec_{}_lrenc_{}.txt".format(args.data, args.model, args.K, args.N,
                                                                               args.learnable_reverse, args.annealing, args.lrdec, args.lrenc),
        np.array(metric_values))

    with open("../logs/log.txt", "a") as myfile:
        myfile.write("!!Success!! \n \n \n \n".format(args))
    print('Success!')


if __name__ == "__main__":
    main(args)
