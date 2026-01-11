
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("pastel")

# Data
data = {
    "OWN DATASET - DOMAIN SPECIFIC REAL HELPLINE DATA": {
        "openchs/sw-en-opus-mt-mul-en-v1": {"BLEU": 12.51, "ChrF": 47.29, "Chrf++": 38.92, "COMET": 0.68, "LaBSE": 85.37},
        "Helsinki-NLP/opus-mt-mul-en": {"BLEU": 0.86, "ChrF": 19.41, "Chrf++": 15.88, "COMET": 0.53, "LaBSE": 58.02},
        "facebook/nllb-200-distilled-600M": {"BLEU": 0.65, "ChrF": 15.3, "Chrf++": 13.68, "COMET": 0.45, "LaBSE": 81.48},
        "google/madlad400-3b-mt": {"BLEU": 18.12, "ChrF": 51.69, "Chrf++": 40.94, "COMET": 0.66, "LaBSE": 88.47},
        "Helsinki-NLP/opus-mt-swc-en": {"BLEU": 2.21, "ChrF": 22.6, "Chrf++": 29.48, "COMET": 0.58, "LaBSE": 73.47},
    },
    "NLLB": {
        "openchs/sw-en-opus-mt-mul-en-v1": {"BLEU": 20.08, "ChrF": 39.2, "Chrf++": 20.74, "COMET": 0.64, "LaBSE": 67.57},
        "Helsinki-NLP/opus-mt-mul-en": {"BLEU": 4.61, "ChrF": 20.3, "Chrf++": 24.41, "COMET": 0.49, "LaBSE": 38.87},
        "facebook/nllb-200-distilled-600M": {"BLEU": 47.64, "ChrF": 64.94, "Chrf++": 64.17, "COMET": 0.85, "LaBSE": 0.89},
        "google/madlad400-3b-mt": {"BLEU": 43.45, "ChrF": 61.69, "Chrf++": 60.94, "COMET": 0.8464, "LaBSE": 88.47},
        "Helsinki-NLP/opus-mt-swc-en": {"BLEU": 36.7, "ChrF": 54.76, "Chrf++": 59.91, "COMET": 0.79, "LaBSE": 81.76},
    },
    "Helsinki-NLP/tatoeba": {
        "openchs/sw-en-opus-mt-mul-en-v1": {"BLEU": 24.56, "ChrF": 39.92, "Chrf++": 40.92, "COMET": 0.69, "LaBSE": 70.14},
        "Helsinki-NLP/opus-mt-mul-en": {"BLEU": 5.75, "ChrF": 19.21, "Chrf++": 30.84, "COMET": 0.53, "LaBSE": 44.38},
        "facebook/nllb-200-distilled-600M": {"BLEU": 48.88, "ChrF": 64.19, "Chrf++": 63.81, "COMET": 0.88, "LaBSE": 0.92},
        "google/madlad400-3b-mt": {"BLEU": 49.12, "ChrF": 63.2, "Chrf++": 62.86, "COMET": 0.8657, "LaBSE": 90.41},
        "Helsinki-NLP/opus-mt-swc-en": {"BLEU": 35.61, "ChrF": 52.43, "Chrf++": 81.22, "COMET": 0.83, "LaBSE": 86.37},
    },
    "FLORES 200+": {
        "openchs/sw-en-opus-mt-mul-en-v1": {"BLEU": 15.94, "ChrF": 40.89, "Chrf++": 41.34, "COMET": 0.6, "LaBSE": 71.29},
        "Helsinki-NLP/opus-mt-mul-en": {"BLEU": 5.91, "ChrF": 26.58, "Chrf++": 26.25, "COMET": 0.45, "LaBSE": 46.31},
        "facebook/nllb-200-distilled-600M": {"BLEU": 43.5, "ChrF": 65.72, "Chrf++": 64.28, "COMET": 0.85, "LaBSE": 0.93},
        "google/madlad400-3b-mt": {"BLEU": 46.64, "ChrF": 67.8, "Chrf++": 66.55, "COMET": 0.8653, "LaBSE": 94.05},
        "Helsinki-NLP/opus-mt-swc-en": {"BLEU": 22.63, "ChrF": 48.12, "Chrf++": 52.01, "COMET": 0.68, "LaBSE": 78.26},
    },
    "Own dataset (Synthetic Data mimicing target domain)": {
        "openchs/sw-en-opus-mt-mul-en-v1": {"BLEU": 70.37, "ChrF": 80.14, "Chrf++": 75.65, "COMET": 0.87, "LaBSE": 98.21},
        "Helsinki-NLP/opus-mt-mul-en": {"BLEU": 1.77, "ChrF": 16.83, "Chrf++": 26.55, "COMET": 0.37, "LaBSE": 42.94},
        "facebook/nllb-200-distilled-600M": {"BLEU": 39.95, "ChrF": 56.75, "Chrf++": 56.53, "COMET": 0.82, "LaBSE": 92},
        "google/madlad400-3b-mt": {"BLEU": 57.74, "ChrF": 74.12, "Chrf++": 73.42, "COMET": 0.8731, "LaBSE": 97.45},
        "Helsinki-NLP/opus-mt-swc-en": {"BLEU": 8.88, "ChrF": 28.74, "Chrf++": 28.41, "COMET": 0.58, "LaBSE": 78.5},
    }
}

# Convert to DataFrame
df_data = []
for dataset, models in data.items():
    for model, metrics in models.items():
        df_data.append({"Dataset": dataset, "Model": model, **metrics})
df = pd.DataFrame(df_data)

# Bar chart
metrics_to_plot = ["BLEU", "Chrf++", "COMET"]
for metric in metrics_to_plot:
    plt.figure(figsize=(12, 8))
    sns.barplot(data=df, x="Model", y=metric, hue="Dataset", dodge=True)
    plt.title(f"{metric} Comparison Across Models and Datasets", fontsize=16)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(f"assets/{metric}_comparison.png")
    plt.close()

# Radar charts
def make_radar_chart(df, dataset_name):
    labels = np.array(["BLEU", "Chrf++", "COMET", "LaBSE"])
    num_vars = len(labels)

    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    for i, (model_name, row) in enumerate(df.iterrows()):
        values = row[labels].values.flatten().tolist()
        values += values[:1]
        ax.plot(angles, values, label=model_name)
        ax.fill(angles, values, alpha=0.1)

    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    plt.title(dataset_name, size=12, y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.savefig(f"assets/radar_{dataset_name.replace(' ', '_').replace('/', '_')}.png")
    plt.close()

for dataset in df["Dataset"].unique():
    df_dataset = df[df["Dataset"] == dataset].set_index("Model")
    make_radar_chart(df_dataset, dataset)

# Heatmap
heatmap_data = df.groupby("Model")[["BLEU", "Chrf++", "COMET", "LaBSE"]].mean()
plt.figure(figsize=(10, 7))
sns.heatmap(heatmap_data, annot=True, cmap="viridis", fmt=".2f")
plt.title("Overall Metric Intensity Map", fontsize=16)
plt.xticks(rotation=45, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig("assets/heatmap.png")
plt.close()

# Trend Line Chart
plt.figure(figsize=(12, 8))
sns.lineplot(data=df, x="Dataset", y="BLEU", hue="Model", marker="o")
plt.title("BLEU Progression Across Datasets", fontsize=16)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("assets/bleu_trend.png")
plt.close()
