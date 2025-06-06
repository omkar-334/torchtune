# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

from typing import Optional

import pytest

from tests.common import ASSETS

from torchtune.data import Message
from torchtune.models.qwen2 import qwen2_tokenizer


class TestQwenTokenizer:
    def tokenizer(self, max_seq_len: Optional[int] = None):
        return qwen2_tokenizer(
            path=str(ASSETS / "tiny_bpe_vocab.json"),
            merges_file=str(ASSETS / "tiny_bpe_merges.txt"),
            special_tokens_path=str(ASSETS / "tiny_bpe_tokenizer.json"),
            max_seq_len=max_seq_len,
        )

    @pytest.fixture
    def messages(self):
        return [
            Message(
                role="user",
                content="Below is an instruction that describes a task. Write a response "
                "that appropriately completes the request.\n\n### Instruction:\nGenerate "
                "a realistic dating profile bio.\n\n### Response:\n",
                masked=True,
            ),
            Message(
                role="assistant",
                content="I'm an outgoing and friendly person who loves spending time with "
                "friends and family. I'm also a big-time foodie and love trying out new "
                "restaurants and different cuisines. I'm a big fan of the arts and enjoy "
                "going to museums and galleries. I'm looking for someone who shares my "
                "interest in exploring new places, as well as someone who appreciates a "
                "good conversation over coffee.",
            ),
        ]

    def test_tokenize_messages(self, messages):
        tokenizer = self.tokenizer()
        tokens, mask = tokenizer.tokenize_messages(messages)

        # fmt: off
        expected_tokens = [2001, 273, 105, 94, 33, 214, 174, 156, 194, 130, 197, 184, 446, 789, 113, 98, 1914, 13, 346,
                           788, 98, 706, 102, 182, 184, 1916, 176, 762, 83, 113, 103, 874, 269, 13, 94, 94, 2, 2, 2,
                           483, 197, 25, 94, 885, 98, 1226, 1960, 348, 114, 1123, 399, 1583, 78, 13, 94, 94, 2, 2, 2,
                           360, 1733, 102, 182, 25, 94, 2002, 94, 2001, 397, 251, 249, 94, 40, 1791, 194, 453, 70, 78,
                           114, 120, 967, 176, 618, 628, 1275, 794, 294, 1095, 445, 212, 1356, 120, 1299, 13, 223, 1791,
                           451, 98, 127, 181, 1047, 375, 915, 380, 120, 1448, 1732, 114, 453, 447, 1219, 64, 187, 921,
                           120, 742, 107, 84, 122, 893, 13, 223, 1791, 98, 127, 181, 123, 124, 131, 103, 744, 82, 120,
                           1506, 416, 114, 128, 1429, 182, 253, 82, 120, 163, 330, 105, 262, 13, 223, 1791, 155, 1551,
                           171, 1951, 628, 296, 64, 237, 886, 1390, 130, 883, 1678, 447, 306, 279, 113, 11, 215, 785,
                           215, 1951, 628, 378, 101, 66, 72, 593, 98, 984, 208, 1580, 167, 510, 737, 318, 1278, 13,
                           2002] # noqa
        # fmt: on

        expected_mask = [True] * 67 + [False] * 121
        assert expected_tokens == tokens
        assert expected_mask == mask

        formatted_messages = tokenizer.decode(tokens)
        expected_formatted_messages = (
            f"<|im_start|>user\n{messages[0].text_content}<|im_end|>\n"
            f"<|im_start|>assistant\n{messages[1].text_content}<|im_end|>"
        )

        assert expected_formatted_messages == formatted_messages

    def test_tokenize_messages_gt_max_seq_len(self, messages):
        # Super basic test to make sure max_seq_len is working properly
        tokenizer = self.tokenizer(max_seq_len=10)
        tokens, mask = tokenizer.tokenize_messages(messages)
        assert len(tokens) == 10
        assert len(mask) == 10

    def test_tokenize_message_drop_eos(self, messages):
        tokenizer = self.tokenizer()

        # fmt: off
        expected_tokens = [2001, 273, 105, 94, 33, 214, 174, 156, 194, 130, 197, 184, 446, 789, 113, 98, 1914, 13, 346,
                           788, 98, 706, 102, 182, 184, 1916, 176, 762, 83, 113, 103, 874, 269, 13, 94, 94, 2, 2, 2,
                           483, 197, 25, 94, 885, 98, 1226, 1960, 348, 114, 1123, 399, 1583, 78, 13, 94, 94, 2, 2, 2,
                           360, 1733, 102, 182, 25, 94, 2002, 94, 2001, 397, 251, 249, 94, 40, 1791, 194, 453, 70, 78,
                           114, 120, 967, 176, 618, 628, 1275, 794, 294, 1095, 445, 212, 1356, 120, 1299, 13, 223, 1791,
                           451, 98, 127, 181, 1047, 375, 915, 380, 120, 1448, 1732, 114, 453, 447, 1219, 64, 187, 921,
                           120, 742, 107, 84, 122, 893, 13, 223, 1791, 98, 127, 181, 123, 124, 131, 103, 744, 82, 120,
                           1506, 416, 114, 128, 1429, 182, 253, 82, 120, 163, 330, 105, 262, 13, 223, 1791, 155, 1551,
                           171, 1951, 628, 296, 64, 237, 886, 1390, 130, 883, 1678, 447, 306, 279, 113, 11, 215, 785,
                           215, 1951, 628, 378, 101, 66, 72, 593, 98, 984, 208, 1580, 167, 510, 737, 318, 1278,
                           13]  # noqa
        # fmt: on

        expected_mask = [True] * 67 + [False] * 120
        tokens, mask = tokenizer.tokenize_messages(messages, add_end_tokens=False)
        assert tokens == expected_tokens
        assert mask == expected_mask
