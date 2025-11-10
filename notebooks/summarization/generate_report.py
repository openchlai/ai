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

# --- 1. Data Parsing ---
try:
    df = pd.read_csv('data.csv')
    # Clean up dataset names
    df['Dataset'] = df['Dataset'].str.replace(r'\(.*?\)', '', regex=True).str.strip()
except FileNotFoundError:
    print("Error: data.csv not found. Please make sure the CSV file is in the same directory.")
    exit()

# Define metrics for analysis
metrics = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'BLEU', 'BERTScore-F1']
domain_datasets = ['Own dataset', 'Own Real dataset']
other_datasets = ['CNN/DailyMail', 'SAMSum']
all_datasets = df['Dataset'].unique()
fine_tuned_model = 'openchs/sum-flan-t5-base-synthetic-v1'

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
styles['Normal'].fontSize = 10
styles['Normal'].leading = 12
styles['Normal'].spaceAfter = 6
styles.add(ParagraphStyle(name='TableText', fontSize=8, leading=10))
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

md_content += "| Metric | Description | Interpretation | Ideal Range |\n"
md_content += "|---|---|---|---|\n"
for row in metric_data[1:]:
    md_content += f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |\n"
md_content += "\n---\n\n"

# --- SECTION 2 — Data & Methodology ---
pdf_story.append(Paragraph("2. Data & Methodology", styles['Heading1']))
md_content += "## SECTION 2 — Data & Methodology\n\n"

methodology_text = [
    "This report evaluates the performance of several summarization models across four distinct datasets: 'Own Synthetic', 'Own Real', 'CNN/DailyMail', and 'SAMSum'. Each dataset comprises 500 samples. 'Own Synthetic' and 'Own Real' represent domain-specific data, with 'Own Synthetic' being synthetically generated and 'Own Real' reflecting production test scenarios. 'CNN/DailyMail' and 'SAMSum' are widely recognized general-purpose summarization benchmarks.",
    "Evaluation metrics include ROUGE-1, ROUGE-2, ROUGE-L (for n-gram and longest common subsequence overlap), BLEU (a precision-oriented metric), and BERTScore (for semantic similarity). All metrics are normalized to a 0-1 scale, with higher values indicating better performance. No specific tokenization or lowercasing steps beyond standard model pre-processing were applied during evaluation. Due to the absence of raw scores or multiple runs, statistical significance testing or bootstrap resampling to estimate confidence intervals could not be performed. Therefore, observed differences are presented without formal uncertainty estimates.",
    "Limitations include the lack of statistical significance data, the absence of LLM_Judge scores, and incomplete C-Sema human evaluation data across all models and datasets. The sample size of 500 per dataset, while substantial, may still limit the power to detect subtle performance differences."
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
    dataset_df['Rank'] = dataset_df['ROUGE-L'].rank(ascending=False, method='min').astype(int)
    
    display_cols = ['Model', 'ROUGE-L', 'BLEU', 'BERTScore-F1', 'Rank']
    table_df = dataset_df[display_cols].copy()

    # PDF Table
    pdf_table_data = [table_df.columns.tolist()] + table_df.values.tolist()
    table_style_summary = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D3D3')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ])
    summary_table = Table(pdf_table_data, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.5*inch])
    summary_table.setStyle(table_style_summary)
    pdf_story.append(summary_table)
    pdf_story.append(Spacer(1, 0.1 * inch))

    # MD Table
    md_content += table_df.to_markdown(index=False) + "\n\n"

# Domain Average Table
pdf_story.append(Paragraph("Domain Average Performance (Own dataset + Own Real dataset)", styles['Heading2']))
md_content += "### Domain Average Performance (Own dataset + Own Real dataset)\n\n"

domain_avg_df = df[df['Dataset'].isin(domain_datasets)].groupby('Model')[metrics].mean().reset_index()
domain_avg_df['ROUGE-L_Rank'] = domain_avg_df['ROUGE-L'].rank(ascending=False, method='min').astype(int)

# PDF Table
pdf_domain_table_data = [domain_avg_df.columns.tolist()] + domain_avg_df.values.tolist()
domain_table_style = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D3D3D3')),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
])
domain_avg_table = Table(pdf_domain_table_data, colWidths=[2.5*inch] + [0.8*inch]*len(metrics) + [0.5*inch])
domain_avg_table.setStyle(domain_table_style)
pdf_story.append(domain_avg_table)
pdf_story.append(PageBreak())

# MD Table
md_content += domain_avg_df.to_markdown(index=False) + "\n\n"
md_content += "---\n\n"


# --- SECTION 4 — Visual Analysis ---
pdf_story.append(Paragraph("4. Visual Analysis", styles['Heading1']))
md_content += "## SECTION 4 — Visual Analysis\n\n"

# 1. Bar Chart
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x='Dataset', y='ROUGE-L', hue='Model', palette='viridis')
plt.title('ROUGE-L by Dataset — Model Comparison', fontsize=14)
plt.xlabel('Dataset', fontsize=12)
plt.ylabel('ROUGE-L Score', fontsize=12)
plt.xticks(rotation=15)
plt.legend(title='Model', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
plt.tight_layout()
bar_chart_path = os.path.join(ASSETS_DIR, 'rouge_l_bar_chart.png')
plt.savefig(bar_chart_path)
plt.close()
pdf_story.append(Paragraph("ROUGE-L by Dataset — Model Comparison", styles['Heading2']))
pdf_story.append(Image(bar_chart_path, width=6*inch, height=3.6*inch))
md_content += "### ROUGE-L by Dataset — Model Comparison\n\n"
md_content += f"![ROUGE-L Bar Chart]({bar_chart_path})\n\n"

# 2. Radar Chart
domain_metrics_avg = df[df['Dataset'].isin(domain_datasets)].groupby('Model')[metrics].mean()
fine_tuned_row = domain_metrics_avg.loc[fine_tuned_model]
baselines_avg_row = domain_metrics_avg.drop(fine_tuned_model).mean()
categories = metrics
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]
fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(111, polar=True)
values = fine_tuned_row[categories].tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label=fine_tuned_model, color='blue')
ax.fill(angles, values, 'blue', alpha=0.1)
values = baselines_avg_row[categories].tolist()
values += values[:1]
ax.plot(angles, values, linewidth=1, linestyle='solid', label='Average Baselines', color='red')
ax.fill(angles, values, 'red', alpha=0.1)
plt.xticks(angles[:-1], categories, color='grey', size=10)
ax.set_rlabel_position(0)
plt.yticks([0.2, 0.4, 0.6, 0.8], ["0.2", "0.4", "0.6", "0.8"], color="grey", size=8)
plt.ylim(0, 1)
plt.title('Radar Chart: Fine-tuned vs. Average Baselines (Domain Avg.)', size=14, color='black', y=1.1)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
plt.tight_layout()
radar_chart_path = os.path.join(ASSETS_DIR, 'radar_chart.png')
plt.savefig(radar_chart_path)
plt.close()
pdf_story.append(Paragraph("Radar Chart: Fine-tuned vs. Average Baselines (Domain Avg.)", styles['Heading2']))
pdf_story.append(Image(radar_chart_path, width=5*inch, height=5*inch))
md_content += "### Radar Chart: Fine-tuned vs. Average Baselines (Domain Avg.)\n\n"
md_content += f"![Radar Chart]({radar_chart_path})\n\n"

# 3. Heatmap
heatmap_df = df.groupby('Model')[metrics].mean()
plt.figure(figsize=(10, 6))
sns.heatmap(heatmap_df, annot=True, cmap='viridis', fmt=".3f", linewidths=.5)
plt.title('Heatmap: Average Metric Scores Across All Datasets', fontsize=14)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
heatmap_path = os.path.join(ASSETS_DIR, 'heatmap.png')
plt.savefig(heatmap_path)
plt.close()
pdf_story.append(Paragraph("Heatmap: Average Metric Scores Across All Datasets", styles['Heading2']))
pdf_story.append(Image(heatmap_path, width=6*inch, height=3.6*inch))
pdf_story.append(PageBreak())
md_content += "### Heatmap: Average Metric Scores Across All Datasets\n\n"
md_content += f"![Heatmap]({heatmap_path})\n\n"
md_content += "---\n\n"

# --- SECTION 5 — Analytical Summary ---
pdf_story.append(Paragraph("5. Analytical Summary", styles['Heading1']))
md_content += "## SECTION 5 — Analytical Summary\n\n"

ft_model_domain_avg = domain_avg_df[domain_avg_df['Model'] == fine_tuned_model]
baselines_domain_avg = domain_avg_df[domain_avg_df['Model'] != fine_tuned_model][metrics].mean()

summary_texts = [
    f"The fine-tuned model, <b>{fine_tuned_model}</b>, demonstrates superior performance on the domain-specific datasets ('Own dataset' and 'Own Real dataset') compared to the general-purpose baselines. Specifically, on 'Own dataset', it achieves the highest ROUGE-L score of {df[(df['Model'] == fine_tuned_model) & (df['Dataset'] == 'Own dataset')]['ROUGE-L'].iloc[0]:.3f} and BERTScore of {df[(df['Model'] == fine_tuned_model) & (df['Dataset'] == 'Own dataset')]['BERTScore-F1'].iloc[0]:.3f}. Across the combined domain datasets, its average ROUGE-L is {ft_model_domain_avg['ROUGE-L'].iloc[0]:.3f}, which is notably higher than the average of baselines ({baselines_domain_avg['ROUGE-L']:.3f}). This suggests strong adaptation and alignment with the characteristics of the target domain.",
    f"When evaluating performance on general-purpose datasets ('CNN/DailyMail' and 'SAMSum'), the performance gap between the fine-tuned model and baselines narrows. For instance, on CNN/DailyMail, the fine-tuned model's ROUGE-L of {df[(df['Model'] == fine_tuned_model) & (df['Dataset'] == 'CNN/DailyMail')]['ROUGE-L'].iloc[0]:.3f} is competitive but not always leading, with models like 'facebook/bart-large-cnn' showing comparable or slightly higher scores in some metrics. This indicates that while the fine-tuned model excels in its specialized domain, its universal applicability might be more aligned with strong general-purpose models rather than universally outperforming them.",
    "Metric tradeoffs are also apparent. While ROUGE scores and BERTScore generally correlate, there are instances where a model might have a high ROUGE-L but a lower BLEU score, suggesting a balance between recall/informativeness and precision/fluency. For example, 'facebook/bart-large-cnn' often shows strong BLEU scores, indicating good lexical precision, even if its ROUGE-L isn't always the absolute highest. BERTScore consistently provides a semantic perspective, often aligning with ROUGE-L for models that produce semantically coherent summaries. The absence of human evaluation (C-Sema) and LLM_Judge scores prevents a more qualitative assessment of coherence and factuality, which are crucial for a holistic understanding of summarization quality.",
    "Overall, the fine-tuned model demonstrates clear advantages within its target domain, validating the fine-tuning approach for specialized tasks. Its performance on general datasets suggests a robust foundation, but without further domain adaptation, it does not universally surpass highly optimized general-purpose models on their respective benchmarks. Future evaluations could benefit from incorporating human judgment and statistical significance testing to provide more robust conclusions."
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
    "<b>Domain-Specific Vocabulary/Style:</b> The performance metrics, particularly ROUGE and BLEU, can be sensitive to domain-specific vocabulary and stylistic nuances. Models fine-tuned on a particular domain might naturally score higher on those datasets due to lexical overlap, which may not fully reflect broader quality improvements.",
    "<b>Human Evaluation Coverage:</b> The provided data lacks comprehensive human evaluation (C-Sema) and LLM_Judge scores. Human judgment is critical for assessing subjective aspects of summarization quality, such as coherence, factuality, and readability, which automated metrics may not fully capture.",
    "<b>Sample Size:</b> Each dataset consists of 500 samples. While this is a reasonable size for initial evaluation, it may not be sufficient to achieve high statistical power for detecting subtle performance differences or to generalize robustly across very diverse inputs within a dataset.",
    "<b>Metric Biases:</b> ROUGE and BLEU are known to have limitations and biases. ROUGE primarily measures overlap, and BLEU is precision-oriented, sometimes penalizing grammatically correct but lexically different summaries. BERTScore mitigates some of these issues by considering semantic similarity but still relies on an underlying language model. A comprehensive evaluation ideally complements these with human judgment.",
    "<b>Lack of Uncertainty Estimates:</b> Without multiple runs or bootstrap resampling, confidence intervals for the metrics could not be computed. Therefore, all reported scores are point estimates, and the statistical significance of observed differences cannot be formally asserted."
]
for text in limitations_texts:
    pdf_story.append(Paragraph(text, styles['Normal']))
    md_content += f"- {text.replace('<b>', '**').replace('</b>', '**')}\n"
pdf_story.append(PageBreak())
md_content += "\n---\n\n"

# --- SECTION 7 — Appendix / Reproducibility ---
pdf_story.append(Paragraph("7. Appendix / Reproducibility", styles['Heading1']))
md_content += "## SECTION 7 — Appendix / Reproducibility\n\n"

pdf_story.append(Paragraph("<b>Raw Data Table:</b>", styles['Heading2']))
md_content += "### Raw Data Table\n\n"
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

pdf_story.append(Paragraph("<b>Plotting Details (Pseudo-code):</b>", styles['Heading2']))
md_content += "### Plotting Details (Pseudo-code)\n\n"

pseudo_code_texts = [
    """
    # Bar Chart (ROUGE-L by Dataset)
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='Dataset', y='ROUGE-L', hue='Model', palette='viridis')
    plt.savefig('assets/rouge_l_bar_chart.png')
    """,
    """
    # Radar Chart (Fine-tuned vs. Average Baselines)
    # Data preparation for radar chart involves averaging metrics for baselines and selecting fine-tuned model.
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)
    # Plotting logic...
    plt.savefig('assets/radar_chart.png')
    """,
    """
    # Heatmap (Average Metric Scores)
    heatmap_df = df.groupby('Model')[metrics].mean()
    sns.heatmap(heatmap_df, annot=True, cmap='viridis', fmt=".3f")
    plt.savefig('assets/heatmap.png')
    """
]
for code in pseudo_code_texts:
    pdf_story.append(Paragraph(code.strip(), styles['Code']))
    md_content += f"```python\n{code.strip()}\n```\n\n"

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