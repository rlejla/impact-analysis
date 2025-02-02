import io
import base64
import matplotlib.pyplot as plt
import json

def load_json_data(file_path: str):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} contains invalid JSON.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None

def get_nested_value(data: dict, field_path: str):
    fields = field_path.split('.')
    value = data
    for field in fields:
        if isinstance(value, dict):
            value = value.get(field)
        else:
            return None
    return value

def generate_bar_chart(data: dict, title: str) -> str:
    keys = list(data.keys())
    values = list(data.values())
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(keys, values, color='skyblue')
    ax.set_title(title)
    ax.set_ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"

def generate_pie_chart(data: dict, title: str) -> str:
    labels = list(data.keys())
    sizes = list(data.values())
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    ax.set_title(title)
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"
