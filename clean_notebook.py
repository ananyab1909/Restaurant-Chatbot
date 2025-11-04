import nbformat, json

path = "chatbot.ipynb"
nb = nbformat.read(path, as_version=4)

# Remove top-level widget metadata
nb["metadata"].pop("widgets", None)

# Remove colab-specific metadata & widget outputs
for cell in nb["cells"]:
    cell["metadata"].pop("colab", None)
    cell["metadata"].pop("outputId", None)
    if "outputs" in cell:
        clean_outputs = []
        for out in cell["outputs"]:
            if "application/vnd.jupyter.widget-view+json" in out.get("data", {}):
                continue
            clean_outputs.append(out)
        cell["outputs"] = clean_outputs

nbformat.write(nb, path)
print("Cleaned chatbot.ipynb successfully!")
