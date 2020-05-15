import argparse
import os
import random
import numpy as np
import torch
import pdb
from training import train_model, train_met_model
from models import MultiVAE, MultiDAE, Multi_our_VAE
from data import Dataset

from args import get_args

parser = argparse.ArgumentParser(
    description='VAE for CF')

parser.add_argument('-data', type=str, choices=['ml20m', 'foursquare', 'gowalla', 'ml25m', 'ml100k'],
                    help='Specify, which data to use', required=True)
parser.add_argument('-model', type=str, choices=['MultiVAE', 'MultiDAE', 'Multi_our_VAE'],
                    help='Specify, which model to use', required=True)
parser.add_argument('-K', type=int, help='Number of transitions (MH)', required=False)
parser.add_argument('-N', type=int, help='Number of leapfrogs', required=False)
parser.add_argument('-learnable_reverse', type=str, choices=['True', 'False'],
                    help='If we use learnable reverse or not', default='False')

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
    if args.model=='MultiVAE':
        layers = [200, 600, dataset.n_items]
        args.l2_coeff = 0.
        model = MultiVAE(layers, args=args).to(args.device)
        metric_values = train_model(model, dataset, args)
    elif args.model=='MultiDAE':
        args.l2_coeff = 0.01 / args.train_batch_size
        model = MultiDAE([200, dataset.n_items], args=args).to(args.device)
        metric_values = train_model(model, dataset, args)
    elif args.model=='Multi_our_VAE':
        layers = [200, 600, dataset.n_items]
        args.z_dim = layers[0]
        args.l2_coeff = 0.
        model = Multi_our_VAE(layers, args=args).to(args.device)
        metric_values = train_met_model(model, dataset, args)

    np.savetxt("./metrics_{}_{}_{}_{}_{}.txt".format(args.data, args.model, args.K, args.N, args.learnable_reverse),
               np.array(metric_values))

    with open("./log.txt", "a") as myfile:
        myfile.write("!!Success!! \n \n \n \n".format(args))
    print('Success!')


if __name__ == "__main__":
    main(args)