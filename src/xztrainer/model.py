import multiprocessing
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Callable, List, Optional, Any

from torch import nn
from torch.optim import Optimizer
from torch.utils.data.dataloader import default_collate

from xztrainer.engines import TrainingEngineConfig
from xztrainer.logger.base import LoggingEngineConfig
from xztrainer.logger.null import NullLoggingEngineConfig


class SchedulerType(Enum):
    STEP = 'step'
    EPOCH = 'epoch'


class SavePolicy(Enum):
    NEVER = 'never'
    LAST_EPOCH = 'last_epoch'
    EVERY_EPOCH = 'every_epoch'


class LRSchedulerProtocol(Protocol):
    def step(self):
        ...


@dataclass
class XZTrainerConfig:
    batch_size: int
    batch_size_eval: int
    epochs: int
    optimizer: Callable[[nn.Module], Optimizer]
    engine: TrainingEngineConfig

    experiment_name: str = 'master'
    gradient_clipping: float = 1.0
    scheduler: Optional[Callable[[Optimizer, int], LRSchedulerProtocol]] = None
    scheduler_type: Optional[SchedulerType] = None
    shuffle_train_dataset: bool = False
    dataloader_num_workers: int = multiprocessing.cpu_count()
    accumulation_batches: int = 1
    print_steps: int = 100
    save_policy: SavePolicy = SavePolicy.EVERY_EPOCH
    save_dir: str = 'checkpoint'
    collate_fn: Callable[[List[object]], Any] = default_collate
    logger: LoggingEngineConfig = NullLoggingEngineConfig()
