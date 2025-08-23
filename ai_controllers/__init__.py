"""
AI控制器包
包含所有AI相关的模块和类
"""

from .trained_ai_controller import (
    TrainedAIController,
    HybridAIController,
    create_ai_controller
)

from .optimized_ai_controller import OptimizedAIController
from .plane_fighter_env import PlaneFighterEnv

__all__ = [
    'TrainedAIController',
    'HybridAIController', 
    'create_ai_controller',
    'OptimizedAIController',
    'PlaneFighterEnv'
]

__version__ = '1.0.0'
__author__ = 'LightPlane AI Team'
