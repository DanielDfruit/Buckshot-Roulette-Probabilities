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
    game_records = []  # Collect detailed game data for download

    # Simulate games
    for _ in range(rounds):
        winner, game_length, game_data = simulate_single_game(
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
        game_records.extend(game_data)    # Append game data

    # Calculate win rates
    total_games = player_wins + dealer_wins + draws
    player_win_rate = player_wins / total_games * 100
    dealer_win_rate = dealer_wins / total_games * 100
    draw_rate = draws / total_games * 100

    # Prepare game records DataFrame
    game_records_df = pd.DataFrame(game_records)

    return {
        'player_win_rate': player_win_rate,
        'dealer_win_rate': dealer_win_rate,
        'draw_rate': draw_rate,
        'game_lengths': game_lengths,
        'game_records_df': game_records_df
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
    initial_player_lives = player_lives
    initial_dealer_lives = dealer_lives
    shells = []
    shell_index = 0  # Tracks the current shell
    turn = 'player'  # 'player' or 'dealer'
    game_length = 0  # Counts the number of turns
    game_data = []   # Collect game data for this game

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
        total_shells = L + B
        if total_shells > 0:
            p_live = L / total_shells
            p_blank = B / total_shells
        else:
            p_live = p_blank = 0

        # Record the state before the action
        state = {
            'Turn': game_length,
            'Player Lives': player_lives,
            'Dealer Lives': dealer_lives,
            'Remaining Live Shells': L,
            'Remaining Blank Shells': B,
            'Current Shell': current_shell,
            'Turn Holder': turn.capitalize()
        }

        if turn == 'player':
            # Decide action based on strategy
            if player_strategy == player_conservative_strategy:
                action = player_strategy(L, B, player_lives, dealer_lives, threshold=player_threshold)
            else:
                action = player_strategy(L, B, player_lives, dealer_lives)
            state['Action'] = action

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
            state['Action'] = action

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

        # Record the state after the action
        state['Post Player Lives'] = player_lives
        state['Post Dealer Lives'] = dealer_lives
        game_data.append(state)

    # Determine the winner and return game length
    if player_lives <= 0:
        winner = 'dealer'
    elif dealer_lives <= 0:
        winner = 'player'
    else:
        winner = 'draw'

    return winner, game_length, game_data

def generate_win_rate_heatmap(
    initial_player_lives,
    initial_dealer_lives,
    player_strategy,
    dealer_strategy,
    rounds_per_combination=100,
    max_shells=10,
    player_threshold=0.7,
    dealer_threshold=0.7
):
    live_shell_range = range(1, max_shells + 1)
    blank_shell_range = range(1, max_shells + 1)
    win_rates = np.zeros((len(live_shell_range), len(blank_shell_range)))

    for i, L in enumerate(live_shell_range):
        for j, B in enumerate(blank_shell_range):
            results = simulate_buckshot_game(
                rounds_per_combination,
                L,
                B,
                initial_player_lives,
                initial_dealer_lives,
                player_strategy,
                dealer_strategy,
                player_threshold,
                dealer_threshold
            )
            win_rates[i, j] = results['player_win_rate']

    return live_shell_range, blank_shell_range, win_rates

def strategy_comparison(
    strategies,
    initial_player_lives,
    initial_dealer_lives,
    live_shells,
    blank_shells,
    rounds=1000,
    player_threshold=0.7,
    dealer_threshold=0.7
):
    comparison_results = []
    for player_strat, dealer_strat in strategies:
        results = simulate_buckshot_game(
            rounds,
            live_shells,
            blank_shells,
            initial_player_lives,
            initial_dealer_lives,
            player_strat,
            dealer_strat,
            player_threshold,
            dealer_threshold
        )
        comparison_results.append({
            'Player Strategy': player_strat.__name__,
            'Dealer Strategy': dealer_strat.__name__,
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
    live_shells = st.sidebar.slider("Number of live shells", min_value=1, max_value=10, value=3)
    blank_shells = st.sidebar.slider("Number of blank shells", min_value=1, max_value=10, value=3)

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

    # Run simulation when the button is clicked
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

        # Option to download simulation data
        csv = results['game_records_df'].to_csv(index=False)
        st.download_button(
            label="Download Simulation Data as CSV",
            data=csv,
            file_name='simulation_data.csv',
            mime='text/csv',
        )

    # Option to generate win rate heatmap
    if st.checkbox("Generate Win Rate Heatmap (may take longer)"):
        with st.spinner('Generating heatmap...'):
            live_shell_range, blank_shell_range, win_rates = generate_win_rate_heatmap(
                initial_player_lives,
                initial_dealer_lives,
                player_strategy,
                dealer_strategy,
                rounds_per_combination=100,  # Adjust as needed
                max_shells=10,
                player_threshold=player_threshold,
                dealer_threshold=dealer_threshold
            )

        # Plot the heatmap
        st.subheader("Win Rate Heatmap")
        fig3, ax3 = plt.subplots()
        c = ax3.imshow(win_rates, origin='lower', aspect='auto',
                       extent=[min(blank_shell_range)-0.5, max(blank_shell_range)+0.5,
                               min(live_shell_range)-0.5, max(live_shell_range)+0.5],
                       cmap='viridis')
        ax3.set_xlabel('Number of Blank Shells')
        ax3.set_ylabel('Number of Live Shells')
        fig3.colorbar(c, ax=ax3, label='Player Win Rate (%)')
        st.pyplot(fig3)

    # Option to run single game simulation and plot probabilities
    if st.checkbox("Run Single Game Simulation and Plot Probabilities"):
        with st.spinner('Simulating single game...'):
            winner, game_length, game_data = simulate_single_game(
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives,
                player_strategy,
                dealer_strategy,
                player_threshold,
                dealer_threshold
            )
            probabilities = []
            for state in game_data:
                L = state['Remaining Live Shells']
                B = state['Remaining Blank Shells']
                total_shells = L + B
                if total_shells > 0:
                    p_live = L / total_shells
                    p_blank = B / total_shells
                else:
                    p_live = p_blank = 0
                probabilities.append((p_live, p_blank))

        # Plot the probabilities
        st.subheader("Probability Evolution During Single Game")
        fig4, ax4 = plt.subplots()
        turns = range(1, len(probabilities) + 1)
        p_live = [p[0] for p in probabilities]
        p_blank = [p[1] for p in probabilities]
        ax4.plot(turns, p_live, label='Probability of Live Shell')
        ax4.plot(turns, p_blank, label='Probability of Blank Shell')
        ax4.set_xlabel('Turn')
        ax4.set_ylabel('Probability')
        ax4.legend()
        st.pyplot(fig4)

    # Option to compare multiple strategies
    if st.checkbox("Compare Multiple Strategies"):
        with st.spinner('Comparing strategies...'):
            strategy_pairs = list(product(player_strategies.values(), dealer_strategies.values()))
            comparison_df = strategy_comparison(
                strategy_pairs,
                initial_player_lives,
                initial_dealer_lives,
                live_shells,
                blank_shells,
                rounds=500,
                player_threshold=player_threshold,
                dealer_threshold=dealer_threshold
            )

        st.subheader("Strategy Comparison Results")
        st.write(comparison_df)

if __name__ == "__main__":
    main()
