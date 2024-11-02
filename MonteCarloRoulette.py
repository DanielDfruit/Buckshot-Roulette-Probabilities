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

    # Simulate games and collect data for plotting
    for game_round in range(1, rounds + 1):
        # Run a single game
        winner = simulate_single_game(
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

        # Record data every 10 rounds for smoother plots
        if game_round % 10 == 0:
            rounds_list.append(game_round)
            player_win_counts.append(player_wins / game_round * 100)
            dealer_win_counts.append(dealer_wins / game_round * 100)

    # Return the collected data
    return rounds_list, player_win_counts, dealer_win_counts, player_wins, dealer_wins

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
            action = player_strategy(L, B, player_lives, dealer_lives)
            if action == 'shoot_self':
                if current_shell == 'live':
                    player_lives -= 1
                    turn = 'dealer'
                else:
                    # Player retains the turn
                    pass
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
                    # Dealer retains the turn
                    pass
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
        return 'dealer'
    elif dealer_lives <= 0:
        return 'player'
    else:
        # This should not happen, but just in case
        return 'draw'

def player_aggressive_strategy(L, B, player_lives, dealer_lives):
    return 'shoot_dealer'

def player_conservative_strategy(L, B, player_lives, dealer_lives):
    if (L + B) == 0:
        return 'shoot_dealer'
    p_blank = B / (L + B)
    if p_blank > 0.7:
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

def dealer_conservative_strategy(L, B, dealer_lives, player_lives):
    if (L + B) == 0:
        return 'shoot_player'
    p_blank = B / (L + B)
    if p_blank > 0.7:
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
            rounds_list, player_win_counts, dealer_win_counts, player_wins, dealer_wins = simulate_buckshot_game_streamlit(
                rounds,
                live_shells,
                blank_shells,
                initial_player_lives,
                initial_dealer_lives,
                player_strategy,
                dealer_strategy
            )

        # Plot the results
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

if __name__ == "__main__":
    main()
