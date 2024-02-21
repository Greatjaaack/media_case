import json
import re

import torch
from cleantext import clean
from transformers import BertTokenizerFast, BertForSequenceClassification

from provider.scanner import extract_data


def clean_text(text):
    text = clean(
        text,
        fix_unicode=True,
        to_ascii=False,
        lower=True,
        no_line_breaks=True,
        no_urls=True,
        no_emails=True,
        no_phone_numbers=True,
        no_numbers=False,
        no_digits=True,
        no_currency_symbols=True,
        no_punct=True,
        no_emoji=True,
        replace_with_url="",
        replace_with_email="",
        replace_with_phone_number="",
        replace_with_digit="",
        lang="ru",
    )

    text = re.sub(r'►|---', '', text)
    return text


def extract_config(config_path: str) -> tuple[dict[int, str], int, str]:
    with open(config_path, 'r', encoding='utf-8') as f:
        config: dict = json.load(f)
        labels: dict[int, str] = {
            int(k): v
            for k, v in config['id2label'].items()
        }
        max_position_embeddings: int = config['max_position_embeddings']
        problem_type: str = config['problem_type']

        return labels, max_position_embeddings, problem_type


def preprocessing(data):
    data['описание_канала'] = data['описание_канала'].apply(clean_text)
    data['Названия_видео_роликов'] = data['Названия_видео_роликов'].apply(clean_text)
    data['combined_text'] = data['название_канала'] + ' ' + data['описание_канала'] + ' ' + data[
        'Названия_видео_роликов']
    return data


if __name__ == '__main__':
    data = preprocessing(
        extract_data(
            target_channels='test_urls.xlsx',
            train_mode=False,
        )
    )
    labels, max_position_embeddings, problem_type = extract_config(
        # config_path='./best_model/config.json',
        config_path='./best_model/config.json',
    )
    tokenizer = BertTokenizerFast.from_pretrained('bert-base-multilingual-cased')
    model = BertForSequenceClassification.from_pretrained(
        # "./best_model",
        "./best_model",
        problem_type=problem_type,
        num_labels=len(labels),
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    print(f'Using: {device}')

    for idx, row in data.iterrows():
        encoded_input = tokenizer.encode_plus(
            row['combined_text'],
            add_special_tokens=True,
            max_length=max_position_embeddings,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        encoded_input = {k: v.to(device) for k, v in encoded_input.items()}

        with torch.no_grad():
            threshold = 0.5
            outputs = model(**encoded_input)
            logits = outputs.logits
            probabilities = torch.sigmoid(logits)
            predictions = (probabilities > threshold).int()
        predicted_classes = predictions.cpu().numpy().flatten()

        predicted_class_names = [
            labels[i]
            for i, value in enumerate(predicted_classes)
            if value == 1
        ]

        print(f"Channel: {row['название_канала']} | {predicted_class_names}")
