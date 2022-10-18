import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==================== Load Data ====================
df = pd.read_csv("task3\eplmatches.csv")

# ==================== Helper Functions ====================
# Function to get wins for a team
def wins_by_year(team):
    df_team = df[((df["Home"] == team)&(df["FTR"] == 'H')) |
                ((df["Away"] == team)&(df["FTR"] == 'A'))]
    wins = df_team.value_counts("Season_End_Year").to_frame(team)
    wins['year'] = wins.index
    wins.sort_values(by='year', inplace=True)
    wins = wins.reset_index(drop=True)
    return wins

# Function to get full team results
def stats_by_year(team):
    df_wins = df[((df["Home"] == team)&(df["FTR"] == 'H')) |
                ((df["Away"] == team)&(df["FTR"] == 'A'))]
    wins = df_wins.value_counts("Season_End_Year").to_frame("Wins")

    df_draws = df[((df["Home"] == team)&(df["FTR"] == 'D')) |
                ((df["Away"] == team)&(df["FTR"] == 'D'))]
    draws = df_draws.value_counts("Season_End_Year").to_frame("Draws")

    df_losses = df[((df["Home"] == team)&(df["FTR"] == 'A')) |
                ((df["Away"] == team)&(df["FTR"] == 'H'))]
    losses = df_losses.value_counts("Season_End_Year").to_frame("Losses")

    stats = wins.join(draws).join(losses)

    stats['year'] = stats.index
    stats.sort_values(by='year', inplace=True)
    stats.drop(['year'], axis=1, inplace=True)
    return stats

# Function to get colors for a team
def get_color_team(team):
    team_colors = {
        "Manchester Utd": "Crimson",
        "Manchester City": "CornflowerBlue",
        "Liverpool": "Crimson",
        "Chelsea": "DodgerBlue",
        "Arsenal": "Crimson",
        "Tottenham": "MidnightBlue",
        "Everton": "DodgerBlue",
        "Leicester": "DodgerBlue",
        "West Ham": "Crimson",
        "Aston Villa": "MidnightBlue",
        "Newcastle": "DarkTurquoise",
        "Crystal Palace": "Crimson",
        "Southampton": "Crimson",
        "Wolves": "MidnightBlue",
        "Brighton": "MidnightBlue",
        "Blackburn": "CornflowerBlue",
    }
    if team in team_colors:
        return team_colors[team]
    return "MediumSeaGreen"

# ==================== Works the data ====================
teams = df['Home'].unique()
wins_by_team = wins_by_year(teams[0]).set_index('year')
for team in teams[1:]:
    wins_by_team = wins_by_team.join(wins_by_year(team).set_index('year'), how='outer')


# ==================== Streamlit App ====================
c = st.container()
fav_team = st.selectbox("Escolha seu time:", teams)
color_team = get_color_team(fav_team)
c.title(f"Histórico do {fav_team} na Premier League")

st.markdown("""
Nesse web app, você pode ver o histórico de vitórias do seu time na Premier League.
Para construí-lo, foram utilizados dados de partidas da Premier League de 1993 a 2022,
disponíveis no [Kaggle](https://www.kaggle.com/datasets/evangower/premier-league-matches-19922022?resource=download). Além disso,
utilizamos a biblioteca [Streamlit](https://streamlit.io/) para construir o web app e
a biblioteca [Plotly](https://plotly.com/python/) para construir os gráficos. 

Como pedido na tarefa, temos múltiplos gráficos que interagem entre si e com o seletor 
de times, possibilitando uma visualização muito mais rica e interativa dos dados.

*Obs: É possível selecionar apenas uma fração do período de tempo disponível, arrastando
o mouse sobre o gráfico horizontalmente.*
""")

# ==================== Plot 1 ====================
# creates subplots and defines favorite team
fig = make_subplots(rows=2, cols=1,
subplot_titles=("Vitórias Comparado aos Outros Times",
"Estatísticas Gerais"),
vertical_spacing=0.2)

# plots teams that are not the favorite team
for team in teams:
    if fav_team != team:
        fig.add_trace(go.Scatter(x=wins_by_team.index, y=wins_by_team[team],
         name=team,
         line=dict(color='gray', width=2),
         opacity=0.5,
         legendgroup="Outros times",
         legendgrouptitle_text="Outros times"),
         row=1, col=1)

# plots the favorite team
fig.add_trace(go.Scatter(x=wins_by_team.index, y=wins_by_team[fav_team],
             name=fav_team, 
             mode='lines+markers',
             marker=dict(color=color_team, size=10, line=dict(color='black', width=1.5)),
             line=dict(color=color_team, width=4),
             legendgroup=fav_team),
             row=1, col=1)

# plots the favorite team's stats
fig.add_trace(go.Bar(x=stats_by_year(fav_team).index, y=stats_by_year(fav_team)['Wins'],
                name='Vitórias',
                marker_color=color_team),
                row=2, col=1)
fig.add_trace(go.Bar(x=stats_by_year(fav_team).index, y=stats_by_year(fav_team)['Draws'],
                name='Empates',
                marker_color='SlateGray'),
                row=2, col=1)
fig.add_trace(go.Bar(x=stats_by_year(fav_team).index, y=stats_by_year(fav_team)['Losses'],
                name='Derrotas',
                marker_color='salmon'),
                row=2, col=1)
fig.update_layout(barmode='stack')


fig.update_layout(title=f'<b>{fav_team}</b> na Premier League por Ano',
                xaxis_title='Ano',
                yaxis_title='Vitórias',
                height=800,
                width=800)
fig.update_xaxes(matches='x')


st.plotly_chart(fig)
# ==================== Plot 2 ====================
fig2 = go.Figure(data=[go.Pie(labels=stats_by_year(fav_team).columns,
                                values=stats_by_year(fav_team).sum(),
                                hole=.3,
                                marker_colors=[color_team, 'SlateGray', 'salmon'])])
fig2.update_layout(title=f'<b>{fav_team}</b> na Premier League no Geral',
                height=500,
                width=500)

st.plotly_chart(fig2)