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
    game_lengths = []  # Collect game lengths

    # Simulate games
    for _ in range(rounds):
        winner, game_length = simulate_single_game(
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

        game_lengths.append(game_length)  # Record game length

    # Calculate win rates
    total_games = player_wins + dealer_wins + draws
    player_win_rate = player_wins / total_games * 100
    dealer_win_rate = dealer_wins / total_games * 100
    draw_rate = draws / total_games * 100

    return {
        'player_win_rate': player_win_rate,
        'dealer_win_rate': dealer_win_rate,
        'draw_rate': draw_rate,
        'game_lengths': game_lengths
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
    game_length = 0  # Counts the number of turns

    while player_lives > 0 and dealer_lives > 0:
        game_length += 1  # Increment game length

        # Check if we need to reload the shotgun
        if shell_index >= len(shells):
            # Reload the shotgun
            shells = ['live'] * live_shells + ['blank'] * blank_shells
            np.random.shuffle(shells)
            shell_index = 0  # Reset the shell index

        L = shells[shell_index:].count('live')
        B = shells[shell_index:].count('blank')
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

    # Determine the winner and return game length
    if player_lives <= 0:
        winner = 'dealer'
    elif dealer_lives <= 0:
        winner = 'player'
    else:
        winner = 'draw'

    return winner, game_length

def strategy_comparison(
    player_strategies_dict,
    dealer_strategies_dict,
    initial_player_lives,
    initial_dealer_lives,
    live_shells,
    blank_shells,
    rounds=1000,
    player_threshold=0.7,
    dealer_threshold=0.7,
    fix_player=True,
    player_strategy=None,
    dealer_strategy=None
):
    comparison_results = []
    if fix_player:
        # Compare different Dealer strategies against a fixed player strategy
        for dealer_strat_name, dealer_strat_func in dealer_strategies_dict.items():
            results = simulate_buckshot_game(
                rounds,
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives,
                player_strategy,
                dealer_strat_func,
                player_threshold,
                dealer_threshold
            )
            comparison_results.append({
                'Player Strategy': player_strategy.__name__,
                'Dealer Strategy': dealer_strat_name,
                'Player Win Rate': results['player_win_rate'],
                'Dealer Win Rate': results['dealer_win_rate'],
                'Draw Rate': results['draw_rate']
            })
    else:
        # Compare different player strategies against a fixed Dealer strategy
        for player_strat_name, player_strat_func in player_strategies_dict.items():
            results = simulate_buckshot_game(
                rounds,
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives,
                player_strat_func,
                dealer_strategy,
                player_threshold,
                dealer_threshold
            )
            comparison_results.append({
                'Player Strategy': player_strat_name,
                'Dealer Strategy': dealer_strategy.__name__,
                'Player Win Rate': results['player_win_rate'],
                'Dealer Win Rate': results['dealer_win_rate'],
                'Draw Rate': results['draw_rate']
            })
    return pd.DataFrame(comparison_results)

# Streamlit App Code
def main():
    st.title("Buckshot Roulette Simulation")

    st.sidebar.header("Simulation Parameters")

    # Number of rounds
    rounds = st.sidebar.number_input("Number of rounds to simulate", min_value=100, max_value=100000, value=1000, step=100)

    # Shell configuration
    live_shells = st.sidebar.slider("Number of live shells", min_value=1, max_value=10, value=2)
    blank_shells = st.sidebar.slider("Number of blank shells", min_value=1, max_value=10, value=2)

    # Initial lives
    initial_player_lives = st.sidebar.slider("Player initial lives", min_value=1, max_value=10, value=2)
    initial_dealer_lives = st.sidebar.slider("Dealer initial lives", min_value=1, max_value=10, value=2)

    # Strategy selection
    st.sidebar.header("Player Strategy")
    player_strategy_option = st.sidebar.selectbox(
        "Select Player Strategy",
        ("Aggressive", "Conservative", "Probability-Based")
    )

    # Player threshold adjustment
    if player_strategy_option == 'Conservative':
        player_threshold = st.sidebar.slider("Player Conservative Threshold", min_value=0.0, max_value=1.0, value=0.7)
    else:
        player_threshold = 0.7  # Default value, won't be used

    # Display the description for the selected player strategy
    st.sidebar.write(f"**Description:** {player_strategy_descriptions[player_strategy_option]}")

    st.sidebar.header("Dealer Strategy")
    dealer_strategy_option = st.sidebar.selectbox(
        "Select Dealer Strategy",
        ("Aggressive", "Conservative", "Probability-Based", "Random")
    )

    # Dealer threshold adjustment
    if dealer_strategy_option == 'Conservative':
        dealer_threshold = st.sidebar.slider("Dealer Conservative Threshold", min_value=0.0, max_value=1.0, value=0.7)
    else:
        dealer_threshold = 0.7  # Default value, won't be used

    # Display the description for the selected dealer strategy
    st.sidebar.write(f"**Description:** {dealer_strategy_descriptions[dealer_strategy_option]}")

    # Map strategy options to functions
    player_strategies = {
        'Aggressive': player_aggressive_strategy,
        'Conservative': player_conservative_strategy,
        'Probability-Based': player_probability_based_strategy
    }
    dealer_strategies = {
        'Aggressive': dealer_aggressive_strategy,
        'Conservative': dealer_conservative_strategy,
        'Probability-Based': dealer_probability_based_strategy,
        'Random': dealer_random_strategy
    }

    player_strategy = player_strategies[player_strategy_option]
    dealer_strategy = dealer_strategies[dealer_strategy_option]

    # Run Optimal Strategy Analysis
    st.header("Optimal Strategy Analysis")

    analysis_type = st.radio(
        "Choose analysis type:",
        ("Find Best Player Strategy", "Find Best Dealer Strategy")
    )

    if analysis_type == "Find Best Player Strategy":
        with st.spinner('Analyzing best player strategy...'):
            comparison_df = strategy_comparison(
                player_strategies_dict=player_strategies,
                dealer_strategies_dict=dealer_strategies,
                initial_player_lives=initial_player_lives,
                initial_dealer_lives=initial_dealer_lives,
                live_shells=live_shells,
                blank_shells=blank_shells,
                rounds=rounds,
                player_threshold=player_threshold,
                dealer_threshold=dealer_threshold,
                fix_player=False,
                dealer_strategy=dealer_strategy
            )

        st.subheader(f"Player Strategies vs. {dealer_strategy_option} Dealer")
        st.dataframe(comparison_df.style.highlight_max(subset=['Player Win Rate'], color='lightgreen'))

        # Find the best player strategy
        best_strategy_row = comparison_df.loc[comparison_df['Player Win Rate'].idxmax()]
        best_strategy = best_strategy_row['Player Strategy']
        best_win_rate = best_strategy_row['Player Win Rate']

        st.write(f"**Optimal Player Strategy:** {best_strategy} with a win rate of {best_win_rate:.2f}%")
    else:
        with st.spinner('Analyzing best Dealer strategy...'):
            comparison_df = strategy_comparison(
                player_strategies_dict=player_strategies,
                dealer_strategies_dict=dealer_strategies,
                initial_player_lives=initial_player_lives,
                initial_dealer_lives=initial_dealer_lives,
                live_shells=live_shells,
                blank_shells=blank_shells,
                rounds=rounds,
                player_threshold=player_threshold,
                dealer_threshold=dealer_threshold,
                fix_player=True,
                player_strategy=player_strategy
            )

        st.subheader(f"{player_strategy_option} Player vs. Dealer Strategies")
        st.dataframe(comparison_df.style.highlight_max(subset=['Dealer Win Rate'], color='lightgreen'))

        # Find the best Dealer strategy
        best_strategy_row = comparison_df.loc[comparison_df['Dealer Win Rate'].idxmax()]
        best_strategy = best_strategy_row['Dealer Strategy']
        best_win_rate = best_strategy_row['Dealer Win Rate']

        st.write(f"**Optimal Dealer Strategy:** {best_strategy} with a win rate of {best_win_rate:.2f}%")

    # Provide explanation
    st.write("""
    The table above shows the win rates for each strategy under the selected game parameters.
    The optimal strategy is the one with the highest win rate.
    """)

    # Optionally, include additional analysis or plots

    # Run simulation with selected strategies
    st.header("Run Simulation with Selected Strategies")

    if st.button("Run Simulation"):
        with st.spinner('Simulating games...'):
            results = simulate_buckshot_game(
                rounds,
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives,
                player_strategy,
                dealer_strategy,
                player_threshold,
                dealer_threshold
            )

        # Display final results
        st.subheader(f"Results after {rounds} rounds:")
        st.write(f"Player Win Rate: **{results['player_win_rate']:.2f}%**")
        st.write(f"Dealer Win Rate: **{results['dealer_win_rate']:.2f}%**")
        st.write(f"Draw Rate: **{results['draw_rate']:.2f}%**")

        # Plot game length distribution
        st.subheader("Game Length Distribution")
        fig2, ax2 = plt.subplots()
        ax2.hist(results['game_lengths'], bins=range(1, max(results['game_lengths'])+2), edgecolor='black')
        ax2.set_xlabel('Game Length (Number of Turns)')
        ax2.set_ylabel('Frequency')
        st.pyplot(fig2)

        # Display average game length
        avg_game_length = sum(results['game_lengths']) / len(results['game_lengths'])
        st.write(f"Average Game Length: **{avg_game_length:.2f} turns**")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
