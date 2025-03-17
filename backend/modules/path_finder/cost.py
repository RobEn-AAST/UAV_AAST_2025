from typing import List, Tuple
from modules.config import MissionConfig

def calc_path_cost(path: List[Tuple[float, float]], fence: List[Tuple[float, float]]) -> float:
    MissionConfig.safe_fence_dist