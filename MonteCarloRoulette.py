import streamlit as st
import numpy as np
import pandas as pd
from itertools import permutations
import altair as alt

# Strategy descriptions
player_strategy_descriptions = {
    'Aggressive': 'Always shoot the Dealer when it is your turn.',
    'Conservative': 'Shoot self when there is a high chance of drawing a blank shell; otherwise, shoot the Dealer.',
    'Probability-Based': 'Decide based on the probabilities of live vs. blank shells. Shoot self if the chance of drawing a blank is higher.'
}

dealer_strategy_descriptions = {
    'Aggressive': 'Always shoot the player.',
    'Conservative': 'Shoot self when there is a high chance of drawing a blank shell; otherwise, shoot the player.',
    'Probability-Based': 'Decide based on the probabilities of live vs. blank shells. Shoot self if the chance of drawing a blank is higher.'
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

# Dealer strategy functions
def dealer_aggressive_strategy(L, B, dealer_lives, player_lives):
    return 'shoot_player'

def dealer_conservative_strategy(L, B, dealer_lives, player_lives):
    if (L + B) == 0:
        return 'shoot_player'
    threshold = 0.5 + (B / (L + B)) * 0.5
    p_blank = B / (L + B)
    return 'shoot_self' if p_blank > threshold else 'shoot_player'

def dealer_probability_based_strategy(L, B, dealer_lives, player_lives):
    if (L + B) == 0:
        return 'shoot_player'
    p_live = L / (L + B)
    p_blank = B / (L + B)
    return 'shoot_self' if p_blank > p_live else 'shoot_player'

# Generate all possible shell permutations
def generate_all_permutations(live_shells, blank_shells):
    shells = ['live'] * live_shells + ['blank'] * blank_shells
    return list(set(permutations(shells)))  # Use set to avoid duplicate permutations

# Simulation functions
def simulate_game(shell_order, player_lives, dealer_lives, player_strategy, dealer_strategy):
    current_player_lives = player_lives
    current_dealer_lives = dealer_lives
    shell_index = 0
    current_turn = 'player'

    game_log = []  # To keep track of each action and outcome

    while current_player_lives > 0 and current_dealer_lives > 0 and shell_index < len(shell_order):
        current_shell = shell_order[shell_index]
        L = shell_order[shell_index:].count('live')
        B = shell_order[shell_index:].count('blank')

        if current_turn == 'player':
            action = player_strategy(L, B, current_player_lives, current_dealer_lives)
            if action == 'shoot_self':
                if current_shell == 'live':
                    current_player_lives -= 1
                game_log.append(f"**Player** shoots self with {'live' if current_shell == 'live' else 'blank'} shell")
            else:
                if current_shell == 'live':
                    current_dealer_lives -= 1
                game_log.append(f"**Player** shoots dealer with {'live' if current_shell == 'live' else 'blank'} shell")
            current_turn = 'dealer'
        else:
            action = dealer_strategy(L, B, current_dealer_lives, current_player_lives)
            if action == 'shoot_self':
                if current_shell == 'live':
                    current_dealer_lives -= 1
                game_log.append(f"**Dealer** shoots self with {'live' if current_shell == 'live' else 'blank'} shell")
            else:
                if current_shell == 'live':
                    current_player_lives -= 1
                game_log.append(f"**Dealer** shoots player with {'live' if current_shell == 'live' else 'blank'} shell")
            current_turn = 'player'

        shell_index += 1

    if current_player_lives <= 0:
        game_log.append("**Dealer** wins")
        return 'dealer', game_log
    elif current_dealer_lives <= 0:
        game_log.append("**Player** wins")
        return 'player', game_log
    else:
        game_log.append("Draw")
        return 'draw', game_log

# Main simulation loop
def simulate_all_possible_games(
    live_shells,
    blank_shells,
    initial_player_lives,
    initial_dealer_lives,
    player_strategy,
    dealer_strategy
):
    all_permutations = generate_all_permutations(live_shells, blank_shells)
    player_wins = dealer_wins = draws = 0
    detailed_logs = []

    for shell_order in all_permutations:
        result, game_log = simulate_game(
            shell_order, initial_player_lives, initial_dealer_lives,
            player_strategy, dealer_strategy
        )
        detailed_logs.append((shell_order, game_log))
        if result == 'player':
            player_wins += 1
        elif result == 'dealer':
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
        'draw_rate': draw_rate,
        'total_results': {'player_wins': player_wins, 'dealer_wins': dealer_wins, 'draws': draws},
        'detailed_logs': detailed_logs
    }

# Streamlit app
def main():
    st.title("Buckshot Roulette Simulation with Different Play Styles")

    st.sidebar.header("Simulation Parameters")
    max_shells = 8  # Reduced for computational feasibility
    live_shells = st.sidebar.slider("Number of live shells", min_value=1, max_value=max_shells, value=1)
    blank_shells = st.sidebar.slider("Number of blank shells", min_value=1, max_value=max_shells - live_shells, value=1)
    total_shells = live_shells + blank_shells

    initial_player_lives = st.sidebar.slider("Player initial lives", min_value=1, max_value=5, value=1)
    initial_dealer_lives = st.sidebar.slider("Dealer initial lives", min_value=1, max_value=5, value=1)

    st.sidebar.header("Strategy Selection")
    player_strategy_option = st.sidebar.selectbox("Select Player Strategy", ("Aggressive", "Conservative", "Probability-Based"))
    dealer_strategy_option = st.sidebar.selectbox("Select Dealer Strategy", ("Aggressive", "Conservative", "Probability-Based"))

    # Assign selected strategies
    player_strategies = {
        'Aggressive': player_aggressive_strategy,
        'Conservative': player_conservative_strategy,
        'Probability-Based': player_probability_based_strategy
    }
    dealer_strategies = {
        'Aggressive': dealer_aggressive_strategy,
        'Conservative': dealer_conservative_strategy,
        'Probability-Based': dealer_probability_based_strategy
    }

    selected_player_strategy = player_strategies[player_strategy_option]
    selected_dealer_strategy = dealer_strategies[dealer_strategy_option]

    # Run the simulation and display results
    if st.button("Run Simulation"):
        with st.spinner('Simulating...'):
            results = simulate_all_possible_games(
                live_shells, blank_shells, initial_player_lives, initial_dealer_lives,
                selected_player_strategy, selected_dealer_strategy
            )
        st.success('Simulation Complete!')

        st.write(f"Player Win Rate: <span style='color: #1f77b4; font-weight: bold;'>{results['player_win_rate']:.2f}%</span>")
        st.write(f"Dealer Win Rate: <span style='color: #ff7f0e; font-weight: bold;'>{results['dealer_win_rate']:.2f}%</span>")
        st.write(f"Draw Rate: **{results['draw_rate']:.2f}%**")

        # Create a DataFrame for plotting
        data = pd.DataFrame({
            'Outcome': ['Player Wins', 'Dealer Wins', 'Draws'],
            'Win Rate (%)': [
                results['player_win_rate'],
                results['dealer_win_rate'],
                results['draw_rate']
            ]
        })

        # Create a bar chart using Altair
        chart = alt.Chart(data).mark_bar().encode(
            color=alt.Color('Outcome', scale=alt.Scale(domain=['Player Wins', 'Dealer Wins', 'Draws'], range=['#1f77b4', '#ff7f0e', '#2ca02c'])),
            x=alt.X('Outcome', sort=None),
            y='Win Rate (%)',
            color='Outcome'
        ).properties(
            width=600,
            height=400,
            title='Simulation Results'
        )

        st.altair_chart(chart, use_container_width=True)

        # Optionally, display the total counts
        st.subheader("Total Outcomes")
        st.write(f"Total Player Wins: <span style='color: #1f77b4; font-weight: bold;'>{results['total_results']['player_wins']}</span>")
        st.write(f"Total Dealer Wins: <span style='color: #ff7f0e; font-weight: bold;'>{results['total_results']['dealer_wins']}</span>")
        st.write(f"Total Draws: **{results['total_results']['draws']}**")

        # Display detailed logs for each game
        st.subheader("Detailed Game Outcomes")
        for shell_order, log in results['detailed_logs']:
            st.write(f"Shell Order: {shell_order}")
            for entry in log:
                st.write(entry)
            st.write("---")

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
