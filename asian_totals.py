import numpy as np
import pandas as pd

def predict_goal_line_from_xg(home_xg, away_xg, requested_lines=None, n_sims=50000, random_seed=42):
    """
    Predict Asian total (goal line) probabilities using expected goals
    Returns win/lose probabilities only (no push)
    """
    np.random.seed(random_seed)
    
    # Simulate matches
    home_goals = np.random.poisson(home_xg, size=n_sims)
    away_goals = np.random.poisson(away_xg, size=n_sims)
    total_goals = home_goals + away_goals
    
    results = []
    
    def calculate_win_lose_probs(lower_line, upper_line):
        """
        Calculate win/lose probabilities (no push) for a split line bet
        """
        # Count outcomes
        under_lower = np.sum(total_goals < lower_line) / n_sims
        exactly_lower = np.sum(total_goals == lower_line) / n_sims
        over_upper = np.sum(total_goals > upper_line) / n_sims
        
        # Calculate raw probabilities including pushes
        over_lower_part = 0.5 * ((1 - under_lower - exactly_lower) + 0.5 * exactly_lower)
        over_upper_part = 0.5 * over_upper
        raw_over_prob = over_lower_part + over_upper_part
        
        under_lower_part = 0.5 * under_lower
        under_upper_part = 0.5 * (1 - over_upper)
        raw_under_prob = under_lower_part + under_upper_part
        
        push_prob = 0.5 * 0.5 * exactly_lower
        
        # Calculate win probability excluding pushes (normalized)
        total_non_push = raw_over_prob + raw_under_prob
        over_win_prob = raw_over_prob / total_non_push
        under_win_prob = raw_under_prob / total_non_push
        
        return over_win_prob, under_win_prob
    
    if requested_lines is None:
        requested_lines = ["0.5, 1.0", "1.0, 1.5", "1.5, 2.0", "2.0, 2.5", 
                         "2.5, 3.0", "3.0, 3.5", "3.5, 4.0", "4.0, 4.5"]
    
    for line in requested_lines:
        if ',' in line:
            # Handle split lines (e.g., "2.5, 3.0")
            lower_line, upper_line = map(float, line.split(','))
            over_prob, under_prob = calculate_win_lose_probs(lower_line, upper_line)
            
            results.extend([
                {
                    "line": f"Over {lower_line}, {upper_line}",
                    "win_prob": over_prob
                },
                {
                    "line": f"Under {lower_line}, {upper_line}",
                    "win_prob": under_prob
                }
            ])
        else:
            # Handle single lines (e.g., "2.5")
            line = float(line)
            if line % 1 == 0:
                # Whole number lines (convert pushes to win/lose)
                over_wins = np.sum(total_goals > line)
                under_wins = np.sum(total_goals < line)
                total_non_push = over_wins + under_wins
                
                over_prob = over_wins / total_non_push
                under_prob = under_wins / total_non_push
                
                results.extend([
                    {
                        "line": f"Over {line}",
                        "win_prob": over_prob
                    },
                    {
                        "line": f"Under {line}",
                        "win_prob": under_prob
                    }
                ])
            else:
                # Half number lines (no pushes possible)
                over_wins = np.sum(total_goals > line)
                over_prob = over_wins / n_sims
                under_prob = 1 - over_prob
                
                results.extend([
                    {
                        "line": f"Over {line}",
                        "win_prob": over_prob
                    },
                    {
                        "line": f"Under {line}",
                        "win_prob": under_prob
                    }
                ])
    
    return pd.DataFrame(results).sort_values('line')

# Example usage:
home_elevenify = 1.51
away_elevenify = 1.06

home_afpl = 1.45
away_afpl = 1.1

home_xg = (0.65*home_elevenify) + (0.35*home_afpl)
away_xg = (0.65*away_elevenify) + (0.35*away_afpl) 

# Get odds for Asian total 2.5, 3.0
odds = predict_goal_line_from_xg( home_xg=0.90, away_xg=1.0, requested_lines=["2.0"])
print(odds)