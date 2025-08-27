from collections import deque
import csv 
import argparse
import streamlit as st
class Ontox:
    def __init__(self, filepath):
        self.graph = {}
        #map each id to a label
        self.label_to_id = {}
        self._load_csv(filepath)
    def _load_csv(self, filepath):
        with open(filepath, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                class_id = row["Class ID"].strip()
                label = row["Preferred Label"].strip() 
                #seperated by a pipe
                parents = row["Parents"].split("|") if row["Parents"] else []
                # Store in graph
                self.graph[class_id] = {
                    "label": label,
                    "parents": [p.strip() for p in parents if p.strip()]
                }

                # Store label lookup
                self.label_to_id[label.upper()] = class_id

                # print("Class ID:", class_id)
                # print("Label   :", label)
                # print("Parents :", parents)
                # print("-" * 40)
    def get_ancestors(self, label):
        entity_id = self.label_to_id.get(label.upper())
        if not entity_id:
            return {}

        relationships = {entity_id: 0}  
        queue = deque([(entity_id, 0)])  

        while queue:
            current_id, depth = queue.popleft()
            for parent_id in self.graph.get(current_id, {}).get("parents", []):
                if parent_id not in relationships or relationships[parent_id] > depth + 1:
                    relationships[parent_id] = depth + 1
                    queue.append((parent_id, depth + 1))

        return {self.graph[cid]["label"]: d for cid, d in relationships.items() if cid in self.graph}




# if __name__ == "__main__":
#     onto = Ontox("./data/onto_x.csv")  
#     # print("Graph dictionary:")
#     # for cid, info in onto.graph.items():
#     #     print(cid, "=>", info)

#     # print("\nLabel lookup:")
#     # print(onto.label_to_id)
# Load ontology 
onto = Ontox("./data/onto_x.csv")
# print("Graph dictionary:")
# for cid, info in onto.graph.items():
#     print(cid, "=>", info)
#     print("\nLabel lookup:")
#     print(onto.label_to_id)
# Streamlit UI better than the cli
st.title("🧬 Onto-X Explorer")

entity_label = st.text_input(" 🔍 Enter an entity label:")

if entity_label:
    relationships = onto.get_ancestors(entity_label)
    if not relationships:
        st.error(f"Entity '{entity_label}' not found.")
    else:
        st.subheader(f"📑 Ancestors for '{entity_label}':")
        for label, depth in sorted(relationships.items(), key=lambda x: x[1]):
            st.write(f"{label}: {depth}")