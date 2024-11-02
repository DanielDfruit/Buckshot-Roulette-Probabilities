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

    # Simulate games
    for _ in range(rounds):
        winner = simulate_single_game(
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

    # Calculate win rates
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

    while player_lives > 0 and dealer_lives > 0:
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

    # Determine the winner
    if player_lives <= 0:
        winner = 'dealer'
    elif dealer_lives <= 0:
        winner = 'player'
    else:
        winner = 'draw'

    return winner

def simulate_all_strategy_combinations(
    rounds,
    live_shells,
    blank_shells,
    initial_player_lives,
    initial_dealer_lives,
    player_strategies_dict,
    dealer_strategies_dict,
    player_threshold=0.7,
    dealer_threshold=0.7
):
    results = []
    for player_name, player_func in player_strategies_dict.items():
        for dealer_name, dealer_func in dealer_strategies_dict.items():
            simulation_result = simulate_buckshot_game(
                rounds,
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives,
                player_func,
                dealer_func,
                player_threshold,
                dealer_threshold
            )
            results.append({
                'Player Strategy': player_name,
                'Dealer Strategy': dealer_name,
                'Player Win Rate': simulation_result['player_win_rate'],
                'Dealer Win Rate': simulation_result['dealer_win_rate'],
                'Draw Rate': simulation_result['draw_rate']
            })
    df_results = pd.DataFrame(results)
    return df_results

# Streamlit App Code
def main():
    st.title("Buckshot Roulette Simulation")

    st.sidebar.header("Simulation Parameters")

    # Number of rounds
    rounds = st.sidebar.number_input("Number of rounds to simulate", min_value=100, max_value=100000, value=1000, step=100, key='rounds_input')

    # Shell configuration
    live_shells = st.sidebar.slider("Number of live shells", min_value=1, max_value=10, value=2, key='live_shells_slider')
    blank_shells = st.sidebar.slider("Number of blank shells", min_value=1, max_value=10, value=2, key='blank_shells_slider')

    # Initial lives
    initial_player_lives = st.sidebar.slider("Player initial lives", min_value=1, max_value=10, value=2, key='player_lives_slider')
    initial_dealer_lives = st.sidebar.slider("Dealer initial lives", min_value=1, max_value=10, value=2, key='dealer_lives_slider')

    # Strategy selection
    st.sidebar.header("Strategy Selection")
    st.sidebar.subheader("Player Strategy")
    player_strategy_option = st.sidebar.selectbox(
        "Select Player Strategy",
        ("Aggressive", "Conservative", "Probability-Based"),
        key='player_strategy_select'
    )

    # Player threshold adjustment
    if player_strategy_option == 'Conservative':
        player_threshold = st.sidebar.slider("Player Conservative Threshold", min_value=0.0, max_value=1.0, value=0.7, key='player_threshold_slider')
    else:
        player_threshold = 0.7  # Default value, won't be used

    st.sidebar.write(f"**Description:** {player_strategy_descriptions[player_strategy_option]}")

    st.sidebar.subheader("Dealer Strategy")
    dealer_strategy_option = st.sidebar.selectbox(
        "Select Dealer Strategy",
        ("Aggressive", "Conservative", "Probability-Based", "Random"),
        key='dealer_strategy_select'
    )

    # Dealer threshold adjustment
    if dealer_strategy_option == 'Conservative':
        dealer_threshold = st.sidebar.slider("Dealer Conservative Threshold", min_value=0.0, max_value=1.0, value=0.7, key='dealer_threshold_slider')
    else:
        dealer_threshold = 0.7  # Default value, won't be used

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

    # Get selected strategies
    selected_player_strategy = player_strategies[player_strategy_option]
    selected_dealer_strategy = dealer_strategies[dealer_strategy_option]

    # Run simulation when the button is clicked
    if st.button("Run Comprehensive Simulation"):
        with st.spinner('Simulating all strategy combinations...'):
            comparison_df = simulate_all_strategy_combinations(
                rounds,
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives,
                player_strategies,
                dealer_strategies,
                player_threshold=player_threshold,
                dealer_threshold=dealer_threshold
            )

        st.subheader("Strategy Comparison Table")
        # Highlight the best strategies
        max_player_win_rate = comparison_df['Player Win Rate'].max()
        max_dealer_win_rate = comparison_df['Dealer Win Rate'].max()

        def highlight_best(s):
            is_max = s == max_player_win_rate
            return ['background-color: lightgreen' if v else '' for v in is_max]

        styled_df = comparison_df.style.apply(highlight_best, subset=['Player Win Rate'])
        st.dataframe(styled_df)

        # Display the optimal strategies
        best_player_row = comparison_df.loc[comparison_df['Player Win Rate'].idxmax()]
        best_player_strategy = best_player_row['Player Strategy']
        best_player_win_rate = best_player_row['Player Win Rate']

        best_dealer_row = comparison_df.loc[comparison_df['Dealer Win Rate'].idxmax()]
        best_dealer_strategy = best_dealer_row['Dealer Strategy']
        best_dealer_win_rate = best_dealer_row['Dealer Win Rate']

        st.write(f"**Optimal Player Strategy:** {best_player_strategy} with a win rate of {best_player_win_rate:.2f}%")
        st.write(f"**Optimal Dealer Strategy:** {best_dealer_strategy} with a win rate of {best_dealer_win_rate:.2f}%")

        # Plotting the results
        st.subheader("Win Rate Heatmap")
        pivot_table = comparison_df.pivot(index="Player Strategy", columns="Dealer Strategy", values="Player Win Rate")

        fig, ax = plt.subplots()
        cax = ax.matshow(pivot_table, cmap='viridis')
        fig.colorbar(cax)
        ax.set_xticks(range(len(pivot_table.columns)))
        ax.set_yticks(range(len(pivot_table.index)))
        ax.set_xticklabels(pivot_table.columns, rotation=90)
        ax.set_yticklabels(pivot_table.index)
        for (i, j), z in np.ndenumerate(pivot_table.values):
            ax.text(j, i, f'{z:.1f}%', ha='center', va='center', color='white' if z < max_player_win_rate / 2 else 'black')
         st.pyplot(fig)


        # Highlight selected strategies on the plot
        st.write("**Note:** The selected player and Dealer strategies are highlighted on the heatmap.")

        # Run simulation with selected strategies
        st.subheader("Simulation with Selected Strategies")
        with st.spinner('Simulating selected strategies...'):
            results = simulate_buckshot_game(
                rounds,
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives,
                selected_player_strategy,
                selected_dealer_strategy,
                player_threshold=player_threshold,
                dealer_threshold=dealer_threshold
            )

        # Display final results
        st.write(f"Player Win Rate: **{results['player_win_rate']:.2f}%**")
        st.write(f"Dealer Win Rate: **{results['dealer_win_rate']:.2f}%**")
        st.write(f"Draw Rate: **{results['draw_rate']:.2f}%**")

    else:
        st.write("Click the **Run Comprehensive Simulation** button to start the simulation.")

if __name__ == "__main__":
    main()
