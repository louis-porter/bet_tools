import numpy as np
import pandas as pd

def kelly_expected(probability, decimal_odds, fractiont = 1.0):
    if decimal_odds <= 1 or probability <= 0 or probability >= 1:
        return 0, 0
        
    # Calculate Kelly Criterion
    q = 1 - probability  # probability of losing
    kelly = (probability * (decimal_odds - 1) - q) / (decimal_odds - 1) # win rate * potential profit subtracitng prob of losing. Divided by potentail profit
    kelly = kelly * fraction  # Apply fractional Kelly
    kelly = max(0, kelly)  # No negative bets
    
    # Calculate Expected Value
    ev = (probability * (decimal_odds - 1)) - (1 - probability)
    ev = ev * 100  # Convert to percentage
    
    return kelly, ev

prob =  0.56687
odds =  1.83
fraction = 1

bet_size, ev = kelly_expected(prob, odds, fraction)
print(f"Optimal bet size: {bet_size:.1%}")
print(f"Expected Value: {ev:.1f}%")
