from transformers import BertTokenizer, BertForSequenceClassification
import torch
import pandas as pd
from sklearn.metrics import classification_report

# Load your dataset
csv = r'C:\Users\akash\Downloads\IntelUnnaati-BusinessValidation\CUAD_v1\master_clauses.csv'
data = pd.read_csv(csv)
data = data.drop(columns=data.filter(like='-Answer').columns)
data = data.drop(columns=data.filter(like='- Answer').columns)

# Load the model and tokenizer globally
model_path = r'C:\Users\akash\Downloads\IntelUnnaati-BusinessValidation\clause_classifier_model'
model = BertForSequenceClassification.from_pretrained(model_path)
tokenizer = BertTokenizer.from_pretrained(model_path)

# Ensure the model is on the correct device
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()

# Generate the label dictionary
label_dict = {idx: label for idx, label in enumerate(data.columns[1:])}
reverse_label_dict = {label: idx for idx, label in label_dict.items()}  # Create reverse mapping for debugging

def find_labels(test_sentences, true_labels=None):
    # Tokenize the test data
    test_encodings = tokenizer(test_sentences, truncation=True, padding=True, return_tensors='pt')

    # Move tensors to the correct device
    input_ids = test_encodings['input_ids'].to(device)
    attention_mask = test_encodings['attention_mask'].to(device)

    # Perform inference
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)

    # Get predicted labels
    logits = outputs.logits
    predicted_labels = torch.argmax(logits, dim=1).cpu().numpy()

    # Map numeric labels back to clause types
    predicted_clause_types = [label_dict[label] for label in predicted_labels]

    results = []
    for sentence, clause_type in zip(test_sentences, predicted_clause_types):
        results.append({
            "sentence": sentence,
            "predicted_clause_type": clause_type
        })

    if true_labels:
        # Convert true labels to numeric format
        true_numeric_labels = [reverse_label_dict[label] for label in true_labels]

        # Find unique classes in true and predicted labels
        unique_labels = sorted(set(true_numeric_labels + list(predicted_labels)))

        # Filter target names to include only these classes
        filtered_target_names = [label_dict[label] for label in unique_labels]

        # Print classification report
        report = classification_report(true_numeric_labels, predicted_labels, target_names=filtered_target_names)
        results.append({"classification_report": report})

    return results
