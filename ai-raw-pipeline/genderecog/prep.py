import os
import librosa
import pandas as pd
import numpy as np
from tqdm import tqdm
from datasets import load_dataset

def extract_feature(file_name, **kwargs):
    """
    Extract feature from audio file `file_name`
        Features supported:
            - MFCC (mfcc)
            - Chroma (chroma)
            - MEL Spectrogram Frequency (mel)
            - Contrast (contrast)
            - Tonnetz (tonnetz)
        e.g:
        `features = extract_feature(path, mel=True, mfcc=True)`
    """
    mfcc = kwargs.get("mfcc")
    chroma = kwargs.get("chroma")
    mel = kwargs.get("mel")
    contrast = kwargs.get("contrast")
    tonnetz = kwargs.get("tonnetz")
    X, sample_rate = librosa.core.load(file_name)

    if chroma or contrast:
        stft = np.abs(librosa.stft(X))

    result = np.array([])

    if mfcc:
        mfccs = np.mean(librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T, axis=0)
        result = np.hstack((result, mfccs))
    if chroma:
        chroma = np.mean(librosa.feature.chroma_stft(S=stft, sr=sample_rate).T,axis=0)
        result = np.hstack((result, chroma))

    if mel:
        mel = np.mean(librosa.feature.melspectrogram(y=X, sr=sample_rate).T, axis=0)
        result = np.hstack((result, mel))

    if contrast:
        contrast = np.mean(librosa.feature.spectral_contrast(S=stft, sr=sample_rate).T,axis=0)
        result = np.hstack((result, contrast))
    if tonnetz:
        tonnetz = np.mean(librosa.feature.tonnetz(y=librosa.effects.harmonic(X), sr=sample_rate).T,axis=0)
        result = np.hstack((result, tonnetz))
    return result

def process_dataset(dataset, output_dir, output_tsv, batch_size=5000):
    """
    Process dataset in batches to efficiently use available memory
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize empty lists to store metadata
    all_paths = []
    all_genders = []
    
    # Get total number of samples
    total_samples = len(dataset)
    print(f"Total samples in dataset: {total_samples}")
    
    # Process in batches
    for start_idx in tqdm(range(0, total_samples, batch_size), desc="Processing batches"):
        end_idx = min(start_idx + batch_size, total_samples)
        batch = dataset[start_idx:end_idx]
        
        # Convert batch to DataFrame for easier filtering
        batch_df = pd.DataFrame(batch)
        batch_df = batch_df[batch_df['gender'].isin(['female', 'male'])]
        
        print(f"Processing batch {start_idx//batch_size + 1}, samples {start_idx}-{end_idx}")
        
        # Process audio files in batch
        for _, row in batch_df.iterrows():
            try:
                features = extract_feature(row['path'], mel=True)
                output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(row['path']))[0]}.npy")
                np.save(output_path, features)
                
                # Store metadata
                all_paths.append(row['path'])
                all_genders.append(row['gender'])
            except Exception as e:
                print(f"Error processing {row['path']}: {str(e)}")
        
        # Clear batch from memory
        del batch_df
        del batch
    
    # Save metadata
    metadata_df = pd.DataFrame({
        'path': all_paths,
        'gender': all_genders
    })
    metadata_df.to_csv(output_tsv, sep='\t', index=False)
    print(f"Processed {len(metadata_df)} samples")

def preprocess_swacv():
    """
    Process Common Voice Swahili Audio using the datasets package
    """
    dirname = "data"
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

    # Load datasets
    print("Loading datasets...")
    common_voice_train = load_dataset(
        "mozilla-foundation/common_voice_11_0",
        "sw",
        split="train+validation",
        trust_remote_code=True
    )

    common_voice_test = load_dataset(
        "mozilla-foundation/common_voice_11_0",
        "sw",
        split="test",
        trust_remote_code=True
    )

    # Process training data
    print("Processing training data...")
    process_dataset(
        common_voice_train,
        os.path.join(dirname, "train"),
        os.path.join(dirname, "train.tsv")
    )

    # Process test data
    print("Processing test data...")
    process_dataset(
        common_voice_test,
        os.path.join(dirname, "test"),
        os.path.join(dirname, "test.tsv")
    )

if __name__ == '__main__':
    preprocess_swacv()
