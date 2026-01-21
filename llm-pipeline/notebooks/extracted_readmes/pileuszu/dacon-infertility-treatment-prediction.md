# Prediction of Pregnancy Success in Infertility Patients

This project develops a machine learning model to predict pregnancy success rates in infertility patients. The model achieves an accuracy of 0.7347 by building separate prediction models for IVF (In Vitro Fertilization) and DI (Donor Insemination) treatments, utilizing various machine learning algorithms and ensemble techniques.

## Project Overview

The success of pregnancy in infertility patients is determined by multiple factors. This project develops a model that predicts pregnancy success probability using various features including treatment information, medical characteristics, and patient history. The data is divided into IVF and DI treatments, with optimized models built for each type.

## Data

The dataset consists of the following files:
- `train.csv`: Training data (patient characteristics and pregnancy success)
- `test.csv`: Test data (patient characteristics)
- `sample_submission.csv`: Submission format file
- `데이터 명세.xlsx`: Data specification file

Key Features:
- Treatment type (IVF/DI)
- Patient age
- Ovulation-related information
- Infertility causes
- Previous treatment and pregnancy/birth history
- Egg/embryo-related information (mainly for IVF)