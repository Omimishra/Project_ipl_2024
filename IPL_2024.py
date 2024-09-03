import streamlit as st
import pandas as pd 
import plotly.express as px

#ui configuration
st.set_page_config(
    page_title='IPL 2024',
    page_icon='🏏',
    layout='wide'
)

# load data
@st.cache_data
def load_data():
    df = pd.read_csv('ipl2024.csv')
    df = df.sort_values('date')
    return df

#ui integration
with st.spinner('Loading dataset ....'):
    df = load_data()
    # st.balloons()

st.title("IPL 2024 Matches Analysis")
st.write('This dashboard provides an interactive analysis of the IPL 2024 season, showcasing team performances and  match outcomes. Explore the data to uncover patterns and trends that defined the season.')

st.sidebar.title('Menu')
choice = st.sidebar.radio('Options',['All teams','Team Analysis'])
st.image("iplimg.jpg")
c1,c2,c3 = st.columns(3)
c1.markdown('IPL 2024 Final Winner - Kolkata Knight Riders')
c2.markdown("Orange Cap Winner - Virat Kohli")
c2.markdown("Runs - 741")
c3.markdown("Purple Cap Winner - Harshal Patel")
c3.markdown("Wickets - 24")

if choice == 'All teams':
    # Example: Calculate total wins and losses for each team
    st.subheader("Win/Loss Distribution for Each Team")
    df['win'] = df.apply(lambda row: row['home_team_abbrev'] if row['home_win'] else row['away_team_abbrev'], axis=1)
    df['loss'] = df.apply(lambda row: row['away_team_abbrev'] if row['home_win'] else row['home_team_abbrev'], axis=1)

    # Count wins and losses for each team
    wins = df['win'].value_counts().reset_index()
    losses = df['loss'].value_counts().reset_index()
    wins.columns= ['team_name','win_counts']
    losses.columns= ['team_name','loss_counts']

    c1 , c2 = st.columns([3,2])

    # Merge wins and losses into a single DataFrame
    team_stats = pd.merge(wins, losses, left_on='team_name', right_on='team_name', how='outer')
    team_stats.columns = ['team', 'wins', 'losses']
    team_stats = team_stats.fillna(0)  # Fill NaN values with 0

    c2.dataframe(team_stats,use_container_width=True)
    # st.sidebar.header("Filter Matches")
    # selected_team = st.sidebar.selectbox("Select Team", team_stats['team'].unique())

    # Visualization: Win/Loss Distribution
    fig1 = px.bar(team_stats, 
                x='team', 
                y=['wins', 'losses'], 
                labels={'value': 'Count', 'team': 'Team'},
                barmode='group')
    c1.plotly_chart(fig1)

    # winning margin
    st.subheader("Winning margins distribution")
    c1 , c2 = st.columns(2)
    df['winning_margin'] = pd.to_numeric(df['winning_margin'], errors='coerce')
    win_by_runs = df[df['winning_type'] == 'Runs']
    # win_by_runs =pd.concat([df['home_team_abbrev'], df['away_team_abbrev']])
    win_by_wickets = df[df['winning_type'] == 'Wickets']
    fig_runs= px.histogram(win_by_runs,
                x='winning_margin',
                nbins=20,
                title='Distribution of Winning Margins (by Runs)',
                labels={'winning_margin': 'Winning Margin (Runs)'},
                marginal='box',  # Add a box plot above the histogram
    )
    fig_wickets = px.histogram(
        win_by_wickets,
        x='winning_margin',
        nbins=8,
        title='Distribution of Winning Margins (by Wickets)',
        labels={'winning_margin': 'Winning Margin (Wickets)'},
        color_discrete_sequence=['orange'],
        marginal='box',  # Add a box plot above the histogram
)
    c1.plotly_chart(fig_runs)
    c2.plotly_chart(fig_wickets)


    #Number of Wins by Team over Time
    st.subheader("Number of wins by each team over the time")
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
# Create a new column to indicate the winner
    df['winner'] = df.apply(lambda x: x['home_team_abbrev'] if x['home_win'] else x['away_team_abbrev'], axis=1)

    # Count the number of wins by team and date
    win_counts = df.groupby(['date', 'winner']).size().reset_index(name='win_count')

    # Create a stacked bar chart
    fig2 = px.bar(
        win_counts,
        x='date',
        y='winner',
        color='winner',
        labels={'date': 'Match Date', 'win_count': 'Number of Wins'},
        hover_data=['winner']
    )

    fig2.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of Wins',
        legend_title='Winning Team',
        plot_bgcolor='white',
        barmode='stack'  # Stacked bar mode
    )

    # Show plot
    st.plotly_chart(fig2)


    #venue analysis
    st.subheader('Total Number of Matches Played at Each Venue')
    venue_matches = df['cleaned_venue'].value_counts().reset_index()
    venue_matches.columns=['Venue','Total Matches']

    # home_wins = df.groupby(by='cleaned_venue')[df['home_win'].sum()]
    venue_wins = df.groupby('cleaned_venue').agg(home_wins=('home_win', 'sum'), away_wins=('away_win', 'sum')).reset_index()
    # Merge both counts into a single DataFrame
    venue_analysis = pd.merge(venue_matches, venue_wins, left_on='Venue', right_on='cleaned_venue')
    venue_analysis.drop('cleaned_venue', axis=1, inplace=True)

    fig3 = px.bar(
    venue_analysis,
    x='Venue',
    y='Total Matches',
    labels={'Total Matches': 'Number of Matches'},
    color='Total Matches',
    color_continuous_scale='Greens'
)
    st.plotly_chart(fig3)

    st.subheader('Home vs Away Wins')
    c1 , c2 = st.columns(2)
    home_wins = df[df['home_win'] == True]
    away_wins = df[df['away_win'] == True]
    # Group by home team and count the number of wins
    home_wins_count = home_wins.groupby('home_team_abbrev').size().reset_index(name='home_win_count')
    home_wins_count.columns = ['Team', 'Wins']
    away_wins_count = home_wins.groupby('away_team_abbrev').size().reset_index(name='away_win_count')
    away_wins_count.columns = ['Team', 'Wins']
    fig5 = px.pie(home_wins_count, names='Team', values='Wins',hole=.5, title='Home Wins Distribution')
    fig6 = px.pie(away_wins_count, names='Team', values='Wins',hole=.5, title='Away Wins Distribution')
    c1.plotly_chart(fig5)
    c2.plotly_chart(fig6)

    st.subheader('Wins by Toss Decision')
    # Group by toss decision and count the number of wins
    toss_win_data = df.groupby('toss_decision')['win'].value_counts().reset_index(name='count')

    # Create a bar chart
    fig = px.bar(toss_win_data, x='toss_decision', y='count', color='win',
                 barmode='group')
    st.plotly_chart(fig)

elif choice == 'Team Analysis':
     st.header('Select a team to view their performance.')
     st.subheader("Detailed data view")
     df['win'] = df.apply(lambda row: row['home_team_abbrev'] if row['home_win'] else row['away_team_abbrev'], axis=1)
     df['loss'] = df.apply(lambda row: row['away_team_abbrev'] if row['home_win'] else row['home_team_abbrev'], axis=1)
    # Count wins and losses for each team
     wins = df['win'].value_counts().reset_index()
     losses = df['loss'].value_counts().reset_index()
     wins.columns= ['team_name','win_counts']
     losses.columns= ['team_name','loss_counts']
    # Merge wins and losses into a single DataFrame
     team_stats = pd.merge(wins, losses, left_on='team_name', right_on='team_name', how='outer')
     team_stats.columns = ['team', 'wins', 'losses']
     team_stats = team_stats.fillna(0) 

     team = st.sidebar.selectbox('Select a team', team_stats['team'].unique())

     h = df.groupby(by='home_team_abbrev').get_group(team)
     a = df.groupby(by='away_team_abbrev').get_group(team)
     team_= pd.concat([h,a])
     team_ = team_.sort_values(by='date')
     team_ = team_.drop(columns=['win','loss'])
     st.dataframe(team_,use_container_width=True)
    
     st.subheader('Team Performance')
     # Create a new column to categorize the outcome
     team_['outcome'] = team_['result_outcome'].apply(lambda x: 'Win' if f'{team} won' in x else 'Loss')

    # Create the sunburst chart
     st.write(f'Here is the performance of team {team} with toss winners, toss decison taken by them and outcome in a heirarchial structure')
     team_ = team_.dropna()
     fig1 = px.treemap(
        team_,
        path=['cleaned_venue', 'toss_winner','toss_decision', 'outcome'],  # Hierarchy of levels to create the treemap
        values=None,  # Optional: Size of each sector; can be set to a numeric column if relevant
        color='outcome',  # Color the segments based on match outcomes
        # color_discrete_map={'Win': 'blue', 'Loss': 'orange'},  # Define colors for win/loss
        title=f'Treemap of {team} Performance'
    )
     st.plotly_chart(fig1)


    