from typing import Tuple, Dict, List

import torch
from sklearn.metrics import accuracy_score
from torch import Tensor
from torch.nn import CrossEntropyLoss
from torch.optim import AdamW
from torch.optim.lr_scheduler import OneCycleLR
from torchvision.datasets import CIFAR10
from torchvision.models import resnet18
from torchvision.transforms import ToTensor

from xztrainer import XZTrainer, XZTrainerConfig, SchedulerType, SavePolicy, XZTrainable, BaseContext, DataType, \
    ModelOutputType, ClassifierType
from xztrainer.engine.standard import StandardEngineConfig
from xztrainer.logger.compose import ComposeLoggingEngineConfig
from xztrainer.logger.stream import StreamLoggingEngineConfig
from xztrainer.logger.tensorboard import TensorboardLoggingEngineConfig

if __name__ == '__main__':
    dataset_train = CIFAR10(root='./cifar10', download=True, train=True, transform=ToTensor())
    dataset_test = CIFAR10(root='./cifar10', download=True, train=False, transform=ToTensor())


    class SimpleTrainable(XZTrainable):
        def __init__(self):
            self.loss = CrossEntropyLoss()

        def step(self, context: BaseContext, data: DataType) -> Tuple[Tensor, Dict[str, ModelOutputType]]:
            img, label = data
            logits = context.model(img)
            preds = torch.argmax(logits, dim=1)
            loss = self.loss(logits, label)

            return loss, {'predictions': preds, 'targets': label}

        def calculate_metrics(
                self,
                context: BaseContext,
                model_outputs: Dict[str, List]
        ) -> Dict[ClassifierType, float]:
            return {'accuracy': accuracy_score(model_outputs['targets'], model_outputs['predictions'])}


    trainer = XZTrainer(
        config=XZTrainerConfig(
            batch_size=128,
            batch_size_eval=256,
            epochs=10,
            optimizer=lambda module: AdamW(module.parameters(), lr=1e-3, weight_decay=1e-4),
            engine=StandardEngineConfig(),
            experiment_name='cifar10',
            gradient_clipping=1.0,
            scheduler=lambda optimizer, total_steps: OneCycleLR(optimizer, 1e-3, total_steps),
            scheduler_type=SchedulerType.STEP,
            shuffle_train_dataset=True,
            dataloader_num_workers=8,
            accumulation_batches=4,
            print_steps=10,
            eval_steps=50,
            save_policy=SavePolicy.EVERY_EPOCH,
            logger=TensorboardLoggingEngineConfig()
            # logger=ComposeLoggingEngineConfig(TensorboardLoggingEngineConfig(), StreamLoggingEngineConfig())
        ),
        model=resnet18(pretrained=False, num_classes=10),
        trainable=SimpleTrainable()
    )
    trainer.train(dataset_train, dataset_test)
