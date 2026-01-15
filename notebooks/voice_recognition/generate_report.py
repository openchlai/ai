import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import numpy as np
import os

# Data extracted from the markdown file
data = {
    "Helpline Audio": {
        "openchs/asr-whisper-large-v4": (61.03, 25.42),
        "facebook/seamless-m4t-v2-large": (62.2, 32.29),
        "openchs/asr-whisper-large-v3-helpline": (67.66, 28.79),
        "facebook/mms-1b-all": (69.3, 29.41),
        "openchs/asr-whisper-helpline-sw-v1": (69.94, 37.26),
        "Sunbird/asr-whisper-large-v2-salt": (103.68, 77.26),
        "openai/whisper-large-v3": (124.94, 74.46),
        "openai/whisper-large-v2": (226.47, 139.65),
    },
    "Mozilla Common Voice 23.0-Swahili": {
        "facebook/seamless-m4t-v2-large": (25.83, 22.03),
        "openchs/asr-whisper-helpline-sw-v1": (31.87, 24.87),
        "openchs/asr-whisper-large-v3-helpline": (38.06, 27.39),
        "facebook/mms-1b-all": (39.91, 24.25),
        "openchs/asr-whisper-large-v4": (46.17, 29.44),
        "openai/whisper-large-v3": (72.17, 38.26),
        "Sunbird/asr-whisper-large-v2-salt": (94.15, 49.78),
        "openai/whisper-large-v2": (95.05, 55.34),
    },
    "FLEURS": {
        "facebook/mms-1b-all": (15.71, 4.12),
        "facebook/seamless-m4t-v2-large": (24.85, 8.81),
        "openchs/asr-whisper-large-v3-helpline": (25.14, 8.19),
        "openchs/asr-whisper-helpline-sw-v1": (25.52, 8.25),
        "openchs/asr-whisper-large-v4": (28.41, 11.59),
        "openai/whisper-large-v3": (46.13, 11.7),
        "openai/whisper-large-v2": (52.72, 13.71),
        "Sunbird/asr-whisper-large-v2-salt": (87.33, 30.04),
    },
    "Domain Test Dataset": {
        "openchs/asr-whisper-large-v4": (70.0, 40.63),
        "openchs/asr-whisper-large-v3-helpline": (70.87, 37.65),
        "facebook/mms-1b-all": (73.2, 41.85),
        "facebook/seamless-m4t-v2-large": (74.03, 43.17),
        "openchs/asr-whisper-helpline-sw-v1": (74.66, 45.01),
        "openai/whisper-large-v3": (86.53, 54.66),
        "openai/whisper-large-v2": (92.91, 75.48),
        "Sunbird/asr-whisper-large-v2-salt": (97.62, 70.4),
    }
}

# Reshape data into a long-format DataFrame
records = []
for dataset, models in data.items():
    for model, metrics in models.items():
        records.append({"Dataset": dataset, "Model": model, "WER": metrics[0], "CER": metrics[1]})

df = pd.DataFrame(records)

# Create assets directory if it doesn't exist
if not os.path.exists("assets"):
    os.makedirs("assets")

# --- Chart Generation ---

# 4.1 Metric-Wise Grouped Bar Charts
def plot_metric_wise_charts(df):
    for metric in ["WER", "CER"]:
        plt.figure(figsize=(14, 8))
        sns.barplot(data=df, x="Model", y=metric, hue="Dataset", palette="viridis")
        plt.title(f"{metric} Across Models by Dataset", fontsize=16)
        plt.xlabel("Model", fontsize=12)
        plt.ylabel(metric, fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.legend(title="Dataset")
        plt.tight_layout()
        plt.savefig(f"assets/{metric.lower()}_metric_chart.png")
        plt.close()

plot_metric_wise_charts(df)

# 4.2 Dataset-Wise Bar Charts
def plot_dataset_wise_charts(df):
    for dataset in df["Dataset"].unique():
        plt.figure(figsize=(12, 7))
        dataset_df = df[df["Dataset"] == dataset].melt(id_vars=["Model"], value_vars=["WER", "CER"], var_name="Metric", value_name="Score")
        sns.barplot(data=dataset_df, x="Model", y="Score", hue="Metric", palette="muted")
        plt.title(f"ASR Performance on {dataset}", fontsize=16)
        plt.xlabel("Model", fontsize=12)
        plt.ylabel("Error Rate (%)", fontsize=12)
        plt.xticks(rotation=45, ha="right")
        plt.legend(title="Metric")
        plt.tight_layout()
        file_path = os.path.join("assets", f"{dataset.replace(' ', '_').lower()}_perf_chart.png")
        plt.savefig(file_path)
        plt.close()

plot_dataset_wise_charts(df)

# 4.3 Dataset-Wise Heatmaps
def plot_dataset_wise_heatmaps(df):
    for dataset in df["Dataset"].unique():
        plt.figure(figsize=(10, 8))
        heatmap_df = df[df["Dataset"] == dataset].set_index("Model")[["WER", "CER"]]
        sns.heatmap(heatmap_df, annot=True, fmt=".2f", cmap="YlGnBu", linewidths=.5)
        plt.title(f"WER/CER Heatmap - {dataset}", fontsize=16)
        plt.xlabel("Metric", fontsize=12)
        plt.ylabel("Model", fontsize=12)
        plt.tight_layout()
        file_path = os.path.join("assets", f"{dataset.replace(' ', '_').lower()}_heatmap.png")
        plt.savefig(file_path)
        plt.close()

plot_dataset_wise_heatmaps(df)

# 4.4 Radar Charts
def plot_radar_charts(df):
    models = df["Model"].unique()
    for dataset in df["Dataset"].unique():
        dataset_df = df[df["Dataset"] == dataset]
        
        metrics = ['WER', 'CER']
        num_vars = len(metrics)

        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        for i, model in enumerate(models):
            values = dataset_df[dataset_df["Model"] == model][metrics].values.flatten().tolist()
            values += values[:1]
            ax.plot(angles, values, label=model)
            ax.fill(angles, values, alpha=0.1)

        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        plt.title(f"Performance Profile - {dataset}", size=16, y=1.1)
        plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        plt.tight_layout()
        file_path = os.path.join("assets", f"{dataset.replace(' ', '_').lower()}_radar.png")
        plt.savefig(file_path)
        plt.close()

plot_radar_charts(df)


# --- PDF Generation ---
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 18)
        self.cell(0, 10, "Speech-to-Text Model Evaluation", 0, 1, "C")
        self.set_font("Arial", "I", 14)
        self.cell(0, 10, "Domain-Specific ASR Performance Comparison", 0, 1, "C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, title.encode('latin-1', 'replace').decode('latin-1'), 0, 1, "L")
        self.ln(5)

    def chapter_body(self, content):
        self.set_font("Arial", "", 12)
        self.multi_cell(0, 10, content.encode('latin-1', 'replace').decode('latin-1'))
        self.ln()

    def add_table(self, header, data, col_widths):
        self.set_font("Arial", "B", 10)
        for i, header_text in enumerate(header):
            self.cell(col_widths[i], 7, header_text.encode('latin-1', 'replace').decode('latin-1'), 1, 0, "C")
        self.ln()
        self.set_font("Arial", "", 10)
        for row in data:
            for i, text in enumerate(row):
                self.cell(col_widths[i], 6, str(text).encode('latin-1', 'replace').decode('latin-1'), 1)
            self.ln()
        self.ln()
        
    def add_image_section(self, title, image_path):
        self.add_page()
        self.chapter_title(title)
        if os.path.exists(image_path):
            self.image(image_path, x=10, w=190)
        else:
            self.cell(0, 10, f"[Image not found: {image_path}]", 0, 1)
        self.ln(5)


pdf = PDF("P", "mm", "A4")
pdf.add_page()

# Section 1
pdf.chapter_title("SECTION 1 - Metric Definitions")
metric_header = ["Metric", "Description", "Interpretation", "Ideal Range"]
metric_data = [
    ["WER (Word Error Rate)", "Percentage of incorrectly predicted words", "Measures transcription accuracy", "0-100 (Lower = better)"],
    ["CER (Character Error Rate)", "Percentage of incorrectly predicted characters", "Captures robustness to accents and noise", "0-100 (Lower = better)"]
]
pdf.add_table(metric_header, metric_data, [50, 70, 50, 25])
pdf.chapter_body("Note: WER and CER are primary indicators of ASR accuracy. Lower values indicate fewer misrecognized words and better noise resilience.")

# Section 2
pdf.add_page()
pdf.chapter_title("SECTION 2 - Data Overview & Methodology")
methodology = (
    "This report evaluates multiple ASR models on four distinct datasets: Helpline (Own), Common Voice (Swahili), FLEURS, and a Domain Test Dataset. "
    "Performance is measured using Word Error Rate (WER) and Character Error Rate (CER), calculated without special normalization. "
    "The models include both general-purpose systems (e.g., Whisper, MMS) and models fine-tuned on specific domains to assess the impact of specialization."
)
pdf.chapter_body(methodology)

# Section 3
pdf.add_page()
pdf.chapter_title("SECTION 3 - Comparative Performance Tables")
for dataset in df["Dataset"].unique():
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Dataset: {dataset}", 0, 1, "L")
    dataset_df = df[df["Dataset"] == dataset].sort_values("WER").reset_index()
    dataset_df["Rank"] = dataset_df.index + 1
    
    table_header = ["Model", "WER ↓", "CER ↓", "Rank"]
    table_data = []
    for _, row in dataset_df.iterrows():
        table_data.append([row["Model"], f"{row['WER']:.2f}", f"{row['CER']:.2f}", row["Rank"]])
    pdf.add_table(table_header, table_data, [90, 25, 25, 20])

# Section 4
pdf.add_image_section("SECTION 4.1 - Metric-Wise Charts: WER", "assets/wer_metric_chart.png")
pdf.add_image_section("SECTION 4.1 - Metric-Wise Charts: CER", "assets/cer_metric_chart.png")

for dataset in df["Dataset"].unique():
    file_path_perf = os.path.join("assets", f"{dataset.replace(' ', '_').lower()}_perf_chart.png")
    pdf.add_image_section(f"SECTION 4.2 - Dataset-Wise Chart: {dataset}", file_path_perf)
    
    file_path_heatmap = os.path.join("assets", f"{dataset.replace(' ', '_').lower()}_heatmap.png")
    pdf.add_image_section(f"SECTION 4.3 - Dataset-Wise Heatmap: {dataset}", file_path_heatmap)

    file_path_radar = os.path.join("assets", f"{dataset.replace(' ', '_').lower()}_radar.png")
    pdf.add_image_section(f"SECTION 4.4 - Radar Chart: {dataset}", file_path_radar)

# Section 5
pdf.add_page()
pdf.chapter_title("SECTION 5 - Analytical Summary")
summary = (
    "The fine-tuned models, particularly 'openchs/asr-whisper-large-v4', demonstrate superior performance on the domain-specific 'Helpline Audio' and 'Domain Test Dataset'. "
    "For instance, on the Helpline dataset, 'openchs/asr-whisper-large-v4' (61.03% WER) shows a significant reduction in errors compared to the general-purpose 'openai/whisper-large-v2' (226.47% WER). "
    "On benchmark datasets like FLEURS, large general-purpose models like 'facebook/mms-1b-all' still hold an advantage (15.71% WER). "
    "This indicates a clear trade-off: fine-tuning yields substantial gains for specific domains but may not surpass the top performers on general, clean audio benchmarks."
)
pdf.chapter_body(summary)

# Section 6
pdf.add_page()
pdf.chapter_title("SECTION 6 - Limitations & Interpretation Caveats")
limitations = (
    "- WER and CER may not fully capture intelligibility or context accuracy.\n"
    "- Fine-tuned models may overfit to specific noise patterns in the training data.\n"
    "- Datasets vary in noise levels, accents, and recording quality, affecting comparability.\n"
    "- Benchmark datasets like FLEURS and Common Voice typically contain cleaner speech than real-world scenarios."
)
pdf.chapter_body(limitations)

# Section 7
pdf.add_page()
pdf.chapter_title("SECTION 7 - Appendix / Reproducibility")
pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Full Raw Data", 0, 1, "L")
raw_header = ["Model", "Dataset", "WER", "CER"]
raw_data = []
for _, row in df.iterrows():
    raw_data.append([row["Model"], row["Dataset"], f"{row['WER']:.2f}", f"{row['CER']:.2f}"])
pdf.add_table(raw_header, raw_data, [80, 60, 25, 25])

pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Generated Charts", 0, 1, "L")
chart_list = "\n".join(os.listdir("assets"))
pdf.chapter_body(chart_list)

pdf.set_font("Arial", "B", 12)
pdf.cell(0, 10, "Tools Used", 0, 1, "L")
pdf.chapter_body("Python (pandas, matplotlib, seaborn, fpdf2)")


pdf.output("Speech_to_Text_Model_Evaluation_Report_Generated.pdf")

print("PDF report generated successfully.")