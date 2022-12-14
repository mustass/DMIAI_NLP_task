from turtle import forward
from omegaconf import DictConfig
from regex import X
from torch import nn

from methazAI.utils.technical_utils import load_obj
from transformers import BertModel, BertForSequenceClassification
import torch.nn.functional as F


class BERT4SC(nn.Module):
    def __init__(self, cfg: DictConfig) -> None:
        """
        Model class.

        Args:
            cfg: main config
        """
        super().__init__()

        self.model = BertForSequenceClassification.from_pretrained(
            "bert-base-uncased",
            num_labels=cfg.model.params.n_clas,
            return_dict=cfg.model.params.return_dict,
        )

        # self.model.classifier.add_module('bert_activation', nn.ReLU())
        # self.model.classifier.add_module('prediction', nn.Linear(cfg.model.params.hidden_size, cfg.model.params.n_clas))

        if cfg.model.params.finetune:
            for param in self.model.bert.parameters():
                param.requires_grad = False

            for param in self.model.classifier.parameters():
                param.requires_grad = True

    def forward(self, x, mask):
        output = self.model(x, mask)
        return output["logits"]


class BERT(nn.Module):
    def __init__(self, cfg: DictConfig) -> None:
        """
        Model class.

        Args:
            cfg: main config
        """
        super(BERT, self).__init__()

        self.bert = BertModel.from_pretrained("bert-base-uncased")
        self.dropout = nn.Dropout(cfg.model.params.dropout)
        self.l1 = nn.Linear(768,512)
        self.l2 = nn.Linear(512,512)
        self.output = nn.Linear(512, cfg.model.params.n_clas)

        if cfg.model.params.finetune:
            for param in self.bert.parameters():
                param.requires_grad = False

    def forward(self, input_id, mask):
        _, pooled_output = self.bert(
            input_ids=input_id, attention_mask=mask, return_dict=False
        )
        dropout_output = self.dropout(pooled_output)
        dropout_output = self.dropout(F.relu(self.l1(dropout_output)))
        dropout_output = self.dropout(F.relu(self.l2(dropout_output)))
        output = self.output(dropout_output)
        return output
