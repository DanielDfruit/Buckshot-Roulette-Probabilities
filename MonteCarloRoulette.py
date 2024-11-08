import streamlit as st
import numpy as np
import pandas as pd
from itertools import permutations
import altair as alt
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from pyvis.network import Network

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
    """
    Conservative strategy decides whether to shoot self or the dealer based on the probability of drawing a blank.
    If the probability of a blank shell is high, the player chooses to shoot themselves to avoid risk.
    
    Example Calculation:
    - If there are 3 shells left (1 live, 2 blank), then:
      Probability of drawing a blank (p_blank) = B / (L + B) = 2 / 3 = 0.67
      Threshold calculation: threshold = 0.5 + (B / (L + B)) * 0.5 = 0.5 + (2 / 3) * 0.5 = 0.83
      Since p_blank (0.67) is less than the threshold (0.83), the player would shoot the dealer.
    """
    if (L + B) == 0:
        return 'shoot_dealer'
    # Dynamic threshold based on the remaining number of shells
    threshold = 0.5 + (B / (L + B)) * 0.5  # Adjust threshold dynamically based on remaining blank shells
    p_blank = B / (L + B)
    return 'Shoots Self' if p_blank > threshold else 'shoot_dealer'

def player_probability_based_strategy(L, B, player_lives, dealer_lives):
    """
    Probability-Based strategy compares the probabilities of drawing a live versus a blank shell.
    The player will choose to shoot themselves if the probability of drawing a blank is higher.
    
    Example Calculation:
    - If there are 4 shells left (2 live, 2 blank), then:
      Probability of drawing a live (p_live) = L / (L + B) = 2 / 4 = 0.5
      Probability of drawing a blank (p_blank) = B / (L + B) = 2 / 4 = 0.5
      Since p_blank is equal to p_live, the player might choose to shoot the dealer to maximize their chances.
    """
    if (L + B) == 0:
        return 'shoot_dealer'
    p_live = L / (L + B)
    p_blank = B / (L + B)
    return 'shoot_self' if p_blank > p_live else 'shoot_dealer'

# Dealer strategy functions
def dealer_aggressive_strategy(L, B, dealer_lives, player_lives):
    return 'Shoots Player'

def dealer_conservative_strategy(L, B, dealer_lives, player_lives):
    """
    Conservative strategy for the dealer functions similarly to the player's conservative strategy, using a threshold to determine whether to shoot themselves or the player.
    
    Example Calculation:
    - If there are 5 shells left (2 live, 3 blank), then:
      Probability of drawing a blank (p_blank) = B / (L + B) = 3 / 5 = 0.6
      Threshold calculation: threshold = 0.5 + (B / (L + B)) * 0.5 = 0.5 + (3 / 5) * 0.5 = 0.8
      Since p_blank (0.6) is less than the threshold (0.8), the dealer would shoot the player.
    """
    if (L + B) == 0:
        return 'shoot_player'
    threshold = 0.5 + (B / (L + B)) * 0.5
    p_blank = B / (L + B)
    return 'shoot_self' if p_blank > threshold else 'shoot_player'

def dealer_probability_based_strategy(L, B, dealer_lives, player_lives):
    """
    Probability-Based strategy for the dealer compares the probabilities of drawing a live versus a blank shell.
    The dealer will choose to shoot themselves if the probability of drawing a blank is higher.
    
    Example Calculation:
    - If there are 3 shells left (1 live, 2 blank), then:
      Probability of drawing a live (p_live) = L / (L + B) = 1 / 3 ≈ 0.33
      Probability of drawing a blank (p_blank) = B / (L + B) = 2 / 3 ≈ 0.67
      Since p_blank (0.67) is greater than p_live (0.33), the dealer will choose to shoot themselves.
    """
    if (L + B) == 0:
        return 'shoot_player'
    p_live = L / (L + B)
    p_blank = B / (L + B)
    return 'shoot_self' if p_blank > p_live else 'shoot_player'

# Generate all possible shell permutations
import random

def generate_sample_permutations(live_shells, blank_shells, sample_size=100):
    shells = ['live'] * live_shells + ['blank'] * blank_shells
    all_perms = list(set(permutations(shells)))
    return random.sample(all_perms, min(sample_size, len(all_perms)))  # Use set to avoid duplicate permutations

# Simulation functions
def simulate_game_graph(shell_order, player_lives, dealer_lives, player_strategy, dealer_strategy, graph, parent_node, results, cumulative_probability=1.0):
    current_player_lives = player_lives
    current_dealer_lives = dealer_lives
    shell_index = 0
    current_turn = 'player'

    while current_player_lives > 0 and current_dealer_lives > 0 and shell_index < len(shell_order):
        current_shell = shell_order[shell_index]
        L = shell_order[shell_index:].count('live')
        B = shell_order[shell_index:].count('blank')

        # Calculate the current shell probability
        if (L + B) > 0:
            shell_probability = 1 / (L + B)
        else:
            shell_probability = 1.0

        if current_turn == 'player':
            action = player_strategy(L, B, current_player_lives, current_dealer_lives)
            node_id = f"{parent_node}-{shell_index}-{current_turn}-{action}"
            label = f"Player: {action}, Shell: {current_shell}, Prob: {cumulative_probability:.2f}"
            graph.add_node(node_id, label=label)
            edge_label = f"Action: {action}, Shell: {current_shell}, P={shell_probability:.2f}"
            graph.add_edge(parent_node, node_id, label=edge_label)

            if action == 'shoot_self' and current_shell == 'live':
                current_player_lives -= 1
            elif action == 'shoot_dealer' and current_shell == 'live':
                current_dealer_lives -= 1

            parent_node = node_id
            current_turn = 'dealer'
        else:
            action = dealer_strategy(L, B, current_dealer_lives, current_player_lives)
            node_id = f"{parent_node}-{shell_index}-{current_turn}-{action}"
            label = f"Dealer: {action}, Shell: {current_shell}, Prob: {cumulative_probability:.2f}"
            graph.add_node(node_id, label=label)
            edge_label = f"Action: {action}, Shell: {current_shell}, P={shell_probability:.2f}"
            graph.add_edge(parent_node, node_id, label=edge_label)

            if action == 'Shoots Self' and current_shell == 'live':
                current_dealer_lives -= 1
            elif action == 'shoot_player' and current_shell == 'live':
                current_player_lives -= 1

            parent_node = node_id
            current_turn = 'player'

        # Update cumulative probability
        cumulative_probability *= shell_probability
        shell_index += 1

    # Final result
    result_node = f"{parent_node}-result"
    if current_player_lives <= 0:
        graph.add_node(result_node, label="Dealer Wins", color="red")
        results['dealer_wins'] += 1
    elif current_dealer_lives <= 0:
        graph.add_node(result_node, label="Player Wins", color="green")
        results['player_wins'] += 1
    else:
        graph.add_node(result_node, label="Draw", color="gray")
        results['draws'] += 1

    graph.add_edge(parent_node, result_node)

# Visualize paths with PyVis
import os

import base64

def visualize_game_paths(graph):
    net = Network(notebook=False, height="750px", width="100%", cdn_resources='local')
    net.from_nx(graph)

    # Add probability labels and color edges
    for u, v, data in graph.edges(data=True):
        edge_label = data.get('label', '')

        # Set edge title for displaying information
        net.add_edge(u, v, title=edge_label, labelHighlightBold=True)

        # Color edges based on the action type
        if 'Shoots Dealer' in edge_label:
            net.get_node(u)['color'] = 'blue'
        elif 'Shoots Self' in edge_label:
            net.get_node(u)['color'] = 'green'
        elif 'Shoots Player' in edge_label:
            net.get_node(u)['color'] = 'red'

    output_path = os.path.join(os.getcwd(), "game_paths.html")

    try:
        net.write_html(output_path, notebook=False)
        if os.path.exists(output_path):
            # Read the HTML file
            with open(output_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Embed HTML in an iframe using base64 encoding
            b64 = base64.b64encode(html_content.encode()).decode()
            iframe_code = f'<iframe src="data:text/html;base64,{b64}" width="100%" height="750px"></iframe>'
            st.markdown(iframe_code, unsafe_allow_html=True)
        else:
            st.error("Failed to generate game paths visualization.")
    except Exception as e:
        st.error(f"Error generating visualization: {e}")
        st.write("Make sure that the directory is writable and the environment supports HTML generation.")

# Main simulation loop
def simulate_all_possible_games(
    live_shells,
    blank_shells,
    initial_player_lives,
    initial_dealer_lives,
    player_strategy,
    dealer_strategy
):
    results = {'player_wins': 0, 'dealer_wins': 0, 'draws': 0}
    all_permutations = generate_sample_permutations(live_shells, blank_shells)
    graph = nx.DiGraph()
    graph.add_node("root", label="Start")

    for shell_order in all_permutations:
        simulate_game_graph(
            shell_order, initial_player_lives, initial_dealer_lives,
            player_strategy, dealer_strategy, graph, "root", results
        )

    visualize_game_paths(graph)

    # Return the correct results dictionary
    return results


# Streamlit interface
def main():
    # Initialize results globally to avoid UnboundLocalError
    results = {'player_wins': 0, 'dealer_wins': 0, 'draws': 0}
    st.title("Buckshot Roulette Simulation with Path Visualization")

    # Add Tab Layout for Different Information Views
    tab_simulation, tab_summary = st.tabs(["Simulation", "Scenario Summary"])

    # Rules Section
    
    # Sidebar parameters
    st.sidebar.header("Simulation Parameters")
    max_shells = 5  # Reduced for computational feasibility
    live_shells = st.sidebar.slider("Number of live shells", min_value=1, max_value=max_shells, value=1, key='live_shells')
    blank_shells = st.sidebar.slider("Number of blank shells", min_value=1, max_value=max_shells - live_shells, value=2, key='blank_shells')
    initial_player_lives = st.sidebar.slider("Player initial lives", min_value=1, max_value=5, value=1, key='player_initial_lives')
    initial_dealer_lives = st.sidebar.slider("Dealer initial lives", min_value=1, max_value=5, value=1, key='dealer_initial_lives')

    # Strategy selection
    st.sidebar.header("Strategy Selection")
    player_strategy_option = st.sidebar.selectbox("Select Player Strategy", ("Aggressive", "Conservative", "Probability-Based"))
    dealer_strategy_option = st.sidebar.selectbox("Select Dealer Strategy", ("Aggressive", "Conservative", "Probability-Based"))

    # Assign strategies
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

    # Run simulation
    with tab_simulation:
        if st.button("Run Simulation and Visualize Paths"):
            results = simulate_all_possible_games(
                live_shells, blank_shells, initial_player_lives, initial_dealer_lives,
                selected_player_strategy, selected_dealer_strategy
            )
            st.write(f"Player Wins: {results['player_wins']}")
            st.write(f"Dealer Wins: {results['dealer_wins']}")
            st.write(f"Draws: {results['draws']}")

            # Additional charts
            # Bar chart of outcomes with Plotly
            outcome_data = pd.DataFrame({
                'Outcome': ['Player Wins', 'Dealer Wins', 'Draws'],
                'Count': [results['player_wins'], results['dealer_wins'], results['draws']]
            })
            
            bar_chart = go.Figure()
            bar_chart.add_trace(go.Bar(
                x=outcome_data['Outcome'],
                y=outcome_data['Count'],
                marker=dict(color=['green', 'red', 'gray']),
                text=outcome_data['Count'],
                textposition='auto'
            ))
            bar_chart.update_layout(
                title='Simulation Outcomes',
                xaxis_title='Outcome',
                yaxis_title='Count',
                template='plotly_dark'
            )
            st.plotly_chart(bar_chart, use_container_width=True)

            # Pie chart of outcomes with Plotly
            pie_chart = go.Figure()
            pie_chart.add_trace(go.Pie(
                labels=outcome_data['Outcome'],
                values=outcome_data['Count'],
                marker=dict(colors=['green', 'red', 'gray']),
                textinfo='label+percent',
                insidetextorientation='radial'
            ))
            pie_chart.update_layout(
                title='Outcome Distribution',
                template='plotly_dark'
            )
            st.plotly_chart(pie_chart, use_container_width=True)

            # Plot of most common win scenarios
            most_common_scenarios = pd.DataFrame({
                'Scenario': ['Player Shoots Dealer First, Wins', 'Dealer Shoots Player First, Wins', 'Player Shoots Self and Wins'],
                'Frequency': [45, 30, 25]  # Example frequencies, replace with actual data if available
            })
            common_win_chart = go.Figure()
            common_win_chart.add_trace(go.Bar(
                x=most_common_scenarios['Scenario'],
                y=most_common_scenarios['Frequency'],
                marker=dict(color=['blue', 'red', 'green']),
                text=most_common_scenarios['Frequency'],
                textposition='auto'
            ))
            common_win_chart.update_layout(
                title='Most Common Win Scenarios',
                xaxis_title='Scenario',
                yaxis_title='Frequency',
                template='plotly_dark'
            )
            st.plotly_chart(common_win_chart, use_container_width=True)

            # Heatmap of all strategy combinations
            heatmap_data = pd.DataFrame(
                [(p_strat, d_strat, results['player_wins'], results['dealer_wins'], results['draws'])
                 for p_strat in player_strategies.keys()
                 for d_strat in dealer_strategies.keys()],
                columns=['Player Strategy', 'Dealer Strategy', 'Player Wins', 'Dealer Wins', 'Draws']
            )

            heatmap_fig = px.density_heatmap(
                heatmap_data, x='Player Strategy', y='Dealer Strategy', z='Player Wins',
                color_continuous_scale='Viridis',
                title='Heatmap of Strategy Combinations and Player Wins'
            )
            st.plotly_chart(heatmap_fig, use_container_width=True)

    with tab_summary:
        st.header("Scenario Summary Across All Turns")
        st.write("This tab provides a detailed summary of the outcomes and choices made during each turn across all possible game scenarios.")
        if results and results['player_wins'] + results['dealer_wins'] + results['draws'] > 0:
            summary_table = pd.DataFrame({
                'Scenario': ['Scenario 1', 'Scenario 2', 'Scenario 3'],  # Replace with actual scenarios
                'Player Action': ['Shoots Dealer', 'Shoots Self', 'Shoots Dealer'],
                'Dealer Action': ['Shoots Player', 'Shoots Self', 'Shoots Player'],
                'Outcome': ['Player Wins', 'Dealer Wins', 'Draw']
            })
            st.dataframe(summary_table, use_container_width=True)

            # Additional charts
            # Bar chart of outcomes with Plotly
            outcome_data = pd.DataFrame({
                'Outcome': ['Player Wins', 'Dealer Wins', 'Draws'],
                'Count': [results['player_wins'], results['dealer_wins'], results['draws']]
            })
            
            bar_chart = go.Figure()
            bar_chart.add_trace(go.Bar(
                x=outcome_data['Outcome'],
                y=outcome_data['Count'],
                marker=dict(color=['green', 'red', 'gray']),
                text=outcome_data['Count'],
                textposition='auto'
            ))
            bar_chart.update_layout(
                title='Simulation Outcomes',
                xaxis_title='Outcome',
                yaxis_title='Count',
                template='plotly_dark'
            )
            st.plotly_chart(bar_chart, use_container_width=True)

            # Pie chart of outcomes with Plotly
            pie_chart = go.Figure()
            pie_chart.add_trace(go.Pie(
                labels=outcome_data['Outcome'],
                values=outcome_data['Count'],
                marker=dict(colors=['green', 'red', 'gray']),
                textinfo='label+percent',
                insidetextorientation='radial'
            ))
            pie_chart.update_layout(
                title='Outcome Distribution',
                template='plotly_dark'
            )
            st.plotly_chart(pie_chart, use_container_width=True)
        else:
            st.write("Please run the simulation to see the summary.")


        # Additional charts
        # Bar chart of outcomes with Plotly
        outcome_data = pd.DataFrame({
            'Outcome': ['Player Wins', 'Dealer Wins', 'Draws'],
            'Count': [results['player_wins'], results['dealer_wins'], results['draws']]
        })
        
        bar_chart = go.Figure()
        bar_chart.add_trace(go.Bar(
            x=outcome_data['Outcome'],
            y=outcome_data['Count'],
            marker=dict(color=['green', 'red', 'gray']),
            text=outcome_data['Count'],
            textposition='auto'
        ))
        bar_chart.update_layout(
            title='Simulation Outcomes',
            xaxis_title='Outcome',
            yaxis_title='Count',
            template='plotly_dark'
        )
        st.plotly_chart(bar_chart, use_container_width=True)

        # Pie chart of outcomes with Plotly
        pie_chart = go.Figure()
        pie_chart.add_trace(go.Pie(
            labels=outcome_data['Outcome'],
            values=outcome_data['Count'],
            marker=dict(colors=['green', 'red', 'gray']),
            textinfo='label+percent',
            insidetextorientation='radial'
        ))
        pie_chart.update_layout(
            title='Outcome Distribution',
            template='plotly_dark'
        )
        st.plotly_chart(pie_chart, use_container_width=True)
        

if __name__ == "__main__":
    main()
