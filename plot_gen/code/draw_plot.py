import seaborn as sns
import pandas as pd
import os
import matplotlib.pyplot as plt

metric_type = [
    "changed files", "diff hunks", "added lines", "deleted lines",
    "modified directories"
]
csv_dir = "../csv"
plot_dir = "../plots"

for metric in metric_type:
    sns.set_theme(style="ticks", palette="pastel")
    data = pd.read_csv(os.path.join(csv_dir, metric + ".csv"))
    f = plt.figure(figsize=[4, 6])
    ax = f.add_subplot(111)
    plot = sns.boxplot(x="commit type",
                       y=metric + " count",
                       data=data,
                       order=["Multi-lang", "Other"],
                       fliersize=2,
                       palette=["m", "g"],
                       dodge=False,
                       ax=ax)
    plot.set_yscale("log")
    plot.set_ylim(bottom=1)
    plot.set_ylabel("Number of " + metric)
    plot.set_xlabel("")
    f.tight_layout()
    fig = plot.get_figure()
    fig.savefig(os.path.join(plot_dir, metric + ".png"))
    fig.clf()
# for metric in metric_type:
#     sns.set_theme(style="whitegrid")
#     data = pd.read_csv(os.path.join(csv_dir, metric + ".csv"))
#     data["all"] = ""
#     plot = sns.violinplot(
#         y=metric + " count",
#         x="all",
#         hue="commit type",
#         data=data,
#         palette="muted",
#         split=True
#     )
#     plot.set_yscale("log")
#     fig = plot.get_figure()
#     fig.savefig(os.path.join(plot_dir, "violin " + metric + ".png"))
#     fig.clf()
