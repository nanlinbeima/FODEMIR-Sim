"""
Deployment Optimizer - Multi-Frequency and Multi-Strategy Comparison

Compares different deployment strategies and recommends optimal configuration.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class DeploymentStrategy:
    """Represents a complete deployment strategy."""
    frequency_mhz: float
    frequency_name: str
    propagation_model: str
    routing_protocol: str
    num_sensors: int
    avg_rssi: float
    min_rssi: float
    coverage_percent: float
    network_energy_wh: float
    uav_distance_km: float
    total_cost_score: float
    reliability_score: float
    deployment_time_min: float
    
    def get_overall_score(self) -> float:
        """Calculate overall performance score (0-100)."""
        # Weighted scoring
        coverage_weight = 0.30
        reliability_weight = 0.25
        cost_weight = 0.20
        energy_weight = 0.15
        deployment_weight = 0.10
        
        # Normalize each metric
        coverage_score = min(self.coverage_percent, 100)
        reliability_score = self.reliability_score
        cost_score = max(0, 100 - self.total_cost_score)
        energy_score = max(0, 100 - self.network_energy_wh / 10)
        deployment_score = max(0, 100 - self.deployment_time_min / 2)
        
        overall = (coverage_weight * coverage_score +
                  reliability_weight * reliability_score +
                  cost_weight * cost_score +
                  energy_weight * energy_score +
                  deployment_weight * deployment_score)
        
        return overall


class DeploymentOptimizer:
    """
    Compares multiple deployment strategies and recommends the best one.
    """
    
    def __init__(self):
        self.strategies = []
        self.frequency_bands = {
            433: {'name': '433 MHz (ISM)', 'range_factor': 1.3, 'cost_factor': 0.9},
            868: {'name': '868 MHz (EU)', 'range_factor': 1.0, 'cost_factor': 1.0},
            915: {'name': '915 MHz (US)', 'range_factor': 0.95, 'cost_factor': 1.0}
        }
        self.routing_protocols = {
            'star': {
                'name': 'Star Topology (Direct to Gateway)',
                'complexity': 'Low',
                'latency': 'Low',
                'energy_factor': 1.0,
                'reliability': 0.85
            },
            'mesh': {
                'name': 'Mesh Network (Multi-hop)',
                'complexity': 'Medium',
                'latency': 'Medium',
                'energy_factor': 0.8,
                'reliability': 0.92
            },
            'tree': {
                'name': 'Tree Routing (Hierarchical)',
                'complexity': 'Medium',
                'latency': 'Low-Medium',
                'energy_factor': 0.85,
                'reliability': 0.88
            },
            'cluster': {
                'name': 'Cluster-based (Cluster Heads)',
                'complexity': 'High',
                'latency': 'Medium',
                'energy_factor': 0.75,
                'reliability': 0.90
            }
        }
    
    def evaluate_frequency_band(self, frequency_mhz: float,
                                coverage_map: np.ndarray,
                                sensor_positions: np.ndarray,
                                link_calculator,
                                gateway_positions: np.ndarray) -> Dict:
        """
        Evaluate performance of a specific frequency band.
        
        Args:
            frequency_mhz: Operating frequency
            coverage_map: RSSI coverage map
            sensor_positions: Sensor locations
            link_calculator: Link calculator instance
            gateway_positions: Gateway locations
        
        Returns:
            Performance metrics dictionary
        """
        freq_info = self.frequency_bands.get(frequency_mhz, self.frequency_bands[868])
        
        # Adjust RSSI based on frequency (lower frequency = better penetration)
        range_factor = freq_info['range_factor']
        adjusted_coverage = coverage_map * range_factor
        
        # Calculate metrics
        avg_rssi = np.mean(adjusted_coverage[~np.isnan(adjusted_coverage)])
        min_rssi = np.min(adjusted_coverage[~np.isnan(adjusted_coverage)])
        max_rssi = np.max(adjusted_coverage[~np.isnan(adjusted_coverage)])
        
        # Coverage at different thresholds
        coverage_85 = np.sum(adjusted_coverage > -85) / adjusted_coverage.size * 100
        coverage_90 = np.sum(adjusted_coverage > -90) / adjusted_coverage.size * 100
        coverage_95 = np.sum(adjusted_coverage > -95) / adjusted_coverage.size * 100
        
        # Link quality distribution
        excellent_links = np.sum(adjusted_coverage > -75)
        good_links = np.sum((adjusted_coverage > -85) & (adjusted_coverage <= -75))
        marginal_links = np.sum((adjusted_coverage > -95) & (adjusted_coverage <= -85))
        
        return {
            'frequency_mhz': frequency_mhz,
            'frequency_name': freq_info['name'],
            'range_factor': range_factor,
            'avg_rssi': avg_rssi,
            'min_rssi': min_rssi,
            'max_rssi': max_rssi,
            'coverage_85': coverage_85,
            'coverage_90': coverage_90,
            'coverage_95': coverage_95,
            'excellent_links_pct': excellent_links / adjusted_coverage.size * 100,
            'good_links_pct': good_links / adjusted_coverage.size * 100,
            'marginal_links_pct': marginal_links / adjusted_coverage.size * 100,
            'cost_factor': freq_info['cost_factor']
        }
    
    def evaluate_routing_protocol(self, protocol: str,
                                  sensor_positions: np.ndarray,
                                  gateway_positions: np.ndarray,
                                  link_calculator) -> Dict:
        """
        Evaluate performance of a routing protocol.
        
        Args:
            protocol: Routing protocol name
            sensor_positions: Sensor locations
            gateway_positions: Gateway locations
            link_calculator: Link calculator instance
        
        Returns:
            Routing performance metrics
        """
        protocol_info = self.routing_protocols.get(protocol, self.routing_protocols['star'])
        
        n_sensors = len(sensor_positions)
        
        # Estimate network parameters based on protocol
        if protocol == 'star':
            # Direct to gateway - simple but requires good signal
            avg_hops = 1
            max_hops = 1
            network_complexity = 1.0
            
        elif protocol == 'mesh':
            # Multi-hop mesh - flexible but more complex
            avg_hops = 2.5
            max_hops = 5
            network_complexity = n_sensors * 0.5
            
        elif protocol == 'tree':
            # Tree structure - balanced
            avg_hops = np.log2(n_sensors) if n_sensors > 0 else 1
            max_hops = int(np.ceil(np.log2(n_sensors))) if n_sensors > 0 else 1
            network_complexity = n_sensors * 0.3
            
        else:  # cluster
            # Cluster heads - efficient but needs organization
            n_clusters = max(1, n_sensors // 10)
            avg_hops = 2.0
            max_hops = 3
            network_complexity = n_clusters * 2
        
        # Energy consumption estimate
        base_energy_per_sensor = 0.1  # Wh per day
        energy_per_hop = 0.02  # Wh per hop per day
        total_energy = (n_sensors * base_energy_per_sensor + 
                       n_sensors * avg_hops * energy_per_hop) * protocol_info['energy_factor']
        
        # Latency estimate (ms)
        latency_per_hop = 50  # ms
        avg_latency = avg_hops * latency_per_hop
        max_latency = max_hops * latency_per_hop
        
        # Reliability (packet delivery ratio)
        reliability = protocol_info['reliability']
        
        return {
            'protocol': protocol,
            'protocol_name': protocol_info['name'],
            'complexity': protocol_info['complexity'],
            'avg_hops': avg_hops,
            'max_hops': max_hops,
            'network_complexity': network_complexity,
            'total_energy_wh': total_energy,
            'avg_latency_ms': avg_latency,
            'max_latency_ms': max_latency,
            'reliability': reliability * 100,
            'energy_factor': protocol_info['energy_factor']
        }
    
    def compare_all_strategies(self, coverage_map: np.ndarray,
                               sensor_positions: np.ndarray,
                               gateway_positions: np.ndarray,
                               link_calculator,
                               uav_trajectory: np.ndarray) -> List[DeploymentStrategy]:
        """
        Compare all combinations of frequency bands and routing protocols.
        
        Args:
            coverage_map: RSSI coverage map
            sensor_positions: Sensor locations
            gateway_positions: Gateway locations
            link_calculator: Link calculator instance
            uav_trajectory: UAV flight path
        
        Returns:
            List of deployment strategies sorted by overall score
        """
        strategies = []
        
        # Calculate UAV path length
        if len(uav_trajectory) > 1:
            distances = np.sqrt(np.sum(np.diff(uav_trajectory[:, :2], axis=0)**2, axis=1))
            uav_distance_km = np.sum(distances) / 1000.0
        else:
            uav_distance_km = 0.0
        
        # Evaluate all combinations
        for freq_mhz in [433, 868, 915]:
            freq_metrics = self.evaluate_frequency_band(
                freq_mhz, coverage_map, sensor_positions, 
                link_calculator, gateway_positions
            )
            
            for protocol in ['star', 'mesh', 'tree', 'cluster']:
                routing_metrics = self.evaluate_routing_protocol(
                    protocol, sensor_positions, gateway_positions, link_calculator
                )
                
                # Calculate cost score (lower is better)
                sensor_cost = len(sensor_positions) * 50  # $50 per sensor
                gateway_cost = len(gateway_positions) * 500  # $500 per gateway
                frequency_cost = sensor_cost * freq_metrics['cost_factor']
                deployment_cost = uav_distance_km * 100  # $100 per km
                total_cost = sensor_cost + gateway_cost + frequency_cost + deployment_cost
                
                # Calculate reliability score (0-100)
                rssi_reliability = min(100, (freq_metrics['avg_rssi'] + 85) * 5)  # Scale from -85 dBm
                protocol_reliability = routing_metrics['reliability']
                coverage_reliability = freq_metrics['coverage_85']
                overall_reliability = (rssi_reliability * 0.4 + 
                                     protocol_reliability * 0.3 + 
                                     coverage_reliability * 0.3)
                
                # Deployment time (minutes)
                deployment_time = uav_distance_km * 5 + len(sensor_positions) * 2  # 5 min/km + 2 min/sensor
                
                # Create strategy
                strategy = DeploymentStrategy(
                    frequency_mhz=freq_mhz,
                    frequency_name=freq_metrics['frequency_name'],
                    propagation_model='ITU-R P.833 (Hybrid)',
                    routing_protocol=routing_metrics['protocol_name'],
                    num_sensors=len(sensor_positions),
                    avg_rssi=freq_metrics['avg_rssi'],
                    min_rssi=freq_metrics['min_rssi'],
                    coverage_percent=freq_metrics['coverage_85'],
                    network_energy_wh=routing_metrics['total_energy_wh'],
                    uav_distance_km=uav_distance_km,
                    total_cost_score=total_cost / 100,  # Normalized
                    reliability_score=overall_reliability,
                    deployment_time_min=deployment_time
                )
                
                strategies.append(strategy)
        
        # Sort by overall score (descending)
        strategies.sort(key=lambda s: s.get_overall_score(), reverse=True)
        
        self.strategies = strategies
        return strategies
    
    def get_recommendation_report(self, top_n: int = 3) -> str:
        """
        Generate a text report of top deployment strategies.
        
        Args:
            top_n: Number of top strategies to include
        
        Returns:
            Formatted recommendation report
        """
        if not self.strategies:
            return "No strategies evaluated yet."
        
        report = "═══════════════════════════════════════════════════════════\n"
        report += "        OPTIMAL DEPLOYMENT STRATEGY RECOMMENDATION\n"
        report += "═══════════════════════════════════════════════════════════\n\n"
        
        for i, strategy in enumerate(self.strategies[:top_n], 1):
            score = strategy.get_overall_score()
            
            if i == 1:
                report += "🏆 RECOMMENDED (OPTIMAL) STRATEGY:\n"
                report += "─────────────────────────────────────────────────────────\n"
            else:
                report += f"\n📊 Alternative Option #{i}:\n"
                report += "─────────────────────────────────────────────────────────\n"
            
            report += f"Overall Performance Score: {score:.1f}/100\n\n"
            
            report += "Communication Configuration:\n"
            report += f"  • Frequency Band: {strategy.frequency_name}\n"
            report += f"  • Propagation Model: {strategy.propagation_model}\n"
            report += f"  • Routing Protocol: {strategy.routing_protocol}\n\n"
            
            report += "Network Performance:\n"
            report += f"  • Number of Sensors: {strategy.num_sensors}\n"
            report += f"  • Average RSSI: {strategy.avg_rssi:.1f} dBm\n"
            report += f"  • Minimum RSSI: {strategy.min_rssi:.1f} dBm\n"
            report += f"  • Coverage (RSSI > -85 dBm): {strategy.coverage_percent:.1f}%\n"
            report += f"  • Network Reliability: {strategy.reliability_score:.1f}/100\n\n"
            
            report += "Resource Requirements:\n"
            report += f"  • Network Energy: {strategy.network_energy_wh:.2f} Wh/day\n"
            report += f"  • UAV Flight Distance: {strategy.uav_distance_km:.2f} km\n"
            report += f"  • Deployment Time: {strategy.deployment_time_min:.0f} minutes\n"
            report += f"  • Estimated Cost: ${strategy.total_cost_score * 100:.0f}\n\n"
            
            if i == 1:
                report += "✅ Recommendation Rationale:\n"
                if score >= 85:
                    report += "  This configuration provides excellent balance between\n"
                    report += "  coverage, reliability, and cost-effectiveness.\n"
                elif score >= 70:
                    report += "  This configuration offers good overall performance\n"
                    report += "  with acceptable trade-offs.\n"
                else:
                    report += "  This is the best available option, but improvements\n"
                    report += "  may be needed for optimal performance.\n"
                report += "\n"
        
        report += "═══════════════════════════════════════════════════════════\n\n"
        
        # Add comparison table
        report += "Comparative Analysis:\n\n"
        report += "Metric                 | " + " | ".join([f"Option {i+1}" for i in range(min(top_n, 3))]) + "\n"
        report += "─" * 75 + "\n"
        
        for i in range(min(top_n, 3)):
            s = self.strategies[i]
            if i == 0:
                report += f"Overall Score         | {s.get_overall_score():.1f}/100"
            else:
                report += f" | {s.get_overall_score():.1f}/100"
        report += "\n"
        
        for i in range(min(top_n, 3)):
            s = self.strategies[i]
            if i == 0:
                report += f"Frequency (MHz)       | {s.frequency_mhz:.0f}"
            else:
                report += f" | {s.frequency_mhz:.0f}"
        report += "\n"
        
        for i in range(min(top_n, 3)):
            s = self.strategies[i]
            routing_short = s.routing_protocol.split('(')[0].strip()
            if i == 0:
                report += f"Routing               | {routing_short[:15]}"
            else:
                report += f" | {routing_short[:15]}"
        report += "\n"
        
        for i in range(min(top_n, 3)):
            s = self.strategies[i]
            if i == 0:
                report += f"Coverage (%)          | {s.coverage_percent:.1f}"
            else:
                report += f" | {s.coverage_percent:.1f}"
        report += "\n"
        
        for i in range(min(top_n, 3)):
            s = self.strategies[i]
            if i == 0:
                report += f"Reliability (/100)    | {s.reliability_score:.1f}"
            else:
                report += f" | {s.reliability_score:.1f}"
        report += "\n"
        
        report += "\n"
        report += "Generated by FODEMIR-Sim Deployment Optimizer\n"
        
        return report

