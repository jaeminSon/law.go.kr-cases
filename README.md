# law.go.kr-cases ([국가법령정보센터](https://www.law.go.kr/LSW/precSc.do) 판례 분석)

## File heirarchy

```
.
├── analysis # misc analyses
├── crawl # collect data from law.go.kr
└── embedding # extract text embeddings using huggingface model
```

## Data Preparation
1. Download `crawled_data.zip` and `text_embeddings.zip` (soon available) from [Hugging Face repo](https://huggingface.co/datasets/woalsdnd/law.go.kr)
2. Extract `crawled_data.zip` and put text files at `crawl/crawled_data`
3. Extract `text_embeddings.zip` and put numpy files at `embedding/embedding_vectors`

