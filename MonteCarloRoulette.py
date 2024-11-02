import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def simulate_buckshot_game_streamlit(
    rounds,
    live_shells,
    blank_shells,
    initial_player_lives,
    initial_dealer_lives,
    player_strategy,
    dealer_strategy
):
    # Initialize data collection
    player_win_counts = []
    dealer_win_counts = []
    rounds_list = []
    player_wins = 0
    dealer_wins = 0
    game_lengths = []  # Collect game lengths

    # Simulate games and collect data for plotting
    for game_round in range(1, rounds + 1):
        # Run a single game
        winner, game_length = simulate_single_game(
            live_shells,
            blank_shells,
            initial_player_lives,
            initial_dealer_lives,
            player_strategy,
            dealer_strategy
        )
        # Update win counts
        if winner == 'player':
            player_wins += 1
        elif winner == 'dealer':
            dealer_wins += 1

        game_lengths.append(game_length)  # Record game length

        # Record data every 10 rounds for smoother plots
        if game_round % 10 == 0:
            rounds_list.append(game_round)
            player_win_counts.append(player_wins / game_round * 100)
            dealer_win_counts.append(dealer_wins / game_round * 100)

    # Return the collected data
    return rounds_list, player_win_counts, dealer_win_counts, player_wins, dealer_wins, game_lengths

def simulate_single_game(
    live_shells,
    blank_shells,
    initial_player_lives,
    initial_dealer_lives,
    player_strategy,
    dealer_strategy
):
    # Initialize game state
    player_lives = initial_player_lives
    dealer_lives = initial_dealer_lives
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
        return 'dealer', game_length
    elif dealer_lives <= 0:
        return 'player', game_length
    else:
        return 'draw', game_length

# Existing strategy functions...

# Add this new function for the probability evolution plot
def simulate_single_game_with_probabilities(
    live_shells,
    blank_shells,
    initial_player_lives,
    initial_dealer_lives,
    player_strategy,
    dealer_strategy
):
    # Initialize game state
    player_lives = initial_player_lives
    dealer_lives = initial_dealer_lives
    shells = []
    shell_index = 0
    turn = 'player'
    game_length = 0
    probabilities = []  # To record probabilities

    while player_lives > 0 and dealer_lives > 0:
        game_length += 1

        if shell_index >= len(shells):
            shells = ['live'] * live_shells + ['blank'] * blank_shells
            np.random.shuffle(shells)
            shell_index = 0

        L = shells[shell_index:].count('live')
        B = shells[shell_index:].count('blank')
        current_shell = shells[shell_index]

        # Record probabilities
        total_shells = L + B
        if total_shells > 0:
            p_live = L / total_shells
            p_blank = B / total_shells
        else:
            p_live = p_blank = 0
        probabilities.append((p_live, p_blank))

        # Rest of the game logic...
        if turn == 'player':
            action = player_strategy(L, B, player_lives, dealer_lives)
            # Existing action handling...
        elif turn == 'dealer':
            action = dealer_strategy(L, B, dealer_lives, player_lives)
            # Existing action handling...

        # Update shell index and other variables as before...

    # Return winner, game length, and probabilities
    if player_lives <= 0:
        return 'dealer', game_length, probabilities
    elif dealer_lives <= 0:
        return 'player', game_length, probabilities
    else:
        return 'draw', game_length, probabilities

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

    # Display the description for the selected player strategy
    st.sidebar.write(f"**Description:** {player_strategy_descriptions[player_strategy_option]}")

    st.sidebar.header("Dealer Strategy")
    dealer_strategy_option = st.sidebar.selectbox(
        "Select Dealer Strategy",
        ("Aggressive", "Conservative", "Probability-Based", "Random")
    )

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
            rounds_list, player_win_counts, dealer_win_counts, player_wins, dealer_wins, game_lengths = simulate_buckshot_game_streamlit(
                rounds,
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives,
                player_strategy,
                dealer_strategy
            )

        # Plot the win rates
        st.subheader("Win Rates Over Time")
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(rounds_list, player_win_counts, label='Player Win Rate')
        ax.plot(rounds_list, dealer_win_counts, label='Dealer Win Rate')
        ax.set_xlabel('Number of Games Played')
        ax.set_ylabel('Win Rate (%)')
        ax.set_title('Win Rates Over Time')
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

        # Display final results
        st.subheader(f"Final Results after {rounds} rounds:")
        st.write(f"Player Win Rate: **{player_wins / rounds * 100:.2f}%**")
        st.write(f"Dealer Win Rate: **{dealer_wins / rounds * 100:.2f}%**")

        # Plot game length distribution
        st.subheader("Game Length Distribution")
        fig2, ax2 = plt.subplots()
        ax2.hist(game_lengths, bins=range(1, max(game_lengths)+2), edgecolor='black')
        ax2.set_xlabel('Game Length (Number of Turns)')
        ax2.set_ylabel('Frequency')
        st.pyplot(fig2)

        # Display average game length
        avg_game_length = sum(game_lengths) / len(game_lengths)
        st.write(f"Average Game Length: **{avg_game_length:.2f} turns**")

    # Option to generate win rate heatmap
    if st.checkbox("Generate Win Rate Heatmap (may take longer)"):
        with st.spinner('Generating heatmap...'):
            live_shell_range, blank_shell_range, win_rates = generate_win_rate_heatmap(
                initial_player_lives,
                initial_dealer_lives,
                player_strategy,
                dealer_strategy,
                rounds_per_combination=100  # Adjust as needed
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
            winner, game_length, probabilities = simulate_single_game_with_probabilities(
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives,
                player_strategy,
                dealer_strategy
            )

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

if __name__ == "__main__":
    main()
