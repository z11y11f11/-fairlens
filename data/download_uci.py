"""
UCI Adult Dataset Download and Preprocessing Script

This script downloads the UCI Adult (Census Income) dataset and preprocesses it
for a loan approval fairness analysis scenario.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import requests
from typing import Tuple


def download_adult_dataset() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Download the UCI Adult dataset from the UCI Machine Learning Repository.
    
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Training and test dataframes
    """
    print("Downloading UCI Adult dataset...")
    
    # UCI Adult dataset URLs
    train_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"
    test_url = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.test"
    
    # Column names for the dataset
    column_names = [
        'age', 'workclass', 'fnlwgt', 'education', 'education-num',
        'marital-status', 'occupation', 'relationship', 'race', 'sex',
        'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income'
    ]
    
    try:
        # Download training data
        train_data = pd.read_csv(train_url, names=column_names, 
                                 skipinitialspace=True, na_values='?')
        print(f"✓ Downloaded training data: {len(train_data)} records")
        
        # Download test data
        test_data = pd.read_csv(test_url, names=column_names, 
                               skipinitialspace=True, skiprows=1, na_values='?')
        print(f"✓ Downloaded test data: {len(test_data)} records")
        
        # Clean the income column in test data (remove trailing period)
        test_data['income'] = test_data['income'].str.rstrip('.')
        
        return train_data, test_data
        
    except Exception as e:
        print(f"✗ Error downloading dataset: {e}")
        raise


def preprocess_for_loan_scenario(train_df: pd.DataFrame, 
                                 test_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Preprocess the Adult dataset for a loan approval scenario.
    
    This function:
    - Removes records with missing values
    - Creates a binary loan approval target (based on income)
    - Selects relevant features for loan decisions
    - Encodes categorical variables
    - Creates derived features
    
    Args:
        train_df: Training dataframe
        test_df: Test dataframe
        
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: Preprocessed training and test dataframes
    """
    print("\nPreprocessing data for loan approval scenario...")
    
    def preprocess_split(df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess a single data split"""
        # Create a copy to avoid modifying original
        df = df.copy()
        
        # Remove records with missing values
        initial_count = len(df)
        df = df.dropna()
        print(f"  Removed {initial_count - len(df)} records with missing values")
        
        # Create binary loan approval target
        # High income (>50K) suggests loan approval
        df['loan_approved'] = (df['income'] == '>50K').astype(int)
        
        # Select relevant features for loan decisions
        features_to_keep = [
            'age', 'workclass', 'education', 'education-num', 'marital-status',
            'occupation', 'relationship', 'race', 'sex', 'capital-gain',
            'capital-loss', 'hours-per-week', 'native-country', 'loan_approved'
        ]
        df = df[features_to_keep]
        
        # Create derived features
        # Employment stability indicator
        stable_workclass = ['Federal-gov', 'Local-gov', 'State-gov', 'Self-emp-inc']
        df['stable_employment'] = df['workclass'].isin(stable_workclass).astype(int)
        
        # Education level (simplified)
        high_education = ['Bachelors', 'Masters', 'Doctorate', 'Prof-school']
        df['high_education'] = df['education'].isin(high_education).astype(int)
        
        # Financial assets indicator
        df['has_capital_gain'] = (df['capital-gain'] > 0).astype(int)
        df['has_capital_loss'] = (df['capital-loss'] > 0).astype(int)
        
        # Age groups
        df['age_group'] = pd.cut(df['age'], 
                                bins=[0, 25, 35, 45, 55, 100],
                                labels=['18-25', '26-35', '36-45', '46-55', '56+'])
        
        # Work hours category
        df['work_hours_category'] = pd.cut(df['hours-per-week'],
                                          bins=[0, 20, 40, 60, 100],
                                          labels=['part-time', 'full-time', 'overtime', 'excessive'])
        
        # Encode categorical variables
        categorical_columns = ['workclass', 'education', 'marital-status', 
                              'occupation', 'relationship', 'native-country']
        
        for col in categorical_columns:
            # Create dummy variables
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True)
            df = pd.concat([df, dummies], axis=1)
        
        # Keep protected attributes as-is for fairness analysis
        df['sex_binary'] = (df['sex'] == 'Male').astype(int)
        df['race_white'] = (df['race'] == 'White').astype(int)
        
        return df
    
    # Preprocess both splits
    print("Processing training data...")
    train_processed = preprocess_split(train_df)
    
    print("Processing test data...")
    test_processed = preprocess_split(test_df)
    
    # Align columns between train and test
    # Get common columns
    common_cols = list(set(train_processed.columns) & set(test_processed.columns))
    train_processed = train_processed[common_cols]
    test_processed = test_processed[common_cols]
    
    print(f"\n✓ Preprocessing complete:")
    print(f"  Training set: {len(train_processed)} records, {len(train_processed.columns)} features")
    print(f"  Test set: {len(test_processed)} records, {len(test_processed.columns)} features")
    print(f"  Loan approval rate (train): {train_processed['loan_approved'].mean():.2%}")
    print(f"  Loan approval rate (test): {test_processed['loan_approved'].mean():.2%}")
    
    return train_processed, test_processed


def save_processed_data(train_df: pd.DataFrame, 
                       test_df: pd.DataFrame,
                       output_dir: str = "data") -> None:
    """
    Save preprocessed data to CSV files.
    
    Args:
        train_df: Preprocessed training dataframe
        test_df: Preprocessed test dataframe
        output_dir: Directory to save the files (default: "data")
    """
    print(f"\nSaving processed data to {output_dir}/...")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save files
    train_file = output_path / "adult_train_processed.csv"
    test_file = output_path / "adult_test_processed.csv"
    
    train_df.to_csv(train_file, index=False)
    test_df.to_csv(test_file, index=False)
    
    print(f"✓ Saved training data to: {train_file}")
    print(f"✓ Saved test data to: {test_file}")
    
    # Save metadata
    metadata = {
        'train_records': len(train_df),
        'test_records': len(test_df),
        'features': len(train_df.columns),
        'target': 'loan_approved',
        'protected_attributes': ['sex', 'sex_binary', 'race', 'race_white'],
        'approval_rate_train': float(train_df['loan_approved'].mean()),
        'approval_rate_test': float(test_df['loan_approved'].mean())
    }
    
    metadata_file = output_path / "dataset_metadata.txt"
    with open(metadata_file, 'w') as f:
        f.write("UCI Adult Dataset - Loan Approval Scenario\n")
        f.write("=" * 50 + "\n\n")
        for key, value in metadata.items():
            f.write(f"{key}: {value}\n")
    
    print(f"✓ Saved metadata to: {metadata_file}")


def main():
    """
    Main function to download and preprocess the UCI Adult dataset.
    """
    print("=" * 60)
    print("UCI Adult Dataset Download and Preprocessing")
    print("=" * 60)
    
    try:
        # Step 1: Download dataset
        train_raw, test_raw = download_adult_dataset()
        
        # Step 2: Preprocess for loan scenario
        train_processed, test_processed = preprocess_for_loan_scenario(train_raw, test_raw)
        
        # Step 3: Save processed data
        save_processed_data(train_processed, test_processed)
        
        print("\n" + "=" * 60)
        print("✓ Dataset preparation complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


if __name__ == "__main__":
    main()

# Made with Bob
