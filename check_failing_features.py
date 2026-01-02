#!/usr/bin/env python3
import json

with open('feature_list.json', 'r') as file:
    features = json.load(file)

failing_features = []
for i, feature in enumerate(features):
    if not feature.get('passes', False):
        failing_features.append({
            'index': i,
            'description': feature.get('description', ''),
            'is_dev_done': feature.get('is_dev_done', False),
            'category': feature.get('category', '')
        })
        if len(failing_features) >= 10:
            break

print('First 10 failing features:')
for feature in failing_features:
    idx = feature['index'] + 1
    desc = feature['description'][:80] if len(feature['description']) > 80 else feature['description']
    print(f"{idx}: {desc}...")
    print(f"   Category: {feature['category']}, Dev Done: {feature['is_dev_done']}")
    print()
