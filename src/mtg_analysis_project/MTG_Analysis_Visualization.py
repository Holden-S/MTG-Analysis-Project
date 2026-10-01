#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests

url = "https://data.scryfall.io/default-cards/default-cards-20260414090745.json"

response = requests.get(url)
with open("cards.json", "wb") as f:
    f.write(response.content)


# In[2]:


import pandas as pd

df = pd.read_json("cards.json")


# In[3]:


full_data = pd.DataFrame({
    "products.name": df["name"],
    "released_at": df["released_at"],
    "mana_cost": df["mana_cost"],
    "cmc": df["cmc"],
    "type_line": df["type_line"],
    "oracle_text": df["oracle_text"],
    "set_name": df["set_name"],
    "set_type": df["set_type"],
    "image_uris": df["image_uris"]
})

full_data["priceGuides.avg"] = df["prices"].apply(lambda x: x.get("usd") if isinstance(x, dict) else None)
full_data["priceGuides.avg-foil"] = df["prices"].apply(lambda x: x.get("usd_foil") if isinstance(x, dict) else None)
full_data["image_uris"] = full_data["image_uris"].str["normal"]

full_data["priceGuides.avg"] = pd.to_numeric(full_data["priceGuides.avg"],errors="coerce")
full_data = full_data[full_data["set_type"] == "expansion"]
full_data.head()


# In[4]:


import numpy as np

color_map = {
    "W": "White",
    "U": "Blue",
    "B": "Black",
    "R": "Red",
    "G": "Green"
}

combo_map = {
    frozenset(["W","U"]): "Azorius",
    frozenset(["U","B"]): "Dimir",
    frozenset(["B","R"]): "Rakdos",
    frozenset(["R","G"]): "Gruul",
    frozenset(["G","W"]): "Selesnya",

    frozenset(["W","B"]): "Orzhov",
    frozenset(["U","R"]): "Izzet",
    frozenset(["B","G"]): "Golgari",
    frozenset(["R","W"]): "Boros",
    frozenset(["G","U"]): "Simic",

    frozenset(["W","U","G"]): "Bant",
    frozenset(["W","U","B"]): "Esper",
    frozenset(["U","B","R"]): "Grixis",
    frozenset(["B","R","G"]): "Jund",
    frozenset(["W","R","G"]): "Naya",
    frozenset(["W","B","G"]): "Abzan",
    frozenset(["U","R","W"]): "Jeskai",
    frozenset(["U","B","G"]): "Sultai",
    frozenset(["W","B","R"]): "Mardu",
    frozenset(["U","R","G"]): "Temur",

    frozenset(["U","B","R","G"]): "Glint-Eye",
    frozenset(["B","R","G","W"]): "Dune-Brood",
    frozenset(["R","G","W","U"]): "Ink-Treader",
    frozenset(["G","W","U","B"]): "Witch-Maw",
    frozenset(["W","U","B","R"]): "Yore-Tiller",

    frozenset(["W","U","B","R","G"]): "Rainbow"
}

def get_color_info(mana_cost):
    if pd.isna(mana_cost):
        return np.nan, []

    mtg_order = ["W", "U", "B", "R", "G"]

    colors = sorted(
        set([c for c in mana_cost if c in "WUBRG"]),
        key=lambda x: mtg_order.index(x)
    )

    # No colors
    if len(colors) == 0:
        return "Colorless", []

    # Mono color
    if len(colors) == 1:
        return f"mono-{color_map[colors[0]]}", colors

    # Multi-color
    key = frozenset(colors)
    name = combo_map.get(key, "".join(colors))

    return name, colors

full_data[["color_identity", "colors"]] = full_data["mana_cost"].apply(lambda x: pd.Series(get_color_info(x)))
full_data.head()


# In[5]:


mono_data = full_data[
    full_data["color_identity"].str.startswith("mono-", na=False) |
    (full_data["color_identity"] == "Colorless")
]

import plotly.express as px

#Color map generated with ChatGPT on 3/30/2026
color_map_plotly = {
    "mono-White": "#FFD84D",   # off-white (avoids pink tint)
    "mono-Blue": "#1E90FF",    # clear blue (more reliable than dark navy)
    "mono-Black": "#2B2B2B",   # dark gray-black (visible on screen)
    "mono-Red": "#E74C3C",     # strong red
    "mono-Green": "#2ECC71",   # green
    "Colorless": "#A0A0A0"     # gray
}

fig = px.scatter(
    mono_data,
    x="released_at",
    y="priceGuides.avg",
    color="color_identity",
    color_discrete_map=color_map_plotly,
    title="Card Prices Over Time (Mono-Colored)",
    labels={
        "released_at": "Release Date",
        "priceGuides.avg": "Average Price",
        "color_identity": "Color Identity"
    }
)

colors = mono_data["color_identity"].dropna().unique()
buttons = []
buttons.append(dict(
    label="All",
    method="update",
    args=[{"visible": [True] * len(fig.data)}]
))
for i, c in enumerate(colors):
    visible = [False] * len(fig.data)
    visible[i] = True
    buttons.append(dict(
        label=c,
        method="update",
        args=[{"visible": visible}]
    ))

fig.update_layout(
    updatemenus=[dict(
        buttons=buttons,
        direction="down"
    )]
)

fig.update_yaxes(type="log")
fig.update_traces(marker=dict(size=5, opacity=0.6))
fig.show()

color_avg = mono_data.groupby("color_identity")["priceGuides.avg"].mean()
print(color_avg)

percentage = full_data["color_identity"].str.startswith("mono").mean() * 100
print(f"Percentage of cards that are mono-colored: {percentage}%")


# In[6]:


full_data["released_at"] = pd.to_datetime(full_data["released_at"])
full_data["year"] = full_data["released_at"].dt.year
year_avg = (
    full_data
    .groupby("year")["priceGuides.avg"]
    .mean()
)
print(year_avg)


# In[7]:


counts = full_data["color_identity"].value_counts()
print(counts)


# In[8]:


from itertools import combinations
import plotly.express as px

def is_subset(card_colors, combo):
    if not isinstance(card_colors, list):
        return False
    return set(card_colors).issubset(combo)

def generate_color_combos(max_colors=3):
    colors = ["W", "U", "B", "R", "G"]
    combos = []

    for r in range(1, max_colors + 1):
        combos.extend([set(c) for c in combinations(colors, r)])

    return combos

def compute_color_averages(df):
    combos = generate_color_combos(max_colors=3)
    results = []

    for combo in combos:
        subset = df[
            df["colors"].apply(lambda x: is_subset(x, combo))
        ]

        if len(subset) < 10:
            continue

        avg_price = subset["priceGuides.avg"].mean()

        results.append({
            "combo": "".join(sorted(combo)),
            "num_colors": len(combo),
            "avg_price": avg_price
        })

    return pd.DataFrame(results).sort_values("avg_price", ascending=True)

combo_data = compute_color_averages(full_data)


fig = px.bar(
    combo_data.sort_values("avg_price"),
    x="combo",
    y="avg_price",
    title="Color Combo Price Efficiency",
    labels={
        "combo": "Color Combination",
        "efficiency": "Efficiency (Cards per Dollar)"
    }
)
fig.update_layout(height=500)
fig.update_yaxes(range=[2.75,5.5])
fig.update_traces(text=combo_data["avg_price"].round(2), textposition="outside")
fig.show()


# In[11]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker

expanded_data = full_data.explode("colors")
expanded_data = expanded_data[expanded_data["colors"].notna()] # Not including colorless cards
expanded_data = expanded_data[expanded_data["priceGuides.avg"] > 0]

plot_data = (
    expanded_data
    .groupby(["set_name", "colors"])["priceGuides.avg"]
    .mean()
    .reset_index()
)
color_map = {
    "W": "White",
    "U": "Blue",
    "B": "Black",
    "R": "Red",
    "G": "Green"
}
plot_data["colors"] = plot_data["colors"].map(color_map)

sns.set_theme(style="whitegrid")

g = sns.FacetGrid(
    plot_data,
    col="colors",
    col_order=["White", "Blue", "Black", "Red", "Green"],
    sharex=True,
    sharey=False,
    height=17,
    aspect=.25
)

g.set(xscale="log")
order = plot_data.groupby("set_name")["priceGuides.avg"].mean().sort_values(ascending=True).index

g.map_dataframe(
    sns.stripplot,
    x="priceGuides.avg",
    y="set_name",
    order=order,
    jitter=True,
    size=8
)

max_price = plot_data["priceGuides.avg"].max()
g.set(xlim=(0, max_price+20))

for ax in g.axes.flat:
    ax.grid(True, axis="y", linestyle="-", alpha=0.6)
    ax.grid(False, axis="x")

for i, ax in enumerate(g.axes.flat):
    if i != 0:
        ax.set_ylabel("")
        ax.set_yticklabels([])

for ax in g.axes.flat:
    ax.xaxis.set_major_locator(mticker.LogLocator(base=10))
    ax.xaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f'))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())

g.fig.tight_layout()
g.set_axis_labels("Average Price", "Set Name")
g.set_titles("{col_name}")
g.fig.subplots_adjust(wspace=0.05)
sns.despine(left=True, bottom=True)
plt.savefig('MTG_Set_Price.png')
plt.show()


# In[13]:


set_avg = (
    expanded_data
    .groupby("set_name")["priceGuides.avg"]
    .mean()
    .sort_values()
)
top20_sets = set_avg.head(20).index

target_combos = {
    "RUW": ["R", "U", "W"],
    "GRW": ["G", "R", "W"],
    "GRU": ["G", "R", "U"],
    "BRW": ["B", "R", "W"],
    "GUW": ["G", "U", "W"]
}

set_data = expanded_data[
    expanded_data["set_name"].isin(top20_sets)
]

results = []

for combo_name, combo_colors in target_combos.items():

    subset = set_data[
        set_data["colors"].isin(combo_colors)
    ]

    grouped = (
        subset
        .groupby("set_name")["priceGuides.avg"]
        .mean()
        .reset_index()
    )

    grouped["combo"] = combo_name
    results.append(grouped)

combo_set_data = pd.concat(results)

top8_per_combo = (
    combo_set_data
    .sort_values(["combo", "priceGuides.avg"])
    .groupby("combo")
    .head(8)
)

pivot = top8_per_combo.pivot(
    index="set_name",
    columns="combo",
    values="priceGuides.avg"
)

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))

sns.heatmap(
    pivot,
    annot=True,
    fmt=".2f",
    cmap="coolwarm"
)

plt.title("Top 8 Cheapest Sets for Selected Color Combos")
plt.xlabel("Color Combo")
plt.ylabel("Set Name")
plt.savefig('MTG_Combos_Best_Sets.png', bbox_inches='tight')

# Using all and only the sets listed with the exception of Khans of Tarkir since it is such a Jeskai heavy set
plt.show()

