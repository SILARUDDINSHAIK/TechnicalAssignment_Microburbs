# 🏠 Property Orientation Analysis (Task 2)

## 📄 Project Overview
This project determines the facing direction of each property by analysing its spatial relationship with the nearest road. Using geospatial data and geometry-based calculations, the script identifies the orientation (e.g., North, South-East) and outputs both tabular and visual insights.

---

## 🎯 Objective
To calculate and visualise the orientation of every property based on its nearest road segment using spatial joins, geometric projections, and trigonometric computations.

---

## 🧠 Approach
1. **Load input data** – property points, road geometries, and related datasets.  
2. **Reproject coordinates** into a metric system (EPSG:7856) for accurate distance and angle calculations.  
3. **Find the nearest road** for each property using spatial join.  
4. **Calculate orientation** by deriving the angle between the property and its road alignment.  
5. **Convert angles** into compass directions (e.g., North-East, West).  
6. **Export results** to a CSV and generate a map visualisation.

---

## 🗂️ Folder Structure
