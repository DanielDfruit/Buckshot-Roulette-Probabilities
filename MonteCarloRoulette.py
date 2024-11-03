import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import permutations

# Strategy descriptions
player_strategy_descriptions = {
    'Aggressive': 'Always shoot the Dealer when it is your turn.',
    'Conservative': 'Shoot self when there is a high chance of drawing a blank shell; otherwise, shoot the Dealer. Threshold is dynamically adjusted based on remaining shells.',
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

def player_conservative_strategy(L, B, player_lives, dealer_lives):
    if (L + B) == 0:
        return 'shoot_dealer'
    # Dynamic threshold based on the remaining number of shells
    threshold = 0.5 + (B / (L + B)) * 0.5  # Adjust threshold dynamically based on remaining blank shells
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
        return 'shoot_player' if np.random.rand() > p_blank else 'shoot_self'
    else:
        return 'shoot_self' if p_blank > caution_level else 'shoot_player'

# Shell reload function
def reload_shells(live_shells, blank_shells):
    # Ensure there are at least two shells, at least one of which must be live, and a maximum of 8 shells
    total_shells = min(max(2, live_shells + blank_shells), 8)
    live_count = max(1, min(live_shells, total_shells - 1))  # At least one shell must be live, but cannot exceed total_shells - 1
    blank_count = total_shells - live_count
    shells = ['live'] * live_count + ['blank'] * blank_count
    np.random.shuffle(shells)
    return shells

# Generate all possible shell permutations
def generate_all_permutations(live_shells, blank_shells):
    shells = ['live'] * live_shells + ['blank'] * blank_shells
    return list(set(permutations(shells)))  # Use set to avoid duplicate permutations

# Simulation functions

def simulate_all_possible_games(
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
    all_permutations = generate_all_permutations(live_shells, blank_shells)
    player_wins = dealer_wins = draws = 0

    for shell_order in all_permutations:
        winner, _ = simulate_single_game(
            shell_order, initial_player_lives, initial_dealer_lives,
            player_strategy, dealer_strategy, player_threshold, dealer_risk_tolerance, dealer_caution_level, dealer_bluff_factor
        )
        if winner == 'player':
            player_wins += 1
        elif winner == 'dealer':
            dealer_wins += 1
        else:
            draws += 1

    total_games = player_wins + dealer_wins + draws
    player_win_rate = player_wins / total_games * 100
    dealer_win_rate = dealer_wins / total_games * 100
    draw_rate = draws / total_games * 100

    return {
        'player_win_rate': player_win_rate,
        'dealer_win_rate': dealer_win_rate,
        'draw_rate': draw_rate
    }

def simulate_single_game(
    shell_order, player_lives, dealer_lives,
    player_strategy, dealer_strategy, player_threshold=0.7,
    dealer_risk_tolerance=0.5, dealer_caution_level=0.7, dealer_bluff_factor=0.1
):
    shell_index = 0
    turn = 'player'
    game_probabilities = []

    while player_lives > 0 and dealer_lives > 0 and shell_index < len(shell_order):
        current_shell = shell_order[shell_index]
        L = shell_order[shell_index:].count('live')
        B = shell_order[shell_index:].count('blank')
        total_shells = L + B
        p_live = L / total_shells if total_shells > 0 else 0
        p_blank = B / total_shells if total_shells > 0 else 0
        game_probabilities.append({'p_live': p_live, 'p_blank': p_blank})

        if turn == 'player':
            action = player_strategy(L, B, player_lives, dealer_lives) if player_strategy == player_conservative_strategy else player_strategy(L, B, player_lives, dealer_lives)
            if action == 'shoot_self':
                player_lives -= 1 if current_shell == 'live' else 0
            else:
                dealer_lives -= 1 if current_shell == 'live' else 0
        else:
            action = dealer_strategy(L, B, dealer_lives, player_lives, dealer_risk_tolerance, dealer_caution_level, dealer_bluff_factor)
            if action == 'shoot_self':
                dealer_lives -= 1 if current_shell == 'live' else 0
            else:
                player_lives -= 1 if current_shell == 'live' else 0

        # Always switch turns after each shot
        turn = 'dealer' if turn == 'player' else 'player'
        shell_index += 1

    winner = 'dealer' if player_lives <= 0 else 'player' if dealer_lives <= 0 else 'draw'
    return winner, game_probabilities

def main():
    st.title("Buckshot Roulette Simulation with Exhaustive Permutations")

    # Create tabs for simulation and rules
    tab_simulation, tab_rules, tab_charts = st.tabs(["Simulation", "Rules", "Charts"])

    # Rules Tab Content
    with tab_rules:
        st.header("Game Rules for Buckshot Roulette Simulation")
        st.markdown("""
        In this simulation of Buckshot Roulette, the following rules and conditions are applied:
        
        1. **Game Structure**:
           - The game consists of a shotgun loaded with a combination of live and blank shells in a random order.
           - The player and the Dealer take turns choosing to shoot either themselves or their opponent.

        2. **Rounds and Reloading**:
           - The game explores every possible combination of live and blank shells to determine the outcome.

        3. **Lives**:
           - Both the player and Dealer start with an initial number of lives, which can be adjusted in the settings.
           - A live shell shot reduces the chosen target’s lives by one.

        4. **Turn-Based Actions**:
           - On each turn, the player or Dealer can choose to shoot themselves or the other.
           - The choice of shooting depends on the selected strategy:
             - **Aggressive**: Always shoot the opponent.
             - **Conservative**: Shoot themselves if there is a high probability of drawing a blank shell; otherwise, shoot the opponent.
             - **Probability-Based**: Based on the probability of live vs. blank shells, shoot themselves if the chance of a blank is higher.

        5. **Dealer AI Behavior Settings**:
           - **Risk Tolerance**: Adjusts the Dealer’s aggressiveness based on relative lives. Higher values mean the Dealer will take more risks.
           - **Caution Level**: Dictates how likely the Dealer is to shoot themselves if there's a high chance of a blank shell.
           - **Bluff Factor**: Adds unpredictability by occasionally making the Dealer ignore probabilities and choose randomly.
        """)

    # Simulation Tab Content
    with tab_simulation:
        st.sidebar.header("Simulation Parameters")
        live_shells = st.sidebar.slider("Number of live shells", min_value=1, max_value=4, value=1)
        blank_shells = st.sidebar.slider("Number of blank shells", min_value=1, max_value=4, value=4)
        initial_player_lives = st.sidebar.slider("Player initial lives", min_value=1, max_value=10, value=2)
        initial_dealer_lives = st.sidebar.slider("Dealer initial lives", min_value=1, max_value=10, value=2)

        st.sidebar.header("Strategy Selection")
        player_strategy_option = st.sidebar.selectbox("Select Player Strategy", ("Aggressive", "Conservative", "Probability-Based"))
        player_threshold = st.sidebar.slider("Player Conservative Threshold", min_value=0.0, max_value=1.0, value=0.7) if player_strategy_option == 'Conservative' else 0.7

        st.sidebar.header("Dealer AI Behavior Settings")
        dealer_risk_tolerance = st.sidebar.slider("Dealer Risk Tolerance", min_value=0.0, max_value=1.0, value=0.5, help="Adjusts the Dealer’s aggressiveness based on relative lives. Higher values mean the Dealer will take more risks.")
        dealer_caution_level = st.sidebar.slider("Dealer Caution Level", min_value=0.0, max_value=1.0, value=0.7, help="Determines the likelihood of the Dealer shooting themselves if a blank shell is likely.")
        dealer_bluff_factor = st.sidebar.slider("Dealer Bluff Factor", min_value=0.0, max_value=1.0, value=0.1, help="Adds unpredictability by occasionally making the Dealer choose randomly.")

        # Assign selected strategies
        player_strategies = {
            'Aggressive': player_aggressive_strategy,
            'Conservative': player_conservative_strategy,
            'Probability-Based': player_probability_based_strategy
        }
        selected_player_strategy = player_strategies[player_strategy_option]

        # Run the simulation and display results
        if st.button("Run Simulation"):
            results = simulate_all_possible_games(
                live_shells, blank_shells, initial_player_lives, initial_dealer_lives,
                selected_player_strategy, dealer_dynamic_strategy,
                player_threshold, dealer_risk_tolerance, dealer_caution_level, dealer_bluff_factor
            )
            st.write(f"Player Win Rate: **{results['player_win_rate']:.2f}%**")
            st.write(f"Dealer Win Rate: **{results['dealer_win_rate']:.2f}%**")
            st.write(f"Draw Rate: **{results['draw_rate']:.2f}%**")

    # Charts Tab Content
    with tab_charts:
        st.header("Charts and Analysis")
        st.markdown("""
        Here you can visualize the results and statistics from the simulation.
        """)
        # Win Probability Heatmap for Player vs Dealer Strategies
        st.subheader("Win Probability Heatmap for Strategies")
        strategy_combinations = [(p, d) for p in player_strategies.keys() for d in dealer_strategy_descriptions.keys()]
        win_rates = [
            simulate_all_possible_games(
                live_shells, blank_shells, initial_player_lives, initial_dealer_lives,
                player_strategies[p], dealer_dynamic_strategy,
                player_threshold, dealer_risk_tolerance, dealer_caution_level, dealer_bluff_factor
            )['player_win_rate'] for p, d in strategy_combinations
        ]

        heatmap_data = pd.DataFrame(
            np.array(win_rates).reshape(len(player_strategies), len(dealer_strategy_descriptions)),
            index=player_strategies.keys(),
            columns=dealer_strategy_descriptions.keys()
        )

        fig, ax = plt.subplots()
        sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        ax.set_xlabel("Dealer Strategy")
        ax.set_ylabel("Player Strategy")
        ax.set_title("Player Win Rate (%) by Strategy Combination")
        st.pyplot(fig)

        # Player vs Dealer Lives Difference Chart
        st.subheader("Player vs Dealer Lives Over Game Progression")
        avg_lives_diff = []

        for shell_order in generate_all_permutations(live_shells, blank_shells):
            _, game_probabilities = simulate_single_game(
                shell_order, initial_player_lives, initial_dealer_lives,
                selected_player_strategy, dealer_dynamic_strategy,
                player_threshold, dealer_risk_tolerance, dealer_caution_level, dealer_bluff_factor
            )
            avg_lives_diff.append(game_probabilities)

        avg_diff_data = [np.mean([prob['p_live'] - prob['p_blank'] for prob in game]) for game in avg_lives_diff]
        fig, ax = plt.subplots()
        ax.plot(range(1, len(avg_diff_data) + 1), avg_diff_data, label="Average Lives Difference", color="green", marker='o')
        ax.set_xlabel("Turn Number")
        ax.set_ylabel("Average Lives Difference (Player - Dealer)")
        ax.set_title("Player vs Dealer Lives Difference Over Game Turns")
        st.pyplot(fig)

if __name__ == "__main__":
    main()
