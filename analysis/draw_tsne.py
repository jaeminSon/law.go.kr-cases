from sklearn.manifold import TSNE
import argparse
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors

CAT_CRIMINAL_LAW = "Criminal Law"
CAT_CIVIL_LAW = "Civil Law"
CAT_PUBLIC_LAW = "Public Law"
CAT_OTHERS = "Others"


def get_laws_from_file(path):
    with open(path) as f:
        lines = f.readlines()
    return [l.rstrip() for l in lines]


def extract_label(path_txt, category_criminal_law, category_civil_law, category_public_law):

    with open(path_txt) as f:
        lines = f.readlines()

    index_reference = [i for i, line in enumerate(lines) if "참조조문" in line]
    assert len(index_reference) < 2, "참조조문은 최대 1개만 존재."

    if len(index_reference) == 0:
        return None
    else:
        index_reference = index_reference[0]
        for tok in lines[index_reference+1].split():
            if any([cat in tok for cat in category_criminal_law]):
                return CAT_CRIMINAL_LAW
            elif any([cat in tok for cat in category_civil_law]):
                return CAT_CIVIL_LAW
            elif any([cat in tok for cat in category_public_law]):
                return CAT_PUBLIC_LAW
            else:
                return CAT_OTHERS


def get_embeddings_and_labels(home_embedding_vectors, home_crawled_data, squeeze=True):
    home_embedding_vectors = Path(home_embedding_vectors)
    home_crawled_data = Path(home_crawled_data)

    category_criminal_law = get_laws_from_file("criminal_law.txt")
    category_civil_law = get_laws_from_file("civil_law.txt")
    category_public_law = get_laws_from_file("public_law.txt")

    list_embedding = [np.load(path_embedding) for path_embedding in home_embedding_vectors.iterdir()]
    list_label = [extract_label(home_crawled_data / path_embedding.name.replace(".npy", ".txt"),
                                category_criminal_law,
                                category_civil_law,
                                category_public_law)
                  for path_embedding in home_embedding_vectors.iterdir()]

    if squeeze:
        return np.squeeze(np.stack(list_embedding, axis=0)), list_label
    else:
        return np.stack(list_embedding, axis=0), list_label


def draw_2d(path_save, features, labels):

    categories = [CAT_OTHERS, CAT_CRIMINAL_LAW, CAT_CIVIL_LAW, CAT_PUBLIC_LAW]

    def label2int(label):
        if label is None:
            return 0
        else:
            return categories.index(label)

    colormap = colors.ListedColormap(['gray', 'r', 'g', 'b'])
    scatter = plt.scatter(features[:, 0], features[:, 1], s=3, c=[label2int(l) for l in labels], cmap=colormap)
    plt.legend(handles=scatter.legend_elements()[0], labels=categories)
    plt.savefig(path_save)
    plt.close()


def run(args):

    embeddings, labels = get_embeddings_and_labels(args.dir_embedding_vectors, args.dir_crawled_data)

    tsne = TSNE(n_components=2)
    print(embeddings.shape)
    tsne_vectors = tsne.fit_transform(embeddings)

    draw_2d(args.path_save, tsne_vectors, labels)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Example script using argparse')
    parser.add_argument('--dir_crawled_data', type=str, required=True)
    parser.add_argument('--dir_embedding_vectors', type=str, required=True)
    parser.add_argument('--path_save', type=str, required=True)
    args = parser.parse_args()

    run(args)
