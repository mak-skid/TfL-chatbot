import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data = {
    "Q01": [3, 3, 4],
    "Q02": [3, 3, 4],
    "Q03": [5, 4, 4],
    "Q04": [3, 4, 3],
    "Q05": [3, 4, 2],
    "Q06": [4, 4, 4],
    "Q07": [3, 3, 3],
    "Q08": [3, 3, 3],
    "Q09": [4, 4, 5],
    "Q10": [4, 4, 4]
}

df = pd.DataFrame(data)

df_long = df.melt(var_name="Question", value_name="Response")

response_pivot = df_long.pivot_table(index="Question", columns="Response", aggfunc=len, fill_value=0)

plt.figure(figsize=(12, 8))
sns.heatmap(response_pivot, annot=True, cmap="YlGnBu", fmt="d")
plt.title("Likert Scale Questionnaire Responses (3 Participants)")
plt.ylabel("Question")
plt.xlabel("Response")
plt.show()