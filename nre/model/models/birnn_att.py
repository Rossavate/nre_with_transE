"""
    Overall model architecture for relation extraction
"""

import torch
import torch.nn as nn

from nre.model.base_model import BaseModel
from nre.layers.embedding.embedding import Embedding
from nre.layers.encoder.birnn import BiRNNEncoder
from nre.layers.selector.attention import Attention
from nre.layers.classifier.classifier import Classifier


class BiRNNATT(BaseModel):
    def __init__(self, pretrained_word_embeddings, gpu_utils, opt):
        super(BiRNNATT, self).__init__(pretrained_word_embeddings, gpu_utils, opt)

        self.embedding_layer = Embedding(pretrained_word_embeddings, opt)
        self.encoder_layer = gpu_utils.module_to_parallel(BiRNNEncoder(opt))
        self.selector_layer = Attention(opt.hidden_size, opt)
        self.classifier_layer = Classifier(opt)

    def forward(self, is_train, input_word, input_pos1, input_pos2,
        input_mask, input_type, input_lens, input_scope, type_label, input_label=None, label_for_select=None):

        embeddings = self.embedding_layer(input_word, input_pos1, input_pos2)
        encoder_out = self.encoder_layer(embeddings, input_lens)
        logits = self.selector_layer(encoder_out, input_scope, is_train, label_for_select)

        return self.model_output(is_train, logits, input_label)
