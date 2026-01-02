#!/usr/bin/env python3
import json

with open('feature_list.json', 'r') as f:
    features = json.load(f)

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
for f in failing_features:
    idx = f['index'] + 1
    desc = f['description'][:80] if len(f['description']) > 80 else f['description']
    print(f"{idx}: {desc}...")
    print(f"   Category: {f['category']}, Dev Done: {f['is_dev_done']}")
    print()