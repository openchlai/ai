"""
!pip install datasets==1.13.3
!pip install transformers==4.11.3
!pip install huggingface_hub==0.0.19
!pip install torchaudio
!pip install librosa
!pip install jiwer
!pip install evaluate

apt install git-lfs
"""
import re
import json
import torch
import random
import evaluate
import torchaudio
import pandas as pd
from time import (
    time, strftime)
from dataclasses import (
    dataclass, field)
from typing import (
    Any, Dict, List, Optional, Union)
from datasets import (
    Audio,
    ClassLabel,
    load_dataset)
from transformers import (
    Trainer,
    Wav2Vec2ForCTC,
    TrainingArguments,
    Wav2Vec2Processor,
    Wav2Vec2CTCTokenizer,
    Wav2Vec2FeatureExtractor)


print("Create Wav2Vec2CTCTokenizer")
"""
Turkish dataset is so small, we will merge both the validation and training 
data into a training dataset and simply use the test data for validation
"""
common_voice_train = load_dataset(
    "mozilla-foundation/common_voice_11_0",
    "sw",
    split="train+validation",
    trust_remote_code=True)

common_voice_test = load_dataset(
    "mozilla-foundation/common_voice_11_0",
    "sw",
    split="test",
    trust_remote_code=True)

print("Remove extra columns")
RCOL = ["accent", "age", "client_id", "down_votes", "gender", "locale", "segment", "up_votes"]
common_voice_train = common_voice_train.remove_columns(RCOL)
common_voice_test = common_voice_test.remove_columns(RCOL)


print("display some random samples")
"""
display some random samples of the dataset and run it a couple of times to get a 
feeling for the transcriptions.
"""
def show_random_elements(dataset, num_examples=10):
    assert num_examples <= len(dataset), "Can't pick more elements than there are in the dataset."
    picks = []
    for _ in range(num_examples):
        pick = random.randint(0, len(dataset)-1)
        while pick in picks:
            pick = random.randint(0, len(dataset)-1)
        picks.append(pick)
    
    df = pd.DataFrame(dataset[picks])
    print(df)
    # display(HTML(df.to_html()))

show_random_elements(common_voice_train.remove_columns(["path", "audio"]), num_examples=10)

"""
Remove unwanted characters - not sure for swahili
added •, *
"""
chars_to_ignore_regex = '[\_\…\(\)\*\•\,\?\.\!\-\;\:\"\“\%\‘\”\�]'

def remove_special_characters(batch):
    batch["sentence"] = re.sub(chars_to_ignore_regex, '', batch["sentence"]).lower() + " "
    return batch

print("Remove unwanted characters")
common_voice_train = common_voice_train.map(remove_special_characters)
common_voice_test = common_voice_test.map(remove_special_characters)


print("Extract Vocabularies")
"""
In CTC, it is common to classify speech chunks into letters, so we will do the same here. 
Let's extract all distinct letters of the training and test data and build our vocabulary 
from this set of letters
"""

def extract_all_chars(batch):
    all_text = " ".join(batch["sentence"])
    vocab = list(set(all_text))
    return {"vocab": [vocab], "all_text": [all_text]}

vocab_train = common_voice_train.map(
    extract_all_chars,
    batched=True,
    batch_size=-1,
    keep_in_memory=True,
    remove_columns=common_voice_train.column_names
    )

vocab_test = common_voice_test.map(
    extract_all_chars,
    batched=True,
    batch_size=-1,
    keep_in_memory=True,
    remove_columns=common_voice_test.column_names
    )

"""
Now, we create the union of all distinct letters in the training dataset and test 
dataset and convert the resulting list into an enumerated dictionary.

ideal we remove non-swahili alphabet characters and numerics? eg é
"""
vocab_list = list(set(vocab_train["vocab"][0]) | set(vocab_test["vocab"][0]))

vocab_dict = {v: k for k, v in enumerate(vocab_list)}
"""
To make it clearer that " " has its own token class, we give it a more visible character |
"""
vocab_dict["|"] = vocab_dict[" "]
del vocab_dict[" "]

vocab_dict["[UNK]"] = len(vocab_dict)
vocab_dict["[PAD]"] = len(vocab_dict)

"""
our vocabulary is complete and consists of 39 tokens, which means that the linear layer that 
we'll add on top of the pretrained XLSR-Wav2Vec2 checkpoint with an output dimension of 39
"""
print("Save Vocabularies")
with open('vocab.json', 'w') as vocab_file:
    json.dump(vocab_dict, vocab_file)


"""
Finally, we use the json file to instantiate an object of the Wav2Vec2CTCTokenizer class.
"""
tokenizer = Wav2Vec2CTCTokenizer(
    "./vocab.json",
    unk_token="[UNK]",
    pad_token="[PAD]",
    word_delimiter_token="|")

print("Create XLSR-Wav2Vec2 Feature Extractor Pipeline")
"""
Speech is a continuous signal and to be treated by computers, it first has to be discretized, 
which is usually called sampling. 
A pretrained checkpoint expects its input data to have been sampled more or less from the same 
distribution as the data it was trained on.
"""

feature_extractor = Wav2Vec2FeatureExtractor(
    feature_size=1,
    sampling_rate=16000,
    padding_value=0.0,
    do_normalize=True,
    return_attention_mask=True
    )

"""
feature extractor and tokenizer are wrapped into a single Wav2Vec2Processor class so that 
one only needs a model and processor object.
"""
processor = Wav2Vec2Processor(
    feature_extractor=feature_extractor,
    tokenizer=tokenizer
    )

# print("Preprocess Path", common_voice_train[0]["path"])
"""
XLSR-Wav2Vec2 expects the input in the format of a 1-dimensional array of 16 kHz. 
This means that the audio file has to be loaded and resampled.
"""
# print("Audio Data", common_voice_train[0]["audio"])

common_voice_train = common_voice_train.cast_column("audio", Audio(sampling_rate=16_000))
common_voice_test = common_voice_test.cast_column("audio", Audio(sampling_rate=16_000))

"""
So far so good: the data is a 1-dimensional array, the sampling rate always corresponds to 16kHz, 
and the target text is normalized.
"""
rand_int = random.randint(0, len(common_voice_train)-1)
print("Target text:", common_voice_train[rand_int]["sentence"])
print("Input array shape:", common_voice_train[rand_int]["audio"]["array"].shape)
print("Sampling rate:", common_voice_train[rand_int]["audio"]["sampling_rate"])

"""
Finally, we can leverage Wav2Vec2Processor to process the data to the format expected 
by Wav2Vec2ForCTC for training. To do so let's make use of Dataset's map(...) function.

DISK-SPACE ISSUES: ~/.cache/huggingface/datasets/mozilla-foundation___common_voice_11_0/
sw/11.0.0/{HASHED_VALUES}/*.arrow
"""
print("Prepare Dataset")
def prepare_dataset(batch):
    audio = batch["audio"]

    # batched output is "un-batched"
    batch["input_values"] = processor(
        audio["array"],
        sampling_rate=audio["sampling_rate"]
        ).input_values[0]
    batch["input_length"] = len(batch["input_values"])
    
    with processor.as_target_processor():
        batch["labels"] = processor(batch["sentence"]).input_ids

    return batch

"""Uncomment for production (Disk-Space)"""

print("Init Process", strftime('%H:%M'))
# common_voice_train = common_voice_train.map(prepare_dataset, remove_columns=common_voice_train.column_names)
# common_voice_test = common_voice_test.map(prepare_dataset, remove_columns=common_voice_test.column_names)
print("Exit Process", strftime('%H:%M'))

"""
Long input sequences require a lot of memory. Since XLSR-Wav2Vec2 is based on self-attention 
the memory requirement scales quadratically with the input length for long input sequences. 
Let's filter all sequences that are longer than 5 seconds out of the training dataset.
"""

"""
print("5-sec Pre-filter", len(common_voice_train))
max_input_length_in_sec = 5.0
common_voice_train = common_voice_train.filter(
    lambda x: x < max_input_length_in_sec * processor.feature_extractor.sampling_rate,
    input_columns=["input_length"])
print("5-sec Post-filter", len(common_voice_train))
"""

print("The Training")
"""
1. Define a data collator. In contrast to most NLP models, XLSR-Wav2Vec2 has a much 
larger input length than output length. E.g., a sample of input length 50000 has an
output length of no more than 100
2. Evaluation metric. During training, the model should be evaluated on the word error 
rate. We should define a compute_metrics function accordingly
3. Load a pretrained checkpoint. We need to load a pretrained checkpoint and configure 
it correctly for training.
4. Define the training configuration.
"""

# Data Collator: https://github.com/huggingface/transformers/blob/9a06b6b11bdfc42eea08
# fa91d0c737d1863c99e3/examples/research_projects/wav2vec2/run_asr.py#L81

@dataclass
class DataCollatorCTCWithPadding:
    """
    Data collator that will dynamically pad the inputs received.
    Args:
        processor (:class:`~transformers.Wav2Vec2Processor`)
            The processor used for proccessing the data.
        padding (:obj:`bool`, :obj:`str` or :class:`~transformers.tokenization_utils_base.PaddingStrategy`, `optional`, 
        defaults to :obj:`True`):
            Select a strategy to pad the returned sequences (according to the model's padding side and padding index)
            among:
            * :obj:`True` or :obj:`'longest'`: Pad to the longest sequence in the batch (or no padding if only a single
              sequence if provided).
            * :obj:`'max_length'`: Pad to a maximum length specified with the argument :obj:`max_length` or to the
              maximum acceptable input length for the model if that argument is not provided.
            * :obj:`False` or :obj:`'do_not_pad'` (default): No padding (i.e., can output a batch with sequences of
              different lengths).
        max_length (:obj:`int`, `optional`):
            Maximum length of the ``input_values`` of the returned list and optionally padding length (see above).
        max_length_labels (:obj:`int`, `optional`):
            Maximum length of the ``labels`` returned list and optionally padding length (see above).
        pad_to_multiple_of (:obj:`int`, `optional`):
            If set will pad the sequence to a multiple of the provided value.
            This is especially useful to enable the use of Tensor Cores on NVIDIA hardware with compute capability >=
            7.5 (Volta).
    """

    processor: Wav2Vec2Processor
    padding: Union[bool, str] = True
    max_length: Optional[int] = None
    max_length_labels: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    pad_to_multiple_of_labels: Optional[int] = None

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # split inputs and labels since they have to be of different lenghts and need
        # different padding methods
        input_features = [{"input_values": feature["input_values"]} for feature in features]
        label_features = [{"input_ids": feature["labels"]} for feature in features]

        batch = self.processor.pad(
            input_features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )
        with self.processor.as_target_processor():
            labels_batch = self.processor.pad(
                label_features,
                padding=self.padding,
                max_length=self.max_length_labels,
                pad_to_multiple_of=self.pad_to_multiple_of_labels,
                return_tensors="pt",
            )

        # replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        batch["labels"] = labels

        return batch

print("""Call Data Collator: Uncomment post-demo""")
data_collator = DataCollatorCTCWithPadding(processor=processor, padding=True)

"""
Define Evaluation Metrics
"""
wer_metric = evaluate.load("wer")

"""
The model will return a sequence of logit vectors: y1,…,ym  with  y1=fθ(x1,…,xn)[0] and n>>m.

A logit vector  y1  contains the log-odds for each word in the vocabulary we defined earlier,
thus  len(yi)= config.vocab_size. We are interested in the most likely prediction of the model 
and thus take the argmax(...) of the logits.
"""

def compute_metrics(pred):
    pred_logits = pred.predictions
    pred_ids = np.argmax(pred_logits, axis=-1)

    pred.label_ids[pred.label_ids == -100] = processor.tokenizer.pad_token_id

    pred_str = processor.batch_decode(pred_ids)
    # we do not want to group tokens when computing the metrics
    label_str = processor.batch_decode(pred.label_ids, group_tokens=False)

    wer = wer_metric.compute(predictions=pred_str, references=label_str)

    return {"wer": wer}

print("Load Pre-Trained Model")
"""
Now, we can load the pretrained XLSR-Wav2Vec2 checkpoint. The tokenizer's pad_token_id 
must be to define the model's pad_token_id or in the case of Wav2Vec2ForCTC also CTC's 
blank token. To save GPU memory, we enable PyTorch's gradient checkpointing and also set
the loss reduction to "mean".
"""
"""
model = Wav2Vec2ForCTC.from_pretrained(
    "facebook/wav2vec2-large-xlsr-53", 
    attention_dropout=0.1,
    hidden_dropout=0.1,
    feat_proj_dropout=0.0,
    mask_time_prob=0.05,
    layerdrop=0.1,
    ctc_loss_reduction="mean", 
    pad_token_id=processor.tokenizer.pad_token_id,
    vocab_size=len(processor.tokenizer)
)
"""
"""
The first component of XLSR-Wav2Vec2 consists of a stack of CNN layers that are used to extract 
acoustically meaningful - but contextually independent - features from the raw speech signal. 
This part of the model has already been sufficiently trained during pretraining and as stated 
in the paper does not need to be fine-tuned anymore. Thus, we can set the requires_grad to False 
for all parameters of the feature extraction part.

UNCOMMENT IN PROD
"""

# model.freeze_feature_extractor()

"""
In a final step, we define all parameters related to training:
group_by_length: makes training more efficient by grouping training samples of similar input 
length into one batch. This can significantly speed up training time by heavily reducing the 
overall number of useless padding tokens that are passed through the model
learning_rate and weight_decay: were heuristically tuned until fine-tuning has become stable. 

Note that those parameters strongly depend on the Common Voice dataset and might be 
suboptimal for other speech datasets.
"""

repo_name = "wav2vec2-large-xlsr-sw-bitz"
"""
training_args = TrainingArguments(
    output_dir=repo_name,
    group_by_length=True,
    per_device_train_batch_size=16,
    gradient_accumulation_steps=2,
    evaluation_strategy="steps",
    num_train_epochs=30,
    gradient_checkpointing=True,
    fp16=True,
    save_steps=400,
    eval_steps=400,
    logging_steps=400,
    learning_rate=3e-4,
    warmup_steps=500,
    save_total_limit=2,
    push_to_hub=False,
)
"""
print("Pass Training-Arguments to Trainer")
"""
trainer = Trainer(
    model=model,
    data_collator=data_collator,
    args=training_args,
    compute_metrics=compute_metrics,
    train_dataset=common_voice_train,
    eval_dataset=common_voice_test,
    tokenizer=processor.feature_extractor,
)
"""

"""
TO-NOTE:
Depending on what GPU was allocated to your google colab it might be possible that you 
are seeing an "out-of-memory" error here. In this case, it's probably best to reduce 
per_device_train_batch_size to 8 or even less and increase gradient_accumulation.
"""

print("Post-Train Evaluation")
"""
model = Wav2Vec2ForCTC.from_pretrained(repo_name).to("cuda")
processor = Wav2Vec2Processor.from_pretrained(repo_name)

input_dict = processor(common_voice_test[0]["input_values"], return_tensors="pt", padding=True)
logits = model(input_dict.input_values.to("cuda")).logits
pred_ids = torch.argmax(logits, dim=-1)[0]
"""

"""
Adapt common_voice_test quite a bit so that the dataset instance does not contain the original 
sentence label anymore. Thus, we re-use the original dataset to get the label of the first example.
"""
common_voice_test_transcription = load_dataset(
    "mozilla-foundation/common_voice_11_0",
    "sw",
    data_dir="./cv-corpus-6.1-2020-12-11",
    split="test"
    )

print("Prediction:")
# print(processor.decode(pred_ids))

print("\nReference:")
# print(common_voice_test_transcription[0]["sentence"].lower())

"""
Alright! The transcription can definitely be recognized from our prediction, but it is far from 
being perfect. Training the model a bit longer, spending more time on the data preprocessing, and 
especially using a language model for decoding would certainly improve the model's overall performance.
For a demonstration model on a low-resource language, the results are acceptable, however
"""

cite = "Wanyama St. James, Bitz ITC"
print(cite)
