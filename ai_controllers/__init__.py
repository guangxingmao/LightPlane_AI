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
from .ai_decision_controller import AIDecisionController, create_ai_decision_controller
from .ai_game_env import AIGameEnvironment
from .game_strategy_controller import GameStrategyController, create_game_strategy_controller
from .game_strategy_env import GameStrategyEnvironment
from .integrated_plane_env import IntegratedPlaneFighterEnv
from .integrated_ai_controller import IntegratedAIController, create_integrated_ai_controller

__all__ = [
    'TrainedAIController',
    'HybridAIController', 
    'create_ai_controller',
    'OptimizedAIController',
    'PlaneFighterEnv',
    'AIDecisionController',
    'create_ai_decision_controller',
    'AIGameEnvironment',
    'GameStrategyController',
    'create_game_strategy_controller',
    'GameStrategyEnvironment',
    'IntegratedPlaneFighterEnv',
    'IntegratedAIController',
    'create_integrated_ai_controller'
]

__version__ = '2.0.0'
__author__ = 'LightPlane AI Team'
