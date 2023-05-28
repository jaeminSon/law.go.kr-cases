import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from sklearn.manifold import TSNE


def get_embeddings(home_embedding, squeeze=True):
    list_embedding = [np.load(path_embedding) for path_embedding in Path(home_embedding).iterdir()]
    if squeeze:
        return np.squeeze(np.stack(list_embedding, axis=0))
    else:
        return np.stack(list_embedding, axis=0)

def draw_2d(path_save, features):
    plt.scatter(features[:, 0], features[:, 1])
    plt.savefig(path_save)
    plt.close()


def run(args):

    embeddings = get_embeddings(args.dir_embedding)

    tsne = TSNE(n_components=2, random_state=42)
    print(embeddings.shape)
    tsne_vectors = tsne.fit_transform(embeddings)

    draw_2d(args.path_save, tsne_vectors)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Example script using argparse')
    parser.add_argument('--dir_embedding', type=str, required=True)
    parser.add_argument('--path_save', type=str, required=True)
    args = parser.parse_args()

    run(args)
