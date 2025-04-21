import streamlit as st
import pandas as pd
import numpy as np
import json
import openai
import time
import random
from openai import OpenAI

# Read the CSV file
df = pd.read_csv("lucidus_career_mapping_all_125_corrected.csv")

# Print all careers
print("All careers in the CSV file:")
for career in df["career"]:
    print(career)

# Print total count
print(f"\nTotal careers: {len(df['career'])}")

# Print unique careers (if there are duplicates)
print(f"Unique careers: {len(df['career'].unique())}")

