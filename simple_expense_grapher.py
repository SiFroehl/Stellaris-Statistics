import json
from matplotlib import pyplot as plt
import numpy as np

#file = input("Please insert file here:").replace("\"", "")
file = "C:\\Users\\Simon\\Simon\\Python\\Git Projects\\Stellaris-Statistics\\mpwirpeitschenleute_765689727\\copied_saves\\gamestate_2257.10.01.json"
game_dict = json.load(open(file))

country = game_dict["country"]["0"]
income = country["budget"]["current_month"]["income"]
expenses = country["budget"]["current_month"]["expenses"]
balance = country["budget"]["current_month"]["balance"]

def pie_plot_dict(to_plot,name):
    resource_dict = dict()

    for income_name, sub_dict in to_plot.items():
        for resource, amount in sub_dict.items():
            if resource not in resource_dict.keys():
                resource_dict[resource] = dict()
            resource_dict[resource][income_name] = float(amount)

    keys = resource_dict.keys()
    nrows = int(np.ceil(len(keys) ** 0.5))
    ncols = int(np.ceil(len(keys) ** 0.5))
    if nrows * (ncols - 1) >= len(keys):
        nrows -= 1

    fig, ax = plt.subplots(nrows, ncols, figsize=(16*2, 9*2))
    ax = ax.flatten()
    for a in ax:
        a.set_visible(False)
    for idx, key in enumerate(keys):
        wedges, _, _ = ax[idx].pie(resource_dict[key].values(), center=(0, -1), autopct="%f",
                                startangle=90)  # , labels=resource_dict[key].keys())
        ax[idx].set_title(key)
        ax[idx].legend(wedges, resource_dict[key].keys(),
                       title="Ingredients",
                       loc="center left",
                       bbox_to_anchor=(1, 0, 0.5, 1))
        # ax[idx].legend(wedges, resource_dict[key].keys())
        ax[idx].set_visible(True)
    plt.savefig(name + ".png")
    # plt.show()


pie_plot_dict(income, "income_plot")
pie_plot_dict(expenses, "expenses_plot")


bip_pos = dict()
bip_neg = dict()
bip = dict()
bip_sum = 0
bip_conversion = {
    "minerals": 1, "energy": 1, "food": 1, "consumer_goods": 2, "alloys": 4, "exotic_gases": 10, "volatile_motes": 10,
    "rare_crystals": 10, "dark_matter": 20, "living_metal": 20, "zro": 20
}

for income_name, sub_dict in balance.items():
    for resource, amount in sub_dict.items():
        if float(amount) > 0:
            if resource in bip_conversion.keys():
                if income_name not in bip_pos:
                    bip_pos[income_name] = 0
                bip_pos[income_name] += float(amount) * bip_conversion[resource]
                bip_sum += float(amount) * bip_conversion[resource]
        else:

            if resource in bip_conversion.keys():
                if income_name not in bip_neg:
                    bip_neg[income_name] = 0
                    bip_neg[income_name] -= float(amount) * bip_conversion[resource]
                    bip_sum += float(amount) * bip_conversion[resource]
        if resource in bip_conversion.keys():
            if income_name not in bip:
                bip[income_name] = 0
            bip[income_name] += float(amount) * bip_conversion[resource]

print(bip_sum)
plt.clf()
wedges, _, _ = plt.pie(bip_neg.values(), autopct="%f")
plt.legend(wedges, bip_neg.keys(),
                       title="Sources",
                       loc="center left",
                       bbox_to_anchor=(1, 0, 0.5, 1))
plt.savefig("bip_expenses.png")
plt.clf()
wedges, _, _ = plt.pie(bip_pos.values(), autopct="%f")
plt.legend(wedges, bip_pos.keys(),
                       title="Sources",
                       loc="center left",
                       bbox_to_anchor=(1, 0, 0.5, 1))
plt.savefig("bip_income.png")

bip_total_income = {key: val for key, val in bip.items() if val > 0}
bip_total_expenses = {key: -val for key, val in bip.items() if val < 0}
plt.clf()
wedges, _, _ = plt.pie(bip_total_expenses.values(), autopct="%f")
plt.legend(wedges, bip_total_expenses.keys(),
                       title="Sources",
                       loc="center left",
                       bbox_to_anchor=(1, 0, 0.5, 1))
plt.savefig("bip_total_expenses.png")
plt.clf()
wedges, _, _ = plt.pie(bip_total_income.values(), autopct="%f")
plt.legend(wedges, bip_total_income.keys(),
                       title="Sources",
                       loc="center left",
                       bbox_to_anchor=(1, 0, 0.5, 1))
plt.savefig("bip_total_income.png")