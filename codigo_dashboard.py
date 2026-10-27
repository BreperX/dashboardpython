"""Dashboard académico para MiTienda. Fuente editable y comentada.
Genera un HTML autocontenido (Plotly CDN) con cuatro gráficos dinámicos y una vista Seaborn.
Por defecto usa ventas_demo.csv; con MITIENDA_DB_URL consulta vw_dashboard_ventas.
"""
from pathlib import Path
import base64, io, json, os, re
from datetime import date, timedelta
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text

CARPETA = Path(__file__).resolve().parent
CSV_DEMO = CARPETA / "ventas_demo.csv"

def cargar_datos():
    """Prioriza la vista de la base de datos si MITIENDA_DB_URL está configurada."""
    dsn = os.getenv("MITIENDA_DB_URL")
    if dsn:
        engine = create_engine(dsn)
        with engine.connect() as conn:
            df = pd.read_sql(text("SELECT fecha, producto, categoria, unidades, precio_unitario, total, medio_pago FROM vw_dashboard_ventas"), conn)
        df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m-%d")
        return df
    return pd.read_csv(CSV_DEMO, parse_dates=["fecha"]).assign(fecha=lambda d: d.fecha.dt.strftime("%Y-%m-%d"))

def crear_figura_seaborn(df):
    """Crea un box plot estático con Seaborn para complementar los gráficos web dinámicos."""
    fig, ax = plt.subplots(figsize=(9, 4), dpi=140)
    sns.boxplot(data=df, x="categoria", y="total", hue="categoria", legend=False,
                palette=["#18a999", "#6878d8", "#eaa34b", "#e16d7a"], ax=ax)
    ax.set_title("Distribución del valor de compra por categoría")
    ax.set_xlabel("Categoría"); ax.set_ylabel("COP por transacción")
    fig.tight_layout()
    return fig

def generar_html(df):
    """Inyecta el conjunto activo y vuelve a renderizar el gráfico Seaborn en el HTML."""
    df = df.copy()
    df["total"] = pd.to_numeric(df["total"])
    df["unidades"] = pd.to_numeric(df["unidades"])
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m-%d")
    fig, ax = plt.subplots(figsize=(9, 4), dpi=140)
    sns.boxplot(data=df, x="categoria", y="total", hue="categoria", legend=False,
                palette=["#18a999", "#6878d8", "#eaa34b", "#e16d7a"], ax=ax)
    ax.set_title("Distribución del valor por compra · Seaborn", loc="left", weight="bold")
    ax.set_xlabel("Categoría"); ax.set_ylabel("Valor de compra (COP)")
    fig.tight_layout()
    buffer = io.BytesIO(); fig.savefig(buffer, format="svg", bbox_inches="tight"); plt.close(fig)
    svg = base64.b64encode(buffer.getvalue()).decode("ascii")
    payload = json.dumps(df.to_dict(orient="records"), ensure_ascii=False).replace("</", "<\\/")
    template = (CARPETA / "dashboard_mitienda.html").read_text(encoding="utf-8")
    template = re.sub(r"const DATA=.*?;const cop=", "const DATA=" + payload + ";const cop=", template, count=1, flags=re.S)
    template = re.sub(r'(src="data:image/svg\+xml;base64,)[^"]+', r"\g<1>" + svg, template, count=1)
    (CARPETA / "dashboard_mitienda.html").write_text(template, encoding="utf-8")
    print("HTML interactivo regenerado con", len(df), "ventas.")

if __name__ == "__main__":
    datos = cargar_datos()
    generar_html(datos)
