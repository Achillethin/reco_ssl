##python3 main.py -data ml20m -model MultiVAE -gpu 0
##
##
##python3 main.py -data ml20m -model MultiHoffmanVAE -K 1 -N 1 -gpu 0
##
##python3 main.py -data ml20m -model MultiHoffmanVAE -K 2 -N 2 -gpu 0
#
#
#python3 main.py -data ml20m -model Multi_our_VAE -K 1 -N 1 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_our_VAE -K 1 -N 1 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_our_VAE -K 2 -N 2 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_our_VAE -K 2 -N 2 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 1 -N 1 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 1 -N 1 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 2 -N 2 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 2 -N 2 -learnable_reverse True -gpu 0
#
#
#
#python3 main.py -data ml20m -model Multi_our_VAE -K 2 -N 1 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_our_VAE -K 2 -N 1 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_our_VAE -K 3 -N 1 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_our_VAE -K 3 -N 1 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_our_VAE -K 5 -N 1 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_our_VAE -K 5 -N 1 -learnable_reverse True -gpu 0
#
#
#python3 main.py -data ml20m -model Multi_our_VAE -K 1 -N 2 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_our_VAE -K 1 -N 2 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_our_VAE -K 1 -N 3 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_our_VAE -K 1 -N 3 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_our_VAE -K 1 -N 5 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_our_VAE -K 1 -N 5 -learnable_reverse True -gpu 0
#
#
#
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 2 -N 1 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 2 -N 1 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 3 -N 1 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 3 -N 1 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 5 -N 1 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 5 -N 1 -learnable_reverse True -gpu 0
#
#
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 1 -N 2 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 1 -N 2 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 1 -N 3 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 1 -N 3 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 1 -N 5 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 1 -N 5 -learnable_reverse True -gpu 0
#
#
#python3 main.py -data ml20m -model MultiHoffmanVAE -K 3 -N 3 -gpu 0
#
#python3 main.py -data ml20m -model MultiHoffmanVAE -K 5 -N 5 -gpu 0
#
#python3 main.py -data ml20m -model Multi_our_VAE -K 3 -N 3 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_our_VAE -K 3 -N 3 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_our_VAE -K 5 -N 5 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_our_VAE -K 5 -N 5 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 3 -N 3 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 3 -N 3 -learnable_reverse True -gpu 0
#
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 5 -N 5 -learnable_reverse False -gpu 0
#python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 5 -N 5 -learnable_reverse True -gpu 0

#python3 main.py -data ml20m -model MultiVAE -gpu 0 -lrdec 1e-3
python3 main.py -data ml20m -model Multi_our_VAE -K 5 -N 1 -learnable_reverse True -gpu 1 -lrdec 3e-4 -lrenc 1e-3
#python3 main.py -data ml20m -model MultiVAE -gpu 0 -lrdec 3e-4 -lrenc 1e-3 -annealing False
python3 main.py -data ml20m -model Multi_our_VAE -K 5 -N 1 -learnable_reverse True -gpu 1 -lrdec 3e-4 -lrenc 1e-3 -annealing False

python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 5 -N 1 -learnable_reverse True -gpu 1 -lrdec 3e-4 -lrenc 1e-3
python3 main.py -data ml20m -model MultiHoffmanVAE -K 5 -N 1 -gpu 1 -lrdec 3e-4 -lrenc 1e-3

python3 main.py -data ml20m -model Multi_ourHoffman_VAE -K 5 -N 1 -learnable_reverse True -gpu 1 -lrdec 3e-4 -lrenc 1e-3 -annealing False
python3 main.py -data ml20m -model MultiHoffmanVAE -K 5 -N 1 -gpu 1 -lrdec 3e-4 -lrenc 1e-3 -annealing False