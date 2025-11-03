"""
Data Export Utility Functions

Export simulation results to various formats (CSV, JSON, GeoJSON, etc.).
"""

import json
import csv
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
import geojson


def export_to_json(data: Dict[str, Any], filepath: Path) -> None:
    """
    Export data to JSON file.
    
    Args:
        data: Dictionary to export
        filepath: Output file path
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Custom encoder for numpy types
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            if isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            return super().default(obj)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, cls=NumpyEncoder)


def export_to_csv(data: List[Dict[str, Any]], filepath: Path) -> None:
    """
    Export list of dictionaries to CSV file.
    
    Args:
        data: List of dictionaries with same keys
        filepath: Output file path
    """
    if not data:
        return
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = list(data[0].keys())
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def export_forest_to_geojson(tree_positions: np.ndarray, tree_attributes: List[Dict[str, Any]],
                             filepath: Path) -> None:
    """
    Export forest map to GeoJSON format.
    
    Args:
        tree_positions: Array of tree positions (N, 2)
        tree_attributes: List of dictionaries with tree attributes
        filepath: Output file path
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    features = []
    
    for pos, attrs in zip(tree_positions, tree_attributes):
        point = geojson.Point((float(pos[0]), float(pos[1])))
        
        # Convert numpy types to Python types
        properties = {}
        for key, value in attrs.items():
            if isinstance(value, (np.integer, np.int64, np.int32)):
                properties[key] = int(value)
            elif isinstance(value, (np.floating, np.float64, np.float32)):
                properties[key] = float(value)
            else:
                properties[key] = value
        
        feature = geojson.Feature(geometry=point, properties=properties)
        features.append(feature)
    
    feature_collection = geojson.FeatureCollection(features)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        geojson.dump(feature_collection, f, indent=2)


def export_sensors_to_geojson(sensor_positions: np.ndarray, sensor_attributes: Optional[List[Dict]] = None,
                              filepath: Path = None) -> None:
    """
    Export sensor positions to GeoJSON format.
    
    Args:
        sensor_positions: Array of sensor positions (N, 2)
        sensor_attributes: Optional list of sensor attributes
        filepath: Output file path
    """
    if filepath is None:
        return
        
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    features = []
    
    for i, pos in enumerate(sensor_positions):
        point = geojson.Point((float(pos[0]), float(pos[1])))
        
        properties = {'sensor_id': i}
        if sensor_attributes and i < len(sensor_attributes):
            for key, value in sensor_attributes[i].items():
                if isinstance(value, (np.integer, np.int64, np.int32)):
                    properties[key] = int(value)
                elif isinstance(value, (np.floating, np.float64, np.float32)):
                    properties[key] = float(value)
                else:
                    properties[key] = value
        
        feature = geojson.Feature(geometry=point, properties=properties)
        features.append(feature)
    
    feature_collection = geojson.FeatureCollection(features)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        geojson.dump(feature_collection, f, indent=2)


def export_pareto_front(pareto_solutions: np.ndarray, objective_names: List[str],
                       filepath: Path) -> None:
    """
    Export Pareto front solutions to CSV.
    
    Args:
        pareto_solutions: Array of objective values (N_solutions, N_objectives)
        objective_names: List of objective names
        filepath: Output file path
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    data = []
    for i, solution in enumerate(pareto_solutions):
        row = {'solution_id': i}
        for obj_name, obj_value in zip(objective_names, solution):
            row[obj_name] = float(obj_value)
        data.append(row)
    
    export_to_csv(data, filepath)


def export_coverage_map(coverage_map: np.ndarray, filepath: Path, 
                       origin: tuple = (0, 0), resolution: float = 1.0) -> None:
    """
    Export coverage map as CSV with coordinates.
    
    Args:
        coverage_map: 2D array of coverage values
        filepath: Output file path
        origin: Grid origin (x, y)
        resolution: Grid cell size in meters
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    rows, cols = coverage_map.shape
    data = []
    
    for i in range(rows):
        for j in range(cols):
            x = origin[0] + j * resolution
            y = origin[1] + i * resolution
            value = coverage_map[i, j]
            
            data.append({
                'x': x,
                'y': y,
                'coverage': float(value)
            })
    
    export_to_csv(data, filepath)


def export_uav_trajectory(trajectory_points: np.ndarray, filepath: Path,
                         energy_values: Optional[np.ndarray] = None) -> None:
    """
    Export UAV trajectory to CSV.
    
    Args:
        trajectory_points: Array of 3D points (N, 3) with x, y, z
        filepath: Output file path
        energy_values: Optional energy consumption at each waypoint
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    data = []
    for i, point in enumerate(trajectory_points):
        row = {
            'waypoint_id': i,
            'x': float(point[0]),
            'y': float(point[1]),
            'z': float(point[2])
        }
        
        if energy_values is not None and i < len(energy_values):
            row['cumulative_energy_wh'] = float(energy_values[i])
        
        data.append(row)
    
    export_to_csv(data, filepath)


def load_from_json(filepath: Path) -> Dict[str, Any]:
    """
    Load data from JSON file.
    
    Args:
        filepath: Input file path
    
    Returns:
        Dictionary with loaded data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def create_simulation_report(simulation_data: Dict[str, Any], filepath: Path) -> None:
    """
    Create comprehensive simulation report as JSON.
    
    Args:
        simulation_data: Dictionary containing all simulation results
        filepath: Output file path
    """
    report = {
        'metadata': {
            'simulation_name': simulation_data.get('name', 'FODEMIR-Sim'),
            'timestamp': simulation_data.get('timestamp', ''),
            'version': '1.0.0'
        },
        'parameters': simulation_data.get('parameters', {}),
        'results': simulation_data.get('results', {}),
        'metrics': simulation_data.get('metrics', {})
    }
    
    export_to_json(report, filepath)


