import matplotlib.pyplot as plt
import pandas as pd


def plot_fig1_donuts(res_data):
    """Plot donut charts for vCPU, Memoria, and Disco resources."""
    
    resources = ["vCPU", "Memoria", "Disco"]

    # Colores (igual al notebook)
    c_sys = "#7f7f7f"
    c_res = "#e67e22"
    c_spare = "#87CEEB"
    c_free = "#2ecc71"
    c_frag = "#8E44AD"

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for i, res in enumerate(resources):
        df = res_data[res]["df"]
        ax = axes[i]

        vals = [df["v_sys"].sum(), df["v_res"].sum(), df["v_frag"].sum(), df["v_spare"].sum(), df["v_free"].sum()]
        labs = ["Sistema", "Asignado", "Fragmentación", "Spare", "Libre"]
        cols = [c_sys, c_res, c_frag, c_spare, c_free]

        v_final, l_final, c_final = [], [], []
        total = float(sum(vals))

        for v, l, c in zip(vals, labs, cols):
            if v and v > 0:
                v_final.append(float(v))
                pct = (float(v) / total * 100.0) if total > 0 else 0.0
                l_final.append(f"{l}: {pct:.1f}%")
                c_final.append(c)

        ax.pie(
            v_final,
            labels=l_final,
            colors=c_final,
            wedgeprops=dict(width=0.3),
            textprops={"fontsize": 13},
        )
        ax.set_title(f"Resumen Global - {res}", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.show()
    print("[plot_fig1_donuts] Plot displayed successfully")


# Sample hardcoded data
sample_data = {
    "vCPU": {
        "df": pd.DataFrame({
            "v_sys": [8, 4, 6],
            "v_res": [32, 24, 28],
            "v_frag": [2, 1, 3],
            "v_spare": [4, 8, 6],
            "v_free": [18, 27, 21],
        })
    },
    "Memoria": {
        "df": pd.DataFrame({
            "v_sys": [16, 8, 12],
            "v_res": [128, 96, 64],
            "v_frag": [8, 4, 6],
            "v_spare": [32, 24, 16],
            "v_free": [72, 124, 158],
        })
    },
    "Disco": {
        "df": pd.DataFrame({
            "v_sys": [50, 30, 40],
            "v_res": [500, 400, 350],
            "v_frag": [25, 15, 20],
            "v_spare": [100, 80, 60],
            "v_free": [325, 475, 530],
        })
    },
}


if __name__ == "__main__":
    print("Generating donut charts with sample data...")
    plot_fig1_donuts(sample_data)