import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import product

# Strategy descriptions
player_strategy_descriptions = {
    'Aggressive': 'Always shoot the Dealer.',
    'Conservative': 'Shoot self when there is a high chance of drawing a blank shell; otherwise, shoot the Dealer.',
    'Probability-Based': 'Decide based on the probabilities of live vs. blank shells. Shoot self if the chance of drawing a blank is higher.'
}

dealer_strategy_descriptions = {
    'Aggressive': 'Always shoot the player.',
    'Conservative': 'Shoot self when there is a high chance of drawing a blank shell; otherwise, shoot the player.',
    'Probability-Based': 'Decide based on the probabilities of live vs. blank shells. Shoot self if the chance of drawing a blank is higher.',
    'Random': 'Randomly choose to shoot self or the player.'
}

# Strategy functions
def player_aggressive_strategy(L, B, player_lives, dealer_lives):
    return 'shoot_dealer'

def player_conservative_strategy(L, B, player_lives, dealer_lives, threshold=0.7):
    if (L + B) == 0:
        return 'shoot_dealer'
    p_blank = B / (L + B)
    return 'shoot_self' if p_blank > threshold else 'shoot_dealer'

def player_probability_based_strategy(L, B, player_lives, dealer_lives):
    if (L + B) == 0:
        return 'shoot_dealer'
    p_live = L / (L + B)
    p_blank = B / (L + B)
    return 'shoot_self' if p_blank > p_live else 'shoot_dealer'

# Enhanced dealer strategy function with AI behavior settings
def dealer_dynamic_strategy(L, B, dealer_lives, player_lives, risk_tolerance, caution_level, bluff_factor):
    if np.random.rand() < bluff_factor:
        return np.random.choice(['shoot_self', 'shoot_player'])  # Random choice as a bluff

    if (L + B) == 0:
        return 'shoot_player'

    p_blank = B / (L + B)
    if dealer_lives <= player_lives * risk_tolerance:
        # High risk tolerance means the dealer is more aggressive
        return 'shoot_player' if np.random.rand() > p_blank else 'shoot_self'
    else:
        # High caution level means the dealer is more conservative
        return 'shoot_self' if p_blank > caution_level else 'shoot_player'

# Simulation functions
def simulate_buckshot_game(
    rounds,
    live_shells,
    blank_shells,
    initial_player_lives,
    initial_dealer_lives,
    player_strategy,
    dealer_strategy,
    player_threshold=0.7,
    dealer_risk_tolerance=0.5,
    dealer_caution_level=0.7,
    dealer_bluff_factor=0.1
):
    player_wins = dealer_wins = draws = 0
    probability_trends = []  # Track probability at each turn

    for _ in range(rounds):
        winner, game_probabilities = simulate_single_game(
            live_shells, blank_shells, initial_player_lives, initial_dealer_lives,
            player_strategy, dealer_strategy, player_threshold, dealer_risk_tolerance, dealer_caution_level, dealer_bluff_factor
        )
        if winner == 'player':
            player_wins += 1
        elif winner == 'dealer':
            dealer_wins += 1
        else:
            draws += 1
        probability_trends.append(game_probabilities)

    total_games = player_wins + dealer_wins + draws
    player_win_rate = player_wins / total_games * 100
    dealer_win_rate = dealer_wins / total_games * 100
    draw_rate = draws / total_games * 100

    avg_prob_trend = calculate_average_probability_trend(probability_trends)

    return {
        'player_win_rate': player_win_rate,
        'dealer_win_rate': dealer_win_rate,
        'draw_rate': draw_rate,
        'average_prob_trend': avg_prob_trend
    }

def simulate_single_game(
    live_shells, blank_shells, player_lives, dealer_lives,
    player_strategy, dealer_strategy, player_threshold=0.7,
    dealer_risk_tolerance=0.5, dealer_caution_level=0.7, dealer_bluff_factor=0.1
):
    shells = []
    shell_index = 0
    turn = 'player'
    game_probabilities = []

    while player_lives > 0 and dealer_lives > 0:
        if shell_index >= len(shells):
            shells = ['live'] * live_shells + ['blank'] * blank_shells
            np.random.shuffle(shells)
            shell_index = 0

        L = shells[shell_index:].count('live')
        B = shells[shell_index:].count('blank')
        total_shells = L + B
        p_live = L / total_shells if total_shells > 0 else 0
        p_blank = B / total_shells if total_shells > 0 else 0
        game_probabilities.append({'p_live': p_live, 'p_blank': p_blank})

        current_shell = shells[shell_index]
        if turn == 'player':
            action = player_strategy(L, B, player_lives, dealer_lives, player_threshold) if player_strategy == player_conservative_strategy else player_strategy(L, B, player_lives, dealer_lives)
            if action == 'shoot_self':
                player_lives -= 1 if current_shell == 'live' else 0
            else:
                dealer_lives -= 1 if current_shell == 'live' else 0
            turn = 'dealer' if current_shell == 'blank' else turn
        else:
            action = dealer_strategy(L, B, dealer_lives, player_lives, dealer_risk_tolerance, dealer_caution_level, dealer_bluff_factor)
            if action == 'shoot_self':
                dealer_lives -= 1 if current_shell == 'live' else 0
            else:
                player_lives -= 1 if current_shell == 'live' else 0
            turn = 'player' if current_shell == 'blank' else turn

        if action in ['shoot_self', 'shoot_dealer', 'shoot_player']:
            shell_index += 1

    winner = 'dealer' if player_lives <= 0 else 'player' if dealer_lives <= 0 else 'draw'
    return winner, game_probabilities

def main():
    st.title("Buckshot Roulette Simulation with Enhanced Dealer AI")

    # Create tabs for simulation and rules
    tab_simulation, tab_rules = st.tabs(["Simulation", "Rules"])

    # Rules Tab Content
    with tab_rules:
        st.header("Game Rules for Buckshot Roulette Simulation")
        st.markdown("""
        In this simulation of Buckshot Roulette, the following rules and conditions are applied:
        
        1. **Game Structure**:
           - The game consists of a shotgun loaded with a combination of live and blank shells in a random order.
           - The player and the Dealer take turns choosing to shoot either themselves or their opponent.

        2. **Rounds and Reloading**:
           - If all shells are used up without a winner, the shotgun is reloaded with a new random order of live and blank shells.
           - The number of live and blank shells can be adjusted by the user.
           - The simulation ends when one party (either the player or the Dealer) depletes all of their "lives."

        3. **Lives**:
           - Both the player and Dealer start with an initial number of lives, which can be adjusted in the settings.
           - A live shell shot reduces the chosen target’s lives by one.

        4. **Turn-Based Actions**:
           - On each turn, the player or Dealer can choose to shoot themselves or the other.
           - The choice of shooting depends on the selected strategy:
             - **Aggressive**: Always shoot the opponent.
             - **Conservative**: Shoot themselves if there is a high probability of drawing a blank shell; otherwise, shoot the opponent.
             - **Probability-Based**: Based on the probability of live vs. blank shells, shoot themselves if the chance of a blank is higher.

        5. **Outcome Determination**:
           - A blank shell shot results in a missed turn but does not reduce lives.
           - A live shell shot reduces the target’s lives by one.
           - The simulation tracks the cumulative outcomes over the defined number of rounds.
           - The game outcome is either a win for the player, a win for the Dealer, or a draw if neither loses all lives in the set rounds.

        6. **Visualization**:
           - This simulation generates a series of visualizations, including win rates by strategy, cumulative win rates over time, and the probability of drawing live or blank shells across turns.
        """)

    # Simulation Tab Content
    with tab_simulation:
        st.sidebar.header("Simulation Parameters")
        rounds = st.sidebar.number_input("Number of rounds to simulate", min_value=100, max_value=100000, value=1000, step=100)
        live_shells = st.sidebar.slider("Number of live shells", min_value=1, max_value=10, value=2)
        blank_shells = st.sidebar.slider("Number of blank shells", min_value=1, max_value=10, value=2)
        initial_player_lives = st.sidebar.slider("Player initial lives", min_value=1, max_value=10, value=2)
        initial_dealer_lives = st.sidebar.slider("Dealer initial lives", min_value=1, max_value=10, value=2)

        st.sidebar.header("Strategy Selection")
        player_strategy_option = st.sidebar.selectbox("Select Player Strategy", ("Aggressive", "Conservative", "Probability-Based"))
        player_threshold = st.sidebar.slider("Player Conservative Threshold", min_value=0.0, max_value=1.0, value=0.7) if player_strategy_option == 'Conservative' else 0.7

        st.sidebar.header("Dealer AI Behavior Settings")
        dealer_risk_tolerance = st.sidebar.slider("Dealer Risk Tolerance", min_value=0.0, max_value=1.0, value=0.5)
        dealer_caution_level = st.sidebar.slider("Dealer Caution Level", min_value=0.0, max_value=1.0, value=0.7)
        dealer_bluff_factor = st.sidebar.slider("Dealer Bluff Factor", min_value=0.0, max_value=1.0, value=0.1)

        # Assign selected strategies
        player_strategies = {
            'Aggressive': player_aggressive_strategy,
            'Conservative': player_conservative_strategy,
            'Probability-Based': player_probability_based_strategy
        }
        selected_player_strategy = player_strategies[player_strategy_option]

        # Run the simulation and display results
        if st.button("Run Simulation"):
            results = simulate_buckshot_game(
                rounds, live_shells, blank_shells, initial_player_lives, initial_dealer_lives,
                selected_player_strategy, dealer_dynamic_strategy,
                player_threshold, dealer_risk_tolerance, dealer_caution_level, dealer_bluff_factor
            )
            st.write(f"Player Win Rate: **{results['player_win_rate']:.2f}%**")
            st.write(f"Dealer Win Rate: **{results['dealer_win_rate']:.2f}%**")
            st.write(f"Draw Rate: **{results['draw_rate']:.2f}%**")

if __name__ == "__main__":
    main()


