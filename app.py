#================= Import des librairies ================#
import dash
from dash import Dash, dcc, html, Output, Input, callback
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

#================= Configuration de l'application ================#
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#================= Import et traitement des données ================#
df = pd.read_csv("./supermarket_sales.csv")
df.columns = [
    "invoice_id", "branch", "city", "customer_type", "gender", 
    "product_line", "unit_price", "quantity", "tax", "total", 
    "date", "time", "payment", "cogs", "gross_margin", 
    "gross_income", "rating"
]
df['date'] = pd.to_datetime(df['date'], format='%m/%d/%Y')

# Définition de couleurs pour les graphiques
couleurs_bleu = [
    "#4A90E2",  # Bleu vif mais adouci
    "#6FAFDE",  # Bleu azur doux
    "#92C5E6",  # Bleu ciel clair
    "#FFFAA0",  # Jaune pastel
    "#FFDB58",  # Jaune miel
    "#E6F5FB"   # Bleu presque blanc
]

# Indicateur du nombre d'achat
def indicateur_nb_achat(data):
    return data['invoice_id'].nunique()  

# Indicateur de la moyenne des évaluations
def indicateur_moy_rating(data):
    return round(data['rating'].mean(), 2)

# Diagramme en barres du nombre total d'achats par sexe et par ville
def plot_achat(data):
    couleurs_genre = {
        "Male": "#4A90E2", 
        "Female": "#FFDB58"
    }
    df_grouped = data.groupby(['city', 'gender'])['invoice_id'].count().reset_index()
    
    fig = px.bar(df_grouped, 
                 x='city', 
                 y='invoice_id', 
                 color='gender', 
                 title="Nombre d'achats par sexe et par ville",
                 labels={'invoice_id': "Nombre d'achats", 'city': "Ville", 'gender': "Sexe"},
                 barmode='group',
                 color_discrete_map= couleurs_genre)
    
    return fig

# Diagramme circulaire montrant la répartition de la catégorie de produit par sexe et par ville
def plot_produit(data):
    df_grouped = data.groupby(['city', 'gender', 'product_line'])['invoice_id'].count().reset_index()

    fig = px.pie(df_grouped, 
                 names='product_line', 
                 values='invoice_id',
                 title="Répartition des catégories de produits par sexe et ville",
                 hole=0.2,
                 color='product_line',
                 color_discrete_map={k: v for k, v in zip(data['product_line'].unique(), couleurs_bleu)})
    
    return fig

# Evolution du montant total des achats par semaine par ville
def plot_achat_semaine(data):
    couleurs_ville = {
        "Mandalay": "#4A90E2",
        "Naypyitaw": "#FFDB58", 
        "Yangon": "#B0D8EE"  
    }
    data['week'] = data['date'].dt.isocalendar().week
    data['year'] = data['date'].dt.year

    df_grouped = data.groupby(['year', 'week', 'city'])['total'].sum().reset_index()
    
    df_grouped['date'] = pd.to_datetime(df_grouped[['year', 'week']].assign(day=1)
                                        .astype(str)
                                        .agg('-'.join, axis=1), format='%Y-%W-%w')

    fig = px.line(df_grouped, 
                  x='date', 
                  y='total', 
                  color='city', 
                  title="Évolution du total des achats par semaine",
                  labels={'total': 'Montant total', 'date': 'Date', 'city': 'Ville'},
                  markers=True,
                  color_discrete_map=couleurs_ville)
    
    return fig

#================= Interface graphique ================#
dropdown_options_ville = [{'label': loc, 'value': loc} for loc in df['city'].unique()]
dropdown_options_sexe = [{'label': loc, 'value': loc} for loc in df['gender'].unique()]

app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row([
            dbc.Col(html.H3("Supermarket Dashboard", className="text-left", style={"fontSize": "30px", "color": "#E6F5FB", "fontWeight": "bold"}), md=5,
                    style={"height": "12vh", "display": "flex", "alignItems": "center", "backgroundColor": "#8B008B", "paddingLeft": "20px"}),
            dbc.Col([
                html.Div([
                    dcc.Dropdown(
                        id='ville-dropdown', 
                        options=dropdown_options_ville, 
                        placeholder='Sélectionnez une ville...', 
                        style={"fontSize": "16px", "width": "100%", "padding": "5px"}
                    ),
                    dcc.Dropdown(
                        id='sexe-dropdown', 
                        options=dropdown_options_sexe, 
                        placeholder='Sélectionnez un genre...', 
                        style={"fontSize": "16px", "width": "100%", "padding": "5px"}
                    )
                ], style={"display": "flex", "justifyContent": "space-evenly", "alignItems": "center", "width": "100%"}),
            ], md=7,
              style={"height": "12vh", "backgroundColor": "#8B008B"})
        ], style={"marginBottom": "10px"}),

        dbc.Row([
            dbc.Col(dcc.Graph(id='graph-1', figure=go.Figure(
                go.Indicator(
        value=round(df['rating'].mean(), 2),
        title={"text": "Moyenne des Évaluations"},
        gauge={'shape': 'bullet', 'axis': {'visible': False}, 'bar': {'color': 'purple'}},
        domain={'x': [0.05, 0.5], 'y': [0.15, 0.35]}
    ))), md=6, style={ 
                "backgroundColor": "#E6E6FA", 
                "border": "2px solid #8B008B", 
                "borderRadius": "10px", 
            }),
            dbc.Col(dcc.Graph(id='graph-2', figure=go.Figure(
                go.Indicator(mode="number", value=indicateur_moy_rating(df)))), md=6
        , style={ 
                "backgroundColor": "#E6E6FA",
                "border": "2px solid #8B008B", 
                "borderRadius": "10px",
            })]),

        dbc.Row([
            dbc.Col(dcc.Graph(id='graph-5', figure=plot_achat_semaine(df)), md=12, style={ 
                "backgroundColor": "#E6E6FA", 
                "border": "2px solid #8B008B", 
                "borderRadius": "10px",
            })
        ], style={"marginBottom": "10px", "backgroundColor": "#E6E6FA"}),

        dbc.Row([
            dbc.Col(dcc.Graph(id='graph-3', figure=plot_achat(df)), md=6, style={ 
                "backgroundColor": "#E6E6FA", 
                "border": "2px solid #8B008B", 
                "borderRadius": "10px", 
                "padding": "5px"
            }
            ),
            dbc.Col(dcc.Graph(id='graph-4', figure=plot_produit(df)), md=6, style={ 
                "backgroundColor": "#E6E6FA",  
                "border": "2px solid #8B008B",  
                "borderRadius": "10px", 
                "padding": "5px"
            }
            )
        ]),
        dbc.Row([
            dbc.Col(html.H5("Informations", className="text-center", 
                            style={"fontSize": "18px", "color": "#8B008B", "fontWeight": "bold"}), 
                    md=12, style={"marginTop": "20px"}),
        ]),
        dbc.Row([
            dbc.Col(html.P("Ce tableau de bord a été conçu dans le cadre du cours Python Avancé du Master ECAP en avril 2025 "
                           "à partir de données fictives. Réalisé par Isaline Hervé.",
                           className="text-center",
                           style={"fontSize": "14px", "color": "#000000"}), 
                    md=12, style={"marginBottom": "20px"})
        ])
    ], style={"backgroundColor": "#E6E6FA"}
)


#================= Callback ================#
@callback(
    [Output('graph-1', 'figure'),
     Output('graph-2', 'figure'),
     Output('graph-3', 'figure'),
     Output('graph-4', 'figure'),
     Output('graph-5', 'figure')],
    [Input('ville-dropdown', 'value'),
     Input('sexe-dropdown', 'value')]
)
def update_graphs(selected_city, selected_gender):
    df_filtered = df.copy()

    if selected_city:
        df_filtered = df_filtered[df_filtered['city'].isin([selected_city] if isinstance(selected_city, str) else selected_city)]
    
    if selected_gender:
        df_filtered = df_filtered[df_filtered['gender'].isin([selected_gender] if isinstance(selected_gender, str) else selected_gender)]

    valeur_reference = df_filtered.iloc[0]['total']

    couleur_fond_1 = "#E6E6FA"
    couleur_fond_2 = "#E6E6FA"

    fig_nb_achat = go.Figure(go.Indicator(
        mode="number+delta",
        title={"text": "Nombre total d'achats",
               "font": {"family": "Tahoma", "size": 25, "color": "#8B008B"}},
        value=indicateur_nb_achat(df_filtered),
        delta={
        'reference': valeur_reference, 
        'relative': True, 
        'valueformat': ".1%",  
        'position': "top",
        'increasing': {'color': "#4A90E2", 'symbol': "▲"},
        'decreasing': {'color': "#FFFAA0", 'symbol': "▼"}
    },
    domain={'x': [0, 1], 'y': [0, 1]}
    ))

    fig_nb_achat.update_layout(template = {'data' : {'indicator': [{ 
                                                       'mode': "number+delta",}]}},
        autosize=False, height=225, margin=dict(l=10, r=10, t=6, b=10),
        plot_bgcolor=couleur_fond_1,  
                              paper_bgcolor=couleur_fond_2)

    fig_moy_rating = go.Figure(
        go.Indicator(
        mode="number+gauge",
        value=indicateur_moy_rating(df_filtered),
        gauge={'shape': 'bullet', 'axis': {'range': [0, 10]}, 
        'bar': {'color': '#FFDB58'}, 
        'bordercolor': 'black',
        'borderwidth': 1,
        },
        domain={'x': [0.1, 1], 'y': [0.2, 0.5]},
    )
    )
    
    fig_moy_rating.add_annotation(
    text="Moyenne des Évaluations",  
    x=0.5, y=0.95, 
    xref="paper", yref="paper",
    showarrow=False,
    font=dict(size=35, family="Tahoma", color="#8B008B") 
)
    
    fig_moy_rating.update_layout(template = {'data' : {'indicator': [{ 
                                                       'mode': "number+gauge",}]}},
      autosize=False, height=210, margin=dict(l=10, r=10, t=6, b=10),
      plot_bgcolor=couleur_fond_1,  
                              paper_bgcolor=couleur_fond_2)

    fig_achat = plot_achat(df_filtered)
    fig_achat.update_layout(autosize=False, height=400, margin=dict(l=10, r=10, t=60, b=10),
                            plot_bgcolor=couleur_fond_1,  
                            paper_bgcolor=couleur_fond_2,
                            title=dict(
        text="Nombre d'achats par sexe et par ville",  
        font=dict(family="Tahoma", size=20, color="#8B008B"),
        x=0.5,  
        xanchor="center"
    ), 
        font=dict(family="Tahoma", size=14, color="#8B008B") 
    )

    fig_produit = plot_produit(df_filtered)
    fig_produit.update_layout(autosize=False, height=400, margin=dict(l=10, r=10, t=60, b=10),
                              plot_bgcolor=couleur_fond_1,  
                              paper_bgcolor=couleur_fond_2,
                              title=dict(
        text="Répartition des catégories de produits",  
        font=dict(family="Tahoma", size=20, color="#8B008B"),
        x=0.5,  
        xanchor="center"
    ), 
        font=dict(family="Tahoma", size=14, color="#8B008B") 
    )

    fig_achat_semaine = plot_achat_semaine(df_filtered)
    fig_achat_semaine.update_layout(autosize=False, height=400, margin=dict(l=10, r=10, t=60, b=10),
                                    plot_bgcolor=couleur_fond_1,  
                                    paper_bgcolor=couleur_fond_2,
                                    title=dict(
        text="Évolution du total des achats par semaine",  
        font=dict(family="Tahoma", size=25, color="#8B008B"),
        x=0.5,  
        xanchor="center"
    ), 
        font=dict(family="Tahoma", size=20, color="#8B008B") 
    )

    return fig_nb_achat, fig_moy_rating, fig_achat, fig_produit, fig_achat_semaine


if __name__ == '__main__':
    app.run(debug=True)