# Topic Selection Algorithm Documentation

## Overview

The YouTube Hobby Maxxxer uses a **weighted random selection algorithm** to intelligently choose topics from your Google Sheets. It balances exploration of new topics with your personal interests while preventing repetitive selections.

## Algorithm Philosophy

**Primary Goal**: Encourage exploration of new hobbies while respecting user preferences
**Secondary Goal**: Prevent boring repetition of recently watched topics
**Approach**: Weighted randomization with multiple scoring factors

## Weight Calculation Factors

### 1. 🆕 **Exploration Bonus (Unwatched Topics)**
- **Multiplier**: `15.0x`
- **Logic**: Topics without a `date_watched` value get massive priority
- **Purpose**: Ensures you discover new areas before revisiting old ones

```python
if not date_watched:
    weight *= 15.0  # 15x more likely to select
```

### 2. 🕒 **Recency Penalties (Anti-Repetition)**
- **Within 3 days**: `0.05x` (95% reduction)
- **Within 14 days**: `0.3x` (70% reduction) 
- **Within 30 days**: `0.6x` (40% reduction)
- **Purpose**: Prevents immediate repetition, encourages variety

```python
if days_since_watched < 3:
    weight *= 0.05      # Almost eliminate recent topics
elif days_since_watched < 14:
    weight *= 0.3       # Strong penalty for 2 weeks
elif days_since_watched < 30:
    weight *= 0.6       # Moderate penalty for a month
```

### 3. ❤️ **Interest Score Adjustments**
- **Based on**: Your video ratings (`loved`, `liked`, `didn't_like`, `boring`)
- **Scoring**: `loved=+2.0`, `liked=+1.0`, `didn't_like=-0.5`, `boring=-1.0`
- **Recent Activity Boost**: Videos rated in last 30 days get recency multiplier
- **Capped Influence**: Max score capped at 2.0 to prevent domination
- **Reduced Impact**: Only 30% of score applied (was 100%)

```python
# Rating to numeric score
rating_scores = {
    'loved': 2.0,
    'liked': 1.0,
    'didn\'t_like': -0.5,
    'boring': -1.0
}

# Cap and reduce influence
capped_score = min(interest_score, 2.0)
if capped_score > 0:
    weight *= (1 + capped_score * 0.3)  # Max 60% boost
```

### 4. 🎲 **Random Variance**
- **Range**: ±20% random variation
- **Purpose**: Prevents completely deterministic selections
- **Implementation**: `weight *= random.uniform(0.8, 1.2)`

## Example Weight Calculations

### Scenario 1: Brand New Topic
```
Base weight: 1.0
Unwatched bonus: × 15.0 = 15.0
Random variance: × 1.15 = 17.25
Final weight: 17.25
```

### Scenario 2: Recently Loved Topic (watched 2 days ago)
```
Base weight: 1.0
Recent penalty: × 0.05 = 0.05
Interest boost (loved=2.0): × (1 + 2.0×0.3) = × 1.6 = 0.08
Random variance: × 0.95 = 0.076
Final weight: 0.076
```

### Scenario 3: Moderately Liked Topic (watched 20 days ago)
```
Base weight: 1.0
Recent penalty: × 0.6 = 0.6
Interest boost (liked=1.0): × (1 + 1.0×0.3) = × 1.3 = 0.78
Random variance: × 1.05 = 0.82
Final weight: 0.82
```

## Selection Process

1. **Calculate weights** for all topics using above factors
2. **Sum total weight** across all candidates
3. **Generate random number** between 0 and total weight
4. **Walk through candidates** until cumulative weight exceeds random number
5. **Select that topic**

## Algorithm Tuning Guide

### To Increase New Topic Priority
- Increase unwatched multiplier (currently `15.0`)
- Strengthen recency penalties (make multipliers smaller)

### To Reduce Interest Score Influence  
- Reduce interest multiplier (currently `0.3`)
- Lower score cap (currently `2.0`)

### To Add More Randomness
- Increase variance range (currently `0.8-1.2`)

### To Change Recency Windows
- Adjust day thresholds (currently `3, 14, 30` days)
- Modify penalty multipliers

## Version History

### Version 2.0 (Current) - "Exploration Focus"
- **Unwatched boost**: 5x → 15x
- **Recent penalties**: Stronger (0.2x → 0.05x within 3 days)
- **Interest influence**: Capped and reduced (100% → 30%)
- **Added**: Random variance (±20%)
- **Goal**: Prioritize new topic discovery

### Version 1.0 - "Interest Driven"
- **Unwatched boost**: 5x
- **Recent penalties**: Moderate (0.2x within 7 days)  
- **Interest influence**: Full score applied (up to 200%+ boost)
- **Issue**: Popular topics dominated selection

## Expected Behavior

### High Priority (Often Selected)
- ✅ **New/unwatched topics** (15x boost)
- ✅ **Topics with positive ratings from 30+ days ago**

### Medium Priority (Sometimes Selected)  
- ⚡ **Topics watched 14-30 days ago** with good ratings
- ⚡ **Topics with mixed/neutral ratings**

### Low Priority (Rarely Selected)
- ⏸️ **Topics watched within 14 days** 
- ⏸️ **Topics with consistently boring ratings**

### Extremely Low Priority (Almost Never)
- 🚫 **Topics watched within 3 days**
- 🚫 **Recently watched + boring rated topics**

## Debugging Output

The algorithm provides detailed console output:

```
🧠 Calculating topic interest scores...
✅ Calculated interest scores for 8 topics
📊 Smart topic selection from Google Sheets...
🆕 Unwatched topic boost: photography basics
❤️ Interest boost for surf intermediate: 1.50 (reduced)
🚫 Strong recent penalty: cooking basics (1 days ago)
🎯 Smart selection: 'photography basics' (weight: 16.85)
📊 Selection from 12 candidates (total weight: 25.30)
```

This shows which factors influenced the selection and why certain topics were boosted or penalized.