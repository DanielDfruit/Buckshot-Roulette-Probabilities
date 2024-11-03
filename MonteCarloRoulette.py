import streamlit as st
import numpy as np
import pandas as pd
from itertools import permutations

# Game simulation functions
def generate_all_permutations(live_shells, blank_shells):
    shells = ['live'] * live_shells + ['blank'] * blank_shells
    return list(set(permutations(shells)))  # Use set to avoid duplicate permutations

def simulate_game_states(
    shell_order,
    player_lives,
    dealer_lives,
    shell_index,
    current_turn,
    results,
    path=[]
):
    """
    Recursively simulate all possible game states from the current state.
    """
    if player_lives <= 0:
        results['dealer_wins'] += 1
        return
    if dealer_lives <= 0:
        results['player_wins'] += 1
        return
    if shell_index >= len(shell_order):
        results['draws'] += 1
        return

    current_shell = shell_order[shell_index]

    # Determine possible actions
    actions = ['shoot_self', 'shoot_opponent']

    for action in actions:
        new_player_lives = player_lives
        new_dealer_lives = dealer_lives
        new_shell_index = shell_index + 1
        new_turn = 'dealer' if current_turn == 'player' else 'player'

        if current_turn == 'player':
            if action == 'shoot_self':
                if current_shell == 'live':
                    new_player_lives -= 1
                # Retain turn if blank shell
                else:
                    new_turn = 'player'
            else:  # shoot_opponent
                if current_shell == 'live':
                    new_dealer_lives -= 1
        else:  # dealer's turn
            if action == 'shoot_self':
                if current_shell == 'live':
                    new_dealer_lives -= 1
            else:  # shoot_opponent
                if current_shell == 'live':
                    new_player_lives -= 1

        simulate_game_states(
            shell_order,
            new_player_lives,
            new_dealer_lives,
            new_shell_index,
            new_turn,
            results,
            path + [(current_turn, action, current_shell)]
        )

def simulate_all_possible_games(
    live_shells,
    blank_shells,
    initial_player_lives,
    initial_dealer_lives
):
    all_permutations = generate_all_permutations(live_shells, blank_shells)
    total_results = {'player_wins': 0, 'dealer_wins': 0, 'draws': 0}

    for shell_order in all_permutations:
        results = {'player_wins': 0, 'dealer_wins': 0, 'draws': 0}
        # Start the game with both possible first turns
        for first_turn in ['player', 'dealer']:
            simulate_game_states(
                shell_order,
                initial_player_lives,
                initial_dealer_lives,
                0,
                first_turn,
                results
            )
        total_results['player_wins'] += results['player_wins']
        total_results['dealer_wins'] += results['dealer_wins']
        total_results['draws'] += results['draws']

    total_games = total_results['player_wins'] + total_results['dealer_wins'] + total_results['draws']
    player_win_rate = total_results['player_wins'] / total_games * 100
    dealer_win_rate = total_results['dealer_wins'] / total_games * 100
    draw_rate = total_results['draws'] / total_games * 100

    return {
        'player_win_rate': player_win_rate,
        'dealer_win_rate': dealer_win_rate,
        'draw_rate': draw_rate
    }

def main():
    st.title("Buckshot Roulette Simulation with All Possible Permutations and Turns")

    st.sidebar.header("Simulation Parameters")
    max_shells = 5  # Reduced for computational feasibility
    live_shells = st.sidebar.slider("Number of live shells", min_value=1, max_value=max_shells, value=1)
    blank_shells = st.sidebar.slider("Number of blank shells", min_value=1, max_value=max_shells - live_shells, value=2)
    total_shells = live_shells + blank_shells

    initial_player_lives = st.sidebar.slider("Player initial lives", min_value=1, max_value=5, value=2)
    initial_dealer_lives = st.sidebar.slider("Dealer initial lives", min_value=1, max_value=5, value=2)

    if st.button("Run Simulation"):
        with st.spinner('Simulating...'):
            results = simulate_all_possible_games(
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives
            )
        st.write(f"Player Win Rate: **{results['player_win_rate']:.2f}%**")
        st.write(f"Dealer Win Rate: **{results['dealer_win_rate']:.2f}%**")
        st.write(f"Draw Rate: **{results['draw_rate']:.2f}%**")

if __name__ == "__main__":
    main()

