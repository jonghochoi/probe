#!/usr/bin/env python

# Copyright 2025 Physical Intelligence and The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CPU smoke test for the pi0.5 Bridge-Attention port (arXiv:2509.09372).

PROBE's *executable* foundry artifact — the runnable counterpart of
``impl.patch``. The validation §🧬 check installs the foundry at its pinned commit
(`scripts/ensure-foundry-runtime.sh lerobot`), applies ``impl.patch`` to that
checkout, and runs this file with pytest. No GPU, no checkpoint, no HF download:
it validates the pure pieces (the gated-attention math: gate=1 parity,
suffix->prefix locality, gate effect) and the config/factory wiring. The heavy
PaliGemma-backed forward is left to a real training run.
"""

import pytest
import torch

from lerobot.configs import PreTrainedConfig
from lerobot.policies.factory import get_policy_class, make_policy_config
from lerobot.policies.pi05.configuration_pi05_bridge import PI05BridgeConfig
from lerobot.policies.pi05.modeling_pi05 import gated_eager_attention
from lerobot.policies.pi05.modeling_pi05_bridge import PI05BridgePolicy, gate_count_for


class _DummyAttn(torch.nn.Module):
    """Minimal stand-in exposing what (gated) eager attention reads."""

    num_key_value_groups = 1


def _qkv(b, h, t, d, seed=0):
    g = torch.Generator().manual_seed(seed)
    q = torch.randn(b, h, t, d, generator=g)
    k = torch.randn(b, h, t, d, generator=g)
    v = torch.randn(b, h, t, d, generator=g)
    return q, k, v


def _ref_eager(q, k, v, scaling):
    """Inline reference eager attention (no transformers dependency)."""
    aw = torch.matmul(q, k.transpose(2, 3)) * scaling
    aw = torch.softmax(aw, dim=-1, dtype=torch.float32).to(q.dtype)
    return torch.matmul(aw, v).transpose(1, 2).contiguous()


def test_gate_one_matches_vanilla_eager():
    """tanh(g)=1 must leave attention numerically identical to ungated eager."""
    b, h, t, d, prefix_len = 2, 4, 7, 8, 5
    q, k, v = _qkv(b, h, t, d, seed=0)
    mod = _DummyAttn().eval()
    scaling = d**-0.5

    ref = _ref_eager(q, k, v, scaling)
    gated, _ = gated_eager_attention(mod, q, k, v, None, scaling, torch.tensor(1.0), prefix_len)
    assert torch.allclose(ref, gated, atol=1e-6)


def test_gate_is_local_to_suffix_to_prefix_block():
    """The gate must change only suffix query rows; prefix rows stay identical."""
    b, h, t, d, prefix_len = 2, 4, 7, 8, 5
    q, k, v = _qkv(b, h, t, d, seed=1)
    mod = _DummyAttn().eval()
    scaling = d**-0.5

    out_closed, _ = gated_eager_attention(mod, q, k, v, None, scaling, torch.tensor(0.0), prefix_len)
    out_open, _ = gated_eager_attention(mod, q, k, v, None, scaling, torch.tensor(1.0), prefix_len)

    # out shape is (B, T_q, H, D) after transpose; index the query axis.
    assert torch.allclose(out_closed[:, :prefix_len], out_open[:, :prefix_len], atol=1e-6)
    assert not torch.allclose(out_closed[:, prefix_len:], out_open[:, prefix_len:], atol=1e-4)


def test_gate_none_path_is_noop_dimension():
    """prefix_len=None (e.g. suffix-only) must not raise and must match eager."""
    b, h, t, d = 2, 4, 6, 8
    q, k, v = _qkv(b, h, t, d, seed=2)
    mod = _DummyAttn().eval()
    scaling = d**-0.5
    gated, _ = gated_eager_attention(mod, q, k, v, None, scaling, torch.tensor(0.3), None)
    assert torch.allclose(_ref_eager(q, k, v, scaling), gated, atol=1e-6)


def test_gate_backprops_to_scalar():
    """The scalar gate must receive gradient through the suffix->prefix block."""
    b, h, t, d, prefix_len = 1, 2, 5, 8, 3
    q, k, v = _qkv(b, h, t, d, seed=3)
    mod = _DummyAttn().eval()
    scaling = d**-0.5
    g = torch.zeros(1, requires_grad=True)
    out, _ = gated_eager_attention(mod, q, k, v, None, scaling, torch.tanh(g), prefix_len)
    out.sum().backward()
    assert g.grad is not None and torch.isfinite(g.grad).all()
    assert g.grad.abs().sum() > 0


def test_gate_count_matches_expert_depth():
    cfg = PI05BridgeConfig()
    assert gate_count_for(cfg.action_expert_variant) == 18  # gemma_300m depth


def test_config_defaults_and_registration():
    cfg = PI05BridgeConfig()
    assert cfg.bridge_attention is False  # vanilla pi0.5 by default
    assert cfg.bridge_gate_init == 0.0  # VLA-Adapter faithful (tanh(0)=0)

    assert "pi05_bridge" in PreTrainedConfig.get_known_choices()
    assert PreTrainedConfig.get_choice_class("pi05_bridge") is PI05BridgeConfig
    assert make_policy_config("pi05_bridge").type == "pi05_bridge"
    assert get_policy_class("pi05_bridge") is PI05BridgePolicy


def test_bridge_gate_init_override():
    cfg = PI05BridgeConfig(bridge_attention=True, bridge_gate_init=4.0)
    assert cfg.bridge_attention is True
    assert pytest.approx(torch.tanh(torch.tensor(cfg.bridge_gate_init)).item(), abs=1e-3) == 0.999
