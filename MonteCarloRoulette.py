import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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
    if p_blank > threshold:
        return 'shoot_self'
    else:
        return 'shoot_dealer'

def player_probability_based_strategy(L, B, player_lives, dealer_lives):
    if (L + B) == 0:
        return 'shoot_dealer'
    p_live = L / (L + B)
    p_blank = B / (L + B)
    if p_blank > p_live:
        return 'shoot_self'
    else:
        return 'shoot_dealer'

def dealer_aggressive_strategy(L, B, dealer_lives, player_lives):
    return 'shoot_player'

def dealer_conservative_strategy(L, B, dealer_lives, player_lives, threshold=0.7):
    if (L + B) == 0:
        return 'shoot_player'
    p_blank = B / (L + B)
    if p_blank > threshold:
        return 'shoot_self'
    else:
        return 'shoot_player'

def dealer_probability_based_strategy(L, B, dealer_lives, player_lives):
    if (L + B) == 0:
        return 'shoot_player'
    p_live = L / (L + B)
    p_blank = B / (L + B)
    if p_blank > p_live:
        return 'shoot_self'
    else:
        return 'shoot_player'

def dealer_random_strategy(L, B, dealer_lives, player_lives):
    return np.random.choice(['shoot_self', 'shoot_player'])

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
    dealer_threshold=0.7
):
    # Initialize data collection
    player_wins = 0
    dealer_wins = 0
    draws = 0
    probability_trends = []  # Track probability at each turn

    # Simulate games
    for _ in range(rounds):
        winner, game_probabilities = simulate_single_game(
            live_shells,
            blank_shells,
            initial_player_lives,
            initial_dealer_lives,
            player_strategy,
            dealer_strategy,
            player_threshold,
            dealer_threshold
        )
        # Update win counts
        if winner == 'player':
            player_wins += 1
        elif winner == 'dealer':
            dealer_wins += 1
        else:
            draws += 1

        # Append game probabilities
        probability_trends.append(game_probabilities)

    # Calculate win rates
    total_games = player_wins + dealer_wins + draws
    player_win_rate = player_wins / total_games * 100
    dealer_win_rate = dealer_wins / total_games * 100
    draw_rate = draws / total_games * 100

    # Aggregate probabilities over all games
    avg_prob_trend = calculate_average_probability_trend(probability_trends)

    return {
        'player_win_rate': player_win_rate,
        'dealer_win_rate': dealer_win_rate,
        'draw_rate': draw_rate,
        'average_prob_trend': avg_prob_trend
    }

def simulate_single_game(
    live_shells,
    blank_shells,
    player_lives,
    dealer_lives,
    player_strategy,
    dealer_strategy,
    player_threshold=0.7,
    dealer_threshold=0.7
):
    # Initialize game state
    shells = []
    shell_index = 0  # Tracks the current shell
    turn = 'player'  # 'player' or 'dealer'
    game_probabilities = []  # Track probability at each turn

    while player_lives > 0 and dealer_lives > 0:
        # Check if we need to reload the shotgun
        if shell_index >= len(shells):
            # Reload the shotgun
            shells = ['live'] * live_shells + ['blank'] * blank_shells
            np.random.shuffle(shells)
            shell_index = 0  # Reset the shell index

        L = shells[shell_index:].count('live')
        B = shells[shell_index:].count('blank')
        total_shells = L + B
        if total_shells > 0:
            p_live = L / total_shells
            p_blank = B / total_shells
        else:
            p_live = p_blank = 0

        # Record the probability of drawing a live and blank shell
        game_probabilities.append({'p_live': p_live, 'p_blank': p_blank})

        current_shell = shells[shell_index]
        if turn == 'player':
            # Decide action based on strategy
            if player_strategy == player_conservative_strategy:
                action = player_strategy(L, B, player_lives, dealer_lives, threshold=player_threshold)
            else:
                action = player_strategy(L, B, player_lives, dealer_lives)

            if action == 'shoot_self':
                if current_shell == 'live':
                    player_lives -= 1
                    turn = 'dealer'
                else:
                    pass  # Player retains the turn
            elif action == 'shoot_dealer':
                if current_shell == 'live':
                    dealer_lives -= 1
                    turn = 'dealer'
                else:
                    turn = 'dealer'
            else:
                raise ValueError("Invalid action from player")
        elif turn == 'dealer':
            # Decide action based on strategy
            if dealer_strategy == dealer_conservative_strategy:
                action = dealer_strategy(L, B, dealer_lives, player_lives, threshold=dealer_threshold)
            else:
                action = dealer_strategy(L, B, dealer_lives, player_lives)

            if action == 'shoot_self':
                if current_shell == 'live':
                    dealer_lives -= 1
                    turn = 'player'
                else:
                    pass  # Dealer retains the turn
            elif action == 'shoot_player':
                if current_shell == 'live':
                    player_lives -= 1
                    turn = 'player'
                else:
                    turn = 'player'
            else:
                raise ValueError("Invalid action from dealer")
        else:
            raise ValueError("Invalid turn")

        # Update shell index
        if action in ['shoot_self', 'shoot_dealer', 'shoot_player']:
            shell_index += 1

    # Determine the winner
    if player_lives <= 0:
        winner = 'dealer'
    elif dealer_lives <= 0:
        winner = 'player'
    else:
        winner = 'draw'

    return winner, game_probabilities

def calculate_average_probability_trend(probability_trends):
    """Calculate average probability trend across all games."""
    max_turns = max(len(game) for game in probability_trends)
    avg_prob_trend = []

    for turn in range(max_turns):
        p_live_sum = p_blank_sum = count = 0
        for game in probability_trends:
            if turn < len(game):
                p_live_sum += game[turn]['p_live']
                p_blank_sum += game[turn]['p_blank']
                count += 1

        if count > 0:
            avg_prob_trend.append({'p_live': p_live_sum / count, 'p_blank': p_blank_sum / count})
        else:
            avg_prob_trend.append({'p_live': None, 'p_blank': None})

    return avg_prob_trend

# Streamlit App Code
def main():
    st.title("Buckshot Roulette Simulation with Probability Analysis")

    st.sidebar.header("Simulation Parameters")
    rounds = st.sidebar.number_input("Number of rounds to simulate", min_value=100, max_value=100000, value=1000, step=100, key='rounds_input')
    live_shells = st.sidebar.slider("Number of live shells", min_value=1, max_value=10, value=2, key='live_shells_slider')
    blank_shells = st.sidebar.slider("Number of blank shells", min_value=1, max_value=10, value=2, key='blank_shells_slider')
    initial_player_lives = st.sidebar.slider("Player initial lives", min_value=1, max_value=10, value=2, key='player_lives_slider')
    initial_dealer_lives = st.sidebar.slider("Dealer initial lives", min_value=1, max_value=10, value=2, key='dealer_lives_slider')

    st.sidebar.header("Strategy Selection")
    player_strategy_option = st.sidebar.selectbox("Select Player Strategy", ("Aggressive", "Conservative", "Probability-Based"), key='player_strategy_select')
    player_threshold = st.sidebar.slider("Player Conservative Threshold", min_value=0.0, max_value=1.0, value=0.7, key='player_threshold_slider') if player_strategy_option == 'Conservative' else 0.7
    dealer_strategy_option = st.sidebar.selectbox("Select Dealer Strategy", ("Aggressive", "Conservative", "Probability-Based", "Random"), key='dealer_strategy_select')
    dealer_threshold = st.sidebar.slider("Dealer Conservative Threshold", min_value=0.0, max_value=1.0, value=0.7, key='dealer_threshold_slider') if dealer_strategy_option == 'Conservative' else 0.7

    player_strategies = {'Aggressive': player_aggressive_strategy, 'Conservative': player_conservative_strategy, 'Probability-Based': player_probability_based_strategy}
    dealer_strategies = {'Aggressive': dealer_aggressive_strategy, 'Conservative': dealer_conservative_strategy, 'Probability-Based': dealer_probability_based_strategy, 'Random': dealer_random_strategy}
    selected_player_strategy = player_strategies[player_strategy_option]
    selected_dealer_strategy = dealer_strategies[dealer_strategy_option]

    if st.button("Run Simulation"):
        with st.spinner('Simulating games...'):
            results = simulate_buckshot_game(
                rounds, live_shells, blank_shells, initial_player_lives, initial_dealer_lives,
                selected_player_strategy, selected_dealer_strategy, player_threshold, dealer_threshold
            )

        st.subheader("Simulation Results")
        st.write(f"Player Win Rate: **{results['player_win_rate']:.2f}%**")
        st.write(f"Dealer Win Rate: **{results['dealer_win_rate']:.2f}%**")
        st.write(f"Draw Rate: **{results['draw_rate']:.2f}%**")

        # Plot probability trends
        st.subheader("Probability Trend of Drawing a Live or Blank Shell Over Turns")
        avg_prob_trend = results['average_prob_trend']
        turns = range(1, len(avg_prob_trend) + 1)
        p_live = [prob['p_live'] for prob in avg_prob_trend]
        p_blank = [prob['p_blank'] for prob in avg_prob_trend]

        fig, ax = plt.subplots()
        ax.plot(turns, p_live, label='Probability of Live Shell', marker='o')
        ax.plot(turns, p_blank, label='Probability of Blank Shell', marker='o')
        ax.set_xlabel("Turn Number")
        ax.set_ylabel("Probability")
        ax.legend()
        st.pyplot(fig)

        # Generate Heatmap
        st.subheader("Win Rate Heatmap for Strategy Combinations")
        strategy_combinations = [(p, d) for p in player_strategies.keys() for d in dealer_strategies.keys()]
        win_rates = [
            simulate_buckshot_game(
                rounds, live_shells, blank_shells, initial_player_lives, initial_dealer_lives,
                player_strategies[p], dealer_strategies[d], player_threshold, dealer_threshold
            )['player_win_rate'] for p, d in strategy_combinations
        ]
        
        heatmap_data = pd.DataFrame(
            np.array(win_rates).reshape(len(player_strategies), len(dealer_strategies)),
            index=player_strategies.keys(),
            columns=dealer_strategies.keys()
        )

        fig, ax = plt.subplots()
        sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
        ax.set_xlabel("Dealer Strategy")
        ax.set_ylabel("Player Strategy")
        st.pyplot(fig)

if __name__ == "__main__":
    main()
