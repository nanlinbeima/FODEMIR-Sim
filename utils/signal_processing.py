"""
Signal Processing Utility Functions

RSSI, SNR, and dB conversions for wireless communication analysis.
"""

import numpy as np
from typing import Union


def dbm_to_mw(dbm: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert power from dBm to milliwatts.
    
    Args:
        dbm: Power in dBm
    
    Returns:
        Power in milliwatts
    """
    return 10 ** (dbm / 10)


def mw_to_dbm(mw: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert power from milliwatts to dBm.
    
    Args:
        mw: Power in milliwatts
    
    Returns:
        Power in dBm
    """
    return 10 * np.log10(mw)


def db_to_linear(db: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert decibel value to linear scale.
    
    Args:
        db: Value in dB
    
    Returns:
        Linear scale value
    """
    return 10 ** (db / 10)


def linear_to_db(linear: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Convert linear value to decibels.
    
    Args:
        linear: Linear scale value
    
    Returns:
        Value in dB
    """
    return 10 * np.log10(linear)


def calculate_fspl(distance_m: Union[float, np.ndarray], 
                   frequency_mhz: float) -> Union[float, np.ndarray]:
    """
    Calculate free-space path loss (FSPL).
    
    FSPL (dB) = 20*log10(d) + 20*log10(f) + 32.45
    where d is in meters and f is in MHz
    
    Args:
        distance_m: Distance in meters
        frequency_mhz: Frequency in MHz
    
    Returns:
        Path loss in dB
    """
    # Avoid log of zero
    distance_m = np.maximum(distance_m, 1e-3)
    
    fspl = 20 * np.log10(distance_m) + 20 * np.log10(frequency_mhz) + 32.45
    return fspl


def calculate_rssi(tx_power_dbm: float, tx_gain_dbi: float, rx_gain_dbi: float,
                   path_loss_db: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate received signal strength indicator (RSSI).
    
    RSSI = Ptx + Gtx + Grx - PL
    
    Args:
        tx_power_dbm: Transmit power in dBm
        tx_gain_dbi: Transmit antenna gain in dBi
        rx_gain_dbi: Receive antenna gain in dBi
        path_loss_db: Path loss in dB
    
    Returns:
        RSSI in dBm
    """
    return tx_power_dbm + tx_gain_dbi + rx_gain_dbi - path_loss_db


def calculate_snr(rssi_dbm: Union[float, np.ndarray], 
                  noise_floor_dbm: float) -> Union[float, np.ndarray]:
    """
    Calculate signal-to-noise ratio (SNR).
    
    SNR = RSSI - Noise Floor
    
    Args:
        rssi_dbm: Received signal strength in dBm
        noise_floor_dbm: Noise floor in dBm
    
    Returns:
        SNR in dB
    """
    return rssi_dbm - noise_floor_dbm


def calculate_link_budget(tx_power_dbm: float, tx_gain_dbi: float, rx_gain_dbi: float,
                         path_loss_db: float, noise_floor_dbm: float) -> dict:
    """
    Calculate complete link budget.
    
    Args:
        tx_power_dbm: Transmit power in dBm
        tx_gain_dbi: Transmit antenna gain in dBi
        rx_gain_dbi: Receive antenna gain in dBi
        path_loss_db: Total path loss in dB
        noise_floor_dbm: Noise floor in dBm
    
    Returns:
        Dictionary with link budget components
    """
    rssi = calculate_rssi(tx_power_dbm, tx_gain_dbi, rx_gain_dbi, path_loss_db)
    snr = calculate_snr(rssi, noise_floor_dbm)
    
    return {
        'tx_power_dbm': tx_power_dbm,
        'tx_gain_dbi': tx_gain_dbi,
        'rx_gain_dbi': rx_gain_dbi,
        'path_loss_db': path_loss_db,
        'rssi_dbm': rssi,
        'noise_floor_dbm': noise_floor_dbm,
        'snr_db': snr
    }


def packet_success_probability(snr_db: Union[float, np.ndarray], 
                               snr_threshold_db: float = 6.0) -> Union[float, np.ndarray]:
    """
    Calculate packet success probability based on SNR.
    
    Uses sigmoid function for smooth transition around threshold.
    
    Args:
        snr_db: Signal-to-noise ratio in dB
        snr_threshold_db: SNR threshold for successful reception
    
    Returns:
        Probability of successful packet reception (0 to 1)
    """
    # Sigmoid with steepness factor
    steepness = 0.5
    return 1 / (1 + np.exp(-steepness * (snr_db - snr_threshold_db)))


def coverage_percentage(snr_map: np.ndarray, snr_threshold_db: float) -> float:
    """
    Calculate coverage percentage from SNR map.
    
    Args:
        snr_map: 2D array of SNR values in dB
        snr_threshold_db: Minimum SNR for coverage
    
    Returns:
        Coverage percentage (0 to 100)
    """
    covered_pixels = np.sum(snr_map >= snr_threshold_db)
    total_pixels = snr_map.size
    return 100 * covered_pixels / total_pixels


def blind_area_ratio(snr_map: np.ndarray, snr_threshold_db: float) -> float:
    """
    Calculate blind area ratio (inverse of coverage).
    
    Args:
        snr_map: 2D array of SNR values in dB
        snr_threshold_db: Minimum SNR for coverage
    
    Returns:
        Blind area ratio (0 to 1)
    """
    return 1.0 - coverage_percentage(snr_map, snr_threshold_db) / 100


def fresnel_zone_radius(distance_m: float, frequency_mhz: float, 
                       zone_number: int = 1) -> float:
    """
    Calculate Fresnel zone radius at midpoint.
    
    Args:
        distance_m: Total link distance in meters
        frequency_mhz: Frequency in MHz
        zone_number: Fresnel zone number (typically 1)
    
    Returns:
        Fresnel zone radius in meters at midpoint
    """
    wavelength_m = 3e8 / (frequency_mhz * 1e6)  # c / f
    d1 = distance_m / 2  # midpoint
    d2 = distance_m / 2
    
    radius = np.sqrt(zone_number * wavelength_m * d1 * d2 / (d1 + d2))
    return radius


