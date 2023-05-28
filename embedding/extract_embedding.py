import os
import argparse
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer


def read_txt(path):
    with open(path, "r") as f:
        return "".join(f.readlines())


def get_embedding(input_text: str, model, tokenizer, max_len_single_sentence, sliding_window):
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    bs, len_seq = input_ids.shape
    if len_seq > max_len_single_sentence:
        # shift the start by sliding_window and compute embedding
        # then finally, average the embeddings
        list_embedding = []
        for s in range(0, len_seq, sliding_window):
            print(s,s+max_len_single_sentence)
            output = model(input_ids[:, s:s+max_len_single_sentence])
            embedding = output["pooler_output"]
            list_embedding.append(embedding)
        return torch.stack(list_embedding).mean(dim=0)
    else:
        output = model(input_ids)
        return output["pooler_output"]


def get_save_path(dir_save_home, path_txt):
    # <dir_save_home> / licPrec100603.npy is saved for licPrec100603.txt
    return Path(dir_save_home) / path_txt.name.replace(".txt", ".npy")


def save_to_npy(path_save, embedding_numpy: np.array):
    os.makedirs(path_save.parent, exist_ok=True)
    np.save(path_save, embedding_numpy)


def run(args):

    # load model and tokenizer
    model = AutoModel.from_pretrained(args.hf_model)
    tokenizer = AutoTokenizer.from_pretrained(args.hf_tokenizer)

    dir_home = Path(__file__).parent / "../crawl/crawled_data"
    for path_txt in dir_home.iterdir():
        input_text = read_txt(path_txt)
        path_save = get_save_path(args.dir_embedding, path_txt)
        if not path_save.exists():
            embedding = get_embedding(input_text, model, tokenizer, args.max_len_single_sentence, args.sliding_window)
            save_to_npy(path_save, embedding.detach().numpy())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Example script using argparse')
    parser.add_argument('--hf_model', type=str, default="monologg/kobigbird-bert-base")
    parser.add_argument('--hf_tokenizer', type=str, default="monologg/kobigbird-bert-base")
    parser.add_argument('--max_len_single_sentence', type=int, default=4094)  # 4096 - 2 (padded by '[CLS]' and 'SEP')
    parser.add_argument('--sliding_window', type=int, default=2047)  # 2047 == 4094 // 2
    parser.add_argument('--dir_embedding', type=str, default="./embedding_vectors")
    args = parser.parse_args()

    run(args)
