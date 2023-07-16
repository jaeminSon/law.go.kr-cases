import os
import shutil
import argparse
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def get_embeddings(home_embedding_vectors):
    home_embedding_vectors = Path(home_embedding_vectors)
    return zip(*[(np.load(path_embedding)[0], path_embedding.name) for path_embedding in home_embedding_vectors.iterdir()])


def run(args):

    embedding_vectors, embedding_npy_names = get_embeddings(args.dir_embedding_vectors)

    for i in np.random.choice(range(len(embedding_vectors)), size=args.n_cases, replace=False):

        id_q = embedding_npy_names[i].replace(".npy", "")
        os.makedirs(id_q, exist_ok=True)

        v_q = embedding_vectors[i]
        v_others = embedding_vectors[:i] + embedding_vectors[i+1:]
        f_others = embedding_npy_names[:i] + embedding_npy_names[i+1:]

        similarities = cosine_similarity([v_q], v_others)[0]
        top_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:args.topk]
        for rank, top_i in enumerate(top_indices):
            src_txt_name = f_others[top_i].replace(".npy", ".txt")
            shutil.copy(os.path.join(args.dir_crawled_data, src_txt_name),
                        os.path.join(id_q, "top{}_sim{}_{}".format(rank+1, str(round(similarities[top_i], 3)), src_txt_name)))

        shutil.copy(os.path.join(args.dir_crawled_data, "{}.txt".format(id_q)), os.path.join(id_q, "query.txt"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Example script using argparse')
    parser.add_argument('--dir_crawled_data', type=str, default="../crawl/crawled_data")
    parser.add_argument('--dir_embedding_vectors', type=str, default="../embedding/embedding_vectors")
    parser.add_argument('--n_cases', type=int, required=True)
    parser.add_argument('--topk', type=int, required=True)
    args = parser.parse_args()

    run(args)
