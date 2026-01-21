# ChatGPT vs Human Text Analysis

This project analyzes and compares text patterns between human-written content and ChatGPT-generated paraphrases. Using various data mining and machine learning techniques, we explore distinctive patterns that can help identify AI-generated content.

## Project Overview

The rise of large language models like ChatGPT has made it increasingly difficult to distinguish between human-written and AI-generated text. This project aims to:

1. Analyze word frequency distributions in both human and ChatGPT-generated texts
2. Identify common word patterns and associations using frequent pattern mining
3. Apply SVD (Singular Value Decomposition) analysis to understand text structure differences
4. Build machine learning models to classify text as human or AI-generated

## Dataset

We used the "ChatGPT Paraphrases" dataset from Kaggle, containing original human-written text and ChatGPT-generated paraphrases of the same content.

## Project Structure

- `codes/`: Jupyter notebooks containing analysis code
  - `Word_frequency.ipynb`: Analyzes word frequency and part-of-speech distributions
  - `Paraphrase_Pattern_GPT.ipynb`: Applies frequent pattern mining to ChatGPT texts
  - `Paraphrase_Pattern_Human.ipynb`: Applies frequent pattern mining to human texts
  - `Paraphrase_SVD.ipynb`: Performs SVD analysis on text data
- `Machine_Learning.ipynb`: Implements machine learning models for classification
- `dataming_result/`: Contains CSV files with analysis results
  - Word counts, frequent sets, association rules, etc.

## Key Findings

1. **Word Usage**: ChatGPT and human text show different distributions in word frequencies and part-of-speech tags
2. **Word Association Patterns**: Frequent pattern mining reveals different word associations between human and AI text
3. **Classification**: Machine learning models can distinguish between human and AI text with promising accuracy

## Technologies Used

- Python
- PySpark for distributed data processing
- NLTK for natural language processing
- Pandas for data manipulation
- Scikit-learn for machine learning models
- Matplotlib for visualization

## How to Run

1. Clone this repository
2. Install required dependencies:
   ```
   pip install pandas numpy matplotlib pyspark nltk scikit-learn
   ```
3. Download the dataset from Kaggle (see notebook code for download instructions)
4. Run the Jupyter notebooks in the following order:
   - `Word_frequency.ipynb`
   - `Paraphrase_Pattern_GPT.ipynb`
   - `Paraphrase_Pattern_Human.ipynb`
   - `Paraphrase_SVD.ipynb`
   - `Machine_Learning.ipynb`

## Contributors

This project was created by Team 13 for the Data Mining course.
