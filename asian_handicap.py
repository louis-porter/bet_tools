import numpy as np
import pandas as pd


def predict_asian_handicap_from_xg(home_team, away_team, home_xg, away_xg, requested_lines=None, handicaps=None, n_sims=50000, random_seed=42):
    np.random.seed(random_seed)
    
    # Determine favorite and underdog based on xG
    if away_xg > home_xg:
        favorite = away_team
        underdog = home_team
        is_away_favorite = True
    else:
        favorite = home_team
        underdog = away_team
        is_away_favorite = False
    
    # Simulate matches
    home_goals = np.random.poisson(home_xg, size=n_sims)
    away_goals = np.random.poisson(away_xg, size=n_sims)
    
    # Calculate goal difference from favorite's perspective
    goal_diff = away_goals - home_goals if is_away_favorite else home_goals - away_goals
    
    if handicaps is None:
        handicaps = [-3.0, -2.75, -2.5, -2.25, -2.0, -1.75, -1.5, -1.25, -1.0, -0.75,
                    -0.5, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0,
                    2.25, 2.5, 2.75, 3.0]
    
    # Filter handicaps if requested_lines is provided
    if requested_lines is not None:
        handicaps = [h for h in handicaps if h in requested_lines]
    
    results = []
    processed_handicaps = set()
    
    # Handle 0.0 lines if requested
    if requested_lines is None or 0.0 in requested_lines:
        fav_wins = np.sum(goal_diff > 0)
        fav_draws = np.sum(goal_diff == 0)
        dog_wins = np.sum(goal_diff < 0)
        
        fav_prob = (fav_wins + 0.5 * fav_draws) / n_sims
        dog_prob = (dog_wins + 0.5 * fav_draws) / n_sims
        
        results.extend([
            {
                "line": f"{favorite} 0.0",
                "fair_prob": fav_prob
            },
            {
                "line": f"{underdog} 0.0",
                "fair_prob": dog_prob
            }
        ])
        processed_handicaps.add(0.0)
    
    # Process remaining handicaps
    for handicap in handicaps:
        if handicap in processed_handicaps:
            continue
            
        if handicap % 0.5 == 0.25:
            # Handle quarter lines
            lower = np.floor(handicap * 2) / 2
            upper = np.ceil(handicap * 2) / 2
            
            if handicap < 0:
                # Favorite lines
                low_wins = np.sum(goal_diff > -lower)
                low_draws = np.sum(goal_diff == -lower)
                up_wins = np.sum(goal_diff > -upper)
                up_draws = np.sum(goal_diff == -upper)
                
                fav_prob = ((low_wins + 0.5 * low_draws) + (up_wins + 0.5 * up_draws)) / (2 * n_sims)
                dog_prob = 1 - fav_prob  # Complementary probability
                
                results.extend([
                    {
                        "line": f"{favorite} {handicap}",
                        "fair_prob": fav_prob
                    },
                    {
                        "line": f"{underdog} +{abs(handicap)}",
                        "fair_prob": dog_prob
                    }
                ])
            else:
                # Already handled when processing negative handicap
                continue
        else:
            # Handle whole and half lines
            if handicap < 0:
                # Favorite lines
                wins = np.sum(goal_diff > -handicap)
                draws = np.sum(goal_diff == -handicap)
                
                fav_prob = (wins + 0.5 * draws) / n_sims
                dog_prob = 1 - fav_prob  # Complementary probability
                
                results.extend([
                    {
                        "line": f"{favorite} {handicap}",
                        "fair_prob": fav_prob
                    },
                    {
                        "line": f"{underdog} +{abs(handicap)}",
                        "fair_prob": dog_prob
                    }
                ])
            else:
                # Already handled when processing negative handicap
                continue
                
        processed_handicaps.add(handicap)
        processed_handicaps.add(-handicap)
    
    return pd.DataFrame(results).sort_values('line')

home_elevenify =  1.59
away_elevenify =  2.01

home_afpl = 1.61
away_afpl = 2.14

home_xg = (0.65*home_elevenify) + (0.35*home_afpl)
away_xg = (0.65*away_elevenify) + (0.35*away_afpl) 

odds = predict_asian_handicap_from_xg("PRE", "BUR", home_xg=0.90, away_xg=1.0, requested_lines=[-0.25, 0.25])

print(odds)