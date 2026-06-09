#!/usr/bin/env python

# Copyright 2025 The HuggingFace Inc. team. All rights reserved.
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

"""CPU-only, weight-free smoke test for the PI05 + DynaFLIP injection
(maps analysis/2605.30350/design.md onto the lerobot pi05 base).

Covers both injection modes' pure / structural pieces — the zero-init
projection convention (copy_branch) and the zero-init gated cross-attention
(bridge_attention), config defaults / validation / registration, the subclass
seam overrides, and factory wiring. The full expert forward (copy-branch pass
or per-layer cross-attention over the action stream) is NOT exercised: it needs
the PaliGemma / gemma weights and the heavy model build, per the foundry §G
contract. Numerical behavior-preservation (zero-init -> identity) is guaranteed
by construction and asserted here at the module level.
"""

import pytest
import torch

from lerobot.policies.factory import get_policy_class, make_policy_config
from lerobot.policies.pi05.configuration_pi05 import PI05Config
from lerobot.policies.pi05.configuration_pi05_dynaflip import PI05DynaflipConfig
from lerobot.policies.pi05.modeling_pi05 import PI05Policy, PI05Pytorch
from lerobot.policies.pi05.modeling_pi05_dynaflip import (
    DynaflipBridgeInjector,
    PI05DynaflipPolicy,
    PI05DynaflipPytorch,
    zero_init_linear,
)


def test_zero_init_linear_outputs_zero():
    # PVI zero-init: the residual is EXACTLY zero at init -> identity, so the
    # injected policy equals the frozen base until training learns it in.
    lin = zero_init_linear(8, 16)
    out = lin(torch.randn(4, 8))
    assert out.shape == (4, 16)
    assert torch.count_nonzero(out) == 0


def test_zero_init_linear_learns_after_update():
    # Once perturbed, the projection is a live (non-dead) path.
    lin = zero_init_linear(8, 16)
    with torch.no_grad():
        lin.weight.add_(torch.randn_like(lin.weight))
    assert torch.count_nonzero(lin(torch.randn(4, 8))) > 0


def test_bridge_injector_zero_gate_is_identity():
    # bridge_attention: g init 0 -> tanh(g)=0 -> residual EXACTLY zero, even
    # though the cross-attention weights are randomly initialized. This is the
    # VLA-Adapter zero-init-gate behavior-preservation property.
    inj = DynaflipBridgeInjector(width=16, num_layers=3, num_heads=4)
    query = torch.randn(2, 5, 16)  # (B, chunk, width)
    kv = torch.randn(2, 7, 16)  # (B, L, width)
    res = inj(layer_idx=1, query=query, kv=kv)
    assert res.shape == (2, 5, 16)
    assert torch.count_nonzero(res) == 0


def test_bridge_injector_learns_after_gate_update():
    # Once the gate leaves zero, the cross-attention residual is a live path.
    inj = DynaflipBridgeInjector(width=16, num_layers=3, num_heads=4)
    with torch.no_grad():
        inj.gate.add_(1.0)
    res = inj(layer_idx=0, query=torch.randn(2, 5, 16), kv=torch.randn(2, 7, 16))
    assert torch.count_nonzero(res) > 0


def test_config_defaults_reproduce_base_behavior():
    cfg = PI05DynaflipConfig()
    # Default OFF -> identical to vanilla PI05.
    assert cfg.inject_dynaflip is False
    # Default mode is the faithful PVI copy-branch (preserves prior behavior).
    assert cfg.dynaflip_inject_mode == "copy_branch"
    # Patch-token feature dim (DINOv2-B token width), not the pooled 1536.
    assert cfg.dynaflip_feature_dim == 768
    assert cfg.dynaflip_feature_key == "observation.dynaflip_feature"
    assert isinstance(cfg, PI05Config)


def test_config_accepts_bridge_attention_mode():
    cfg = PI05DynaflipConfig(dynaflip_inject_mode="bridge_attention", dynaflip_num_heads=8)
    assert cfg.dynaflip_inject_mode == "bridge_attention"
    assert cfg.dynaflip_gate_per_layer is True


def test_config_rejects_out_of_range_values():
    with pytest.raises(ValueError):
        PI05DynaflipConfig(dynaflip_feature_dim=0)
    with pytest.raises(ValueError):
        PI05DynaflipConfig(dynaflip_inject_mode="not_a_mode")
    with pytest.raises(ValueError):
        PI05DynaflipConfig(dynaflip_num_heads=0)


def test_config_action_query_reserved_not_implemented():
    # CA2 (ActionQuery + proprio) is reserved but not wired in the first cut.
    with pytest.raises(NotImplementedError):
        PI05DynaflipConfig(dynaflip_use_action_query=True)


def test_registered_type_name():
    assert PI05DynaflipConfig().type == "pi05_dynaflip"


def test_class_hierarchy():
    assert issubclass(PI05DynaflipPytorch, PI05Pytorch)
    assert issubclass(PI05DynaflipPolicy, PI05Policy)
    assert PI05DynaflipPolicy.name == "pi05_dynaflip"


def test_base_seams_present():
    # Factory seam for the core model ...
    assert hasattr(PI05Policy, "_build_model")
    # ... and the per-layer expert injection callback hook on the base model
    # (an instance attr defaulting to None; the source wires it in __init__).
    import inspect

    from lerobot.policies.pi05 import modeling_pi05

    src = inspect.getsource(modeling_pi05.PaliGemmaWithExpertModel)
    assert "expert_layer_injector" in src


def test_subclass_overrides_in_place():
    # The copy-branch subclass overrides exactly the seams it needs.
    for name in ("_build_model",):
        assert name in PI05DynaflipPolicy.__dict__
    for name in ("embed_suffix", "_inject_expert_layer", "_compute_copy_hidden", "set_dynaflip_feature"):
        assert name in PI05DynaflipPytorch.__dict__


def test_factory_resolves_new_policy_name():
    assert get_policy_class("pi05_dynaflip") is PI05DynaflipPolicy
    cfg = make_policy_config("pi05_dynaflip")
    assert isinstance(cfg, PI05DynaflipConfig)
