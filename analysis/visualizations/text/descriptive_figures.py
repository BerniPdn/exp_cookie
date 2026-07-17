import pandas as pd
import matplotlib.pyplot as plt


def plot_metric(
    df,
    metric,
    ylabel=None,
    title=None,
    figsize=(10, 5),
    save_path=None,
):

    plot_df = df.copy()

    # IDs cortos
    subjects = sorted(plot_df["subject_id"].unique())
    subject_map = {s: f"P{i+1}" for i, s in enumerate(subjects)}
    plot_df["participant"] = plot_df["subject_id"].map(subject_map)

    # Ordenar participantes por promedio de Word Count
    participant_order = (
        plot_df.groupby("participant")["word_count"]
        .mean()
        .sort_values()
        .index
        .tolist()
    )

    colors = {
        "lamina_vieja": "#4C72B0",
        "lamina_nueva": "#DD8452",
    }

    fig, ax = plt.subplots(figsize=figsize)

    for i, participant in enumerate(participant_order):

        participant_data = (
            plot_df[plot_df["participant"] == participant]
            .set_index("condition")
        )

        y_old = participant_data.loc["lamina_vieja", metric]
        y_new = participant_data.loc["lamina_nueva", metric]

        # Línea que une ambas condiciones
        ax.plot(
            [i - 0.08, i + 0.08],
            [y_old, y_new],
            color="lightgray",
            linewidth=2,
            zorder=1,
        )

        # Imagen original
        ax.scatter(
            i - 0.08,
            y_old,
            s=80,
            color=colors["lamina_vieja"],
            edgecolor="black",
            linewidth=0.8,
            zorder=3,
            label="Original" if i == 0 else "",
        )

        # Imagen nueva
        ax.scatter(
            i + 0.08,
            y_new,
            s=80,
            color=colors["lamina_nueva"],
            edgecolor="black",
            linewidth=0.8,
            zorder=3,
            label="New" if i == 0 else "",
        )

    ax.set_xticks(range(len(participant_order)))
    ax.set_xticklabels(participant_order)

    ax.set_xlabel("Participant")
    ax.set_ylabel(ylabel if ylabel else metric)

    if title:
        ax.set_title(title)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax.legend(frameon=False)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    plt.show()