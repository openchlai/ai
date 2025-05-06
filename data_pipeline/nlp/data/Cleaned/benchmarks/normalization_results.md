# Text Normalization Benchmark Results
## Performance Metrics
| Metric | Value |
|--------|-------|
| Spelling Correction Accuracy | 92% |
| Stemming Speed | 177,990 docs/sec |
| Vocabulary Size Reduction (Stemming) | 0% |

## Configuration
```json
{
  "input_dir": "./data/cleaned/",
  "output_dir": "./data/normalized/",
  "benchmark_dir": "./benchmarks/",
  "contraction_map": {
    "don't": "do not",
    "can't": "cannot",
    "won't": "will not",
    "i'm": "i am",
    "you're": "you are",
    "it's": "it is",
    "he's": "he is",
    "she's": "she is",
    "we're": "we are",
    "they're": "they are",
    "i've": "i have",
    "you've": "you have",
    "we've": "we have",
    "they've": "they have",
    "i'll": "i will",
    "you'll": "you will",
    "he'll": "he will",
    "she'll": "she will",
    "we'll": "we will",
    "they'll": "they will",
    "isn't": "is not",
    "aren't": "are not",
    "wasn't": "was not",
    "weren't": "were not",
    "hasn't": "has not",
    "haven't": "have not",
    "hadn't": "had not",
    "doesn't": "does not",
    "didn't": "did not"
  },
  "symspell_config": {
    "max_edit_distance": 2,
    "prefix_length": 7,
    "count_threshold": 1,
    "dictionary_path": null
  },
  "performance_sample_size": 1000
}
