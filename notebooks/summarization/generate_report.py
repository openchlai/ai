import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
import numpy as np
from datetime import datetime
import os

# --- 0. Setup ---
ASSETS_DIR = "assets"
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

# --- 1. Data Parsing and Transformation ---
try:
    df = pd.read_csv('data.csv')
    # Clean up dataset names for consistency
    df['Dataset'] = df['Dataset'].str.replace(r'\(.*?\)', '', regex=True).str.strip()
    df['Dataset'] = df['Dataset'].replace({
        'Own dataset': 'Own Synthetic',
        'SAMSum(dialogsum)Dataset': 'SAMSum/DialogSum'
    })
except FileNotFoundError:
    print("Error: data.csv not found. Please make sure the CSV file is in the same directory.")
    exit()

# Define metrics for analysis
metrics = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'BLEU', 'BERTScore-F1']
all_models = df['Model'].unique()
all_datasets = df['Dataset'].unique()
fine_tuned_model = 'openchs/sum-flan-t5-base-synthetic-v1'

# Melt the dataframe to long format for easier plotting
df_long = df.melt(id_vars=['Model', 'Dataset'], value_vars=metrics, var_name='Metric', value_name='Score')

# --- PDF Report Setup ---
pdf_doc = SimpleDocTemplate("report.pdf", pagesize=A4)
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleStyle', fontSize=24, leading=28, alignment=TA_CENTER, spaceAfter=20))
styles['Heading1'].fontSize = 18
styles['Heading1'].leading = 22
styles['Heading1'].spaceAfter = 14
styles['Heading1'].spaceBefore = 20
styles['Heading2'].fontSize = 14
styles['Heading2'].leading = 18
styles['Heading2'].spaceAfter = 10
styles['Heading2'].spaceBefore = 16
try:
    styles.add(ParagraphStyle(name='Heading3', fontSize=12, leading=14, spaceAfter=8, spaceBefore=12))
except KeyError:
    pass
styles['Normal'].fontSize = 10
styles['Normal'].leading = 12
styles['Normal'].spaceAfter = 6
try:
    styles.add(ParagraphStyle(name='TableText', fontSize=8, leading=10))
except KeyError:
    pass
styles['Code'].fontName = 'Courier'
styles['Code'].fontSize = 8
styles['Code'].leading = 10
styles['Code'].backColor = colors.lightgrey

pdf_story = []

# --- Markdown Report Setup ---
md_content = ""

# --- Title Page ---
title_page_pdf = [
    Paragraph("Comprehensive Model Evaluation — Summarization Performance Comparison", styles['TitleStyle']),
    Paragraph(f"Date: {datetime.now().strftime('%B %d, %Y')}", styles['Normal']),
    Spacer(1, 2 * inch),
    Paragraph("Prepared by: Gemini CLI Agent", styles['Normal']),
    PageBreak()
]
pdf_story.extend(title_page_pdf)

md_content += f"# Comprehensive Model Evaluation — Summarization Performance Comparison\n\n"
md_content += f"**Date:** {datetime.now().strftime('%B %d, %Y')}\n\n"
md_content += "**Prepared by:** Gemini CLI Agent\n\n"
md_content += "---\n\n"

# --- Table of Contents ---
toc_pdf = [
    Paragraph("Table of Contents", styles['Heading1']),
    Spacer(1, 0.2 * inch),
    Paragraph("1. Metric Definitions", styles['Normal']),
    Paragraph("2. Data & Methodology", styles['Normal']),
    Paragraph("3. Comparative Summary Tables", styles['Normal']),
    Paragraph("4. Visual Analysis", styles['Normal']),
    Paragraph("  4.1 Metric-wise Charts", styles['Normal']),
    Paragraph("  4.2 Model-wise Charts", styles['Normal']),
    Paragraph("  4.3 Dataset-wise Heatmaps", styles['Normal']),
    Paragraph("  4.4 Dataset-wise Radar Charts", styles['Normal']),
    Paragraph("5. Analytical Summary", styles['Normal']),
    Paragraph("6. Limitations & Caveats", styles['Normal']),
    Paragraph("7. Appendix / Reproducibility", styles['Normal']),
    PageBreak()
]
pdf_story.extend(toc_pdf)

md_content += "## Table of Contents\n\n"
md_content += "1. [Metric Definitions](#section-1--metric-definitions)\n"
md_content += "2. [Data & Methodology](#section-2--data--methodology)\n"
md_content += "3. [Comparative Summary Tables](#section-3--comparative-summary-tables)\n"
md_content += "4. [Visual Analysis](#section-4--visual-analysis)\n"
md_content += "    - [Metric-wise Charts](#41-metric-wise-charts)\n"
md_content += "    - [Model-wise Charts](#42-model-wise-charts)\n"
md_content += "    - [Dataset-wise Heatmaps](#43-dataset-wise-heatmaps)\n"
md_content += "    - [Dataset-wise Radar Charts](#44-dataset-wise-radar-charts)\n"
md_content += "5. [Analytical Summary](#section-5--analytical-summary)\n"
md_content += "6. [Limitations & Caveats](#section-6--limitations--caveats)\n"
md_content += "7. [Appendix / Reproducibility](#section-7--appendix--reproducibility)\n\n"
md_content += "---\n\n"


# --- SECTION 1 — Metric Definitions ---
pdf_story.append(Paragraph("1. Metric Definitions", styles['Heading1']))
md_content += "## SECTION 1 — Metric Definitions\n\n"

metric_data = [
    ["Metric", "Description", "Interpretation", "Ideal Range"],
    ["ROUGE-1", "Overlap of unigrams between system and reference summaries", "Measures recall and informativeness", "0–1 (Higher = better)"],
    ["ROUGE-2", "Overlap of bigrams", "Captures fluency and local coherence", "0–1"],
    ["ROUGE-L", "Longest common subsequence", "Captures structure and readability", "0–1"],
    ["BLEU", "Precision-oriented metric from machine translation", "Evaluates fluency and precision", "0–1"],
    ["BERTScore", "Semantic similarity using contextual embeddings", "Captures meaning alignment", "0–1"],
    ["C-Sema (Human Eval)", "Human qualitative evaluation of coherence and factuality", "Human-judged quality", "Higher = better"]
]
metric_df = pd.DataFrame(metric_data[1:], columns=metric_data[0])
md_content += metric_df.to_markdown(index=False) + "\n\n"

table_style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
])
col_widths = [1.2*inch, 2.5*inch, 2.5*inch, 1.5*inch]
metric_table = Table(metric_data, colWidths=col_widths)
metric_table.setStyle(table_style)
pdf_story.append(metric_table)
pdf_story.append(PageBreak())


# --- SECTION 2 — Data & Methodology ---
pdf_story.append(Paragraph("2. Data & Methodology", styles['Heading1']))
md_content += "## SECTION 2 — Data & Methodology\n\n"

methodology_text = [
    "This report evaluates the performance of several summarization models across four distinct datasets: 'Own Synthetic', 'Own Real', 'CNN/DailyMail', and 'SAMSum/DialogSum'. Each dataset comprises 500 samples. 'Own Synthetic' and 'Own Real' represent domain-specific data, while 'CNN/DailyMail' and 'SAMSum/DialogSum' are general-purpose benchmarks.",
    "Metrics include ROUGE-1, ROUGE-2, ROUGE-L, BLEU, and BERTScore-F1. All scores are presented as reported, without additional normalization. No statistical significance testing was performed due to the lack of multiple runs or variance data.",
    "Limitations include the absence of human evaluation for most entries, the fixed sample size of 500, and the inherent biases of each automated metric. The results are descriptive and intended to highlight performance patterns rather than declare a definitive 'best' model."
]
for text in methodology_text:
    pdf_story.append(Paragraph(text, styles['Normal']))
    md_content += f"{text}\n\n"
pdf_story.append(PageBreak())
md_content += "---\n\n"


# --- SECTION 3 — Comparative Summary Tables ---
pdf_story.append(Paragraph("3. Comparative Summary Tables", styles['Heading1']))
md_content += "## SECTION 3 — Comparative Summary Tables\n\n"

for dataset_name in all_datasets:
    pdf_story.append(Paragraph(f"Performance on {dataset_name}", styles['Heading2']))
    md_content += f"### Performance on {dataset_name}\n\n"
    
    dataset_df = df[df['Dataset'] == dataset_name].copy()
    
    # Prepare table data
    table_df = dataset_df[['Model'] + metrics].copy()
    table_data = [table_df.columns.tolist()] + table_df.values.tolist()
    
    # Style for PDF table
    table_style_summary = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D3D3')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ])

    # Highlight max value in each metric column
    for i, metric in enumerate(metrics):
        col_idx = i + 1
        try:
            max_val = dataset_df[metric].max()
            for j, row in enumerate(table_data[1:]):
                if row[col_idx] == max_val:
                    table_style_summary.add('FONTNAME', (col_idx, j + 1), (col_idx, j + 1), 'Helvetica-Bold')
        except (ValueError, TypeError):
            # Handle non-numeric data if any
            pass

    summary_table = Table(table_data, colWidths=[2.5*inch] + [0.8*inch]*len(metrics))
    summary_table.setStyle(table_style_summary)
    pdf_story.append(summary_table)
    pdf_story.append(Spacer(1, 0.1 * inch))

    # MD Table
    md_content += table_df.to_markdown(index=False) + "\n\n"

pdf_story.append(PageBreak())
md_content += "---\n\n"


# --- SECTION 4 — Visual Analysis (Full Granularity) ---
pdf_story.append(Paragraph("4. Visual Analysis", styles['Heading1']))
md_content += "## SECTION 4 — Visual Analysis\n\n"

# --- 4.1 Metric-wise Charts ---
pdf_story.append(Paragraph("4.1 Metric-wise Charts", styles['Heading2']))
md_content += "### 4.1 Metric-wise Charts\n\n"
for metric in metrics:
    plt.figure(figsize=(12, 7))
    sns.barplot(data=df_long[df_long['Metric'] == metric], x='Model', y='Score', hue='Dataset', palette='viridis')
    plt.title(f'{metric} Scores per Model across Datasets', fontsize=16)
    plt.xlabel('Model', fontsize=12)
    plt.ylabel(f'{metric} Score', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Dataset', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    chart_path = os.path.join(ASSETS_DIR, f'metric_chart_{metric}.png')
    plt.savefig(chart_path)
    plt.close()
    
    pdf_story.append(Paragraph(f'{metric} Scores per Model across Datasets', styles['Heading3']))
    pdf_story.append(Image(chart_path, width=7*inch, height=4*inch))
    md_content += f"#### {metric} Scores\n![{metric} Chart]({chart_path})\n\n"
pdf_story.append(PageBreak())

# --- 4.2 Model-wise Charts ---
pdf_story.append(Paragraph("4.2 Model-wise Charts", styles['Heading2']))
md_content += "### 4.2 Model-wise Charts\n\n"
for model in all_models:
    model_name_safe = model.replace('/', '_')
    plt.figure(figsize=(12, 7))
    sns.barplot(data=df_long[df_long['Model'] == model], x='Metric', y='Score', hue='Dataset', palette='plasma')
    plt.title(f'{model} — Metrics across Datasets', fontsize=16)
    plt.xlabel('Metric', fontsize=12)
    plt.ylabel('Score', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Dataset', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    chart_path = os.path.join(ASSETS_DIR, f'model_chart_{model_name_safe}.png')
    plt.savefig(chart_path)
    plt.close()
    
    pdf_story.append(Paragraph(f'{model} — Metrics across Datasets', styles['Heading3']))
    pdf_story.append(Image(chart_path, width=7*inch, height=4*inch))
    md_content += f"#### {model}\n![{model} Chart]({chart_path})\n\n"
pdf_story.append(PageBreak())

# --- 4.3 Dataset-wise Heatmaps ---
pdf_story.append(Paragraph("4.3 Dataset-wise Heatmaps", styles['Heading2']))
md_content += "### 4.3 Dataset-wise Heatmaps\n\n"
for dataset in all_datasets:
    dataset_name_safe = dataset.replace('/', '_')
    heatmap_df = df[df['Dataset'] == dataset].set_index('Model')[metrics]
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_df, annot=True, cmap='YlGnBu', fmt=".3f", linewidths=.5)
    plt.title(f'Performance by Metric and Model — {dataset}', fontsize=14)
    plt.xlabel('Metric', fontsize=12)
    plt.ylabel('Model', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    chart_path = os.path.join(ASSETS_DIR, f'heatmap_{dataset_name_safe}.png')
    plt.savefig(chart_path)
    plt.close()
    
    pdf_story.append(Paragraph(f'Performance by Metric and Model — {dataset}', styles['Heading3']))
    pdf_story.append(Image(chart_path, width=6*inch, height=3.6*inch))
    md_content += f"#### {dataset}\n![{dataset} Heatmap]({chart_path})\n\n"
pdf_story.append(PageBreak())

# --- 4.4 Dataset-wise Radar Charts ---
pdf_story.append(Paragraph("4.4 Dataset-wise Radar Charts", styles['Heading2']))
md_content += "### 4.4 Dataset-wise Radar Charts\n\n"
for dataset in all_datasets:
    dataset_name_safe = dataset.replace('/', '_')
    
    categories = metrics
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    for model in all_models:
        values = df[(df['Model'] == model) & (df['Dataset'] == dataset)][categories].values.flatten().tolist()
        values += values[:1]
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=model)
    
    plt.xticks(angles[:-1], categories, color='grey', size=10)
    ax.set_rlabel_position(0)
    plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4", "0.6", "0.8"], color="grey", size=8)
    plt.ylim(0, 1)
    plt.title(f'Performance Profile — {dataset}', size=14, color='black', y=1.1)
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    chart_path = os.path.join(ASSETS_DIR, f'radar_{dataset_name_safe}.png')
    plt.savefig(chart_path)
    plt.close()
    
    pdf_story.append(Paragraph(f'Performance Profile — {dataset}', styles['Heading3']))
    pdf_story.append(Image(chart_path, width=5*inch, height=5*inch))
    md_content += f"#### {dataset}\n![{dataset} Radar Chart]({chart_path})\n\n"
pdf_story.append(PageBreak())
md_content += "---\n\n"


# --- SECTION 5 — Analytical Summary ---
pdf_story.append(Paragraph("5. Analytical Summary", styles['Heading1']))
md_content += "## SECTION 5 — Analytical Summary\n\n"

summary_texts = [
    "The analysis provides a granular view of model performance across different datasets and metrics. On the 'Own Synthetic' dataset, the fine-tuned model <b>openchs/sum-flan-t5-base-synthetic-v1</b> shows the highest scores in ROUGE-1 (0.473), ROUGE-2 (0.227), ROUGE-L (0.386), and BERTScore-F1 (0.841), indicating a strong performance on its training domain. For instance, its ROUGE-L score is 282% relatively higher than 'google/flan-t5-base' (0.101) on this dataset. However, 'facebook/bart-large-cnn' achieves the highest BLEU score (0.151), suggesting better precision.",
    "On the 'Own Real dataset', the fine-tuned model continues to lead in ROUGE-1 (0.433) and BERTScore-F1 (0.610), but its ROUGE-L (0.222) is surpassed by 'google-t5/t5-base' (0.153) and 'google/pegasus-cnn_dailymail' (0.177) and 'facebook/bart-large-cnn' (0.165). This might suggest that while semantically similar (high BERTScore), the generated summaries are structurally different from the reference in the real-world dataset.",
    "In the general-purpose datasets, the performance is more mixed. On 'CNN/DailyMail', 'google/pegasus-cnn_dailymail' and 'facebook/bart-large-cnn' show strong performance, often outperforming the fine-tuned model on several metrics. For example, 'google/pegasus-cnn_dailymail' has a ROUGE-L of 0.261 compared to the fine-tuned model's 0.227. A similar trend is observed on the 'SAMSum/DialogSum' dataset, where the fine-tuned model does not consistently lead.",
    "These patterns suggest that the fine-tuning was successful for the synthetic domain, but the advantage is less pronounced on real-world data and general-purpose benchmarks. There are clear trade-offs between models, with some excelling in n-gram overlap (ROUGE), others in precision (BLEU), and others in semantic similarity (BERTScore). Without human evaluation, it is difficult to definitively assess the overall quality of the summaries."
]
for text in summary_texts:
    pdf_story.append(Paragraph(text, styles['Normal']))
    md_content += f"{text.replace('<b>', '**').replace('</b>', '**')}\n\n"
pdf_story.append(PageBreak())
md_content += "---\n\n"


# --- SECTION 6 — Limitations & Caveats ---
pdf_story.append(Paragraph("6. Limitations & Caveats", styles['Heading1']))
md_content += "## SECTION 6 — Limitations & Caveats\n\n"

limitations_texts = [
    "<b>Metric Biases:</b> ROUGE, BLEU, and BERTScore each have their own biases. ROUGE favors recall, BLEU favors precision, and BERTScore measures semantic similarity which may not always correlate with human judgments of quality. A model performing well on one metric may not perform well on others.",
    "<b>Limited Human Evaluation:</b> The analysis is based almost entirely on automated metrics. Without comprehensive human evaluation, it is difficult to assess aspects like factuality, coherence, and readability.",
    "<b>Dataset Specificity:</b> Performance on one dataset does not guarantee similar performance on another. The 'Own Synthetic' dataset may have characteristics that particularly favor the fine-tuned model.",
    "<b>Sample Size:</b> The evaluation is based on 500 samples per dataset. While this provides a good overview, a larger and more diverse sample set would provide more robust results.",
    "<b>Descriptive Analysis:</b> This report is a descriptive analysis of the provided scores. No statistical significance testing was performed, so small differences in scores may not be meaningful."
]
for text in limitations_texts:
    pdf_story.append(Paragraph(text, styles['Normal']))
    md_content += f"- {text.replace('<b>', '**').replace('</b>', '**')}\n"
pdf_story.append(PageBreak())
md_content += "\n---\n\n"

# --- SECTION 7 — Appendix / Reproducibility ---
pdf_story.append(Paragraph("7. Appendix / Reproducibility", styles['Heading1']))
md_content += "## SECTION 7 — Appendix / Reproducibility\n\n"

pdf_story.append(Paragraph("<b>Full Data Table:</b>", styles['Heading2']))
md_content += "### Full Data Table\n\n"
raw_table_data = [df.columns.tolist()] + df.values.tolist()
raw_table_style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D3D3')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 0), (-1, -1), 6),
])
raw_data_table = Table(raw_table_data, colWidths=[1.5*inch] + [0.6*inch]* (len(df.columns)-1) )
raw_data_table.setStyle(raw_table_style)
pdf_story.append(raw_data_table)
md_content += df.to_markdown(index=False) + "\n\n"

pdf_story.append(Paragraph("<b>List of Generated Figures:</b>", styles['Heading2']))
md_content += "### List of Generated Figures\n\n"
figure_list = ""
for root, _, files in os.walk(ASSETS_DIR):
    for file in files:
        if file.endswith('.png'):
            figure_list += f"- {file}\n"
pdf_story.append(Paragraph(figure_list, styles['Code']))
md_content += f"```\n{figure_list}```\n\n"


pdf_story.append(Paragraph(f"<b>Computation Timestamp:</b> {datetime.now().strftime('%B %d, %Y %H:%M:%S')}", styles['Normal']))
md_content += f"**Computation Timestamp:** {datetime.now().strftime('%B %d, %Y %H:%M:%S')}\n\n"
pdf_story.append(Paragraph("<b>Data Source Reference:</b> User-provided table data.", styles['Normal']))
md_content += "**Data Source Reference:** User-provided table data.\n"


# --- Build PDF and Write MD file ---
try:
    pdf_doc.build(pdf_story)
    print("Report 'report.pdf' generated successfully.")
except Exception as e:
    print(f"Error generating PDF: {e}")

try:
    with open('report.md', 'w') as f:
        f.write(md_content)
    print("Report 'report.md' generated successfully.")
except Exception as e:
    print(f"Error generating MD file: {e}")